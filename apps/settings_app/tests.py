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
