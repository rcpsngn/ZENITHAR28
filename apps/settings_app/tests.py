"""
apps/settings_app için testler:
- Aşama 36 (Belge Tasarımı: seri no öneki gerçekten fatura numaralandırmasını etkiliyor mu)
- Aşama 37 (Portal Ayarları şifreleme)

Çalıştırmak için:
    python manage.py test apps.settings_app
"""
from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import User
from apps.invoices.models import Invoice
from .models import DocumentDesignSettings, PortalSettings


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


class DocumentDesignSettingsTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_varsayilan_prefix_znt_dir(self):
        response = self.client.get(reverse("document_design"))
        self.assertEqual(response.status_code, 200)
        design = DocumentDesignSettings.objects.get(user=self.user)
        self.assertEqual(design.invoice_number_prefix, "ZNT")

    def test_ozel_prefix_kaydedilir_ve_kucuk_harf_buyutulur(self):
        response = self.client.post(reverse("document_design"), {
            "invoice_number_prefix": "abc", "footer_note": "Test notu",
        })
        self.assertEqual(response.status_code, 302)
        design = DocumentDesignSettings.objects.get(user=self.user)
        self.assertEqual(design.invoice_number_prefix, "ABC")

    def test_ozel_karakterli_prefix_reddedilir(self):
        response = self.client.post(reverse("document_design"), {
            "invoice_number_prefix": "AB-C!", "footer_note": "",
        })
        self.assertEqual(response.status_code, 200)  # forma hata ile geri döner
        design, _ = DocumentDesignSettings.objects.get_or_create(user=self.user)
        self.assertEqual(design.invoice_number_prefix, "ZNT")  # değişmemiş olmalı

    def test_kaydedilen_prefix_yeni_fatura_numarasina_yansir(self):
        DocumentDesignSettings.objects.create(user=self.user, invoice_number_prefix="ABC")
        response = self.client.post(reverse("invoices_page"), {
            "customer_name": "Test Müşteri", "type": "e-fatura",
        })
        self.assertEqual(response.status_code, 302)
        invoice = Invoice.objects.filter(user=self.user).first()
        self.assertIsNotNone(invoice)
        self.assertTrue(invoice.invoice_number.startswith("ABC"))


class PortalSettingsTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_sifre_veritabaninda_duz_metin_olarak_tutulmaz(self):
        self.client.post(reverse("portal_settings"), {
            "provider": "foriba", "api_username": "test_user",
            "api_url": "https://api.foriba.com", "api_password": "cok-gizli-sifre-123",
        })
        portal = PortalSettings.objects.get(user=self.user)
        self.assertNotEqual(portal.encrypted_password, "cok-gizli-sifre-123")
        self.assertNotIn("cok-gizli-sifre-123", portal.encrypted_password)

    def test_sifre_dogru_sekilde_cozulebilir(self):
        self.client.post(reverse("portal_settings"), {
            "provider": "foriba", "api_username": "test_user",
            "api_url": "https://api.foriba.com", "api_password": "cok-gizli-sifre-123",
        })
        portal = PortalSettings.objects.get(user=self.user)
        self.assertEqual(portal.get_password(), "cok-gizli-sifre-123")


# ============================================================
# AŞAMA 38 — BİLDİRİM TERCİHLERİ
# ============================================================
class NotificationPreferencesTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_varsayilan_tercihler_acik_gelir(self):
        from .models import NotificationPreferences
        self.client.get(reverse("notification_settings"))
        prefs = NotificationPreferences.objects.get(user=self.user)
        self.assertTrue(prefs.email_on_new_invoice)
        self.assertTrue(prefs.notify_overdue_checks)

    def test_tercih_kapatilip_kaydedilebilir(self):
        from .models import NotificationPreferences
        response = self.client.post(reverse("notification_settings"), {})  # checkbox'lar işaretsiz gönderildi
        self.assertEqual(response.status_code, 302)
        prefs = NotificationPreferences.objects.get(user=self.user)
        self.assertFalse(prefs.email_on_new_invoice)
        self.assertFalse(prefs.notify_overdue_checks)


# ============================================================
# AŞAMA 39 — SİSTEM TERCİHLERİ VE YEDEKLEME
# ============================================================
class SystemPreferencesTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_dil_tercihi_kaydedilir(self):
        response = self.client.post(reverse("system_settings"), {"language": "en"})
        self.assertEqual(response.status_code, 302)
        from .models import SystemPreferences
        prefs = SystemPreferences.objects.get(user=self.user)
        self.assertEqual(prefs.language, "en")

    def test_yedek_indirme_sqlite_dosyasi_doner(self):
        import tempfile
        from django.test import override_settings

        with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
            tmp.write(b"sahte-sqlite-icerigi")
            tmp_path = tmp.name

        test_databases = {
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": tmp_path}
        }
        with override_settings(DATABASES=test_databases):
            response = self.client.get(reverse("system_backup_download"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get("Content-Disposition", "").startswith("attachment"))

    def test_postgres_kullanilirken_yedek_indirme_404_doner(self):
        from django.test import override_settings
        test_databases = {
            "default": {"ENGINE": "django.db.backends.postgresql", "NAME": "zenithar"}
        }
        with override_settings(DATABASES=test_databases):
            response = self.client.get(reverse("system_backup_download"))
        self.assertEqual(response.status_code, 404)

    def test_giris_yapmamis_kullanici_yedek_indiremez(self):
        anon_client = Client()
        response = anon_client.get(reverse("system_backup_download"))
        self.assertEqual(response.status_code, 302)
