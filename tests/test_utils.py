import pytest
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from nexus_auth.utils import get_oauth_provider
from nexus_auth.models import OAuthProvider
from nexus_auth.exceptions import NoActiveProviderError, MultipleActiveProvidersError

@pytest.mark.django_db
def test_get_oauth_provider_success():
    """Get active provider"""
    OAuthProvider.objects.create(
        provider_type='microsoft_tenant',
        client_id='test_client_id',
        client_secret='test_client_secret',
        tenant_id='test_tenant_id',
        is_active=True
    )

    provider = get_oauth_provider()

    assert provider is not None
    assert provider.provider_type == 'microsoft_tenant'
    assert provider.client_id == 'test_client_id'
    assert provider.client_secret == 'test_client_secret'
    assert provider.tenant_id == 'test_tenant_id'


@pytest.mark.django_db
def test_get_oauth_provider_no_active_provider():
    """Get active provider when no active provider exists"""
    OAuthProvider.objects.create(
        provider_type='microsoft_tenant',
        client_id='test_client_id',
        client_secret='test_client_secret',
        tenant_id='test_tenant_id',
        is_active=False
    )

    with pytest.raises(NoActiveProviderError):
        get_oauth_provider()


@pytest.mark.django_db
def test_get_oauth_provider_multiple_active_providers():
    """Get active provider when multiple active providers exist"""
    # Bulk create providers
    OAuthProvider.objects.bulk_create([
        OAuthProvider(
            provider_type='microsoft_tenant',
            client_id='test_client_id',
            client_secret='test_client_secret',
            tenant_id='test_tenant_id',
            is_active=True
        ),
        OAuthProvider(
            provider_type='google', 
            client_id='test_client_id',
            client_secret='test_client_secret',
            is_active=True
        )
    ]) 

    with pytest.raises(MultipleActiveProvidersError):
        get_oauth_provider()
