from typing import Any, Dict

from django.conf import settings
from django.utils.module_loading import import_string
from nexus_auth.exceptions import NoActiveProviderError


class NexusAuthSettings:
    _FIELD_NEXUS_AUTH = "NEXUS_AUTH"
    _FIELD_PROVIDERS = "CONFIG"
    _FIELD_HANDLER = "PROVIDERS_HANDLER"
    _FIELD_BUILDERS = "PROVIDER_BUILDERS"
    _DEFAULT_HANDLER = "nexus_auth.utils.load_providers_config"

    def __init__(self, defaults=None):
        self.defaults = defaults or {}

    def __getattr__(self, attr: str) -> Any:
        if attr in self.defaults:
            return self.defaults[attr]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def _get_user_settings(self) -> Dict[str, Any]:
        """
        Always fetch a fresh copy of user settings from Django's settings.
        This avoids keeping a stale/mutated version in memory and fixes the multitenant bug.
        """
        user_settings = getattr(settings, self._FIELD_NEXUS_AUTH, {}).copy()

        # If CONFIG is provided but no handler is set, use the default handler
        if self._FIELD_PROVIDERS in user_settings and self._FIELD_HANDLER not in user_settings:
            user_settings[self._FIELD_HANDLER] = self._DEFAULT_HANDLER

        return user_settings

    def providers_config_setting(self) -> Dict[str, Dict[str, str]]:
        """Get the CONFIG setting. This will be the value you have set in your Django settings for NEXUS_AUTH.CONFIG.

        Returns:
            Dict[str, Dict[str, str]]: Provider configuration
        """
        provider_config = self._get_user_settings().get(self._FIELD_PROVIDERS)
        if not provider_config:
            raise NoActiveProviderError()
        return provider_config

    def get_providers_config(self, **kwargs) -> Dict[str, Dict[str, str]]:
        """Call the providers configuration handler and load the configuration. 
        This will interface for getting the provider configs in the views.

        Args:
            **kwargs: Additional keyword arguments to pass to the handler

        Returns:
            Dict[str, Dict[str, str]]: Provider configuration
        """
        user_settings = self._get_user_settings()
        handler_path = user_settings.get(self._FIELD_HANDLER)
        if handler_path:
            handler = import_string(handler_path)
            return handler(**kwargs)
        return None

    def get_provider_builders(self) -> Dict[str, str]:
        """Get the PROVIDER_BUILDERS setting.

        Returns:
            Dict[str, str]: Builder configuration
        """
        user_builders = self._get_user_settings().get(self._FIELD_BUILDERS, {})
        merged_builders = {
            **self.defaults.get(self._FIELD_BUILDERS, {}),
            **user_builders,
        }
        return merged_builders


DEFAULTS = {
    "CONFIG": {},
    "PROVIDER_BUILDERS": {
        "google": "nexus_auth.providers.google.GoogleOAuth2ProviderBuilder",
        "microsoft_tenant": "nexus_auth.providers.microsoft.MicrosoftEntraTenantOAuth2ProviderBuilder",
    },
}

nexus_settings = NexusAuthSettings(defaults=DEFAULTS)
