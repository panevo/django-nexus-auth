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
    "PROVIDERS_CONFIG": {
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
    # Register the providers
    "PROVIDER_BUILDERS": {
        "google": "nexus_auth.providers.google.GoogleOAuth2ProviderBuilder",
        "microsoft_tenant": "nexus_auth.providers.microsoft.MicrosoftEntraTenantOAuth2ProviderBuilder",
    },
    "PROVIDERS_HANDLER": "nexus_auth.utils.get_provider_types",
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

## Multi-Tenant Support

The package supports multi-tenant providers by modifying the `PROVIDERS_CONFIG` and `PROVIDERS_HANDLER` settings.

```python
NEXUS_AUTH = {
    "PROVIDERS_CONFIG": {
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
}
```

Define your own handler function for getting the provider types.

```python
from nexus_auth.settings import nexus_settings

def your_handler_function(request):
    tenant = request.headers.get("X-Tenant")

    if tenant:
        provider_settings = nexus_settings.get_provider_settings().get(tenant)
        if provider_settings:
            return list(provider_settings.keys())

    return []
```

Add the handler function to your `settings.py` file:

```python
NEXUS_AUTH = {
    "PROVIDERS_HANDLER": "path.to.your_handler_function",
}
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

Register the provider in the PROVIDER_BUILDERS setting:

```python
NEXUS_AUTH = {
    "PROVIDER_BUILDERS": {
        # ... other providers
        "custom_provider_key": "path.to.CustomProviderBuilder",
    },
}
```
