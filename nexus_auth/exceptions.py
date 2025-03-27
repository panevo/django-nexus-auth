from django.core.exceptions import ImproperlyConfigured

from rest_framework import status
from rest_framework.exceptions import APIException


class MultipleActiveProvidersError(ImproperlyConfigured):
    def __init__(self) -> None:
        super().__init__(
            "Multiple active identity providers found. Only one provider can be active at a time."
        )


class NoActiveProviderError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No active identity provider found."
    default_code = "no_active_provider"


class NoRegisteredBuilderError(ImproperlyConfigured):
    def __init__(self) -> None:
        super().__init__(
            "PROVIDER_BUILDERS setting is empty. Please register at least one builder."
        )


class MissingIDTokenError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No ID token received from identity provider."
    default_code = "missing_id_token"


class NoAssociatedUserError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No user associated with the provided email."
    default_code = "no_associated_user"


class UserNotActiveError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "User associated with the email is not active."
    default_code = "user_not_active"


class IDTokenExchangeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Error to retrieve ID token from identity provider."
    default_code = "id_token_exchange_error"


class InvalidTokenError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid ID token received from identity provider."
    default_code = "invalid_id_token"
