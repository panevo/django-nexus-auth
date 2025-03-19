from typing import List, Optional

from rest_framework.request import Request

from nexus_auth.exceptions import NoActiveProviderError
from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.providers.factory import providers
from nexus_auth.settings import nexus_settings


def get_oauth_provider(provider_type: str) -> Optional[OAuth2IdentityProvider]:
    """Get the OAuth provider object by provider type.

    Args:
        provider_type: Type of provider to get

    Returns:
        Optional[OAuth2IdentityProvider]: The active provider if found, None if no provider exists.

    Raises:
        NoActiveProviderError: If no active provider is found.
    """
    provider_config = nexus_settings.get_provider_config(provider_type)
    if not provider_config:
        raise NoActiveProviderError()

    return providers.get(
        provider_type,
        **provider_config,
    )


def get_provider_types(request: Request) -> List[str]:
    """Get the list of provider types.

    Returns:
        List[str]: List of provider types
    """
    return list(nexus_settings.get_provider_settings().keys())
