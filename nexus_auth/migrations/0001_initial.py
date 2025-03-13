from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OAuthProvider",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider_type",
                    models.CharField(
                        max_length=32,
                        choices=[
                            ("microsoft_tenant", "Microsoft Entra ID Tenant"),
                            ("google", "Google"),
                        ],
                        help_text="Type of OAuth provider",
                        null=False,
                        blank=False,
                    ),
                ),
                (
                    "client_id",
                    models.CharField(
                        max_length=255,
                        help_text="OAuth client ID obtained from the provider",
                        null=False,
                        blank=False,
                    ),
                ),
                (
                    "client_secret",
                    models.CharField(
                        max_length=255,
                        help_text="OAuth client secret obtained from the provider",
                        null=False,
                        blank=False,
                    ),
                ),
                (
                    "tenant_id",
                    models.CharField(
                        max_length=255,
                        null=True,
                        blank=True,
                        help_text="Tenant ID for OAuth provider (e.g. Microsoft Entra ID Tenant UUID). Leave blank when using common tenant",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this provider is currently active",
                    ),
                ),
            ],
            options={
                "verbose_name": "OAuth Provider",
                "verbose_name_plural": "OAuth Providers",
            },
        ),
    ]
