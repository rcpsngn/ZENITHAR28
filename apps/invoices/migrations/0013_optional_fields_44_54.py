# Aşama 46/47 (E-Fatura Diğer Seçenekler + KDV Muafiyet), Aşama 50/51/52
# (E-İrsaliye Senaryo/Tip/Fiili Sevk Tarihi), Aşama 48/49 (İhracat bilgileri),
# Aşama 54 (E-İrsaliye Diğer Seçenekler — InvoiceItem alanları ortak).
# Tüm alanlar opsiyoneldir (blank=True), mevcut kayıtlar etkilenmez.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0012_invoice_template_uuid_length"),
    ]

    operations = [
        # ---- InvoiceItem: Diğer Seçenekler + KDV Muafiyet ----
        migrations.AddField(model_name="invoiceitem", name="vat_exemption_reason", field=models.CharField(blank=True, choices=[("", "— Muafiyet Yok —"), ("301", "301 - İhracat İstisnası"), ("350", "350 - Askeri Alanlar İstisnası"), ("999", "999 - Diğer")], default="", max_length=3)),
        migrations.AddField(model_name="invoiceitem", name="seller_code", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="buyer_code", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="barcode", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="brand", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="invoiceitem", name="model_name", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="invoiceitem", name="additional_description", field=models.CharField(blank=True, max_length=500)),
        migrations.AddField(model_name="invoiceitem", name="item_note", field=models.CharField(blank=True, max_length=500)),
        migrations.AddField(model_name="invoiceitem", name="origin_country", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="classification_value", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="classification_version", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="invoiceitem", name="classification_code", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="invoiceitem", name="related_waybill_number", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="related_waybill_date", field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name="invoiceitem", name="order_number", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoiceitem", name="order_date", field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name="invoiceitem", name="additional_info_id", field=models.CharField(blank=True, max_length=100)),

        # ---- Invoice: E-İrsaliye senaryo/tip/fiili sevk tarihi ----
        migrations.AddField(model_name="invoice", name="waybill_scenario", field=models.CharField(blank=True, choices=[("", "—"), ("temel", "Temel İrsaliye"), ("hks", "HKS İrsaliye"), ("insaat_demiri", "İnşaat Demiri İzleme Sistemi")], default="", max_length=20)),
        migrations.AddField(model_name="invoice", name="waybill_type", field=models.CharField(blank=True, choices=[("sevk", "Sevk"), ("matbu", "Matbu")], default="sevk", max_length=10)),
        migrations.AddField(model_name="invoice", name="actual_shipment_date", field=models.DateField(blank=True, help_text="Fiili sevk tarihi — irsaliye düzenleme tarihinden (issue_date) farklı, malın gerçekten yola çıktığı tarih.", null=True)),

        # ---- Invoice: İhracat fatura + teslim yeri bilgileri ----
        migrations.AddField(model_name="invoice", name="export_gtip_no", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="invoice", name="export_delivery_terms", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_shipping_method", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_package_marks", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="invoice", name="export_package_number", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="invoice", name="export_package_count", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="invoice", name="export_customs_tracking_no", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_country", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_district", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_town", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_street", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="invoice", name="export_delivery_postal_code", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="invoice", name="export_delivery_building_name", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invoice", name="export_delivery_building_no", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="invoice", name="export_delivery_door_no", field=models.CharField(blank=True, max_length=20)),
    ]
