# Aşama 36 (Genel Ayarlar - Belge Tasarımı) için DocumentDesignSettings modeli.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("settings_app", "0002_portalsettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentDesignSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number_prefix", models.CharField(
                    default="ZNT", max_length=10,
                    help_text="Fatura numaralarının başına eklenecek harf kodu (ör. ZNT -> ZNT2026000000001).",
                )),
                ("footer_note", models.TextField(
                    blank=True,
                    default="Mal bedeli banka hesaplarımıza ödenmelidir. Gecikme faizi %2 olarak uygulanır.",
                )),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="document_design_settings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Belge Tasarım Ayarı",
                "verbose_name_plural": "Belge Tasarım Ayarları",
                "db_table": "document_design_settings",
            },
        ),
    ]
