import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("settings_app", "0005_fix_portalsettings_api_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("document_type", models.CharField(choices=[
                    ("e-fatura", "e-Fatura"), ("e-arsiv", "E-Arşiv"), ("e-irsaliye", "e-İrsaliye"),
                ], default="e-fatura", max_length=20)),
                ("name", models.CharField(max_length=150)),
                ("creation_type", models.CharField(choices=[
                    ("customized", "Özelleştirilmiş"), ("uploaded", "Yüklenmiş (.xslt)"),
                ], default="customized", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sender_title", models.CharField(blank=True, help_text="Faturada 'Gönderici' olarak görünecek ünvan.", max_length=255)),
                ("discount_replaces", models.BooleanField(default=False, help_text="İskonto, birim fiyatın yerine mi geçsin?")),
                ("unit_price_format", models.CharField(choices=[("2", "0,00"), ("4", "0,0000"), ("6", "0,000000")], default="2", max_length=2)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="document_templates/logos/")),
                ("signature", models.ImageField(blank=True, null=True, upload_to="document_templates/signatures/")),
                ("bank_info_html", models.TextField(blank=True, help_text="Belge altında görünecek banka hesap bilgileri (zengin metin).")),
                ("note", models.TextField(blank=True)),
                ("sender_note", models.TextField(blank=True)),
                ("recipient_note", models.TextField(blank=True)),
                ("uploaded_file", models.FileField(blank=True, null=True, upload_to="document_templates/uploads/")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="document_templates", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Belge Tasarımı",
                "verbose_name_plural": "Belge Tasarımları",
                "db_table": "document_templates",
                "ordering": ["-created_at"],
            },
        ),
    ]
