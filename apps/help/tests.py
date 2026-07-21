"""
apps/help için testler — Yardım Videoları (Aşama 32), Kullanım İpuçları
(Aşama 33) ve Duyuru modeli (ana sayfa entegrasyonu).

Çalıştırmak için:
    python manage.py test apps.help
"""
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import User
from .models import HelpVideo, UsageTip, Announcement


def make_user(username="testuser"):
    return User.objects.create_user(username=username, password="test-pass-123")


class HelpVideosTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_giris_yapmamis_kullanici_yonlendirilir(self):
        anon_client = Client()
        response = anon_client.get(reverse("help_videos"))
        self.assertEqual(response.status_code, 302)

    def test_baslangic_verisi_migration_ile_yuklenmis(self):
        """0002 migration'ı ile 2 örnek video seed edilmişti."""
        response = self.client.get(reverse("help_videos"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["videos"]), 2)

    def test_pasif_video_listede_gorunmez(self):
        HelpVideo.objects.create(title="Pasif Video", is_active=False)
        response = self.client.get(reverse("help_videos"))
        titles = [v.title for v in response.context["videos"]]
        self.assertNotIn("Pasif Video", titles)

    def test_aktif_video_siralamaya_gore_listelenir(self):
        HelpVideo.objects.all().delete()
        HelpVideo.objects.create(title="İkinci", order=2)
        HelpVideo.objects.create(title="Birinci", order=1)
        response = self.client.get(reverse("help_videos"))
        titles = [v.title for v in response.context["videos"]]
        self.assertEqual(titles, ["Birinci", "İkinci"])


class UsageTipsTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_baslangic_verisi_migration_ile_yuklenmis(self):
        response = self.client.get(reverse("usage_tips"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["tips"]), 2)

    def test_pasif_ipucu_listede_gorunmez(self):
        UsageTip.objects.create(title="Pasif İpucu", content="...", is_active=False)
        response = self.client.get(reverse("usage_tips"))
        titles = [t.title for t in response.context["tips"]]
        self.assertNotIn("Pasif İpucu", titles)


class AnnouncementModelTests(TestCase):
    def test_str_kategori_ve_basligi_icerir(self):
        a = Announcement.objects.create(category="gib", title="Test Duyurusu", published_date=date.today())
        self.assertIn("Test Duyurusu", str(a))
        self.assertIn("GİB", str(a))

    def test_varsayilan_siralama_tarihe_gore_azalandir(self):
        old = Announcement.objects.create(title="Eski", published_date=date(2026, 1, 1))
        new = Announcement.objects.create(title="Yeni", published_date=date(2026, 6, 1))
        results = list(Announcement.objects.all())
        self.assertEqual(results[0].id, new.id)
