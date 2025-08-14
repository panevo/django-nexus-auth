import pytest
from django.test import SimpleTestCase, override_settings
from nexus_auth.settings import NexusAuthSettings, DEFAULTS


@override_settings(NEXUS_AUTH={
    "CONFIG": {
        "microsoft_tenant": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tenant_id": "test_tenant_id",
        },
        "google": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        },
        "custom": {
            "client_id": "id1",
            "client_secret": "secret1",
        },
    },
    "PROVIDER_BUILDERS": {
        "custom": "path.to.CustomProviderBuilder",
    },
})
class TestNexusAuthSettings(SimpleTestCase):
    
    def setUp(self):
        """Create a NexusAuthSettings instance with default settings."""
        self.nexus_auth_settings = NexusAuthSettings(defaults=DEFAULTS)

    def _builders_config(self):
        config = self.nexus_auth_settings.get_providers_config()
        self.assertEqual(config, {
            "microsoft_tenant": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "tenant_id": "test_tenant_id",
            },
            "google": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            },
            "custom": {
                "client_id": "id1",
                "client_secret": "secret1",
            },
        })

    def test_default_get_provider_builders(self):
        """Test that get_provider_builders returns the correct providers."""
        providers = self.nexus_auth_settings.get_provider_builders()
        # Check that default providers are merged with the additional providers
        self.assertEqual(providers, {
            "google": "nexus_auth.providers.google.GoogleOAuth2ProviderBuilder",
            "microsoft_tenant": "nexus_auth.providers.microsoft.MicrosoftEntraTenantOAuth2ProviderBuilder",
            "custom": "path.to.CustomProviderBuilder",
        })

    @override_settings(NEXUS_AUTH={
        "CONFIG": {
            "microsoft_tenant": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "tenant_id": "test_tenant_id",
            },
            "google": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            },
            "custom": {
                "client_id": "id1",
                "client_secret": "secret1",
            },
        },
        "PROVIDER_BUILDERS": {
            "custom": "path.to.CustomProviderBuilder",
            # Override the default providers to test overwriting
            "google": "my.custom.GoogleProviderBuilder",
            "microsoft_tenant": "my.custom.MicrosoftProviderBuilder",
        },
    })
    def test_get_provider_builders_overwrite_defaults(self):
        """Test additional providers overwrite default providers."""
        providers = self.nexus_auth_settings.get_provider_builders()
        self.assertEqual(providers, {
            "google": "my.custom.GoogleProviderBuilder",  # Overwritten by method-level settings
            "microsoft_tenant": "my.custom.MicrosoftProviderBuilder",  # Overwritten by method-level settings
            "custom": "path.to.CustomProviderBuilder",
        })

    def test_default_providers_handler(self):
        """Test that the default handler is used when PROVIDERS_HANDLER is not set."""
        user_settings = self.nexus_auth_settings._get_user_settings()
        # Assert that the default handler is used
        self.assertEqual(user_settings['PROVIDERS_HANDLER'], 'nexus_auth.utils.load_providers_config')
