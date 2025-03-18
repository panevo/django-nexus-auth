from nexus_auth.providers.google import GoogleOAuth2ProviderBuilder
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2ProviderBuilder
from nexus_auth.providers.base import OAuth2IdentityProvider
from typing import Optional

class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class IdentityProviderFactory(ObjectFactory):
    """Factory for identity providers."""

    def get(self, provider_type: str, **kwargs) -> Optional[OAuth2IdentityProvider]:
        return self.create(provider_type, **kwargs)


providers = IdentityProviderFactory()
providers.register_builder('google', GoogleOAuth2ProviderBuilder())
providers.register_builder('microsoft_tenant', MicrosoftEntraTenantOAuth2ProviderBuilder())
