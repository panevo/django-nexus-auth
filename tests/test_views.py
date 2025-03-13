import pytest
from rest_framework.test import APIClient
from nexus_auth.models import OAuthProvider, ProviderType
from unittest.mock import patch
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from unittest.mock import MagicMock
from django.urls import reverse

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
@pytest.mark.parametrize('provider_type', [ProviderType.GOOGLE, ProviderType.MICROSOFT_TENANT])
def test_oauth_provider_view(api_client, provider_type):
    """Test getting the active provider type."""
    OAuthProvider.objects.create(provider_type=provider_type, client_id='test_id', client_secret='test_secret', is_active=True)
    response = api_client.get(reverse('oauth-provider'))
    assert response.status_code == 200
    assert 'provider_type' in response.data
    assert response.data['provider_type'] == provider_type


@pytest.mark.django_db
def test_oauth_url_view_valid_request(api_client):
    """Test getting the authorization URL with a valid request."""
    OAuthProvider.objects.create(provider_type=ProviderType.GOOGLE, client_id='test_id', client_secret='test_secret', is_active=True)
    response = api_client.get(reverse('oauth-url'), {'redirect_uri': 'https://redirect.com'})
    assert response.status_code == 200
    assert 'auth_url' in response.data
    assert response.data['auth_url'].startswith('https://accounts.google.com/o/oauth2/v2/auth')
    assert 'redirect_uri=https%3A%2F%2Fredirect.com' in response.data['auth_url']
    assert 'client_id=test_id' in response.data['auth_url']
    assert 'response_type=code' in response.data['auth_url']
    assert 'scope=openid+email' in response.data['auth_url']

@pytest.mark.django_db
def test_oauth_url_view_invalid_request(api_client):
    """Test getting the authorization URL with an invalid request."""
    OAuthProvider.objects.create(provider_type=ProviderType.GOOGLE, client_id='test_id', client_secret='test_secret', is_active=True)
    response = api_client.get(reverse('oauth-url'))
    assert response.status_code == 400
    assert 'redirect_uri' in response.data
    assert 'This field is required.' in response.data['redirect_uri']

@pytest.mark.django_db
def test_oauth_url_view_no_active_provider(api_client):
    """Test getting the authorization URL with no active provider."""
    response = api_client.get(reverse('oauth-url'), {'redirect_uri': 'https://redirect.com'})
    assert response.status_code == 404
    assert 'detail' in response.data
    assert 'No active identity provider found.' in str(response.data['detail'])

@pytest.mark.django_db
@patch('requests.post')
def test_oauth_exchange_view_no_associated_user(mock_post, api_client):
    """Test exchanging the authorization code with the active provider for JWT tokens."""
    OAuthProvider.objects.create(provider_type=ProviderType.GOOGLE, client_id='test_id', client_secret='test_secret', is_active=True)
    
    email = 'test@example.com'
    id_token = jwt.encode({'email': email}, 'test_secret', algorithm='HS256')
    
    mock_post.return_value.json.return_value = {'id_token': id_token}
    mock_post.return_value.raise_for_status = lambda: None

    response = api_client.post(reverse('oauth-exchange'), {'code': 'test_code', 'code_verifier': 'test_verifier', 'redirect_uri': 'https://redirect.com'})

    # Check that no user exists with the email
    assert response.status_code == 404
    assert 'detail' in response.data
    assert 'No user associated with the provided email.' in str(response.data['detail'])


@pytest.mark.django_db
@patch('requests.post')
def test_oauth_exchange_view_user_not_active(mock_post, api_client):
    """Test exchanging the authorization code with the active provider for JWT tokens."""
    OAuthProvider.objects.create(provider_type=ProviderType.GOOGLE, client_id='test_id', client_secret='test_secret', is_active=True)
    
    email = 'test@example.com'
    id_token = jwt.encode({'email': email}, 'test_secret', algorithm='HS256')
    
    mock_post.return_value.json.return_value = {'id_token': id_token}
    mock_post.return_value.raise_for_status = lambda: None

    User.objects.create_user(email=email, password='test_password', username=email, is_active=False)

    response = api_client.post(reverse('oauth-exchange'), {'code': 'test_code', 'code_verifier': 'test_verifier', 'redirect_uri': 'https://redirect.com'})

    assert response.status_code == 400
    assert 'detail' in response.data
    assert 'User associated with the email is not active.' in str(response.data['detail'])

@pytest.mark.django_db
@patch('requests.post')
def test_oauth_exchange_view_success(mock_post, api_client):
    """Test exchanging the authorization code with the active provider for JWT tokens."""
    OAuthProvider.objects.create(
        provider_type=ProviderType.GOOGLE, client_id='test_id', client_secret='test_secret', is_active=True
    )

    email = 'test@example.com'
    id_token = jwt.encode({'email': email}, 'test_secret', algorithm='HS256')
    
    mock_post.return_value.json.return_value = {'id_token': id_token}
    mock_post.return_value.raise_for_status = lambda: None

    User.objects.create_user(email=email, password='test_password', username=email, is_active=True)

    response = api_client.post(
        reverse('oauth-exchange'),
        {'code': 'test_code', 'code_verifier': 'test_verifier', 'redirect_uri': 'https://redirect.com'}
    )

    assert response.status_code == 200
    assert 'refresh' in response.data
    assert 'access' in response.data

    mock_post.assert_called_once_with(
        'https://www.googleapis.com/oauth2/v4/token',
        data={
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'redirect_uri': 'https://redirect.com',
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'code_verifier': 'test_verifier',
        },
        timeout=10,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
