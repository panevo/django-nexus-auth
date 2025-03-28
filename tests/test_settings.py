import pytest
from nexus_auth.settings import NexusAuthSettings, DEFAULTS


@pytest.fixture
def default_settings():
    return {
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
        },
        "PROVIDER_BUILDERS": {
            "custom": "path.to.CustomProviderBuilder",
        },
    }

@pytest.fixture
def nexus_auth_settings(default_settings):
    """Create a NexusAuthSettings instance with default settings."""
    return NexusAuthSettings(user_settings=default_settings, defaults=DEFAULTS)

def test_default_get_providers_config(nexus_auth_settings):
    config = nexus_auth_settings.providers_config()
    assert config == {
        "microsoft_tenant": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tenant_id": "test_tenant_id",
        },
        "google": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        },
    }

def test_get_providers(nexus_auth_settings):
    """Test that get_provider_builders returns the correct providers."""
    providers = nexus_auth_settings.get_provider_builders()
    # Check that default providers are merged with the additional providers
    assert providers == {
        "google": "nexus_auth.providers.google.GoogleOAuth2ProviderBuilder",
        "microsoft_tenant": "nexus_auth.providers.microsoft.MicrosoftEntraTenantOAuth2ProviderBuilder",
        "custom": "path.to.CustomProviderBuilder",
    }

def test_get_providers_overwrite_defaults():
    """Test additional providers overwrite default providers."""
    settings = NexusAuthSettings(user_settings={
        "PROVIDER_BUILDERS": {
            "google": "my.custom.GoogleProviderBuilder",
        },
    }, defaults=DEFAULTS)

    providers = settings.get_provider_builders()
    assert providers == {
        "google": "my.custom.GoogleProviderBuilder",
        "microsoft_tenant": "nexus_auth.providers.microsoft.MicrosoftEntraTenantOAuth2ProviderBuilder",
    }

def test_getattr_defaults():
    """Test that getattr returns default values."""
    settings = NexusAuthSettings(defaults={"SOME_SETTING": "default_value"})
    assert settings.SOME_SETTING == "default_value"
    with pytest.raises(AttributeError):
        settings.NON_EXISTENT_SETTING

def test_default_providers_handler():
    """Test that the default handler is used when PROVIDERS_HANDLER is not set."""
    # Simulate settings with CONFIG set but without PROVIDERS_HANDLER
    user_settings = {
        'CONFIG': {'provider1': {'client_id': 'id1', 'client_secret': 'secret1'}}
    }

    nexus_settings = NexusAuthSettings(user_settings=user_settings)
    # Assert that the default handler is used
    assert nexus_settings._user_settings['PROVIDERS_HANDLER'] == 'nexus_auth.utils.load_providers_config'
