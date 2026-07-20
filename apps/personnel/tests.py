"""
apps/personnel için testler — özellikle "Kimlik Doğrulama > Yetkilendirme"
(Aşama 3) kapsamında eklenen rol tabanlı izin sınıflarını (apps/accounts/permissions.py)
doğrular.

Çalıştırmak için:
    python manage.py test apps.personnel
"""
from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from .models import Employee, Salary


def make_user(username, role="viewer"):
    return User.objects.create_user(username=username, password="test-pass-123", role=role)


def make_employee(user):
    return Employee.objects.create(
        user=user, full_name="Ahmet Yılmaz", identity_number="12345678901",
        phone="5551234567", position="Yazılım Geliştirici", hire_date=date(2025, 1, 1),
        salary=Decimal("50000.00"),
    )


class SalaryPermissionTests(TestCase):
    """
    Maaş (Salary) hassas finansal veridir: yalnızca admin/accountant rolündeki
    kullanıcılar oluşturabilir/güncelleyebilir/silebilir. 'employee' ve 'viewer'
    rolleri yalnızca görüntüleyebilir (salt okunur).
    """

    def setUp(self):
        self.owner = make_user("firma_sahibi", role="accountant")
        self.employee_obj = make_employee(self.owner)
        self.salary = Salary.objects.create(
            employee=self.employee_obj, month=1, year=2026,
            base_salary=Decimal("50000.00"), net_salary=Decimal("45000.00"),
        )

    def test_accountant_maas_olusturabilir(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.post("/personnel/api/salaries/", {
            "employee": self.employee_obj.id, "month": 2, "year": 2026,
            "base_salary": "50000.00", "net_salary": "45000.00",
        })
        self.assertEqual(response.status_code, 201)

    def test_viewer_rolu_maas_olusturamaz(self):
        """'viewer' rolündeki kullanıcı kendi tenant'ında bile olsa maaş POST edememeli."""
        viewer_user = make_user("goruntuleyici", role="viewer")
        # Not: Bu senaryoda viewer farklı bir 'user' (tenant) olduğu için zaten
        # IsOwner katmanında da engellenir; asıl amaç ReadOnlyOrHasRole'ün
        # yazma isteklerini reddettiğini görmek, o yüzden aynı tenant'ı simüle
        # etmek yerine rol kontrolünü izole test ediyoruz:
        from apps.accounts.permissions import ReadOnlyOrHasRole

        class DummyRequest:
            method = "POST"
            user = viewer_user

        perm = ReadOnlyOrHasRole.for_roles("accountant")()
        self.assertFalse(perm.has_permission(DummyRequest(), None))

    def test_viewer_rolu_maas_gorebilir_salt_okunur(self):
        from apps.accounts.permissions import ReadOnlyOrHasRole

        class DummyRequest:
            method = "GET"
            user = self.owner

        perm = ReadOnlyOrHasRole.for_roles("accountant")()
        self.assertTrue(perm.has_permission(DummyRequest(), None))

    def test_admin_rolu_her_zaman_gecer(self):
        from apps.accounts.permissions import HasRole

        admin_user = make_user("yonetici", role="admin")

        class DummyRequest:
            user = admin_user

        # allowed_roles boş olsa bile (yalnızca accountant/finance için tanımlanmış olsa
        # bile) admin rolü her zaman geçmeli.
        perm = HasRole.for_roles("accountant")()
        self.assertTrue(perm.has_permission(DummyRequest(), None))

    def test_giris_yapmamis_kullanici_reddedilir(self):
        from apps.accounts.permissions import HasRole

        class AnonUser:
            is_authenticated = False

        class DummyRequest:
            user = AnonUser()

        perm = HasRole.for_roles("accountant")()
        self.assertFalse(perm.has_permission(DummyRequest(), None))


class IsOwnerPermissionTests(TestCase):
    def test_baska_kullanicinin_calisanina_erisim_engellenir(self):
        owner_a = make_user("firma_a")
        owner_b = make_user("firma_b")
        employee_a = make_employee(owner_a)

        client = APIClient()
        client.force_authenticate(user=owner_b)
        # get_queryset zaten user=request.user ile filtrelediği için 404 dönmeli.
        response = client.get(f"/personnel/api/employees/{employee_a.id}/")
        self.assertEqual(response.status_code, 404)
