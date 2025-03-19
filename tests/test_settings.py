from unittest.mock import patch

import pytest
from nexus_auth.settings import NexusAuthSettings


@pytest.fixture
def default_settings():
    return {
        "PROVIDERS": {
            "microsoft_tenant": {"client_id": "123", "client_secret": "abc"},
            "google": {"client_id": "456", "client_secret": "def"},
        },
        "PROVIDERS_HANDLER": "nexus_auth.utils.get_provider_types",
    }

@pytest.fixture
def nexus_auth_settings(default_settings):
    return NexusAuthSettings(user_settings=default_settings)

def test_get_provider_config(nexus_auth_settings):
    config = nexus_auth_settings.get_provider_config("microsoft_tenant")
    assert config == {"client_id": "123", "client_secret": "abc"}

    config = nexus_auth_settings.get_provider_config("google")
    assert config == {"client_id": "456", "client_secret": "def"}

    assert nexus_auth_settings.get_provider_config("non_existent") is None

def test_get_provider_settings(nexus_auth_settings):
    providers = nexus_auth_settings.get_provider_settings()
    assert "microsoft_tenant" in providers
    assert "google" in providers
    assert providers["microsoft_tenant"] == {"client_id": "123", "client_secret": "abc"}

def test_provider_types_handler(nexus_auth_settings):
    with patch("nexus_auth.utils.get_provider_types") as mock_get_provider_types:
        mock_get_provider_types.return_value = ["microsoft_tenant"]
        result = nexus_auth_settings.provider_types_handler()
        assert result == ["microsoft_tenant"]

def test_getattr_defaults():
    settings = NexusAuthSettings(defaults={"SOME_SETTING": "default_value"})
    assert settings.SOME_SETTING == "default_value"
    with pytest.raises(AttributeError):
        settings.NON_EXISTENT_SETTING
