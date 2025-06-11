from django.core.exceptions import ImproperlyConfigured

from rest_framework import status
from rest_framework.exceptions import APIException


class NexusAuthBaseException(APIException):
    """Base exception for all Nexus Auth exceptions."""
    pass


class MultipleActiveProvidersError(ImproperlyConfigured):
    def __init__(self) -> None:
        super().__init__(
            "Multiple active identity providers found. Only one provider can be active at a time."
        )


class NoActiveProviderError(NexusAuthBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No active identity provider found."
    default_code = "no_active_provider"


class NoRegisteredBuilderError(ImproperlyConfigured):
    def __init__(self) -> None:
        super().__init__(
            "PROVIDER_BUILDERS setting is empty. Please register at least one builder."
        )


class MissingIDTokenError(NexusAuthBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No ID token received from identity provider."
    default_code = "missing_id_token"


class MissingAccessTokenError(NexusAuthBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No access token received from identity provider."
    default_code = "missing_access_token"


class NoAssociatedUserError(NexusAuthBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No user associated with the provided email."
    default_code = "no_associated_user"


class UserNotActiveError(NexusAuthBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "User associated with the email is not active."
    default_code = "user_not_active"


class IDTokenExchangeError(NexusAuthBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Error to retrieve ID token from identity provider."
    default_code = "id_token_exchange_error"


class AccessTokenExchangeError(NexusAuthBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Error to retrieve access token from identity provider."
    default_code = "access_token_exchange_error"


class InvalidTokenResponseError(NexusAuthBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid token response received from identity provider."
    default_code = "invalid_token_response"


class MicrosoftGraphAPIError(NexusAuthBaseException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Error when retrieving user email from Microsoft Graph API"
    default_code = "microsoft_graph_api_error"


class MissingEmailFromProviderError(NexusAuthBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "No email returned from provider"
    default_code = "missing_email_from_provider"
