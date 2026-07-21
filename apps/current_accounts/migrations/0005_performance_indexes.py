# Aşama 42 (Final - Performans): sık kullanılan sorgular için DB indeksleri.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('current_accounts', '0004_product_cost_price'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='currentaccount',
            index=models.Index(fields=['user', 'type'], name='idx_curracc_user_type'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['current_account', 'date'], name='idx_transaction_account_date'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['user', 'is_active'], name='idx_product_user_active'),
        ),
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['product', 'date'], name='idx_stockmov_product_date'),
        ),
    ]
