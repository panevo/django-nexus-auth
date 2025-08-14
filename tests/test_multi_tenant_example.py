import copy
from unittest.mock import Mock, patch
from django.test import TestCase
from django.test.utils import override_settings
from nexus_auth.settings import nexus_settings
from nexus_auth.views import OAuthProvidersView
from rest_framework.test import APIRequestFactory
from typing import Optional, Dict


def create_mock_request(tenant_schema_name):
    """Create a mock request object with tenant information."""
    request = Mock()
    request.tenant = Mock()
    request.tenant.schema_name = tenant_schema_name
    return request


TENANT_CONFIG = {
    "tenant1": {
        "microsoft_tenant": {
            "CLIENT_ID": "tenant1-client-id-12345678",
            "CLIENT_SECRET": "tenant1-secret",
            "TENANT_ID": "tenant1-tenant-id",
        }
    },
    "tenant2": {
        "microsoft_tenant": {
            "CLIENT_ID": "tenant2-client-id-87654321",
            "CLIENT_SECRET": "tenant2-secret",
            "TENANT_ID": "tenant2-tenant-id",
        }
    },
}


# Example handler that loads providers config for the current tenant
def multi_tenant_load_providers_config(request) -> Optional[Dict[str, Dict[str, str]]]:
    """Get the provider configuration for the current tenant."""
    tenant = request.tenant
    if tenant and tenant.schema_name:
        return nexus_settings.providers_config_setting().get(tenant.schema_name)
    return None


@override_settings(NEXUS_AUTH={
    "CONFIG": TENANT_CONFIG,
    "PROVIDERS_HANDLER": "test_multi_tenant_example.multi_tenant_load_providers_config",
})
class TenantCacheTest(TestCase):
    """Tests that provider settings are correctly isolated per tenant in a multi-tenant setup."""

    def test_provider_config_is_isolated_between_tenants(self):
        """Ensure tenant1 and tenant2 each receive their own provider configuration."""
        tenant1_request = create_mock_request("tenant1")
        tenant1_result = nexus_settings.get_providers_config(request=tenant1_request)

        tenant2_request = create_mock_request("tenant2")
        tenant2_result = nexus_settings.get_providers_config(request=tenant2_request)

        self.assertEqual(tenant1_result, TENANT_CONFIG["tenant1"])
        self.assertEqual(tenant2_result, TENANT_CONFIG["tenant2"])
        self.assertNotEqual(tenant1_result, tenant2_result)

    @patch('nexus_auth.utils.build_oauth_provider')
    def test_oauth_providers_view_respects_tenant_config(self, mock_build_provider):
        """Ensure the /oauth/providers view returns tenant-specific provider data."""
        factory = APIRequestFactory()
        view = OAuthProvidersView()

        tenant1_request = factory.get('/oauth/providers')
        tenant1_request.tenant = Mock()
        tenant1_request.tenant.schema_name = "tenant1"

        tenant2_request = factory.get('/oauth/providers')
        tenant2_request.tenant = Mock()
        tenant2_request.tenant.schema_name = "tenant2"

        tenant1_response = view.get(tenant1_request)
        tenant2_response = view.get(tenant2_request)

        tenant1_auth_url = tenant1_response.data["providers"][0]["auth_url"]
        tenant2_auth_url = tenant2_response.data["providers"][0]["auth_url"]

        tenant2_has_correct_tenant = "tenant2-tenant-id" in tenant2_auth_url
        tenant2_has_correct_client = "tenant2-client-id-87654321" in tenant2_auth_url

        if not (tenant2_has_correct_tenant and tenant2_has_correct_client):
            self.fail("Multi-tenant configuration bug detected: tenant2 received tenant1's configuration.")

        self.assertNotEqual(tenant1_response.data, tenant2_response.data)
        self.assertIn("tenant1-tenant-id", tenant1_auth_url)
        self.assertIn("tenant2-tenant-id", tenant2_auth_url)

    @patch('nexus_auth.utils.build_oauth_provider')
    def test_oauth_view_tenant_switching_no_leak(self, mock_build_provider):
        """Calling /oauth/providers for one tenant should not change the output for another tenant."""
        factory = APIRequestFactory()
        view = OAuthProvidersView()

        t1_request = factory.get('/oauth/providers')
        t1_request.tenant = Mock()
        t1_request.tenant.schema_name = "tenant1"

        t2_request = factory.get('/oauth/providers')
        t2_request.tenant = Mock()
        t2_request.tenant.schema_name = "tenant2"

        # Call tenant1 first, then tenant2, then tenant1 again
        resp1a = view.get(t1_request)
        resp2 = view.get(t2_request)
        resp1b = view.get(t1_request)

        self.assertEqual(resp1a.data, resp1b.data, "Tenant1's config changed after tenant2's request — possible state leak")
        self.assertNotEqual(resp1a.data, resp2.data, "Tenant1 and Tenant2 responses are identical — possible config leak")
