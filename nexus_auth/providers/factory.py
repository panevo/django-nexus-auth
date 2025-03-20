from typing import Optional

from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.settings import nexus_settings
from django.utils.module_loading import import_string


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


# Load the provider builders specified in the PROVIDER_BUILDERS setting
providers = IdentityProviderFactory()
builder_config = nexus_settings.get_provider_builders()
for provider_type, builder_path in builder_config.items():
    builder = import_string(builder_path)
    providers.register_builder(provider_type, builder())
