# invoice_template artık Belge Tasarımları (DocumentTemplate) modülünden
# seçilen bir tasarımın UUID'sini de tutabilsin diye max_length artırıldı.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0011_invoice_current_account"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="invoice_template",
            field=models.CharField(
                default="varsayilan", max_length=40,
                help_text="'varsayilan' ya da Belge Tasarımları (DocumentTemplate) modülünden seçilen bir tasarımın UUID'si.",
            ),
        ),
    ]
