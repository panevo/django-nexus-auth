from typing import Dict, Optional

from rest_framework.request import Request

from nexus_auth.exceptions import NoActiveProviderError
from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.providers.factory import providers
from nexus_auth.settings import nexus_settings


def build_oauth_provider(
    provider_type: str, providers_config: Dict[str, Dict[str, str]]
) -> Optional[OAuth2IdentityProvider]:
    """Build an OAuth provider object by provider type.

    Args:
        provider_type: Type of provider to get
        providers_config: Providers configuration

    Returns:
        Optional[OAuth2IdentityProvider]: The active provider if found, None if no provider exists.

    Raises:
        NoActiveProviderError: If no active provider is found.
    """
    provider_config = providers_config.get(provider_type)
    if not provider_config:
        raise NoActiveProviderError()

    config_kwargs = {k.lower(): v for k, v in provider_config.items()}

    return providers.get(
        provider_type,
        **config_kwargs,
    )


def load_providers_config(
    request: Optional[Request] = None,
) -> Dict[str, Dict[str, str]]:
    """Load providers configuration.

    Args:
        request: HTTP request

    Returns:
        Dict[str, Dict[str, str]]: Provider configuration
    """
    return nexus_settings.providers_config()
