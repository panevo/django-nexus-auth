from nexus_auth.providers.base import OAuth2IdentityProvider, ProviderBuilder


class MicrosoftEntraTenantOAuth2Provider(OAuth2IdentityProvider):
    def get_authorization_url(self):
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        )

    def get_token_url(self):
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"


class MicrosoftEntraTenantOAuth2ProviderBuilder(ProviderBuilder):
    def __call__(self, client_id, client_secret, tenant_id, **_ignored):
        if self._instance is None:
            self._instance = MicrosoftEntraTenantOAuth2Provider(
                client_id, client_secret, tenant_id
            )
        return self._instance
