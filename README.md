# Django Nexus Auth

Django Nexus Auth is a Django package that provides OAuth authentication support following the Authentication Code Grant Flow with PKCE. It is designed to work seamlessly for Single-Page Applications that use [Django REST Framework](https://www.django-rest-framework.org/) and [simplejwt](https://github.com/davesque/django-rest-framework-simplejwt) for authentication.

## Features

- Support for Microsoft Entra ID and Google
- Provides API endpoints for facilitating OAuth 2.0 + OIDC authentication flow
- Uses Proof Key for Code Exchange (PKCE) as defined in [RFC 7636](https://tools.ietf.org/html/rfc7636)
- Returns JWT tokens to the frontend client

## Installation

```bash
pip install django-nexus-auth
```

## Configuration

Define the configuration in your `settings.py` file:

```python
NEXUS_AUTH = {
    "CONFIG": {
        "microsoft_tenant": {
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
            "tenant_id": "your-tenant-id",
        },
        "google": {
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
        },
    },
}
```

Add `nexus_auth` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    ...
    'nexus_auth',
]
```

Include the URLs in your project's URL configuration:

```python
from django.urls import include, re_path

urlpatterns = [
    ...
    re_path(r"", include("nexus_auth.urls")),
]
```

## API Endpoints

- `GET /oauth/providers`: Get the active provider types and the corresponding authorization URLs.
- `POST /oauth/<str:provider_type>/exchange`: Exchange the authorization code retrieved from the authorization URL for JWT tokens for your Django application.

## Multi-Tenant Example

By providing a custom `PROVIDERS_HANDLER` value in the settings, you can implement multi-tenant support.

```python
NEXUS_AUTH = {
    "CONFIG": {
        # Tenant A configuration
        "tenantA": {
            "microsoft_tenant": {
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret",
                "tenant_id": "your-tenant-id",
            },
            "google": {
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
            },
        },
        # Tenant B configuration
        "tenantB": {
            "microsoft_tenant": {
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "tenant_id": "your-tenant-id",
            },
            "google": {
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
            },
        },
    },
    "PROVIDERS_HANDLER": "path.to.your_handler_function",
}
```

- Note: It is not mandatory to set the `CONFIG` value if you don't plan to use it. You may modify the handler function to retrieve the provider settings from your own source.

Define your own handler function for getting the provider types.

```python
from nexus_auth.settings import nexus_settings

def your_handler_function(request):
    # Get the tenant from the request headers
    tenant = request.headers.get("X-Tenant")

    if tenant:
        # Get the provider settings for the tenant
        provider_settings = nexus_settings.get_provider_settings().get(tenant)
        if provider_settings:
            return provider_settings

    return None
```

## Adding a new provider

Define the provider object and builder class for your new provider.

```python
from nexus_auth.providers.base import ProviderBuilder, OAuth2IdentityProvider

# Extend OAuth2IdentityProvider class
class CustomProvider(OAuth2IdentityProvider):
    def get_authorization_url(self):
        return "https://your-provider.com/o/oauth2/authorize"

    def get_token_url(self):
        return "https://your-provider.com/o/oauth2/token"


# Define the builder class
class CustomProviderBuilder(ProviderBuilder):
    def __init__(self):
        self._instance = None

    def __call__(self, client_id, client_secret, **_ignored):
        if self._instance is None:
            self._instance = CustomProvider(client_id, client_secret)
        return self._instance
```

Register additional providers in the PROVIDER_BUILDERS setting:

```python
NEXUS_AUTH = {
    "PROVIDER_BUILDERS": {
        "custom_provider_key": "path.to.CustomProviderBuilder",
    },
}
```

This will effectively add the new provider on top of the existing default providers.
