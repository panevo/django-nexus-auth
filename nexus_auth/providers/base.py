from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlencode

import requests
import jwt
from nexus_auth.exceptions import (
    MissingIDTokenError,
    IDTokenExchangeError,
    InvalidTokenResponseError,
)


class OAuth2IdentityProvider(ABC):
    """Base class for OAuth2 Identity Providers.

    Implements common OAuth2 functionality and defines abstract methods that
    specific providers must implement.
    """

    provider_type: str = ""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Initialize the OAuth2 provider.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tenant_id: Optional tenant ID for multi-tenant providers
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    @abstractmethod
    def get_authorization_url(self) -> str:
        """Get the authorization URL for the IdP.

        Returns:
            Full authorization URL to redirect the user to
        """
        pass

    @abstractmethod
    def get_token_url(self) -> str:
        """Get the token endpoint URL for the IdP.

        Returns:
            Token endpoint URL used for retrieving tokens
        """
        pass

    def build_auth_url(self) -> str:
        """Build the authorization URL for the IdP.

        Returns:
            Full authorization URL to redirect the user to
        """
        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
        }

        return f"{self.get_authorization_url()}?{urlencode(query_params)}"

    def fetch_id_token(
        self, authorization_code: str, code_verifier: str, redirect_uri: str
    ) -> str:
        """Exchange authorization code for an ID token. This ID token
        usually contains information about the user and can be used to
        authenticate the user.

        Args:
            authorization_code: OAuth2 authorization code
            code_verifier: PKCE code verifier
            redirect_uri: Redirect URI used in the authorization request

        Returns:
            str: ID token

        Raises:
            IDTokenExchangeError: If the token exchange requests fails
            MissingIDTokenError: If the token response is missing the ID token
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
            raise IDTokenExchangeError() from e

        try:
            token_data = response.json()
        except ValueError as e:
            raise InvalidTokenResponseError() from e

        if "id_token" not in token_data:
            raise MissingIDTokenError()

        return token_data["id_token"]

    def extract_email_from_id_token(self, id_token: str) -> Optional[str]:
        """Extract the user's email address from the ID token.

        Args:
            id_token: ID token from the IdP

        Returns:
            Optional[str]: User's email address
        """
        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
        return decoded_id_token.get("email", None)

    def exchange_code_for_email(
        self, authorization_code: str, code_verifier: str, redirect_uri: str
    ) -> Optional[str]:
        """Exchange authorization code for an email address.

        Args:
            authorization_code: OAuth2 authorization code
            code_verifier: PKCE code verifier
            redirect_uri: Redirect URI used in the authorization request

        Returns:
            Optional[str]: User's email address
        """
        id_token = self.fetch_id_token(
            authorization_code=authorization_code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
        )
        return self.extract_email_from_id_token(id_token)


class ProviderBuilder(ABC):
    """Base class for provider builders."""

    def __init__(self, **kwargs):
        self._instance = None

    @abstractmethod
    def __call__(self, **kwargs):
        pass
