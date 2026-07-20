"""
apps/invoices için otomatik testler.

Önceki durum raporunda bu dosya tamamen boştu (3 satırlık Django iskeleti).
Parasal işlemler içeren bu modül risk açısından en öncelikli test hedefiydi;
bu yüzden Final - Test görevinde ilk ele alınan modül burası oldu.

Çalıştırmak için:
    python manage.py test apps.invoices
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import User
from .models import Invoice, InvoiceItem
from . import integrations
from . import notifications


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


def make_invoice(user, **overrides):
    defaults = dict(
        invoice_number=f"ZNT2026{overrides.pop('seq', '000000001')}",
        customer_name="Test Müşteri A.Ş.",
        issue_date=date(2026, 1, 15),
        status="draft",
    )
    defaults.update(overrides)
    return Invoice.objects.create(user=user, **defaults)


# ============================================================
# MODEL TESTLERİ
# ============================================================
class InvoiceModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.invoice = make_invoice(self.user)

    def test_invoice_item_hesaplar_kdv_ve_toplami_dogru(self):
        """1 kalem: 100 birim x 10 adet, %20 KDV -> toplam ve KDV doğru hesaplanmalı."""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Dizüstü Bilgisayar",
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            vat_rate=Decimal("20"),
        )
        self.assertEqual(item.total, Decimal("1000.00"))
        self.assertEqual(item.vat_amount, Decimal("200.00"))

    def test_fatura_toplamlari_birden_fazla_kalemde_dogru_toplanir(self):
        """update_totals(): faturadaki tüm kalemlerin toplamı fatura üzerine yansımalı."""
        InvoiceItem.objects.create(
            invoice=self.invoice, description="Kalem 1",
            quantity=Decimal("2"), unit_price=Decimal("50.00"), vat_rate=Decimal("20"),
        )
        InvoiceItem.objects.create(
            invoice=self.invoice, description="Kalem 2",
            quantity=Decimal("1"), unit_price=Decimal("300.00"), vat_rate=Decimal("10"),
        )
        self.invoice.refresh_from_db()
        # Kalem1: 100 tutar + 20 kdv | Kalem2: 300 tutar + 30 kdv
        self.assertEqual(self.invoice.amount, Decimal("400.00"))
        self.assertEqual(self.invoice.vat_amount, Decimal("50.00"))
        self.assertEqual(self.invoice.total_amount, Decimal("450.00"))

    def test_kalem_silinince_fatura_toplami_guncellenir(self):
        item = InvoiceItem.objects.create(
            invoice=self.invoice, description="Silinecek Kalem",
            quantity=Decimal("1"), unit_price=Decimal("500.00"), vat_rate=Decimal("20"),
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.total_amount, Decimal("600.00"))

        item.delete()
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.total_amount, Decimal("0.00"))


# ============================================================
# ENTEGRASYON KATMANI TESTLERİ (apps/invoices/integrations.py)
# ============================================================
class IntegrationsTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_lookup_vkn_bilinen_vkn_icin_basarili_doner(self):
        result = integrations.lookup_vkn("1234567890")
        self.assertTrue(result["success"])
        self.assertIn("title", result)

    def test_lookup_vkn_bilinmeyen_vkn_icin_basarisiz_doner(self):
        result = integrations.lookup_vkn("0000000000")
        self.assertFalse(result["success"])
        self.assertIn("message", result)

    def test_kimlik_bilgisi_yokken_gonderim_simulasyona_duser(self):
        """
        Portal Ayarları / settings.py'de GİB kimlik bilgisi tanımlı değilken
        send_invoice_to_gib() sistemi bozmadan simülasyon sonucu dönmeli.
        """
        invoice = make_invoice(self.user, status="draft")
        result = integrations.send_invoice_to_gib(invoice, user=self.user)
        self.assertTrue(result["success"])
        self.assertTrue(result["simulated"])
        self.assertTrue(result["ettn"])

    def test_kimlik_bilgisi_yokken_iptal_simulasyona_duser(self):
        invoice = make_invoice(self.user, status="sent")
        result = integrations.cancel_invoice_at_gib(invoice, user=self.user)
        self.assertTrue(result["success"])
        self.assertTrue(result["simulated"])

    def test_exchange_rate_tl_icin_her_zaman_bir_doner(self):
        self.assertEqual(integrations.get_exchange_rate("TL"), "1.0000")
        self.assertEqual(integrations.get_exchange_rate("TRY"), "1.0000")

    def test_exchange_rate_ag_erisimi_yokken_fallback_degeri_doner(self):
        """İnternet erişimi olmayan bir test ortamında bile fonksiyon çökmemeli."""
        rate = integrations.get_exchange_rate("USD")
        self.assertIsInstance(rate, str)
        self.assertGreater(float(rate), 0)


# ============================================================
# VIEW / URL TESTLERİ (giriş yapmış kullanıcı senaryoları)
# ============================================================
class InvoiceViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_giris_yapmamis_kullanici_fatura_listesine_yonlendirilir(self):
        anon_client = Client()
        response = anon_client.get(reverse("invoices_draft"))
        self.assertEqual(response.status_code, 302)  # login sayfasına yönlenir

    def test_taslak_fatura_gonderilince_durumu_sent_olur(self):
        invoice = make_invoice(self.user, status="draft")
        response = self.client.get(reverse("invoice_send", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(invoice.status, "sent")
        self.assertTrue(invoice.ettn)  # simülasyon modunda bile bir ETTN atanmalı

    def test_gonderilmis_fatura_iptal_edilince_durumu_cancelled_olur(self):
        invoice = make_invoice(self.user, status="sent")
        response = self.client.get(reverse("invoice_cancel", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(invoice.status, "cancelled")

    def test_taslak_olmayan_fatura_silinemez(self):
        """invoice_delete view'ı yalnızca status='draft' faturaları siler (get_object_or_404 filtresi)."""
        invoice = make_invoice(self.user, status="sent")
        response = self.client.get(reverse("invoice_delete", args=[invoice.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Invoice.objects.filter(id=invoice.id).exists())

    def test_baska_kullanicinin_faturasina_erisilemez(self):
        """user filtresi sayesinde başka kullanıcının faturası 404 dönmeli (veri izolasyonu)."""
        other_user = make_user(username="baskakullanici")
        other_invoice = make_invoice(other_user, seq="000000002", status="draft")
        response = self.client.get(reverse("invoice_send", args=[other_invoice.id]))
        self.assertEqual(response.status_code, 404)


# ============================================================
# GELEN FATURA ONAY/RED TESTLERİ — Aşama 9
# ============================================================
class InvoiceApproveRejectTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_gonderilmis_fatura_onaylanabilir(self):
        invoice = make_invoice(self.user, status="sent")
        response = self.client.get(reverse("invoice_approve", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(invoice.status, "approved")

    def test_taslak_fatura_onaylanamaz(self):
        """Bir taslak (draft) fatura, 'gelen kutusu' onay akışından geçmeden onaylanamamalı."""
        invoice = make_invoice(self.user, status="draft")
        response = self.client.get(reverse("invoice_approve", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(invoice.status, "draft")  # değişmemiş olmalı

    def test_gonderilmis_fatura_reddedilebilir(self):
        invoice = make_invoice(self.user, status="sent")
        response = self.client.get(reverse("invoice_reject", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(invoice.status, "rejected")

    def test_zaten_onaylanmis_fatura_tekrar_reddedilemez(self):
        invoice = make_invoice(self.user, status="approved")
        response = self.client.get(reverse("invoice_reject", args=[invoice.id]))
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(invoice.status, "approved")  # değişmemiş olmalı


# ============================================================
# E-ARŞİV BİLDİRİM (MAIL/SMS) TESTLERİ — Aşama 11
# ============================================================
class EArchiveNotificationTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_email_alani_bosken_gonderim_basarisiz_doner(self):
        invoice = make_invoice(self.user, seq="000000003", status="sent", customer_email="")
        result = notifications.send_earchive_email(invoice)
        self.assertFalse(result["success"])

    def test_email_alani_doluyken_konsol_modunda_basarili_doner(self):
        """Test ortamında EMAIL_BACKEND=locmem kullanılır (Django test runner varsayılanı); yine de başarı dönmeli."""
        invoice = make_invoice(self.user, seq="000000004", status="sent", customer_email="musteri@example.com")
        result = notifications.send_earchive_email(invoice)
        self.assertTrue(result["success"])

    def test_telefon_alani_bosken_sms_basarisiz_doner(self):
        invoice = make_invoice(self.user, seq="000000005", status="sent", customer_phone="")
        result = notifications.send_earchive_sms(invoice)
        self.assertFalse(result["success"])

    def test_sms_api_anahtari_yokken_simulasyona_duser(self):
        invoice = make_invoice(self.user, seq="000000006", status="sent", customer_phone="05551234567")
        result = notifications.send_earchive_sms(invoice)
        self.assertTrue(result["success"])
        self.assertTrue(result["simulated"])

    def test_earsiv_olmayan_fatura_icin_bildirim_view_404_doner(self):
        """invoice_notify_customer yalnızca type='e-arsiv' faturalar için çalışmalı."""
        invoice = make_invoice(self.user, seq="000000007", type="e-fatura", status="sent")
        response = self.client.get(reverse("invoice_notify_customer", args=[invoice.id]))
        self.assertEqual(response.status_code, 404)

    def test_earsiv_faturasi_icin_bildirim_view_yonlendirir(self):
        invoice = make_invoice(
            self.user, seq="000000008", type="e-arsiv", status="sent",
            customer_email="musteri@example.com",
        )
        response = self.client.get(reverse("invoice_notify_customer", args=[invoice.id]))
        self.assertEqual(response.status_code, 302)
