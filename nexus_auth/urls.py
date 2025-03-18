from django.urls import path

from nexus_auth.views import OAuthProvidersView, OAuthExchangeView

__all__ = ["urlpatterns"]

urlpatterns = [
    path("oauth/providers", OAuthProvidersView.as_view(), name="oauth-provider"),
    path("oauth/<str:provider_type>/exchange", OAuthExchangeView.as_view(), name="oauth-exchange"),
]
