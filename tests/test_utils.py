from nexus_auth.providers.google import GoogleOAuth2Provider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider
from nexus_auth.utils import get_oauth_provider, get_provider_types


def test_get_provider_types():
   
    provider_types = get_provider_types(None) 
    assert provider_types == ['microsoft_tenant', 'google']

def test_get_oauth_provider():
    provider = get_oauth_provider('microsoft_tenant')
    assert provider is not None
    assert isinstance(provider, MicrosoftEntraTenantOAuth2Provider)

    provider = get_oauth_provider('google')
    assert provider is not None
    assert isinstance(provider, GoogleOAuth2Provider)
