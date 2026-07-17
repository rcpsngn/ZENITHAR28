# Bu Pakette Ne Yapıldı?

Öncelik listesindeki 3 kalem gerçek koda dönüştürüldü. Üçüncüsü (E-Fatura Giden),
sizin isteğinizle "API anahtarı girme" adımına kadar tamamlandı — kalan tek eksik
gerçek bir entegratörden alacağınız URL/anahtar bilgisi.

## 1) Kimlik Doğrulama - Oturum (JWT Login/Refresh/Logout) — TAMAMLANDI
- `zenithar/settings.py`: `rest_framework_simplejwt` ve `token_blacklist` INSTALLED_APPS'e
  eklendi, `SIMPLE_JWT` ayarları (30 dk access, 7 gün refresh, rotation + blacklist) yazıldı,
  REST_FRAMEWORK'e JWT authentication class eklendi (session auth da bozulmadı).
- `apps/accounts/serializers.py`: `CustomTokenObtainPairSerializer` eklendi (token + kullanıcı bilgisi döner).
- `apps/accounts/views.py`: `CustomTokenObtainPairView` (login) ve `LogoutAPIView` (refresh token'ı blacklist'e alır) eklendi.
- `apps/accounts/urls.py`: `api/token/`, `api/token/refresh/`, `api/token/verify/`, `api/logout/`,
  `api/register/`, `api/profile/`, `api/subscription/` uçları eklendi (önceden yazılmış ama
  hiçbir yere bağlanmamış RegisterView/ProfileView/SubscriptionView de artık devrede).

**Kurulumdan sonra çalıştırılması gerekenler:**
```bash
pip install -r requirements.txt
python manage.py migrate      # token_blacklist tablolarını oluşturur
```

## 2) Genel Ayarlar - Portal (Şifreli Saklama) — TAMAMLANDI
- `apps/settings_app/crypto.py` (yeni): Fernet (AES tabanlı) şifreleme yardımcı fonksiyonları.
- `apps/settings_app/models.py`: `PortalSettings` modeli eklendi — şifre yalnızca
  `encrypted_password` alanında şifreli tutulur, düz metin hiç yazılmaz.
- `apps/settings_app/migrations/0002_portalsettings.py` (yeni migration).
- `apps/settings_app/forms.py` (yeni): `PortalSettingsForm`.
- `apps/settings_app/views.py`: `portal_settings` artık gerçek GET/POST + kayıt mantığı içeriyor.
- `templates/settings_app/portal.html`: Form gerçek verilerle çalışıyor, şifre maskeli gösteriliyor.

**Kurulumdan önce mutlaka yapılması gereken:**
```bash
# 1) Anahtar üret
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2) .env dosyanıza ekleyin (repoya COMMIT ETMEYİN):
PORTAL_ENCRYPTION_KEY=<üretilen_anahtar>

python manage.py migrate
```

## 3) E-Fatura - Giden (Aşama 10) — API ANAHTARINA KADAR TAMAMLANDI
- `apps/invoices/integrations.py`: `send_invoice_to_gib()` ve `cancel_invoice_at_gib()`
  fonksiyonları eklendi. Gerçek HTTP isteği (requests + Bearer token + JSON gövde),
  otomatik yeniden deneme (retry/backoff), timeout, logging ve hata yönetimi TAM olarak
  yazıldı. Kimlik bilgisi (URL + API anahtarı) önce kullanıcının Genel Ayarlar > Portal
  sayfasına girdiği (şifreli) bilgiden, yoksa `settings.py > GIB_API_URL/GIB_API_KEY`'den
  okunur. **Hiçbiri girilmediyse otomatik olarak simülasyon moduna düşer** — sistem bozulmaz.
- `apps/settings_app/models.py`: `PortalSettings` modeline `api_url` alanı eklendi
  (entegratörün verdiği API adresi buraya girilecek).
- `apps/invoices/views.py`: `invoice_send` ve `invoice_cancel` artık gerçek sonucu kontrol
  ediyor — başarısız olursa fatura durumu değişmiyor, kullanıcıya (base.html'e eklenen
  genel mesaj kutusuyla) hata gösteriliyor.
- `templates/base.html`: Django messages framework'ü artık her sayfada görünür
  (başarı=yeşil, hata=kırmızı, bilgi=mavi kutu).

**Sizin yapmanız gereken TEK şey (API anahtarı):**
1. Genel Ayarlar > Portal sayfasından gerçek entegratörünüzü (Foriba/Uyumsoft/Logo/Mikro)
   seçin, **API Adresi**, **Kullanıcı Adı** ve **Şifre/Anahtar**'ı girip kaydedin.
2. `_build_invoice_payload()` ve `_parse_gib_response()` fonksiyonlarındaki alan adlarını
   (`belgeNo`, `ettn` vb.) sağlayıcınızın gerçek API dokümanına göre birebir eşleyin —
   burada GENEL/varsayımsal bir JSON sözleşmesi kullanıldı, sağlayıcı belgesi elinize
   geçince küçük bir alan-adı eşlemesi yapmanız yeterli.
3. Kaydedip test faturası gönderin — kod tarafında başka hiçbir değişikliğe gerek yok.

**Bilerek basitleştirilen kısım:** UBL-TR XML yerine JSON gövde varsayıldı (çoğu modern
entegratör wrapper API'si JSON kabul ediyor). Sağlayıcınız yalnızca UBL-TR XML kabul
ediyorsa `_build_invoice_payload()` XML üretecek şekilde güncellenmeli — bu da tek
fonksiyonluk bir değişiklik.

## Kasıtlı Olarak Yapılmayanlar
- **Sağlayıcıya özel alan adı eşlemesi**: Genel/varsayımsal JSON sözleşmesiyle yazıldı,
  gerçek sağlayıcı dokümanı gelince küçük bir isim eşlemesi gerekiyor (yukarıda anlatıldı).
- **"Bağlantıyı Test Et" butonu**: Şu an pasif; gerçek entegratör bağlanınca aktif edilmeli.

## Test Edilemeyen Kısım (Önemli)
Bu ortamda internet erişimi ve Django kurulumu olmadığı için kod **çalıştırılarak
test edilemedi**, yalnızca `python -m py_compile` ile sözdizimi kontrolü yapıldı.
Projeyi indirdikten sonra mutlaka şunları çalıştırın:
```bash
python manage.py migrate
python manage.py runserver
# sonra: /accounts/api/token/  ve  /settings/portal/  uçlarını elle test edin
```
