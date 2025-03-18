from django.conf import settings
from typing import Any, Optional, List, Dict
from django.utils.module_loading import import_string

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

    def get_provider_config(self, provider_type: str) -> Optional[Dict[str, str]]:
        provider_settings = self._user_settings.get(self._FIELD_PROVIDERS, {}).get(
            provider_type
        )
        if not provider_settings:
            return None
        return {k.lower(): v for k, v in provider_settings.items()}

    def get_provider_types(self) -> List[str]:
        return list(self._user_settings.get(self._FIELD_PROVIDERS, {}).keys())

    def provider_types_handler(self, **kwargs) -> List[str]:
        handler_path = self._user_settings.get(self._FIELD_HANDLER)
        if handler_path:
            handler = import_string(handler_path)  # Dynamically import function
            return handler(**kwargs)  # Call the function
        return []


DEFAULTS = {
    "PROVIDERS": {},
}

nexus_settings = NexusAuthSettings(user_settings=None, defaults=DEFAULTS)
