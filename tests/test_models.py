from django.core.exceptions import ValidationError
from nexus_auth.models import OAuthProvider, ProviderType
import pytest

@pytest.mark.django_db
def test_clean_method_requires_tenant_id_for_microsoft_tenant():
    """Clean method raises ValidationError when tenant_id is missing for Microsoft Entra ID Tenant"""
    provider = OAuthProvider(provider_type=ProviderType.MICROSOFT_TENANT, client_id='test_id', client_secret='test_secret')
    with pytest.raises(ValidationError):
        provider.clean()

@pytest.mark.django_db
def test_save_method_ensures_only_one_active_provider():
    """Save method ensures only one active provider"""
    provider1 = OAuthProvider.objects.create(provider_type=ProviderType.GOOGLE, client_id='test_id_1', client_secret='test_secret_1', is_active=True)
    provider2 = OAuthProvider(provider_type=ProviderType.GOOGLE, client_id='test_id_2', client_secret='test_secret_2', is_active=True)
    provider2.save()
    provider1.refresh_from_db()
    assert not provider1.is_active
    assert provider2.is_active
