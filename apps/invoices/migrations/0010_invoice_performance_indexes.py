# Aşama 42 (Final - Performans): sık kullanılan sorgular için DB indeksleri.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0009_alter_invoice_status_partial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', 'type', 'issue_date'], name='idx_invoice_user_type_date'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', 'status'], name='idx_invoice_user_status'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['invoice_number'], name='idx_invoice_number'),
        ),
    ]
