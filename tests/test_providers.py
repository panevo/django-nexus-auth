import pytest
from unittest.mock import patch
from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.exceptions import MissingIDTokenError

class MockOAuth2IdentityProvider(OAuth2IdentityProvider):
    def get_authorization_url(self):
        return "https://example.com/auth"

    def get_token_url(self):
        return "https://example.com/token"

@pytest.fixture
def mock_provider():
    return MockOAuth2IdentityProvider(client_id='test_id', client_secret='test_secret', tenant_id='test_tenant')

def test_build_auth_url(mock_provider):
    """Test building the authorization URL."""
    auth_url = mock_provider.build_auth_url(redirect_uri='https://redirect.com')
    assert auth_url.startswith("https://example.com/auth?")
    assert "redirect_uri=https%3A%2F%2Fredirect.com" in auth_url

@patch('requests.post')
def test_fetch_id_token(mock_post, mock_provider):
    """Test fetching ID token."""
    mock_response = mock_post.return_value
    mock_response.json.return_value = {'id_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'}
    mock_response.raise_for_status = lambda: None

    id_token = mock_provider.fetch_id_token(
        authorization_code='auth_code',
        code_verifier='code_verifier',
        redirect_uri='https://redirect.com'
    )
    assert id_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'

    mock_response.json.return_value = {}
    with pytest.raises(MissingIDTokenError):
        mock_provider.fetch_id_token(
            authorization_code='auth_code',
            code_verifier='code_verifier',
            redirect_uri='https://redirect.com'
        )