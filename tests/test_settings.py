import pytest
from nexus_auth.settings import NexusAuthSettings, NoActiveProviderError
from unittest.mock import MagicMock


@pytest.fixture
def default_settings():
    return {
        "PROVIDERS": {
            "microsoft_tenant": {
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                "tenant_id": "test_tenant_id",
            },
            "google": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            },
        },
        "PROVIDERS_HANDLER": "nexus_auth.utils.provider_config_handler",
    }

@pytest.fixture
def nexus_auth_settings(default_settings):
    return NexusAuthSettings(user_settings=default_settings)

def test_default_get_provider_config(nexus_auth_settings):
    config = nexus_auth_settings.get_provider_config()
    assert config == {
        "microsoft_tenant": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tenant_id": "test_tenant_id",
        },
        "google": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        },
    }

def test_getattr_defaults():
    settings = NexusAuthSettings(defaults={"SOME_SETTING": "default_value"})
    assert settings.SOME_SETTING == "default_value"
    with pytest.raises(AttributeError):
        settings.NON_EXISTENT_SETTING
