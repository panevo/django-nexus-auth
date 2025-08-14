import copy
from unittest.mock import Mock, patch
from django.conf import settings
from django.test import TestCase
from nexus_auth.settings import nexus_settings
from nexus_auth.views import OAuthProvidersView
from rest_framework.test import APIRequestFactory

from typing import Optional, Dict


def create_mock_request(tenant_schema_name):
    """Create a mock request object with tenant information.

    This mock request is used to simulate a request from a specific tenant for a multitenant application.
    """
    request = Mock()
    request.tenant = Mock()
    request.tenant.schema_name = tenant_schema_name
    return request

TENANT_CONFIG = {
    "panevo": {
        "microsoft_tenant": {
            "CLIENT_ID": "panevo-client-id-12345678",
            "CLIENT_SECRET": "panevo-secret",
            "TENANT_ID": "panevo-tenant-id",
        }
    },
    "panevo2": {
        "microsoft_tenant": {
            "CLIENT_ID": "panevo2-client-id-87654321",
            "CLIENT_SECRET": "panevo2-secret",
            "TENANT_ID": "panevo2-tenant-id",
        }
    },
}

# Example handler that loads providers config for the current tenant
def multi_tenant_load_providers_config(request) -> Optional[Dict[str, Dict[str, str]]]:
    """Get the provider configuration for the current tenant."""
    tenant = request.tenant
    if tenant and tenant.schema_name:
        print(f"Handler called for tenant: {tenant.schema_name}")
        
        # Get the full provider config
        full_config = nexus_settings.providers_config()
        print(f"Full config from nexus_settings: {full_config}")
        
        # Get the tenant-specific config
        provider_settings = full_config.get(tenant.schema_name)
        print(f"Tenant-specific config for {tenant.schema_name}: {provider_settings}")
        
        if provider_settings:
            return provider_settings

    return None


class TenantCacheTest(TestCase):
    def setUp(self):
        settings.NEXUS_AUTH = {
            "CONFIG": copy.deepcopy(TENANT_CONFIG),
            "PROVIDERS_HANDLER": "test_multi_tenant_example.multi_tenant_load_providers_config",
        }

    def test_old_settings_cache_issue(self):
        """Test that old settings module-level singleton causes caching bug in production."""
        
        
        # Simulate first request from panevo tenant
        panevo_request = create_mock_request("panevo")
        panevo_result = nexus_settings.get_providers_config(request=panevo_request)
        
        # Simulate second request from panevo2 tenant
        # In production, this would use the same cached singleton instance
        panevo2_request = create_mock_request("panevo2")
        panevo2_result = nexus_settings.get_providers_config(request=panevo2_request)
        
        print("OLD SETTINGS SINGLETON - panevo config:", panevo_result)
        print("OLD SETTINGS SINGLETON - panevo2 config:", panevo2_result)
        
        # The module-level singleton caches the first configuration it sees
        # This assertion will FAIL in production because both results will be the same
        # (both will return the config for whichever tenant was processed first)
        self.assertEqual(panevo_result, TENANT_CONFIG["panevo"])
        self.assertEqual(panevo2_result, TENANT_CONFIG["panevo2"])
        
        # This is the key assertion that will FAIL due to the singleton caching bug
        self.assertNotEqual(panevo_result, panevo2_result)

    @patch('nexus_auth.utils.build_oauth_provider')
    def test_oauth_providers_view_caching_bug(self, mock_build_provider):
        """Test that /oauth/providers view is affected by the caching bug."""
        
        factory = APIRequestFactory()
        view = OAuthProvidersView()
        
        # Create requests for different tenants
        panevo_request = factory.get('/oauth/providers')
        panevo_request.tenant = Mock()
        panevo_request.tenant.schema_name = "panevo"
        
        panevo2_request = factory.get('/oauth/providers')
        panevo2_request.tenant = Mock()
        panevo2_request.tenant.schema_name = "panevo2"
        
        # Call the view for both tenants
        panevo_response = view.get(panevo_request)
        panevo2_response = view.get(panevo2_request)
        
        print("OAUTH VIEW - panevo response:", panevo_response.data)
        print("OAUTH VIEW - panevo2 response:", panevo2_response.data)
        
        # Extract the auth URLs to see the actual tenant IDs and client IDs
        panevo_auth_url = panevo_response.data["providers"][0]["auth_url"]
        panevo2_auth_url = panevo2_response.data["providers"][0]["auth_url"]
        
        print(f"panevo auth URL: {panevo_auth_url}")
        print(f"panevo2 auth URL: {panevo2_auth_url}")
        
        # Check if panevo2 is getting its correct tenant-specific configuration
        panevo2_should_have_own_tenant = "panevo2-tenant-id" in panevo2_auth_url
        panevo2_should_have_own_client = "panevo2-client-id-87654321" in panevo2_auth_url
        
        if not panevo2_should_have_own_tenant or not panevo2_should_have_own_client:
            print("BUG DETECTED: panevo2 is getting panevo's configuration due to caching!")
            print(f"Expected panevo2-tenant-id in URL: {panevo2_should_have_own_tenant}")
            print(f"Expected panevo2-client-id-87654321 in URL: {panevo2_should_have_own_client}")
            
            # This assertion will FAIL, demonstrating the caching bug
            self.fail("Caching bug detected: panevo2 tenant is getting panevo's configuration!")
        
        # If we reach here, the bug is fixed
        self.assertNotEqual(panevo_response.data, panevo2_response.data)
        self.assertTrue("panevo-tenant-id" in panevo_auth_url)
        self.assertTrue("panevo2-tenant-id" in panevo2_auth_url)
