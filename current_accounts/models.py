from django.db import models
from accounts.models import User

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
