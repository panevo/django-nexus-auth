from typing import Optional

from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.settings import nexus_settings
from django.utils.module_loading import import_string


class ObjectFactory:
    """Factory for creating objects."""

    def __init__(self):
        """Initialize the factory with no builders."""
        self._builders = {}

    def register_builder(self, key, builder):
        """Register a builder for a specific key.

        Args:
            key: The key for the builder.
            builder: The builder to register.
        """
        self._builders[key] = builder

    def create(self, key, **kwargs):
        """Create an object using the registered builder.

        Args:
            key: The key for the builder.
            **kwargs: Keyword arguments to pass to the builder.

        Returns:
            The created object.
        """
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class IdentityProviderFactory(ObjectFactory):
    """Factory for identity providers."""

    def get(self, provider_type: str, **kwargs) -> Optional[OAuth2IdentityProvider]:
        """Get an identity provider instance.

        Args:
            provider_type: The type of provider to get.
            **kwargs: Keyword arguments to pass to the builder.

        Returns:
            Optional[OAuth2IdentityProvider]: The identity provider instance.
        """
        return self.create(provider_type, **kwargs)


# Load the provider builders specified in the PROVIDER_BUILDERS setting
providers = IdentityProviderFactory()
builder_config = nexus_settings.get_provider_builders()
for provider_type, builder_path in builder_config.items():
    builder = import_string(builder_path)
    providers.register_builder(provider_type, builder())
