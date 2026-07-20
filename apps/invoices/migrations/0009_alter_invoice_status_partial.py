# Aşama 14 (E-İrsaliye - Gelen/Giden: Kabul/Kısmi Kabul/Red Süreçleri) için
# 'partially_accepted' (Kısmi Kabul) durumu eklendi.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0008_invoice_customer_email_invoice_customer_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Taslak'),
                    ('sent', 'Gönderildi'),
                    ('approved', 'Onaylandı'),
                    ('partially_accepted', 'Kısmi Kabul'),
                    ('paid', 'Ödendi'),
                    ('cancelled', 'İptal'),
                    ('rejected', 'Reddedildi'),
                    ('returned', 'İade'),
                ],
                default='draft', max_length=20,
            ),
        ),
    ]
