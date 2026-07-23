"""
zenithar/tests.py — proje düzeyinde tanımlı view'lar (home, reports_view) için
testler. Bunlar bir Django app'i içinde değil doğrudan zenithar/urls.py'de
tanımlı olduğu için, çalıştırmak üzere modülü açıkça belirtmek gerekir:

    python manage.py test zenithar

Aşama 30 (Raporlar - Stok): "maliyet analizi ve en çok satan ürün kırılımı
eklenirse tamamlanabilir" notu kapsamında eklenen `top_selling_products` ve
kâr marjı (`total_potential_profit`, `most_profitable_products`) verilerini
doğrular.
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from apps.accounts.models import User
from apps.current_accounts.models import Product
from apps.invoices.models import Invoice, InvoiceItem
from apps.help.models import Announcement


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


class ReportsStockAnalysisTests(TestCase):
    def setUp(self):
        cache.clear()  # reports_view Aşama 42'de 5 dk cache'leniyor; testler arası sızıntıyı önler
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_giris_yapmamis_kullanici_yonlendirilir(self):
        anon_client = Client()
        response = anon_client.get(reverse("reports"))
        self.assertEqual(response.status_code, 302)

    def test_kar_marji_sifir_maliyetli_urunde_satis_fiyatina_esittir(self):
        Product.objects.create(
            user=self.user, name="Maliyetsiz Ürün", quantity=Decimal("10"),
            unit_price=Decimal("100"), cost_price=Decimal("0"),
        )
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_potential_profit"], Decimal("1000"))

    def test_kar_marji_dogru_hesaplanir(self):
        # (100 - 60) birim kâr * 10 adet = 400 potansiyel kâr
        Product.objects.create(
            user=self.user, name="Kârlı Ürün", quantity=Decimal("10"),
            unit_price=Decimal("100"), cost_price=Decimal("60"),
        )
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.context["total_potential_profit"], Decimal("400"))
        self.assertEqual(len(response.context["most_profitable_products"]), 1)

    def test_en_cok_satan_urun_kirilimi_dogru_gruplanir(self):
        invoice = Invoice.objects.create(
            user=self.user, invoice_number="ZNT2026TEST01", type="e-fatura",
            customer_name="Test Müşteri", issue_date=date.today(), status="sent",
        )
        InvoiceItem.objects.create(
            invoice=invoice, description="Dizüstü Bilgisayar",
            quantity=Decimal("2"), unit_price=Decimal("1000"), vat_rate=Decimal("20"),
        )
        InvoiceItem.objects.create(
            invoice=invoice, description="Dizüstü Bilgisayar",
            quantity=Decimal("1"), unit_price=Decimal("1000"), vat_rate=Decimal("20"),
        )
        response = self.client.get(reverse("reports"))
        top = list(response.context["top_selling_products"])
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["description"], "Dizüstü Bilgisayar")
        self.assertEqual(top[0]["total_quantity"], Decimal("3"))  # 2 + 1 birleşti

    def test_taslak_faturalar_en_cok_satan_hesaba_katilmaz(self):
        invoice = Invoice.objects.create(
            user=self.user, invoice_number="ZNT2026TEST02", type="e-fatura",
            customer_name="Test Müşteri", issue_date=date.today(), status="draft",
        )
        InvoiceItem.objects.create(
            invoice=invoice, description="Taslak Kalem",
            quantity=Decimal("5"), unit_price=Decimal("500"), vat_rate=Decimal("20"),
        )
        response = self.client.get(reverse("reports"))
        descriptions = [row["description"] for row in response.context["top_selling_products"]]
        self.assertNotIn("Taslak Kalem", descriptions)

    def test_baska_kullanicinin_urunu_raporlara_karismaz(self):
        other = make_user(username="baskakullanici6")
        Product.objects.create(
            user=other, name="Başkasının Ürünü", quantity=Decimal("100"),
            unit_price=Decimal("1000"), cost_price=Decimal("1"),
        )
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.context["total_potential_profit"], 0)

    def test_rapor_sonucu_cache_e_yaziliyor(self):
        """Aşama 42: reports_view sonucu kullanıcı+gün bazında cache'leniyor mu?"""
        self.client.get(reverse("reports"))
        cache_key = f"reports_view:{self.user.id}:{date.today().isoformat()}"
        self.assertIsNotNone(cache.get(cache_key))

    def test_cache_farkli_kullanicilar_icin_karismaz(self):
        Product.objects.create(
            user=self.user, name="Ürün A", quantity=Decimal("1"),
            unit_price=Decimal("500"), cost_price=Decimal("0"),
        )
        self.client.get(reverse("reports"))  # self.user için cache'e yazılır

        other = make_user(username="baskakullanici7")
        other_client = Client()
        other_client.force_login(other)
        response = other_client.get(reverse("reports"))
        # other kullanıcının cache anahtarı farklı olduğu için kendi (boş) verisini görmeli
        self.assertEqual(response.context["total_potential_profit"], 0)


