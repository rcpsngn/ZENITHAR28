from django.db import models
from accounts.models import User

class Invoice(models.Model):
    TYPE_CHOICES = [
        ('e-fatura', 'E-Fatura'),
        ('e-irsaliye', 'E-İrsaliye'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('sent', 'Gönderildi'),
        ('paid', 'Ödendi'),
        ('cancelled', 'İptal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    invoice_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_tax_id = models.CharField(max_length=20, blank=True)
    customer_address = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
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

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoice_items'
        verbose_name = 'Fatura Kalemi'
        verbose_name_plural = 'Fatura Kalemleri'
