from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nexus_auth.utils import get_oauth_provider
from nexus_auth.exceptions import NoAssociatedUserError, UserNotActiveError
from rest_framework.permissions import AllowAny
from nexus_auth.serializers import (
    OAuth2AuthQueryParamsSerializer,
    OAuth2ExchangeSerializer,
)

import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

User = get_user_model()


class OAuthProviderView(APIView):
    """View to get the active provider type."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Get the active provider type.

        Returns:
            Response: Active provider type

        Raises:
            NoActiveProviderError: If no active provider is found
        """
        provider = get_oauth_provider()
        return Response({"provider_type": provider.provider_type}, status=200)


class OAuthUrlView(APIView):
    """View to get the authorization URL for the active provider."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Get the authorization URL for the active provider.

        Args:
            request: HTTP request containing the redirect URI

        Returns:
            Response: Authorization URL

        Raises:
            NoActiveProviderError: If no active provider is found
        """
        serializer = OAuth2AuthQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        provider = get_oauth_provider()
        if not provider:
            return Response({"error": "No active provider found."}, status=404)

        url = provider.build_auth_url(redirect_uri=serializer.validated_data["redirect_uri"])

        return Response({"auth_url": url}, status=200)


class OAuthExchangeView(APIView):
    """View to exchange the authorization code with the active provider for JWT tokens."""

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        """Exchange the authorization code with the active provider for the application's JWT tokens.

        Args:
            request: HTTP request containing the authorization code

        Returns:
            Response: JWT tokens (refresh and access)

        Raises:
            NoActiveProviderError: If no active provider is found
        """
        serializer = OAuth2ExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = get_oauth_provider()

        id_token = provider.fetch_id_token(
            authorization_code=serializer.validated_data["code"],
            code_verifier=serializer.validated_data["code_verifier"],
            redirect_uri=serializer.validated_data["redirect_uri"],
        )

        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
        email = decoded_id_token.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NoAssociatedUserError()

        if not user.is_active:
            raise UserNotActiveError()

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        # Trigger user_logged_in signal
        user_logged_in.send(sender=self.__class__, request=request, user=user)

        return Response({"refresh": str(refresh_token), "access": str(access_token)}, status=200)
