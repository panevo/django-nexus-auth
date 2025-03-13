from rest_framework import serializers


class OAuth2AuthQueryParamsSerializer(serializers.Serializer):
    """Serializer for the authorization URL request"""

    redirect_uri = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


class OAuth2ExchangeSerializer(serializers.Serializer):
    """Serializer for the exchange of an authorization code for an ID token"""

    code = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    code_verifier = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    redirect_uri = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )
