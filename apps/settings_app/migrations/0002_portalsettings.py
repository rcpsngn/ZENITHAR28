from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("settings_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[
                    ("zenithar", "Zenithar Entegrasyon Altyapısı"),
                    ("gib_manual", "GİB Portal (Manuel)"),
                    ("foriba", "Foriba"),
                    ("uyumsoft", "Uyumsoft"),
                    ("logo", "Logo"),
                    ("mikro", "Mikro"),
                ], default="zenithar", max_length=20)),
                ("api_url", models.URLField(blank=True, help_text="Entegratörün verdiği API adresi (ör. https://api.saglayici.com)")),
                ("api_username", models.CharField(blank=True, max_length=255)),
                ("encrypted_password", models.TextField(blank=True)),
                ("is_verified", models.BooleanField(default=False)),
                ("last_tested_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="portal_settings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Portal Ayarı",
                "verbose_name_plural": "Portal Ayarları",
                "db_table": "portal_settings",
            },
        ),
    ]
