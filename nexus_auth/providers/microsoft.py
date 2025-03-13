from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.models import ProviderType


class MicrosoftEntraTenantOAuth2Provider(OAuth2IdentityProvider):
    provider_type = ProviderType.MICROSOFT_TENANT

    def get_authorization_url(self):
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        )

    def get_token_url(self):
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
