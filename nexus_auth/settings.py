from typing import Any, Dict, List

from django.conf import settings
from django.utils.module_loading import import_string
from nexus_auth.exceptions import NoActiveProviderError


class NexusAuthSettings:
    _FIELD_USER_SETTINGS = "_user_settings"
    _FIELD_NEXUS_AUTH = "NEXUS_AUTH"
    _FIELD_PROVIDERS = "PROVIDERS"
    _FIELD_HANDLER = "PROVIDERS_HANDLER"

    def __init__(self, user_settings=None, defaults=None):
        self.defaults = defaults or {}
        self._user_settings = user_settings or getattr(
            settings, self._FIELD_NEXUS_AUTH, {}
        )

    def __getattr__(self, attr: str) -> Any:
        if attr in self.defaults:
            return self._user_settings.get(attr, self.defaults[attr])
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def get_provider_config(self) -> Dict[str, Dict[str, str]]:
        """Get the provider configuration.

        Returns:
            Dict[str, Dict[str, str]]: Provider configuration
        """
        provider_config = self._user_settings.get(self._FIELD_PROVIDERS)
        if not provider_config:
            raise NoActiveProviderError()
        return provider_config

    def get_provider_config_handler(self, **kwargs) -> List[str]:
        """Call the provider configuration handler.

        Args:
            **kwargs: Additional keyword arguments to pass to the handler

        Returns:
            List[str]: List of provider types
        """
        handler_path = self._user_settings.get(self._FIELD_HANDLER)
        if handler_path:
            handler = import_string(handler_path)  # Dynamically import function
            return handler(**kwargs)  # Call the function
        return None


DEFAULTS = {
    "PROVIDERS": {},
}

nexus_settings = NexusAuthSettings(user_settings=None, defaults=DEFAULTS)
