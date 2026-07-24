from django.db import models
from apps.accounts.models import User
from decimal import Decimal


class Invoice(models.Model):
    TYPE_CHOICES = [
        ('e-fatura', 'E-Fatura'),
        ('e-irsaliye', 'E-İrsaliye'),
        ('e-arsiv', 'E-Arşiv'),
    ]

    INVOICE_TYPE_CHOICES = [
        ('temel', 'Temel'),
        ('ticari', 'Ticari'),
        ('yolcu_beraber', 'Yolcu Beraber'),
        ('ihracat', 'İhracat'),
        ('hal', 'Hal'),
        ('kamu', 'Kamu'),
        ('enerji', 'Enerji'),
        ('ilac_tibbi_cihaz', 'İlaç ve Tıbbi Cihaz'),
        ('yatirim_tesvik', 'Yatırım Teşvik'),
        ('insaat_demiri_izleme_sistemi', 'İnşaat Demiri İzleme Sistemi'),
    ]

    INVOICE_CATEGORY_CHOICES = [
        ('satis', 'Satış'),
        ('iade', 'İade'),
        ('tevkifat', 'Tevkifat'),
        ('istisna', 'İstisna'),
        ('ozel_matrah', 'Özel Matrah'),
        ('ihrac_kayitli', 'İhraç Kayıtlı'),
        ('sgk', 'SGK'),
        ('komisyoncu', 'Komisyoncu'),
        ('hks_satis', 'HKS Satış'),
        ('hks_komisyoncu', 'HKS Komisyoncu'),
        ('tevkifat_iade', 'Tevkifat İade'),
        ('konaklama_vergisi', 'Konaklama Vergisi'),
        ('sarj', 'Şarj'),
        ('sarj_anlik', 'Şarj Anlık'),
        ('teknoloji_destek', 'Teknoloji Destek'),
        ('ytb_satis', 'YTB Satış'),
        ('ytb_istisna', 'YTB İstisna'),
        ('ytb_iade', 'YTB İade'),
        ('ytb_tevkifat', 'YTB Tevkifat'),
        ('ytb_tevkifat_iade', 'YTB Tevkifat İade'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('sent', 'Gönderildi'),
        ('approved', 'Onaylandı'),
        ('partially_accepted', 'Kısmi Kabul'),
        ('paid', 'Ödendi'),
        ('cancelled', 'İptal'),
        ('rejected', 'Reddedildi'),
        ('returned', 'İade'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')

    # Gelen kutusu / arşiv yönetimi (Uyumsoft tarzı ekran için)
    is_read = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    # Aşama 56 (Cari Ekstre - Fatura Entegrasyonu): fatura bir cari hesaba
    # bağlanabilir. Onaylanınca/ödendiğinde apps/invoices/signals.py otomatik
    # bir Transaction (borç) oluşturur — bkz. ledger_posted (tekrar tekrar
    # kayıt oluşmasını önleyen bayrak).
    current_account = models.ForeignKey(
        "current_accounts.CurrentAccount", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoices",
    )
    ledger_posted = models.BooleanField(
        default=False,
        help_text="Bu fatura için cari ekstreye otomatik borç kaydı zaten oluşturuldu mu?"
    )

    # ---- Aşama 50/51/52: E-İrsaliye'ye özel alanlar (yalnızca type='e-irsaliye' iken anlamlı) ----
    WAYBILL_SCENARIO_CHOICES = [
        ("", "—"),
        ("temel", "Temel İrsaliye"),
        ("hks", "HKS İrsaliye"),
        ("insaat_demiri", "İnşaat Demiri İzleme Sistemi"),
    ]
    WAYBILL_TYPE_CHOICES = [
        ("sevk", "Sevk"),
        ("matbu", "Matbu"),
    ]
    waybill_scenario = models.CharField(max_length=20, choices=WAYBILL_SCENARIO_CHOICES, blank=True, default="")
    waybill_type = models.CharField(max_length=10, choices=WAYBILL_TYPE_CHOICES, blank=True, default="sevk")
    actual_shipment_date = models.DateField(
        null=True, blank=True,
        help_text="Fiili sevk tarihi — irsaliye düzenleme tarihinden (issue_date) farklı, malın gerçekten yola çıktığı tarih."
    )

    # ---- Aşama 48/49: İhracat senaryosuna özel alanlar (yalnızca invoice_type='ihracat' iken anlamlı) ----
    export_gtip_no = models.CharField(max_length=50, blank=True, verbose_name="GTİP No")
    export_delivery_terms = models.CharField(max_length=100, blank=True, verbose_name="Teslim Şartı")
    export_shipping_method = models.CharField(max_length=100, blank=True, verbose_name="Gönderilme Şekli")
    export_package_marks = models.CharField(max_length=200, blank=True, verbose_name="Kabın Markası/Cinsi")
    export_package_number = models.CharField(max_length=50, blank=True, verbose_name="Kap Numarası")
    export_package_count = models.CharField(max_length=20, blank=True, verbose_name="Kap Adedi")
    export_customs_tracking_no = models.CharField(max_length=100, blank=True, verbose_name="Gümrük Takip No")

    export_delivery_country = models.CharField(max_length=100, blank=True, verbose_name="Teslim Yeri - Ülke")
    export_delivery_city = models.CharField(max_length=100, blank=True, verbose_name="Teslim Yeri - Şehir")
    export_delivery_district = models.CharField(max_length=100, blank=True, verbose_name="Teslim Yeri - İlçe")
    export_delivery_town = models.CharField(max_length=100, blank=True, verbose_name="Teslim Yeri - Kasaba/Köy")
    export_delivery_street = models.CharField(max_length=200, blank=True, verbose_name="Teslim Yeri - Cadde/Sokak")
    export_delivery_postal_code = models.CharField(max_length=20, blank=True, verbose_name="Teslim Yeri - Posta Kodu")
    export_delivery_building_name = models.CharField(max_length=100, blank=True, verbose_name="Teslim Yeri - Bina Adı")
    export_delivery_building_no = models.CharField(max_length=20, blank=True, verbose_name="Teslim Yeri - Bina No")
    export_delivery_door_no = models.CharField(max_length=20, blank=True, verbose_name="Teslim Yeri - Kapı No")

    # Otomatik & Genel Bilgiler
    ettn = models.CharField(max_length=100, unique=True, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='e-fatura')
    invoice_type = models.CharField(max_length=30, choices=INVOICE_TYPE_CHOICES, default='temel')
    invoice_category = models.CharField(max_length=30, choices=INVOICE_CATEGORY_CHOICES, default='satis')
    invoice_template = models.CharField(
        max_length=40, default='varsayilan',
        help_text="'varsayilan' ya da Belge Tasarımları (DocumentTemplate) modülünden seçilen bir tasarımın UUID'si."
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    custom_no = models.CharField(max_length=50, blank=True)

    # Gelişmiş Döviz Yönetimi
    currency = models.CharField(max_length=10, default='TL')
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1.0000)

    # Alıcı Bilgileri
    customer_name = models.CharField(max_length=200)
    customer_first_name = models.CharField(max_length=100, blank=True)
    customer_last_name = models.CharField(max_length=100, blank=True)
    customer_tax_id = models.CharField(max_length=20, blank=True)
    customer_tax_office = models.CharField(max_length=100, blank=True)

    # Adres Bilgileri
    customer_country = models.CharField(max_length=100, blank=True, default='Türkiye')
    customer_city = models.CharField(max_length=100, blank=True)
    customer_district = models.CharField(max_length=100, blank=True)
    customer_street = models.CharField(max_length=255, blank=True)
    customer_postal_code = models.CharField(max_length=20, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_website = models.URLField(blank=True)

    # Sevk Adresi (Alıcı adresinden farklı olabilir)
    delivery_country = models.CharField(max_length=100, blank=True, default='Türkiye')
    delivery_district = models.CharField(max_length=100, blank=True)
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_street = models.CharField(max_length=500, blank=True)
    customer_address = models.TextField(blank=True)

    # Finansal Toplamlar
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturalar'
        ordering = ['-issue_date']
        indexes = [
            # Aşama 42 (Final - Performans). Bu 3 indeks, en sık çalışan
            # sorguları hedefler:
            #   - dashboard/reports_view: user + type + issue_date (tarih aralığı taraması)
            #   - gelen kutusu/onay ekranları: user + status (durum filtresi)
            #   - fatura numarası üretimi: invoice_number üzerinden startswith araması
            models.Index(fields=['user', 'type', 'issue_date'], name='idx_invoice_user_type_date'),
            models.Index(fields=['user', 'status'], name='idx_invoice_user_status'),
            models.Index(fields=['invoice_number'], name='idx_invoice_number'),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"

    def update_totals(self):
        items = self.items.all()
        self.amount = sum(item.total for item in items)
        self.vat_amount = sum(item.vat_amount for item in items)
        self.total_amount = self.amount + self.vat_amount
        super().save(update_fields=['amount', 'vat_amount', 'total_amount'])


class InvoiceItem(models.Model):
    VAT_EXEMPTION_CHOICES = [
        ("", "— Muafiyet Yok —"),
        ("301", "301 - İhracat İstisnası"),
        ("350", "350 - Askeri Alanlar İstisnası"),
        ("999", "999 - Diğer"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=50, default='Adet')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Aşama 47: kalem bazında KDV muafiyet sebebi (zorunlu değil).
    vat_exemption_reason = models.CharField(max_length=3, choices=VAT_EXEMPTION_CHOICES, blank=True, default="")

    # Aşama 46 / 54: "Diğer Seçenekler" — tamamı opsiyonel, hem e-Fatura hem
    # e-İrsaliye kalemlerinde ortak kullanılır (aynı InvoiceItem modeli).
    seller_code = models.CharField(max_length=100, blank=True, verbose_name="Satıcı Kodu")
    buyer_code = models.CharField(max_length=100, blank=True, verbose_name="Alıcı Kodu")
    barcode = models.CharField(max_length=100, blank=True, verbose_name="Üretici Kodu / Barkod")
    brand = models.CharField(max_length=150, blank=True, verbose_name="Marka")
    model_name = models.CharField(max_length=150, blank=True, verbose_name="Model")
    additional_description = models.CharField(max_length=500, blank=True, verbose_name="Açıklama (Ek)")
    item_note = models.CharField(max_length=500, blank=True, verbose_name="Not")
    origin_country = models.CharField(max_length=100, blank=True, verbose_name="Menşei")
    classification_value = models.CharField(max_length=100, blank=True, verbose_name="Sınıflandırma Değeri")
    classification_version = models.CharField(max_length=50, blank=True, verbose_name="Sınıflandırma Versiyonu")
    classification_code = models.CharField(max_length=50, blank=True, verbose_name="Sınıflandırma Kodu")
    related_waybill_number = models.CharField(max_length=100, blank=True, verbose_name="İrsaliye No")
    related_waybill_date = models.DateField(null=True, blank=True, verbose_name="İrsaliye Tarihi")
    order_number = models.CharField(max_length=100, blank=True, verbose_name="Sipariş No")
    order_date = models.DateField(null=True, blank=True, verbose_name="Sipariş Tarihi")
    additional_info_id = models.CharField(max_length=100, blank=True, verbose_name="Ek Bilgi ID")

    class Meta:
        db_table = 'invoice_items'

    def __str__(self):
        return f"{self.description}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        self.vat_amount = (self.total * self.vat_rate) / Decimal('100')
        super().save(*args, **kwargs)
        self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_totals()