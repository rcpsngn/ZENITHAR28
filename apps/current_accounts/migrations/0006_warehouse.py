# Aşama 19 (Cari & Stok - Depo): Warehouse ve ProductWarehouseStock modelleri.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("current_accounts", "0005_performance_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="warehouses", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Depo",
                "verbose_name_plural": "Depolar",
                "db_table": "warehouses",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ProductWarehouseStock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="warehouse_stocks", to="current_accounts.product")),
                ("warehouse", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_stocks", to="current_accounts.warehouse")),
            ],
            options={
                "verbose_name": "Depo Stok Dağılımı",
                "verbose_name_plural": "Depo Stok Dağılımları",
                "db_table": "product_warehouse_stock",
                "unique_together": {("product", "warehouse")},
            },
        ),
    ]
