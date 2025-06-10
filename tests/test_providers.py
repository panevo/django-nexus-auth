from unittest.mock import patch

import jwt
import pytest
from requests import RequestException
from nexus_auth.exceptions import MissingIDTokenError, IDTokenExchangeError, InvalidTokenResponseError, MicrosoftGraphAPIError, AccessTokenExchangeError, MissingAccessTokenError
from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.providers.microsoft import MicrosoftEntraTenantOAuth2Provider

class MockOAuth2Provider(OAuth2IdentityProvider):
    def get_authorization_url(self):
        return "https://mockidp.com/auth"

    def get_token_url(self):
        return "https://mockidp.com/token"

class TestMockOAuth2Provider:
    @pytest.fixture
    def provider(self):
        return MockOAuth2Provider(client_id="test_client", client_secret="test_secret")

    def test_get_authorization_url(self, provider):
        assert provider.get_authorization_url() == "https://mockidp.com/auth"

    def test_get_token_url(self, provider):
        assert provider.get_token_url() == "https://mockidp.com/token"

    def test_build_auth_url(self, provider):
        auth_url = provider.build_auth_url()
        assert "https://mockidp.com/auth" in auth_url
        assert "client_id=test_client" in auth_url
        assert "response_type=code" in auth_url
        assert "scope=openid+email" in auth_url

    @patch("requests.post")
    def test_fetch_id_token_success(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'}

        token = provider.fetch_id_token("auth_code", "verifier", "https://redirect.url")
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

    @patch("requests.post")
    def test_fetch_id_token_missing(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        with pytest.raises(MissingIDTokenError):
            provider.fetch_id_token("auth_code", "verifier", "https://redirect.url")

    @patch("requests.post")
    def test_fetch_id_token_exchange_error(self, mock_post, provider):
        mock_post.side_effect = RequestException

        with pytest.raises(IDTokenExchangeError):
            provider.fetch_id_token("auth_code", "verifier", "https://redirect.url")

    @patch("requests.post")
    def test_fetch_id_token_invalid_json(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = ValueError

        with pytest.raises(InvalidTokenResponseError):
            provider.fetch_id_token("auth_code", "verifier", "https://redirect.url")

    def test_extract_email_from_id_token(self, provider):
        encoded_jwt_token = jwt.encode({"email": "test_user@example.com"}, "secret", algorithm="HS256")

        email = provider.extract_email_from_id_token(encoded_jwt_token)
        assert email == "test_user@example.com"

class TestMicrosoftEntraTenantOAuth2Provider:
    """
    Test Microsoft Entra (formerly Azure AD) tenant OAuth2 provider due to a more complex implementation.
    """

    @pytest.fixture
    def provider(self):
        return MicrosoftEntraTenantOAuth2Provider(client_id="test_client", client_secret="test_secret", tenant_id="test_tenant")

    @patch("requests.post")
    def test_fetch_access_token(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        token = provider.fetch_access_token("auth_code", "verifier", "https://redirect.url")
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

    @patch("requests.post")
    def test_fetch_access_token_exchange_error(self, mock_post, provider):
        mock_post.side_effect = RequestException

        with pytest.raises(AccessTokenExchangeError):
            provider.fetch_access_token("auth_code", "verifier", "https://redirect.url")

    @patch("requests.post")
    def test_fetch_access_token_invalid_json(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = ValueError

        with pytest.raises(InvalidTokenResponseError):
            provider.fetch_access_token("auth_code", "verifier", "https://redirect.url")

    @patch("requests.post")
    def test_fetch_access_token_missing(self, mock_post, provider):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        with pytest.raises(MissingAccessTokenError):
            provider.fetch_access_token("auth_code", "verifier", "https://redirect.url")

    @patch("requests.get")
    def test_fetch_user_email(self, mock_get, provider):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"userPrincipalName": "test_user@example.com"}

        email = provider.fetch_user_email("access_token")
        assert email == "test_user@example.com"

    @patch("requests.get")
    def test_fetch_user_email_invalid_json(self, mock_get, provider):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = ValueError

        with pytest.raises(InvalidTokenResponseError):
            provider.fetch_user_email("wrong_access_token")

    @patch("requests.get")
    def test_fetch_user_email_exchange_error(self, mock_get, provider):
        mock_get.side_effect = RequestException

        with pytest.raises(MicrosoftGraphAPIError):
            provider.fetch_user_email("access_token")

    @patch("requests.get")
    def test_fetch_user_email_missing(self, mock_get, provider):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}

        with pytest.raises(InvalidTokenResponseError):
            provider.fetch_user_email("access_token")