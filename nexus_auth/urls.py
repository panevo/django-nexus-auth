from django.urls import path

from nexus_auth.views import OAuthProviderView, OAuthUrlView, OAuthExchangeView

__all__ = ["urlpatterns"]

urlpatterns = [
    path("oauth/provider", OAuthProviderView.as_view(), name="oauth-provider"),
    path("oauth/url", OAuthUrlView.as_view(), name="oauth-url"),
    path("oauth/exchange", OAuthExchangeView.as_view(), name="oauth-exchange"),
]
