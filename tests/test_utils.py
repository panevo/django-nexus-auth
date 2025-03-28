from nexus_auth.providers.google import GoogleOAuth2Provider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider
from nexus_auth.utils import build_oauth_provider, load_providers_config
from nexus_auth.settings import nexus_settings

def test_build_oauth_provider():
    """
    Test build oauth provider function
    """
    providers_config = {
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
    provider = build_oauth_provider(provider_type='microsoft_tenant', providers_config=providers_config)
    assert provider is not None
    assert isinstance(provider, MicrosoftEntraTenantOAuth2Provider)

    provider = build_oauth_provider(provider_type='google', providers_config=providers_config)
    assert provider is not None
    assert isinstance(provider, GoogleOAuth2Provider)


def test_default_load_providers_config():
    """
    Test default load providers config function
    """
    config = load_providers_config()
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

