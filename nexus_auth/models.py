from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ProviderType(models.TextChoices):
    """Supported OAuth provider types"""
    MICROSOFT_TENANT = "microsoft_tenant", _("Microsoft Entra ID Tenant")
    GOOGLE = "google", _("Google")


class OAuthProvider(models.Model):
    """Model to store OAuth provider configuration."""

    provider_type = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=ProviderType.choices,
        help_text=_("Type of OAuth provider"),
    )
    client_id = models.CharField(
        max_length=255, help_text=_("OAuth client ID obtained from the provider"),
        null=False,
        blank=False,
    )
    client_secret = models.CharField(
        max_length=255, help_text=_("OAuth client secret obtained from the provider"),
        null=False,
        blank=False,
    )
    tenant_id = models.CharField(
        max_length=255,
        help_text=_(
            "Tenant ID for OAuth provider (e.g. Microsoft Entra ID Tenant UUID). Leave blank when using common tenant"
        ),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether this provider is currently active")
    )

    class Meta:
        verbose_name = _("OAuth Provider")
        verbose_name_plural = _("OAuth Providers")

    def __str__(self) -> str:
        return f"{self.provider_type}"

    def clean(self) -> None:
        """Validate model fields"""
        if self.provider_type == ProviderType.MICROSOFT_TENANT and not self.tenant_id:
            raise ValidationError(
                {"tenant_id": _("Tenant ID is required for Microsoft Entra ID Tenant")}
            )

    def save(self, *args, **kwargs) -> None:
        """Ensure only one provider can be active at a time."""
        if self.is_active:
            # Set all other rows to False before saving this instance
            OAuthProvider.objects.update(is_active=False)
        super().save(*args, **kwargs)
