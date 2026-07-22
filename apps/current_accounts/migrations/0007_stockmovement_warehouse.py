# Aşama 55 (Cari & Stok - Depo-Stok Entegrasyonu): StockMovement'a warehouse/
# target_warehouse alanları ve 'transfer' tipi eklendi.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("current_accounts", "0006_warehouse"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stockmovement",
            name="type",
            field=models.CharField(choices=[
                ("in", "Giriş"), ("out", "Çıkış"), ("transfer", "Depolar Arası Transfer"),
            ], max_length=10),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="reason",
            field=models.CharField(choices=[
                ("purchase", "Satın Alma"), ("sale", "Satış"), ("return", "İade"),
                ("count_adjustment", "Sayım Düzeltmesi"), ("damaged", "Fire / Hasar"),
                ("transfer", "Depolar Arası Transfer"), ("other", "Diğer"),
            ], default="other", max_length=20),
        ),
        migrations.AddField(
            model_name="stockmovement",
            name="warehouse",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="movements_out", to="current_accounts.warehouse",
                help_text="Giriş/Çıkış işleminin gerçekleştiği depo, ya da transferde KAYNAK depo.",
            ),
        ),
        migrations.AddField(
            model_name="stockmovement",
            name="target_warehouse",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="movements_in", to="current_accounts.warehouse",
                help_text="Yalnızca 'Depolar Arası Transfer' türünde: malın gittiği HEDEF depo.",
            ),
        ),
    ]
