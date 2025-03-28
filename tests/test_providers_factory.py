import pytest
from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.providers.factory import IdentityProviderFactory, ObjectFactory
from nexus_auth.providers.google import GoogleOAuth2ProviderBuilder
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2ProviderBuilder


class MockBuilder:
    def __call__(self, **kwargs):
        return kwargs

def test_object_factory():
    """Test that the ObjectFactory creates objects using registered builders."""
    factory = ObjectFactory()
    mock_builder = MockBuilder()
    
    factory.register_builder("mock", mock_builder)
    obj = factory.create("mock", key1="value1")
    
    assert obj == {"key1": "value1"}
    
    with pytest.raises(ValueError, match="unknown_key"):
        factory.create("unknown_key")

def test_identity_provider_factory():
    """Test that the IdentityProviderFactory creates identity providers using registered builders."""
    factory = IdentityProviderFactory()
    
    google_provider_builder = GoogleOAuth2ProviderBuilder()
    microsoft_provider_builder = MicrosoftEntraTenantOAuth2ProviderBuilder()
    
    factory.register_builder("google", google_provider_builder)
    factory.register_builder("microsoft_tenant", microsoft_provider_builder)
    
    google_provider_config = {"client_id": "", "client_secret": ""}
    google_provider = factory.get("google", **google_provider_config)
    microsoft_provider_config = {"client_id": "", "client_secret": "", "tenant_id": ""}
    microsoft_provider = factory.get("microsoft_tenant", **microsoft_provider_config)
    
    assert isinstance(google_provider, OAuth2IdentityProvider)
    assert isinstance(microsoft_provider, OAuth2IdentityProvider)
    
    with pytest.raises(ValueError, match="unknown_provider"):
        factory.get("unknown_provider")
