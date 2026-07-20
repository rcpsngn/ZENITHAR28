# Aşama 20 (Cari & Stok - Stok Hareket) için StockMovement modeli.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("current_accounts", "0002_product"),
    ]

    operations = [
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("type", models.CharField(choices=[("in", "Giriş"), ("out", "Çıkış")], max_length=10)),
                ("reason", models.CharField(choices=[
                    ("purchase", "Satın Alma"),
                    ("sale", "Satış"),
                    ("return", "İade"),
                    ("count_adjustment", "Sayım Düzeltmesi"),
                    ("damaged", "Fire / Hasar"),
                    ("other", "Diğer"),
                ], default="other", max_length=20)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=12)),
                ("date", models.DateField()),
                ("reference_note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movements", to="current_accounts.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_movements", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Stok Hareketi",
                "verbose_name_plural": "Stok Hareketleri",
                "db_table": "stock_movements",
                "ordering": ["-date", "-created_at"],
            },
        ),
    ]
