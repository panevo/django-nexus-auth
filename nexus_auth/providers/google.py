from nexus_auth.providers.base import OAuth2IdentityProvider
from nexus_auth.models import ProviderType


class GoogleOAuth2Provider(OAuth2IdentityProvider):
    provider_type = ProviderType.GOOGLE

    def get_authorization_url(self):
        return "https://accounts.google.com/o/oauth2/v2/auth"

    def get_token_url(self):
        return "https://www.googleapis.com/oauth2/v4/token"
