from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

import jwt
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from nexus_auth.exceptions import (
    NoActiveProviderError,
    NoAssociatedUserError,
    UserNotActiveError,
    IDTokenExchangeError,
    MissingIDTokenError,
    InvalidTokenError,
)
from nexus_auth.serializers import (
    OAuth2ExchangeSerializer,
)
from nexus_auth.settings import nexus_settings
from nexus_auth.utils import build_oauth_provider


User = get_user_model()


class OAuthProvidersView(APIView):
    """View to get the providers"""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """
        Retrieve active providers with authorization URLs.
        """
        providers_config = nexus_settings.get_providers_config(request=request) or {}
        providers = []

        for provider_type, _ in providers_config.items():
            provider = build_oauth_provider(provider_type, providers_config)
            if provider:
                providers.append(
                    {
                        "type": provider_type,
                        "auth_url": provider.build_auth_url(),
                    }
                )

        return Response({"providers": providers}, status=200)


class OAuthExchangeView(APIView):
    """View to exchange the authorization code with the active provider for JWT tokens."""

    permission_classes = (AllowAny,)

    def post(self, request: Request, provider_type: str) -> Response:
        """Exchange the authorization code with the active provider for the application's JWT tokens.

        Args:
            request: HTTP request containing the authorization code
            provider_type: Type of provider to use

        Returns:
            Response: JWT tokens (refresh and access)

        Raises:
            NoActiveProviderError: If no active provider is found
        """
        serializer = OAuth2ExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        providers_config = nexus_settings.get_providers_config(request=request)
        provider = build_oauth_provider(provider_type, providers_config)
        if not provider:
            raise NoActiveProviderError()

        try:
            id_token = provider.fetch_id_token(
                authorization_code=serializer.validated_data["code"],
                code_verifier=serializer.validated_data["code_verifier"],
                redirect_uri=serializer.validated_data["redirect_uri"],
            )
        except (IDTokenExchangeError, MissingIDTokenError, InvalidTokenError) as e:
            return Response(
                {"error": str(e), "code": e.default_code}, status=e.status_code
            )

        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
        email = decoded_id_token.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise NoAssociatedUserError() from e

        if not user.is_active:
            raise UserNotActiveError()

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        # Trigger user_logged_in signal
        user_logged_in.send(sender=self.__class__, request=request, user=user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)}, status=200
        )