# ============================================================
# ANA SAYFA (home) — TREND GRAFİĞİ VE DUYURULAR TESTLERİ
# ============================================================
class HomeDashboardTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_ana_sayfa_giris_yapmis_kullaniciya_acilir(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_trend_verisi_90_gun_uzunlugundadir(self):
        """Trend verisi artık 90 gün; ana sayfadaki 7/30/90 gün butonları bunu istemci tarafında dilimler."""
        response = self.client.get(reverse("home"))
        import json
        labels = json.loads(response.context["trend_labels_json"])
        efatura = json.loads(response.context["trend_efatura_json"])
        self.assertEqual(len(labels), 90)
        self.assertEqual(len(efatura), 90)

    def test_gonderilen_efatura_trend_grafigine_yansir(self):
        Invoice.objects.create(
            user=self.user, invoice_number="ZNT2026TREND01", type="e-fatura",
            customer_name="Trend Test", issue_date=date.today(), status="sent",
        )
        response = self.client.get(reverse("home"))
        import json
        efatura_series = json.loads(response.context["trend_efatura_json"])
        pending_series = json.loads(response.context["trend_pending_json"])
        self.assertEqual(sum(efatura_series), 1)
        self.assertEqual(sum(pending_series), 1)  # status='sent' olduğu için bekleyen sayılır

    def test_taslak_fatura_trend_grafigine_yansimaz(self):
        Invoice.objects.create(
            user=self.user, invoice_number="ZNT2026TREND02", type="e-fatura",
            customer_name="Taslak Test", issue_date=date.today(), status="draft",
        )
        response = self.client.get(reverse("home"))
        import json
        efatura_series = json.loads(response.context["trend_efatura_json"])
        self.assertEqual(sum(efatura_series), 0)

    def test_durum_sayaclari_dogru_hesaplanir(self):
        Invoice.objects.create(user=self.user, invoice_number="A1", type="e-fatura", customer_name="X", issue_date=date.today(), status="approved")
        Invoice.objects.create(user=self.user, invoice_number="A2", type="e-fatura", customer_name="X", issue_date=date.today(), status="approved")
        Invoice.objects.create(user=self.user, invoice_number="A3", type="e-fatura", customer_name="X", issue_date=date.today(), status="rejected")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["status_counts"]["approved"], 2)
        self.assertEqual(response.context["status_counts"]["rejected"], 1)

    def test_duyuru_yokken_bos_liste_doner(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context["gib_announcements"]), 0)
        self.assertEqual(len(response.context["general_announcements"]), 0)

    def test_aktif_duyuru_dogru_kategoride_gorunur(self):
        Announcement.objects.create(category="gib", title="GİB test duyurusu", published_date=date.today())
        Announcement.objects.create(category="general", title="Genel test duyurusu", published_date=date.today())
        Announcement.objects.create(category="gib", title="Pasif duyuru", published_date=date.today(), is_active=False)

        response = self.client.get(reverse("home"))
        gib_titles = [a.title for a in response.context["gib_announcements"]]
        general_titles = [a.title for a in response.context["general_announcements"]]
        self.assertIn("GİB test duyurusu", gib_titles)
        self.assertIn("Genel test duyurusu", general_titles)
        self.assertNotIn("Pasif duyuru", gib_titles)
