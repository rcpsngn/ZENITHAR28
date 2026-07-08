from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0004_alter_invoiceitem_options_invoice_exchange_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='is_read',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]
