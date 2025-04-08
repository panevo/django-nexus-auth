# Example Project for nexus_auth

This is a simple example project demonstrating how to use the nexus_auth package with Django and Django Rest Framework.

## Setup

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Modify the `settings.py` file to include the configuration for the providers:

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

6. Run the development server:

```bash
python manage.py runserver
```

## Available Endpoints

- `/admin/` - Django admin interface
- `/auth/oauth/providers` - Nexus Auth endpoints
- `/auth/oauth/<str:provider_type>/exchange` - Exchange the authorization code retrieved from the authorization URL for JWT tokens for your Django application
