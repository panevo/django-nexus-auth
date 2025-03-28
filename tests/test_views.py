from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from nexus_auth.exceptions import (
    NoActiveProviderError,
    NoAssociatedUserError,
    UserNotActiveError,
)
from nexus_auth.utils import build_oauth_provider
from rest_framework import status
from rest_framework.test import APIClient
from nexus_auth.settings import nexus_settings

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def active_user(db):
    return User.objects.create_user(email="active@example.com", password="password", username="user_is_active", is_active=True)

@pytest.fixture
def mock_fetch_id_token():
    """Mock the fetch_id_token method of the OAuth provider."""
    with patch("nexus_auth.utils.build_oauth_provider") as mock_provider, \
         patch("jwt.decode", return_value={"email": "active@example.com"}) as mock_jwt_decode:
        providers_config = nexus_settings.get_providers_config()
        provider = build_oauth_provider(provider_type="google", providers_config=providers_config)
        provider.fetch_id_token = MagicMock(return_value="fake_id_token")
        mock_provider.return_value = provider
        yield mock_provider, mock_jwt_decode

def test_oauth_providers_success(api_client):
    """Test that the OAuth providers endpoint returns the correct providers."""
    response = api_client.get(reverse("oauth-provider"))
    assert response.status_code == status.HTTP_200_OK
    assert "providers" in response.data
    assert len(response.data["providers"]) == 2
    assert response.data["providers"][0]["type"] == "microsoft_tenant"
    assert response.data["providers"][1]["type"] == "google"

def test_oauth_providers_no_active_provider(api_client):
    """Test that the OAuth providers endpoint returns an error when no active provider is found."""
    with patch("nexus_auth.settings.nexus_settings.get_providers_config", side_effect=NoActiveProviderError):
        response = api_client.get(reverse("oauth-provider"))
    assert response.status_code == NoActiveProviderError.status_code
    assert response.data["detail"] == NoActiveProviderError.default_detail

def test_oauth_exchange_success(api_client, active_user, mock_fetch_id_token):
    """Test that the OAuth exchange endpoint returns a 200 response with access and refresh tokens."""
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
    """Test that the OAuth exchange endpoint returns an error when no user is associated with the provider."""
    response = api_client.post(reverse("oauth-exchange", args=["google"]), data={
        "code": "auth_code",
        "code_verifier": "verifier",
        "redirect_uri": "https://app.com/callback"
    })
    assert response.status_code == NoAssociatedUserError.status_code
    assert response.data["detail"] == NoAssociatedUserError.default_detail

@pytest.mark.django_db
def test_oauth_exchange_inactive_user(api_client, active_user, mock_fetch_id_token):
    """Test that the OAuth exchange endpoint returns an error when the user is inactive."""
    active_user.is_active = False
    active_user.save()
    response = api_client.post(reverse("oauth-exchange", args=["google"]), data={
        "code": "auth_code",
        "code_verifier": "verifier",
        "redirect_uri": "https://app.com/callback"
    })
    assert response.status_code == UserNotActiveError.status_code
    assert response.data["detail"] == UserNotActiveError.default_detail