from rest_framework import serializers


class OAuth2ExchangeSerializer(serializers.Serializer):
    """Serializer for the exchange of an authorization code for an ID token"""

    code = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        label="Authorization Code",
        help_text="The authorization code received from the authorization server.",
    )

    code_verifier = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        label="PKCE Code Verifier",
        help_text="The corresponding code verifier that was generated along with the code challenge in the authorization request.",
    )

    redirect_uri = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        label="Redirect URI",
        help_text="The redirect URI that was provided in the authorization request.",
    )
