from django.db import models
from apps.accounts.models import User

class CurrentAccount(models.Model):
    TYPE_CHOICES = [
        ('customer', 'Müşteri'),
        ('supplier', 'Tedarikçi'),
        ('both', 'Her İkisi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_accounts')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=20, blank=True)
    tax_office = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'current_accounts'
        verbose_name = 'Cari Hesap'
        verbose_name_plural = 'Cari Hesaplar'
        ordering = ['name']

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('debit', 'Borç'),
        ('credit', 'Alacak'),
    ]
    
    current_account = models.ForeignKey(CurrentAccount, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=500)
    date = models.DateField()
    document_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'İşlem'
        verbose_name_plural = 'İşlemler'
        ordering = ['-date']

class VATOperation(models.Model):
    TYPE_CHOICES = [
        ('refund', 'İade'),
        ('offset', 'Mahsup'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('in_progress', 'İşlemde'),
        ('completed', 'Tamamlandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vat_operations')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    period = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    guidance_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vat_operations'
        verbose_name = 'KDV İşlemi'
        verbose_name_plural = 'KDV İşlemleri'
        ordering = ['-application_date']

class Product(models.Model):
    UNIT_CHOICES = [
        ('Adet', 'Adet'),
        ('Kg', 'Kilogram'),
        ('Metre', 'Metre'),
        ('Litre', 'Litre'),
        ('Kutu', 'Kutu'),
        ('Paket', 'Paket'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    code = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='Adet')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Ürünün alış/maliyet fiyatı (kâr marjı raporları için)."
    )
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    min_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Ürün / Stok'
        verbose_name_plural = 'Ürünler / Stoklar'
        ordering = ['name']

    @property
    def stock_value(self):
        return self.quantity * self.unit_price

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock_level

    @property
    def profit_margin_per_unit(self):
        """Birim başına kâr (satış fiyatı - maliyet fiyatı). Maliyet girilmemişse 0."""
        return self.unit_price - self.cost_price

    @property
    def potential_profit(self):
        """Mevcut stoğun tamamı satılırsa elde edilecek toplam kâr (Raporlar > Stok, Aşama 30)."""
        return self.profit_margin_per_unit * self.quantity


class StockMovement(models.Model):
    """
    Stok giriş/çıkış fişi (Aşama 20). Kaydedildiğinde apps/current_accounts/signals.py
    içindeki post_save sinyali Product.quantity alanını OTOMATİK günceller —
    Excel notundaki "Stok hareket fişi kesildiğinde ürün adedini güncelleyen
    Django Sinyalleri (Signals) yazılmalı" isteği tam olarak budur.

    Miktarın yetersiz olup olmadığı (çıkışta negatif stoğa düşmemesi) VIEW
    katmanında (kayıttan ÖNCE) kontrol edilir; sinyal yalnızca zaten doğrulanmış
    bir hareketi Product.quantity'e yansıtır.
    """
    TYPE_CHOICES = [
        ('in', 'Giriş'),
        ('out', 'Çıkış'),
    ]

    REASON_CHOICES = [
        ('purchase', 'Satın Alma'),
        ('sale', 'Satış'),
        ('return', 'İade'),
        ('count_adjustment', 'Sayım Düzeltmesi'),
        ('damaged', 'Fire / Hasar'),
        ('other', 'Diğer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    reference_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movements'
        verbose_name = 'Stok Hareketi'
        verbose_name_plural = 'Stok Hareketleri'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_type_display()} - {self.quantity}"
