from unittest.mock import patch

import pytest
from requests import RequestException
from nexus_auth.exceptions import MissingIDTokenError, IDTokenExchangeError, InvalidTokenError
from nexus_auth.providers.base import OAuth2IdentityProvider


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

        with pytest.raises(InvalidTokenError):
            provider.fetch_id_token("auth_code", "verifier", "https://redirect.url")
