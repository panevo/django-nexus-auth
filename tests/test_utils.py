from nexus_auth.providers.google import GoogleOAuth2Provider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider
from nexus_auth.utils import get_oauth_provider, load_provider_config
from unittest.mock import MagicMock

def test_get_oauth_provider():
    mock_request = MagicMock()
    provider = get_oauth_provider(request=mock_request, provider_type='microsoft_tenant')
    assert provider is not None
    assert isinstance(provider, MicrosoftEntraTenantOAuth2Provider)

    provider = get_oauth_provider(request=mock_request, provider_type='google')
    assert provider is not None
    assert isinstance(provider, GoogleOAuth2Provider)


def test_default_load_provider_config():
    config = load_provider_config(None)
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

