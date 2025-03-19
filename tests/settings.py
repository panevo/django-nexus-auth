DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "rest_framework",
    "nexus_auth",
)

MIDDLEWARE = []

ROOT_URLCONF = "nexus_auth.urls"

USE_TZ = True

TIME_ZONE = "UTC"

SECRET_KEY = "foobar"

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

NEXUS_AUTH = {
    "PROVIDERS": {
        "microsoft_tenant": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tenant_id": "test_tenant_id",
        },
        "google": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        },
    },
    "PROVIDERS_HANDLER": "nexus_auth.utils.get_provider_types",
}
