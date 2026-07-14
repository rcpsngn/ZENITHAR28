from django.db import models
from apps.accounts.models import User

class Check(models.Model):
    TYPE_CHOICES = [
        ('received', 'Alınan Çek'),
        ('issued', 'Verilen Çek'),
    ]
    
    STATUS_CHOICES = [
        ('portfolio', 'Portföyde'),
        ('banked', 'Bankaya Verildi'),
        ('cashed', 'Tahsil Edildi'),
        ('returned', 'İade'),
        ('cancelled', 'İptal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checks')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    check_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    payer_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='portfolio')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'checks'
        verbose_name = 'Çek'
        verbose_name_plural = 'Çekler'
        ordering = ['-due_date']

class Promissory(models.Model):
    TYPE_CHOICES = [
        ('received', 'Alınan Senet'),
        ('issued', 'Verilen Senet'),
    ]
    
    STATUS_CHOICES = [
        ('portfolio', 'Portföyde'),
        ('banked', 'Bankaya Verildi'),
        ('cashed', 'Tahsil Edildi'),
        ('returned', 'İade'),
        ('cancelled', 'İptal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promissories')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    promissory_number = models.CharField(max_length=50)
    drawer_name = models.CharField(max_length=200)
    endorser_name = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    place_of_issue = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='portfolio')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promissories'
        verbose_name = 'Senet'
        verbose_name_plural = 'Senetler'
        ordering = ['-due_date']

class BankTransaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Para Girişi'),
        ('withdrawal', 'Para Çıkışı'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_transactions')
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bank_transactions'
        verbose_name = 'Banka Hareketi'
        verbose_name_plural = 'Banka Hareketleri'
        ordering = ['-date']


class CashTransaction(models.Model):
    TYPE_CHOICES = [
        ('in', 'Kasa Girişi'),
        ('out', 'Kasa Çıkışı'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cash_transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cash_transactions'
        verbose_name = 'Kasa İşlemi'
        verbose_name_plural = 'Kasa İşlemleri'
        ordering = ['-date']


class POSTransaction(models.Model):
    CARD_TYPE_CHOICES = [
        ('credit', 'Kredi Kartı'),
        ('debit', 'Banka Kartı'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pos_transactions')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='credit')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateField()
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pos_transactions'
        verbose_name = 'POS İşlemi'
        verbose_name_plural = 'POS İşlemleri'
        ordering = ['-date']

    @property
    def commission_amount(self):
        return self.amount * self.commission_rate / 100

    @property
    def net_amount(self):
        return self.amount - self.commission_amount
