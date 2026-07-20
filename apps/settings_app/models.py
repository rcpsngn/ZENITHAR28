from django.db import models
from apps.accounts.models import User
from .crypto import encrypt_value, decrypt_value, mask_value


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


class PortalSettings(models.Model):
    """
    E-Fatura entegratörü / GİB portal bağlantı bilgileri.
    Şifre hiçbir zaman düz metin olarak saklanmaz; encrypted_password alanında
    Fernet ile şifrelenmiş hâli tutulur (bkz. apps/settings_app/crypto.py).
    """
    PROVIDER_CHOICES = [
        ("zenithar", "Zenithar Entegrasyon Altyapısı"),
        ("gib_manual", "GİB Portal (Manuel)"),
        ("foriba", "Foriba"),
        ("uyumsoft", "Uyumsoft"),
        ("logo", "Logo"),
        ("mikro", "Mikro"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portal_settings')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="zenithar")
    api_url = models.URLField(blank=True, help_text="Entegratörün verdiği API adresi (ör. https://api.saglayici.com)")
    api_username = models.CharField(max_length=255, blank=True)
    encrypted_password = models.TextField(blank=True)  # DB'de her zaman şifreli tutulur
    is_verified = models.BooleanField(default=False)  # "Bağlantıyı Test Et" başarılı oldu mu
    last_tested_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portal_settings'
        verbose_name = 'Portal Ayarı'
        verbose_name_plural = 'Portal Ayarları'

    def __str__(self):
        return f"{self.user} - {self.get_provider_display()}"

    def set_password(self, plain_password: str) -> None:
        """Şifreyi ŞİFRELEYEREK saklar. Düz metni asla self.encrypted_password'e yazma."""
        self.encrypted_password = encrypt_value(plain_password) if plain_password else ""

    def get_password(self) -> str:
        """Gerçek şifreyi çözüp döner (yalnızca sunucu tarafı entegrasyon çağrılarında kullanılmalı)."""
        return decrypt_value(self.encrypted_password)

    def get_masked_password(self) -> str:
        """Şablonda göstermek için maskelenmiş hâl, örn. 'ze******er'."""
        return mask_value(self.get_password())


class DocumentDesignSettings(models.Model):
    """
    Belge & Fatura Tasarım Ayarları (Aşama 36). Excel notundaki tam sürükle-bırak
    şablon tasarım motoru (görsel düzenleyici) bu pakete dahil edilmedi — bu,
    ayrı bir frontend editör bileşeni gerektiren büyük bir özellik; burada
    gerçekten kullanılan ve fatura numarası üretimini etkileyen temel ayarlar
    (seri no öneki, alt not metni) gerçek bir modele bağlandı.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='document_design_settings')
    invoice_number_prefix = models.CharField(
        max_length=10, default="ZNT",
        help_text="Fatura numaralarının başına eklenecek harf kodu (ör. ZNT -> ZNT2026000000001)."
    )
    footer_note = models.TextField(
        blank=True,
        default="Mal bedeli banka hesaplarımıza ödenmelidir. Gecikme faizi %2 olarak uygulanır.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_design_settings'
        verbose_name = 'Belge Tasarım Ayarı'
        verbose_name_plural = 'Belge Tasarım Ayarları'

    def __str__(self):
        return f"{self.user} - {self.invoice_number_prefix}"