# 🐺 ZENITHAR - Profesyonel Muhasebe Yönetim Platformu

![ZENITHAR Logo](https://static.prod-images.emergentagent.com/jobs/1fb06072-670b-49e1-9107-e57d39d3aeac/images/48d24952772b007d8f1595c8f786b20ff8832a50d29b7a2c9de063350c241f5c.png)

Güçlü, modern ve kullanıcı dostu muhasebe yönetim platformu.
Zenithar, Türk işletmeler için geliştirilmiş, kullanımı kolay bir muhasebe takip sistemidir. E-fatura, e-irsaliye, cari hesap, çek/senet takibi, personel yönetimi ve abonelik sistemi ile muhasebenizi kolaylaştırır.

## 🚀 Özellikler

### ✅ Aktif Modüller
- **E-Fatura** - Fatura oluşturma, taslak, gönderilen/gelen faturalar, e-arşiv takibi
- **E-İrsaliye** - İrsaliye oluşturma, taslak, gönderilen/gelen irsaliyeler
- **Cari Hesap** - Cari bakiye, cari ekstre, stok takip, alınan/giden faturalar
- **Çek/Senet & Kasa** - Banka hareketleri, kasa işlemleri, POS/kredi kartı, çek-senet takibi
- **Personel Yönetimi** - Çalışan bilgileri (CRUD), giriş-çıkış takibi, hızlı giriş/çıkış kaydı
- **Maaş Yönetimi** - Bordro takibi, maaş ödeme durumu işaretleme
- **İzin Yönetimi** - İzin talepleri, onay/ret sistemi
- **Kullanıcı Yönetimi** - Kayıt, giriş, rol tabanlı yetkilendirme (yönetici / muhasebeci / çalışan / görüntüleyici)
- **Abonelik Sistemi** - 7 gün deneme, aylık/yıllık planlar, otomatik yenileme desteği
- **Ayarlar** - Firma bilgileri, tanımlamalar, muhasebeci bağlantısı, belge tasarımı, bildirimler, sistem ayarları
- **Yardım Merkezi** - Kullanım ipuçları, yardım videoları

## 🛠️ Teknoloji Stack

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - Personel modülü için REST API
- **djangorestframework-simplejwt** - JWT token authentication
- **django-allauth** - Hesap/kimlik doğrulama yönetimi
- **django-ckeditor** - Zengin metin editörü (belge/içerik alanları için)
- **django-cors-headers** - CORS yönetimi
- **django-modeltranslation** + **django-rosetta** - Çoklu dil desteği
- **django-filter** - API filtreleme
- **Pillow** - Görsel işleme
- **SQLite** - Varsayılan veritabanı (geliştirme ortamı)

### Frontend
- **Django Templates** - Sunucu taraflı sayfa render (HTML)
- **Vanilla JavaScript** - Sayfa etkileşimleri (menü, dropdown, form davranışları)
- **CSS** - Modüler yapı (`core`, `components`, `pages` olarak ayrılmış)

> **Not:** `static/js/` altında birkaç dosya (`DashboardHome.js`, `LandingPage.js`, `InvoicePage.js`, `PersonnelPage.js`, `use-toast.js`) React importu içeriyor ancak projede bir React derleme/build sistemi (`package.json`, bundler vb.) bulunmuyor. Bu dosyalar aktif olarak kullanılmıyor gibi görünüyor; temizlenmesi veya ileride gerçek bir React entegrasyonu planlanıyorsa ayrı bir frontend projesi olarak yapılandırılması önerilir.

## 📦 Kurulum

### Gereksinimler
- Python 3.9+
- pip

### Kurulum Adımları

```bash
# Depoyu klonlayın
git clone https://github.com/rcpsngn/ZENITHAR28.git
cd ZENITHAR28

# Sanal ortam oluşturun ve aktif edin
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux

# Bağımlılıkları kurun
pip install -r requirements.txt

# Veritabanını oluşturun
python manage.py migrate

# (Opsiyonel) Yönetici hesabı oluşturun
python manage.py createsuperuser

# Sunucuyu başlatın
python manage.py runserver
```

Uygulama `http://127.0.0.1:8000` adresinde çalışacak.

## 🎯 Kullanım

### İlk Kullanıcı Oluşturma

1. Uygulamaya gidin: `http://127.0.0.1:8000/accounts/register/`
2. Kayıt formunu doldurun
3. Giriş yapın: `http://127.0.0.1:8000/accounts/login/`
4. 7 günlük ücretsiz deneme aboneliği otomatik başlar

### Yönetim Paneli

Django admin paneline `http://127.0.0.1:8000/admin/` adresinden, oluşturduğunuz superuser bilgileriyle erişebilirsiniz.

## 📝 Uygulama Rotaları (URLs)

### Kimlik Doğrulama (`/accounts/`)
```
GET/POST  /accounts/login/           - Giriş
GET/POST  /accounts/register/        - Kayıt
GET       /accounts/dashboard/       - Kontrol paneli
GET       /accounts/logout/          - Çıkış
GET/POST  /accounts/password-reset/  - Şifre sıfırlama
```

### Fatura (`/invoices/`)
```
GET  /invoices/                   - Fatura ana sayfa
GET  /invoices/create/            - Fatura oluştur
GET  /invoices/draft/             - Taslaklar
GET  /invoices/sent/              - Gönderilenler
GET  /invoices/incoming/          - Gelenler
GET  /invoices/earchive/incoming/ - E-arşiv gelen
GET  /invoices/earchive/sent/     - E-arşiv gönderilen
POST /invoices/send/<id>/         - Fatura gönder
POST /invoices/delete/<id>/       - Fatura sil
```

### İrsaliye (`/waybill/`)
```
GET  /waybill/create/    - İrsaliye oluştur
GET  /waybill/draft/     - Taslaklar
GET  /waybill/incoming/  - Gelenler
GET  /waybill/sent/      - Gönderilenler
```

### Personel (`/personnel/`) - REST API + Şablon sayfaları
```
GET/POST   /personnel/api/employees/                    - Personel listesi/ekleme
POST       /personnel/api/employees/{id}/toggle_active/ - Aktif/Pasif
GET/POST   /personnel/api/attendance/                   - Giriş-çıkış kayıtları
POST       /personnel/api/attendance/quick_entry/       - Hızlı giriş/çıkış
GET/POST   /personnel/api/salaries/                     - Maaşlar
POST       /personnel/api/salaries/{id}/mark_paid/      - Maaş ödendi
GET/POST   /personnel/api/leaves/                       - İzinler
POST       /personnel/api/leaves/{id}/approve/          - İzin onayla
POST       /personnel/api/leaves/{id}/reject/           - İzin reddet

GET  /personnel/calisanlar/    - Çalışanlar sayfası
GET  /personnel/giris-cikis/   - Giriş-çıkış sayfası
GET  /personnel/yillik-izin/   - Yıllık izin sayfası
```

### Çek/Senet & Kasa (`/checks/`)
```
GET  /checks/banka-hareketleri/  - Banka hareketleri
GET  /checks/kasa-islemleri/     - Kasa işlemleri
GET  /checks/pos-kredi-karti/    - POS/kredi kartı
GET  /checks/cek-senet-takip/    - Çek-senet takip
```

### Cari Hesap (`/current-accounts/`)
```
GET  /current-accounts/stok-takip/       - Stok takip
GET  /current-accounts/cari-ekstre/      - Cari ekstre
GET  /current-accounts/cari-bakiye/      - Cari bakiye
GET  /current-accounts/alinan-faturalar/ - Alınan faturalar
GET  /current-accounts/giden-faturalar/  - Giden faturalar
```

### Ayarlar (`/settings/`)
```
GET  /settings/company-info/      - Firma bilgileri
GET  /settings/definitions/       - Tanımlamalar
GET  /settings/accountant/        - Muhasebeci
GET  /settings/document-design/   - Belge tasarımı
GET  /settings/portal/            - Portal ayarları
GET  /settings/notifications/     - Bildirim ayarları
GET  /settings/system/            - Sistem ayarları
```

### Yardım (`/help/`)
```
GET  /help/videos/  - Yardım videoları
GET  /help/tips/    - Kullanım ipuçları
```

## 🔐 Güvenlik

- Django'nun yerleşik session/authentication sistemi
- Personel API'si için JWT token desteği (`djangorestframework_simplejwt`)
- `@login_required` ile korunan sayfalar
- CORS koruması (`django-cors-headers`)
- Django ORM sayesinde SQL injection koruması

> ⚠️ Bilinen açık: `db.sqlite3` veritabanı dosyası ve `.idea/` klasörü daha önce depoya (git) commit edilmişti. Gerçek/hassas veri içeriyorsa `.gitignore`'a eklenip geçmiş commit'lerden temizlenmesi önerilir.

## 🌍 Çoklu Dil Desteği

Proje `django-modeltranslation` ve `django-rosetta` ile çoklu dil altyapısına sahiptir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - detaylar için LICENSE dosyasına bakın.

## 👥 İletişim

Proje Link: [https://github.com/rcpsngn/ZENITHAR28](https://github.com/rcpsngn/ZENITHAR28)

## 🙏 Teşekkürler

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [django-allauth](https://django-allauth.readthedocs.io/)

---

**ZENITHAR** - Muhasebenizi güçlü bir şekilde yönetin 🐺