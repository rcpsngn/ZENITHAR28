"""
apps/current_accounts için testler:
- Aşama 16 (Cari Ekstre - Excel/CSV export)
- Aşama 20 (Stok Hareket - hareket fişi + Django sinyali ile otomatik stok güncelleme)

Çalıştırmak için:
    python manage.py test apps.current_accounts
"""
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import User
from .models import CurrentAccount, Transaction, Product, StockMovement, Warehouse


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


def make_account(user, **overrides):
    defaults = dict(type="customer", name="Test Cari A.Ş.")
    defaults.update(overrides)
    return CurrentAccount.objects.create(user=user, **defaults)


def make_product(user, **overrides):
    defaults = dict(name="Test Ürün", quantity=Decimal("100"), unit_price=Decimal("50"))
    defaults.update(overrides)
    return Product.objects.create(user=user, **defaults)


# ============================================================
# AŞAMA 20 — STOK HAREKETİ + SİNYAL TESTLERİ
# ============================================================
class StockMovementSignalTests(TestCase):
    """
    Bu testler doğrudan model üzerinden çalışır (view'ı atlar) çünkü asıl
    doğrulanmak istenen şey Django sinyalinin (apps/current_accounts/signals.py)
    StockMovement kaydedildiğinde Product.quantity'i otomatik güncellediğidir.
    """
    def setUp(self):
        self.user = make_user()
        self.product = make_product(self.user, quantity=Decimal("100"))

    def test_giris_hareketi_stogu_artirir(self):
        StockMovement.objects.create(
            user=self.user, product=self.product, type="in",
            quantity=Decimal("25"), date=date(2026, 1, 10),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("125"))

    def test_cikis_hareketi_stogu_azaltir(self):
        StockMovement.objects.create(
            user=self.user, product=self.product, type="out",
            quantity=Decimal("30"), date=date(2026, 1, 10),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("70"))

    def test_birden_fazla_hareket_dogru_birikir(self):
        StockMovement.objects.create(user=self.user, product=self.product, type="in", quantity=Decimal("10"), date=date(2026, 1, 1))
        StockMovement.objects.create(user=self.user, product=self.product, type="out", quantity=Decimal("40"), date=date(2026, 1, 2))
        StockMovement.objects.create(user=self.user, product=self.product, type="in", quantity=Decimal("5"), date=date(2026, 1, 3))
        self.product.refresh_from_db()
        # 100 + 10 - 40 + 5 = 75
        self.assertEqual(self.product.quantity, Decimal("75"))

    def test_hareket_kaydi_guncellenince_stok_tekrar_degismez(self):
        """Sinyal yalnızca created=True (yeni kayıt) durumunda tetiklenmeli."""
        movement = StockMovement.objects.create(
            user=self.user, product=self.product, type="in", quantity=Decimal("10"), date=date(2026, 1, 1),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("110"))

        movement.reference_note = "not güncellendi"
        movement.save()  # created=False -> sinyal stoğu tekrar değiştirmemeli
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("110"))


class StockMovementViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)
        self.product = make_product(self.user, quantity=Decimal("50"))

    def test_yetersiz_stokla_cikis_reddedilir(self):
        response = self.client.post(reverse("stock_movement_save"), {
            "product": self.product.id, "type": "out", "quantity": "999",
            "date": "2026-01-15", "reason": "sale",
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("50"))  # değişmemiş olmalı
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_yeterli_stokla_cikis_kabul_edilir(self):
        response = self.client.post(reverse("stock_movement_save"), {
            "product": self.product.id, "type": "out", "quantity": "20",
            "date": "2026-01-15", "reason": "sale",
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal("30"))

    def test_sifir_veya_negatif_miktar_reddedilir(self):
        response = self.client.post(reverse("stock_movement_save"), {
            "product": self.product.id, "type": "in", "quantity": "0",
            "date": "2026-01-15",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_baska_kullanicinin_urunune_hareket_girilemez(self):
        other = make_user(username="baskakullanici4")
        other_product = make_product(other, quantity=Decimal("10"))
        response = self.client.post(reverse("stock_movement_save"), {
            "product": other_product.id, "type": "in", "quantity": "5", "date": "2026-01-15",
        })
        self.assertEqual(response.status_code, 404)


# ============================================================
# AŞAMA 16 — CARİ EKSTRE EXPORT TESTLERİ
# ============================================================
class AccountStatementExportTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)
        self.account = make_account(self.user)
        Transaction.objects.create(
            current_account=self.account, type="debit", amount=Decimal("1000"),
            description="Satış Faturası", date=date(2026, 1, 5),
        )
        Transaction.objects.create(
            current_account=self.account, type="credit", amount=Decimal("400"),
            description="Tahsilat", date=date(2026, 1, 10),
        )

    def test_csv_export_calisir_ve_dogru_icerige_sahiptir(self):
        response = self.client.get(reverse("account_statement_export", args=[self.account.id, "csv"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8-sig")
        content = response.content.decode("utf-8-sig")
        self.assertIn("Satış Faturası", content)
        self.assertIn("Tahsilat", content)

    def test_xlsx_export_calisir(self):
        response = self.client.get(reverse("account_statement_export", args=[self.account.id, "xlsx"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertGreater(len(response.content), 0)

    def test_gecersiz_format_400_doner(self):
        response = self.client.get(reverse("account_statement_export", args=[self.account.id, "pdf"]))
        self.assertEqual(response.status_code, 400)

    def test_baska_kullanicinin_carisi_export_edilemez(self):
        other = make_user(username="baskakullanici5")
        other_account = make_account(other, name="Başkasının Carisi")
        response = self.client.get(reverse("account_statement_export", args=[other_account.id, "csv"]))
        self.assertEqual(response.status_code, 404)


# ============================================================
# AŞAMA 19 — DEPO TESTLERİ
# ============================================================
class WarehouseTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_depo_eklenir(self):
        response = self.client.post(reverse("warehouse_save"), {"name": "Ana Depo", "location": "İstanbul"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Warehouse.objects.filter(user=self.user).count(), 1)

    def test_isim_bos_olunca_depo_eklenmez(self):
        response = self.client.post(reverse("warehouse_save"), {"name": "", "location": "İstanbul"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Warehouse.objects.filter(user=self.user).count(), 0)

    def test_baska_kullanicinin_deposu_silinemez(self):
        other = make_user(username="baskakullanici8")
        other_warehouse = Warehouse.objects.create(user=other, name="Başkasının Deposu")
        response = self.client.get(reverse("warehouse_delete", args=[other_warehouse.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Warehouse.objects.filter(id=other_warehouse.id).exists())


# ============================================================
# AŞAMA 17 — CARİ HESAP YAŞLANDIRMA TESTLERİ
# ============================================================
class AgingBucketTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)
        self.account = make_account(self.user)

    def test_odenmis_hesapta_yaslandirma_sifirdir(self):
        Transaction.objects.create(current_account=self.account, type="debit", amount=Decimal("1000"), description="Borç", date=date.today())
        Transaction.objects.create(current_account=self.account, type="credit", amount=Decimal("1000"), description="Ödeme", date=date.today())
        response = self.client.get(reverse("account_statement_detail", args=[self.account.id]))
        aging = response.context["aging"]
        self.assertEqual(sum(aging.values()), 0)

    def test_90_gunden_eski_borc_dogru_kovaya_duser(self):
        old_date = date.today() - timedelta(days=120)
        Transaction.objects.create(current_account=self.account, type="debit", amount=Decimal("500"), description="Eski borç", date=old_date)
        response = self.client.get(reverse("account_statement_detail", args=[self.account.id]))
        aging = response.context["aging"]
        self.assertEqual(aging["d90_plus"], Decimal("500"))
        self.assertEqual(aging["d0_30"], Decimal("0"))

    def test_yeni_borc_0_30_kovasina_duser(self):
        Transaction.objects.create(current_account=self.account, type="debit", amount=Decimal("300"), description="Yeni borç", date=date.today())
        response = self.client.get(reverse("account_statement_detail", args=[self.account.id]))
        aging = response.context["aging"]
        self.assertEqual(aging["d0_30"], Decimal("300"))
