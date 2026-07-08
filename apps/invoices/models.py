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
        ('satis', 'Satış'),
        ('ihracat', 'İhracat'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('sent', 'Gönderildi'),
        ('approved', 'Onaylandı'),
        ('paid', 'Ödendi'),
        ('cancelled', 'İptal'),
        ('rejected', 'Reddedildi'),
        ('returned', 'İade'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')

    # Gelen kutusu / arşiv yönetimi (Uyumsoft tarzı ekran için)
    is_read = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    # Otomatik & Genel Bilgiler
    ettn = models.CharField(max_length=100, unique=True, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='e-fatura')
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='satis')
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
    customer_address = models.TextField(blank=True)

    # Finansal Toplamlar
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

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

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"

    def update_totals(self):
        items = self.items.all()
        self.amount = sum(item.total for item in items)
        self.vat_amount = sum(item.vat_amount for item in items)
        self.total_amount = self.amount + self.vat_amount
        super().save(update_fields=['amount', 'vat_amount', 'total_amount'])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=50, default='Adet')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

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