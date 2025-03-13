from django.contrib import admin

from nexus_auth.models import OAuthProvider


@admin.register(OAuthProvider)
class OAuthProviderAdmin(admin.ModelAdmin):
    list_display = (
        "get_provider_type_display",
        "is_active",
    )
