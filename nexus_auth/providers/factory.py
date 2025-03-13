from nexus_auth.models import ProviderType
from nexus_auth.providers.google import GoogleOAuth2Provider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider
from nexus_auth.providers.base import OAuth2IdentityProvider
from typing import Optional


class IdentityProviderFactory:
    """Factory for identity providers."""

    PROVIDERS = {
        ProviderType.MICROSOFT_TENANT: MicrosoftEntraTenantOAuth2Provider,
        ProviderType.GOOGLE: GoogleOAuth2Provider,
    }

    @staticmethod
    def create_provider(
        provider_type: str,
        client_id: str,
        client_secret: str,
        tenant_id: Optional[str] = None,
    ) -> OAuth2IdentityProvider:
        """Create an identity provider instance.

        Args:
            provider_type: Type of provider to create
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tenant_id: Optional tenant ID for multi-tenant providers

        Returns:
            OAuth2IdentityProvider: Instance of the provider

        Raises:
            ValueError: If the provider type is invalid
        """
        if provider_type not in IdentityProviderFactory.PROVIDERS:
            raise ValueError(f"Invalid provider type: {provider_type}")

        return IdentityProviderFactory.PROVIDERS[provider_type](
            client_id, client_secret, tenant_id
        )
