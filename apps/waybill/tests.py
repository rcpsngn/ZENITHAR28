"""
apps/waybill için testler — Aşama 14 (E-İrsaliye - Gelen/Giden: Kabul/Kısmi
Kabul/Red Süreçleri ve Fiili sevk tarihi doğrulaması).

Çalıştırmak için:
    python manage.py test apps.waybill
"""
from datetime import date, timedelta

from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import User
from apps.invoices.models import Invoice
from .views import _validate_waybill_date, MAX_BACKDATE_DAYS


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


def make_waybill(user, **overrides):
    defaults = dict(
        invoice_number=f"IRS{overrides.pop('seq', '000000001')}",
        type="e-irsaliye",
        customer_name="Test Müşteri A.Ş.",
        issue_date=date.today(),
        status="draft",
    )
    defaults.update(overrides)
    return Invoice.objects.create(user=user, **defaults)


# ============================================================
# TARİH DOĞRULAMA TESTLERİ
# ============================================================
class WaybillDateValidationTests(TestCase):
    def test_bugunun_tarihi_gecerlidir(self):
        self.assertIsNone(_validate_waybill_date(date.today().isoformat()))

    def test_gelecek_tarih_reddedilir(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        error = _validate_waybill_date(future)
        self.assertIsNotNone(error)
        self.assertIn("gelecekte", error)

    def test_izin_verilen_sinirdaki_gecmis_tarih_gecerlidir(self):
        allowed = (date.today() - timedelta(days=MAX_BACKDATE_DAYS)).isoformat()
        self.assertIsNone(_validate_waybill_date(allowed))

    def test_izin_verilenden_fazla_gecmis_tarih_reddedilir(self):
        too_old = (date.today() - timedelta(days=MAX_BACKDATE_DAYS + 1)).isoformat()
        error = _validate_waybill_date(too_old)
        self.assertIsNotNone(error)
        self.assertIn("geriye tarihlenebilir", error)

    def test_bos_tarih_hata_vermez(self):
        self.assertIsNone(_validate_waybill_date(None))
        self.assertIsNone(_validate_waybill_date(""))


# ============================================================
# VIEW TESTLERİ: OLUŞTURMA + TARİH KISITI
# ============================================================
class WaybillCreateTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_gelecek_tarihli_irsaliye_olusturulamaz(self):
        future = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.post(reverse("waybill_create"), {
            "customer_name": "ABC Ticaret", "date": future, "items_json_data": "[]",
        })
        self.assertEqual(response.status_code, 200)  # forma geri döner, redirect olmaz
        self.assertEqual(Invoice.objects.filter(user=self.user, type="e-irsaliye").count(), 0)

    def test_gecerli_tarihli_irsaliye_olusturulur(self):
        response = self.client.post(reverse("waybill_create"), {
            "customer_name": "ABC Ticaret", "date": date.today().isoformat(), "items_json_data": "[]",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Invoice.objects.filter(user=self.user, type="e-irsaliye").count(), 1)


# ============================================================
# VIEW TESTLERİ: KABUL / KISMİ KABUL / RED
# ============================================================
class WaybillApprovalFlowTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_gonderilmis_irsaliye_tam_kabul_edilir(self):
        wb = make_waybill(self.user, status="sent")
        response = self.client.get(reverse("waybill_approve", args=[wb.id]))
        wb.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(wb.status, "approved")

    def test_taslak_irsaliye_kabul_edilemez(self):
        wb = make_waybill(self.user, status="draft")
        response = self.client.get(reverse("waybill_approve", args=[wb.id]))
        wb.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(wb.status, "draft")

    def test_gonderilmis_irsaliye_kismi_kabul_edilir_ve_not_eklenir(self):
        wb = make_waybill(self.user, status="sent")
        response = self.client.post(reverse("waybill_partial_accept", args=[wb.id]), {
            "partial_note": "3 adet ürün hasarlı geldi, kabul edilmedi.",
        })
        wb.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(wb.status, "partially_accepted")
        self.assertIn("hasarlı", wb.notes)

    def test_gonderilmis_irsaliye_reddedilir(self):
        wb = make_waybill(self.user, status="sent")
        response = self.client.get(reverse("waybill_reject", args=[wb.id]))
        wb.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(wb.status, "rejected")

    def test_zaten_kabul_edilmis_irsaliye_tekrar_reddedilemez(self):
        wb = make_waybill(self.user, status="approved")
        response = self.client.get(reverse("waybill_reject", args=[wb.id]))
        wb.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(wb.status, "approved")

    def test_baska_kullanicinin_irsaliyesine_erisilemez(self):
        other = make_user(username="baskakullanici3")
        other_wb = make_waybill(other, seq="000000002", status="sent")
        response = self.client.get(reverse("waybill_approve", args=[other_wb.id]))
        self.assertEqual(response.status_code, 404)


class WaybillTemplateSelectionTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_aktif_eirsaliye_sablonu_secenek_olarak_gelir(self):
        from apps.settings_app.models import DocumentTemplate
        DocumentTemplate.objects.create(user=self.user, document_type="e-irsaliye", name="İrsaliye Şablonu")
        DocumentTemplate.objects.create(user=self.user, document_type="e-fatura", name="Fatura Şablonu")
        response = self.client.get(reverse("waybill_create"))
        names = [t.name for t in response.context["document_templates"]]
        self.assertIn("İrsaliye Şablonu", names)
        self.assertNotIn("Fatura Şablonu", names)

    def test_secilen_sablon_irsaliyeye_kaydedilir(self):
        from apps.settings_app.models import DocumentTemplate
        template = DocumentTemplate.objects.create(user=self.user, document_type="e-irsaliye", name="İrsaliye Şablonu")
        response = self.client.post(reverse("waybill_create"), {
            "customer_name": "Test Müşteri", "date": date.today().isoformat(),
            "items_json_data": "[]", "invoice_template": str(template.id),
        })
        self.assertEqual(response.status_code, 302)
        wb = Invoice.objects.filter(user=self.user, type="e-irsaliye").first()
        self.assertEqual(wb.invoice_template, str(template.id))
