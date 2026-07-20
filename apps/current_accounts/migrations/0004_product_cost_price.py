# Aşama 30 (Raporlar - Stok: maliyet analizi) için Product.cost_price alanı.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("current_accounts", "0003_stockmovement"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="cost_price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=12,
                help_text="Ürünün alış/maliyet fiyatı (kâr marjı raporları için).",
            ),
        ),
    ]
