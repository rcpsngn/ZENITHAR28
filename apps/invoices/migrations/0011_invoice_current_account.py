# Aşama 56 (Cari & Stok - Cari Ekstre-Fatura Entegrasyonu): Invoice modeline
# current_account FK ve ledger_posted bayrağı eklendi.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("current_accounts", "0007_stockmovement_warehouse"),
        ("invoices", "0010_invoice_performance_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="current_account",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="invoices", to="current_accounts.currentaccount",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="ledger_posted",
            field=models.BooleanField(
                default=False,
                help_text="Bu fatura için cari ekstreye otomatik borç kaydı zaten oluşturuldu mu?",
            ),
        ),
    ]
