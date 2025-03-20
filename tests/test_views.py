from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from nexus_auth.exceptions import (
    NoActiveProviderError,
    NoAssociatedUserError,
    UserNotActiveError,
)
from nexus_auth.utils import get_oauth_provider
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def active_user(db):
    return User.objects.create_user(email="active@example.com", password="password", username="user_is_active", is_active=True)

@pytest.fixture
def mock_fetch_id_token():
    with patch("nexus_auth.utils.get_oauth_provider") as mock_provider, \
         patch("jwt.decode", return_value={"email": "active@example.com"}) as mock_jwt_decode:
        provider = get_oauth_provider(request=None, provider_type="google")
        provider.fetch_id_token = MagicMock(return_value="fake_id_token")
        mock_provider.return_value = provider
        yield mock_provider, mock_jwt_decode

def test_oauth_providers_success(api_client):
    response = api_client.get(reverse("oauth-provider"))
    assert response.status_code == status.HTTP_200_OK
    assert "providers" in response.data
    assert len(response.data["providers"]) == 2
    assert response.data["providers"][0]["type"] == "microsoft_tenant"
    assert response.data["providers"][1]["type"] == "google"

def test_oauth_providers_no_active_provider(api_client):
    with patch("nexus_auth.settings.nexus_settings.get_provider_config_handler", side_effect=NoActiveProviderError):
        response = api_client.get(reverse("oauth-provider"))
    assert response.status_code == NoActiveProviderError.status_code
    assert response.data["detail"] == NoActiveProviderError.default_detail

def test_oauth_exchange_success(api_client, active_user, mock_fetch_id_token):
    response = api_client.post(reverse("oauth-exchange", args=["google"]), data={
        "code": "auth_code",
        "code_verifier": "verifier",
        "redirect_uri": "https://app.com/callback"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_oauth_exchange_no_user(api_client, mock_fetch_id_token):
    response = api_client.post(reverse("oauth-exchange", args=["google"]), data={
        "code": "auth_code",
        "code_verifier": "verifier",
        "redirect_uri": "https://app.com/callback"
    })
    assert response.status_code == NoAssociatedUserError.status_code
    assert response.data["detail"] == NoAssociatedUserError.default_detail

@pytest.mark.django_db
def test_oauth_exchange_inactive_user(api_client, active_user, mock_fetch_id_token):
    active_user.is_active = False
    active_user.save()
    response = api_client.post(reverse("oauth-exchange", args=["google"]), data={
        "code": "auth_code",
        "code_verifier": "verifier",
        "redirect_uri": "https://app.com/callback"
    })
    assert response.status_code == UserNotActiveError.status_code
    assert response.data["detail"] == UserNotActiveError.default_detail