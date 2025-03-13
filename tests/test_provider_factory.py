import pytest
from nexus_auth.providers.factory import IdentityProviderFactory
from nexus_auth.models import ProviderType
from nexus_auth.providers.google import GoogleOAuth2Provider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider

def test_create_provider_valid_type():
    """Test creating a provider with a valid type."""
    provider = IdentityProviderFactory.create_provider(
        provider_type=ProviderType.GOOGLE,
        client_id='test_client_id',
        client_secret='test_client_secret'
    )
    assert isinstance(provider, GoogleOAuth2Provider)

    provider = IdentityProviderFactory.create_provider(
        provider_type=ProviderType.MICROSOFT_TENANT,
        client_id='test_client_id',
        client_secret='test_client_secret',
        tenant_id='test_tenant_id'
    )
    assert isinstance(provider, MicrosoftEntraTenantOAuth2Provider)

def test_create_provider_invalid_type():
    """Test creating a provider with an invalid type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid provider type: invalid_type"):
        IdentityProviderFactory.create_provider(
            provider_type='invalid_type',
            client_id='test_client_id',
            client_secret='test_client_secret'
        )