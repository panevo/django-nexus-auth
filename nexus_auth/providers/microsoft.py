from typing import Dict, Optional

import requests

from nexus_auth.exceptions import (
    AccessTokenExchangeError,
    InvalidTokenResponseError,
    MissingAccessTokenError,
    MicrosoftGraphAPIError
)
from nexus_auth.providers.base import OAuth2IdentityProvider, ProviderBuilder


class MicrosoftEntraTenantOAuth2Provider(OAuth2IdentityProvider):
    """Microsoft Entra (formerly Azure AD) tenant OAuth2 provider.
    
    Note: Microsoft Entra requires sending a request to the Microsoft Graph API to get the user's email address 
    as documented here: https://learn.microsoft.com/en-us/entra/identity-platform/id-tokens#claims-in-an-id-token
    """

    def get_authorization_url(self):
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        )

    def get_token_url(self):
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def fetch_access_token(
        self, authorization_code: str, code_verifier: str, redirect_uri: str
    ) -> Dict:
        """Exchange authorization code for an access token.

        Args:
            authorization_code: OAuth2 authorization code
            code_verifier: PKCE code verifier
            redirect_uri: Redirect URI used in the authorization request

        Returns:
            Dict containing ID token and other token response data

        Raises:
            AccessTokenExchangeError: If the token exchange requests fails
            MissingAccessTokenError: If the token response is missing the access token
            InvalidTokenResponseError: If the token response from the IdP is invalid
        """
        token_url = self.get_token_url()
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "code_verifier": code_verifier,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(
                token_url,
                data=data,
                timeout=10,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AccessTokenExchangeError() from e

        try:
            token_data = response.json()
        except ValueError as e:
            raise InvalidTokenResponseError() from e

        if "access_token" not in token_data:
            raise MissingAccessTokenError()

        return token_data["access_token"]

    def fetch_user_email(self, access_token: str) -> Optional[str]:
        """
        Using the access token, get the user's email address by fetching from the Microsoft Graph API.
        Endpoint: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http

        Args:
            access_token: OAuth2 access token. To be used with the Microsoft Graph API.

        Returns:
            Optional[str]: User's email address

        Raises:
            MicrosoftGraphAPIError: If the Microsoft Graph API request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise MicrosoftGraphAPIError() from e

        try:
            user_data = response.json()
        except ValueError as e:
            raise InvalidTokenResponseError() from e

        # Select the User Principal Name (UPN) as the email address
        if "userPrincipalName" not in user_data:
            raise InvalidTokenResponseError()

        return user_data["userPrincipalName"]

    def exchange_code_for_email(
        self, authorization_code: str, code_verifier: str, redirect_uri: str
    ) -> Optional[str]:
        """
        Exchange authorization code for an email address.

        Args:
            authorization_code: OAuth2 authorization code
            code_verifier: PKCE code verifier
            redirect_uri: Redirect URI used in the authorization request

        Returns:
            Optional[str]: User's email address
        """
        access_token = self.fetch_access_token(
            authorization_code=authorization_code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
        )
        email = self.fetch_user_email(access_token)
        return email


class MicrosoftEntraTenantOAuth2ProviderBuilder(ProviderBuilder):
    def __call__(self, client_id, client_secret, tenant_id, **_ignored):
        if self._instance is None:
            self._instance = MicrosoftEntraTenantOAuth2Provider(
                client_id, client_secret, tenant_id
            )
        return self._instance
