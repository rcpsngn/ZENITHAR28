"""
apps/checks için otomatik testler (Kasa / Banka / POS / Çek-Senet).

Önceki durum raporunda bu dosya tamamen boştu. Bu modül de doğrudan parasal
işlem içerdiği için invoices ile birlikte önceliklendirildi.

Çalıştırmak için:
    python manage.py test apps.checks
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from .models import BankTransaction, CashTransaction, POSTransaction, Check, Promissory


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


# ============================================================
# MODEL TESTLERİ
# ============================================================
class POSTransactionModelTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_komisyon_ve_net_tutar_dogru_hesaplanir(self):
        """1000 TL, %2.5 komisyon -> 25 TL komisyon, 975 TL net tutar."""
        tx = POSTransaction.objects.create(
            user=self.user, card_type="credit",
            amount=Decimal("1000.00"), commission_rate=Decimal("2.5"),
            date=date(2026, 1, 10),
        )
        self.assertEqual(tx.commission_amount, Decimal("25.000"))
        self.assertEqual(tx.net_amount, Decimal("975.000"))

    def test_komisyon_orani_sifirsa_net_tutar_brut_ile_esittir(self):
        tx = POSTransaction.objects.create(
            user=self.user, amount=Decimal("500.00"), commission_rate=Decimal("0"),
            date=date(2026, 1, 10),
        )
        self.assertEqual(tx.net_amount, tx.amount)


class CheckModelTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_cek_varsayilan_durumu_portfoyde(self):
        check = Check.objects.create(
            user=self.user, type="received", check_number="CEK-001",
            bank_name="Ziraat Bankası", payer_name="ABC Ticaret",
            amount=Decimal("10000.00"), issue_date=date(2026, 1, 1), due_date=date(2026, 3, 1),
        )
        self.assertEqual(check.status, "portfolio")

    def test_gecersiz_vade_tarihi_sirasina_gore_siralanir(self):
        """Meta.ordering = ['-due_date'] -> en yakın vadeli en üstte olmamalı, en uzak vadeli üstte olmalı."""
        c1 = Check.objects.create(
            user=self.user, type="received", check_number="CEK-A", bank_name="X Bank",
            payer_name="Müşteri A", amount=Decimal("100"), issue_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
        )
        c2 = Check.objects.create(
            user=self.user, type="received", check_number="CEK-B", bank_name="X Bank",
            payer_name="Müşteri B", amount=Decimal("100"), issue_date=date(2026, 1, 1), due_date=date(2026, 5, 1),
        )
        checks = list(Check.objects.filter(user=self.user))
        self.assertEqual(checks[0].id, c2.id)  # en uzak vade (mayıs) önce gelmeli


# ============================================================
# VIEW TESTLERİ
# ============================================================
class ChecksViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_kasa_islemi_kaydi_olusturur(self):
        response = self.client.post(reverse("cash_transaction_save"), {
            "type": "in", "amount": "1500,50", "date": "2026-01-15", "description": "Nakit tahsilat",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CashTransaction.objects.filter(user=self.user).count(), 1)
        tx = CashTransaction.objects.get(user=self.user)
        # to_decimal() virgülü noktaya çevirmeli
        self.assertEqual(tx.amount, Decimal("1500.50"))

    def test_banka_islemi_kaydi_olusturur(self):
        response = self.client.post(reverse("bank_transaction_save"), {
            "bank_name": "Garanti BBVA", "type": "withdrawal", "amount": "250.00", "date": "2026-01-15",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BankTransaction.objects.filter(user=self.user).count(), 1)

    def test_gecersiz_tutar_hata_vermez_sifir_kabul_edilir(self):
        """to_decimal() bozuk veri karşısında ValueError/InvalidOperation fırlatmak yerine 0 dönmeli."""
        response = self.client.post(reverse("cash_transaction_save"), {
            "type": "in", "amount": "abc-bozuk-veri", "date": "2026-01-15",
        })
        self.assertEqual(response.status_code, 302)
        tx = CashTransaction.objects.get(user=self.user)
        self.assertEqual(tx.amount, Decimal("0"))

    def test_cek_durumu_gecerli_degere_guncellenebilir(self):
        check = Check.objects.create(
            user=self.user, type="received", check_number="CEK-100", bank_name="X Bank",
            payer_name="Müşteri", amount=Decimal("100"), issue_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
        )
        response = self.client.get(reverse("check_update_status", args=[check.id, "banked"]))
        check.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(check.status, "banked")

    def test_cek_durumu_gecersiz_degerle_guncellenemez(self):
        """URL üzerinden rastgele bir status değeri gönderilirse (ör. 'HACKED') kabul edilmemeli."""
        check = Check.objects.create(
            user=self.user, type="received", check_number="CEK-101", bank_name="X Bank",
            payer_name="Müşteri", amount=Decimal("100"), issue_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
        )
        response = self.client.get(reverse("check_update_status", args=[check.id, "HACKED"]))
        check.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(check.status, "portfolio")  # değişmemiş olmalı

    def test_baska_kullanicinin_cekine_erisilemez(self):
        other_user = make_user(username="baskakullanici2")
        other_check = Check.objects.create(
            user=other_user, type="received", check_number="CEK-200", bank_name="X Bank",
            payer_name="Müşteri", amount=Decimal("100"), issue_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
        )
        response = self.client.get(reverse("check_update_status", args=[other_check.id, "banked"]))
        self.assertEqual(response.status_code, 404)

    def test_senet_kaydi_olusturur(self):
        response = self.client.post(reverse("promissory_save"), {
            "type": "received", "promissory_number": "SNT-001", "drawer_name": "Keşideci A.Ş.",
            "amount": "2500.00", "issue_date": "2026-01-01", "due_date": "2026-06-01",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Promissory.objects.filter(user=self.user).count(), 1)

    def test_giris_yapmamis_kullanici_yonlendirilir(self):
        anon_client = Client()
        response = anon_client.get(reverse("checks_notes_tracking"))
        self.assertEqual(response.status_code, 302)


# ============================================================
# DURUM MAKİNESİ (STATE MACHINE) TESTLERİ — Aşama 24
# ============================================================
class CheckStateMachineTests(TestCase):
    """
    Excel notu: "ayrı bir 'state machine' sınıfı yok" (Aşama 24). Artık var
    (bkz. apps/checks/models.py > StatusTransitionMixin). Bu testler geçerli
    ve GEÇERSİZ geçişlerin doğru şekilde kabul/reddedildiğini doğrular.
    """
    def setUp(self):
        self.user = make_user("state_machine_user")
        self.client = Client()
        self.client.force_login(self.user)
        self.check = Check.objects.create(
            user=self.user, type="received", check_number="CEK-SM-1", bank_name="X Bank",
            payer_name="Müşteri", amount=Decimal("1000"), issue_date=date(2026, 1, 1), due_date=date(2026, 3, 1),
        )

    def test_portfoyden_bankaya_gecis_gecerlidir(self):
        self.assertTrue(self.check.can_transition_to("banked"))
        self.check.transition_to("banked")
        self.assertEqual(self.check.status, "banked")

    def test_portfoyden_dogrudan_tahsile_gecis_gecersizdir(self):
        """Bir çek önce bankaya verilmeden doğrudan 'tahsil edildi' olamaz."""
        self.assertFalse(self.check.can_transition_to("cashed"))
        with self.assertRaises(ValidationError):
            self.check.transition_to("cashed")
        self.check.refresh_from_db()
        self.assertEqual(self.check.status, "portfolio")  # değişmemiş olmalı

    def test_tahsil_edilmis_cek_geri_alinamaz(self):
        """'cashed' SON durumdur — hiçbir duruma geçemez."""
        self.check.status = "banked"
        self.check.save(update_fields=["status"])
        self.check.transition_to("cashed")
        self.assertFalse(self.check.can_transition_to("portfolio"))
        with self.assertRaises(ValidationError):
            self.check.transition_to("portfolio")

    def test_view_uzerinden_gecersiz_gecis_hata_mesaji_verir_ve_durum_degismez(self):
        response = self.client.get(reverse("check_update_status", args=[self.check.id, "cashed"]))
        self.check.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.check.status, "portfolio")

    def test_view_uzerinden_gecerli_gecis_basarili_olur(self):
        response = self.client.get(reverse("check_update_status", args=[self.check.id, "banked"]))
        self.check.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.check.status, "banked")

    def test_iade_edilen_cek_tekrar_portfoye_alinabilir(self):
        self.check.status = "banked"
        self.check.save(update_fields=["status"])
        self.check.transition_to("returned")
        self.assertTrue(self.check.can_transition_to("portfolio"))
        self.check.transition_to("portfolio")
        self.assertEqual(self.check.status, "portfolio")
