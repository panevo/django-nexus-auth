from typing import Optional

from nexus_auth.models import OAuthProvider
from nexus_auth.providers.factory import IdentityProviderFactory
from nexus_auth.exceptions import MultipleActiveProvidersError, NoActiveProviderError
from nexus_auth.providers.base import OAuth2IdentityProvider


def get_oauth_provider() -> Optional[OAuth2IdentityProvider]:
    """Get the active OAuth provider.

    Returns:
        Optional[OAuth2IdentityProvider]: The active provider if found, None if no provider exists.

    Raises:
        MultipleActiveProvidersError: If multiple active providers are found.
    """
    try:
        provider = OAuthProvider.objects.get(is_active=True)
        return IdentityProviderFactory.create_provider(
            provider_type=provider.provider_type,
            client_id=provider.client_id,
            client_secret=provider.client_secret,
            tenant_id=provider.tenant_id,
        )
    except OAuthProvider.DoesNotExist as exc:
        raise NoActiveProviderError() from exc
    except OAuthProvider.MultipleObjectsReturned as exc:
        raise MultipleActiveProvidersError() from exc
