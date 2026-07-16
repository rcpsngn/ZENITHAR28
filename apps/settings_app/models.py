from django.db import models
from apps.accounts.models import User


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255, default='Firmanızın Adı')
    tax_id = models.CharField(max_length=20, blank=True)
    tax_office = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_profiles'
        verbose_name = 'Firma Bilgisi'
        verbose_name_plural = 'Firma Bilgileri'

    def __str__(self):
        return self.company_name