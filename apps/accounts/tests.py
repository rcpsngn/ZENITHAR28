"""
apps/accounts için testler — Kimlik Doğrulama modülü (JWT, izin sınıfları).

Çalıştırmak için:
    python manage.py test apps.accounts
"""
from django.test import TestCase, Client
from django.urls import reverse

from .models import User
from .permissions import IsOwner, HasRole, ReadOnlyOrHasRole, IsAdminOrAccountant


def make_user(username="testuser", role="viewer"):
    return User.objects.create_user(username=username, password="test-pass-123", role=role)


# ============================================================
# JWT LOGIN / REFRESH / LOGOUT (Aşama 4)
# ============================================================
class JWTAuthTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()

    def test_dogru_bilgilerle_token_alinir(self):
        response = self.client.post(reverse("api_token_obtain"), {
            "username": "testuser", "password": "test-pass-123",
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertIn("user", data)

    def test_yanlis_sifreyle_token_alinamaz(self):
        response = self.client.post(reverse("api_token_obtain"), {
            "username": "testuser", "password": "yanlis-sifre",
        })
        self.assertEqual(response.status_code, 401)

    def test_refresh_token_ile_yeni_access_token_alinir(self):
        obtain = self.client.post(reverse("api_token_obtain"), {
            "username": "testuser", "password": "test-pass-123",
        }).json()
        response = self.client.post(reverse("api_token_refresh"), {"refresh": obtain["refresh"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_logout_sonrasi_refresh_token_kullanilamaz(self):
        obtain = self.client.post(reverse("api_token_obtain"), {
            "username": "testuser", "password": "test-pass-123",
        }).json()

        # Logout uç noktası IsAuthenticated gerektiriyor -> access token ile giriş yapılmalı.
        response = self.client.post(
            reverse("api_logout"), {"refresh": obtain["refresh"]},
            HTTP_AUTHORIZATION=f"Bearer {obtain['access']}",
        )
        self.assertEqual(response.status_code, 205)

        # Blacklist'e alınan refresh token artık kullanılamamalı.
        second_try = self.client.post(reverse("api_token_refresh"), {"refresh": obtain["refresh"]})
        self.assertEqual(second_try.status_code, 401)

    def test_gecersiz_refresh_tokenla_logout_400_doner(self):
        obtain = self.client.post(reverse("api_token_obtain"), {
            "username": "testuser", "password": "test-pass-123",
        }).json()
        response = self.client.post(
            reverse("api_logout"), {"refresh": "gecersiz-bir-token"},
            HTTP_AUTHORIZATION=f"Bearer {obtain['access']}",
        )
        self.assertEqual(response.status_code, 400)


# ============================================================
# ROL TABANLI İZİN SINIFLARI (Aşama 3)
# ============================================================
class PermissionClassesTests(TestCase):
    def test_hasrole_admin_rolu_her_zaman_gecer(self):
        admin = make_user(username="admin1", role="admin")

        class DummyRequest:
            user = admin

        perm = HasRole.for_roles("accountant")()
        self.assertTrue(perm.has_permission(DummyRequest(), None))

    def test_hasrole_yetkisiz_rol_reddedilir(self):
        viewer = make_user(username="viewer1", role="viewer")

        class DummyRequest:
            user = viewer

        perm = HasRole.for_roles("accountant")()
        self.assertFalse(perm.has_permission(DummyRequest(), None))

    def test_readonly_or_hasrole_get_herkese_acik(self):
        viewer = make_user(username="viewer2", role="viewer")

        class DummyRequest:
            method = "GET"
            user = viewer

        perm = ReadOnlyOrHasRole.for_roles("accountant")()
        self.assertTrue(perm.has_permission(DummyRequest(), None))

    def test_readonly_or_hasrole_post_yetkisiz_role_kapali(self):
        viewer = make_user(username="viewer3", role="viewer")

        class DummyRequest:
            method = "POST"
            user = viewer

        perm = ReadOnlyOrHasRole.for_roles("accountant")()
        self.assertFalse(perm.has_permission(DummyRequest(), None))

    def test_isowner_kendi_nesnesine_erisebilir(self):
        user = make_user(username="owner1")

        class DummyObj:
            pass
        obj = DummyObj()
        obj.user = user

        class DummyRequest:
            pass
        request = DummyRequest()
        request.user = user

        perm = IsOwner()
        self.assertTrue(perm.has_object_permission(request, None, obj))

    def test_isowner_baskasinin_nesnesine_erisemez(self):
        user_a = make_user(username="owner2")
        user_b = make_user(username="owner3")

        class DummyObj:
            pass
        obj = DummyObj()
        obj.user = user_a

        class DummyRequest:
            pass
        request = DummyRequest()
        request.user = user_b

        perm = IsOwner()
        self.assertFalse(perm.has_object_permission(request, None, obj))


# ============================================================
# WEB (SESSION) LOGIN / LOGOUT
# ============================================================
class SessionAuthTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()

    def test_dogru_bilgilerle_session_girisi_yapilir(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser", "password": "test-pass-123",
        })
        self.assertEqual(response.status_code, 302)

    def test_giris_yapmamis_kullanici_dashboard_a_giremez(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_giris_yapmis_kullanici_dashboard_a_erisir(self):
        self.client.login(username="testuser", password="test-pass-123")
        response = self.client.get(reverse("dashboard"))
        self.assertIn(response.status_code, (200, 302))
