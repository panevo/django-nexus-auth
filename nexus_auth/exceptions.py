from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import APIException
from rest_framework import status


class MultipleActiveProvidersError(ImproperlyConfigured):
    def __init__(self) -> None:
        super().__init__(
            "Multiple active identity providers found. Only one provider can be active at a time."
        )

class NoActiveProviderError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No active identity provider found."
    default_code = "no_active_provider"

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
    default_detail = "User is not active."
    default_code = "user_not_active"