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
    "PROVIDERS": {
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
- `POST /oauth/exchange`: Exchange the authorization code retrieved from the authorization URL for JWT tokens for your Django application.
