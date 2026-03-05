# 🐺 ZENITHAR - Profesyonel Muhasebe Yönetim Platformu

![ZENITHAR Logo](https://static.prod-images.emergentagent.com/jobs/1fb06072-670b-49e1-9107-e57d39d3aeac/images/48d24952772b007d8f1595c8f786b20ff8832a50d29b7a2c9de063350c241f5c.png)

Güçlü, modern ve kullanıcı dostu muhasebe yönetim platformu.

## 🚀 Özellikler

### ✅ Aktif Modüller
- **E-Fatura & E-İrsaliye** - Fatura oluşturma, yönetim ve takip
- **Personel Yönetimi** - Çalışan bilgileri, giriş-çıkış takibi
- **Maaş Yönetimi** - Bordro oluşturma ve ödeme takibi
- **İzin Yönetimi** - İzin talepleri, onay/ret sistemi
- **Kullanıcı Yönetimi** - Kayıt, giriş, yetkilendirme
- **Abonelik Sistemi** - 7 gün deneme, aylık/yıllık planlar

### 🔜 Yakında
- Çek/Senet takibi
- Cari hesap yönetimi
- KDV işlemleri rehberi
- Detaylı raporlama

## 🛠️ Teknoloji Stack

### Backend
- **FastAPI** - Modern, hızlı Python web framework
- **MongoDB** - NoSQL veritabanı
- **Motor** - Async MongoDB driver
- **JWT** - Token-based authentication
- **Bcrypt** - Şifre hashleme

### Frontend
- **React 18** - UI library
- **React Router** - Routing
- **Tailwind CSS** - Utility-first CSS
- **Shadcn/UI** - Component library
- **Axios** - HTTP client
- **Sonner** - Toast notifications

## 📦 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+
- MongoDB

### Backend Kurulumu

```bash
cd backend
pip install -r requirements.txt

# .env dosyası oluşturun
cp .env.example .env

# Veritabanı bağlantısını yapılandırın
MONGO_URL=mongodb://localhost:27017
DB_NAME=zenithar_db
JWT_SECRET=your-secret-key

# Sunucuyu başlatın
python server.py
```

Backend `http://localhost:8001` adresinde çalışacak.

### Frontend Kurulumu

```bash
cd frontend
yarn install

# .env dosyası oluşturun
cp .env.example .env

# Backend URL'ini yapılandırın
REACT_APP_BACKEND_URL=http://localhost:8001

# Development server'ı başlatın
yarn start
```

Frontend `http://localhost:3000` adresinde çalışacak.

## 🎯 Kullanım

### İlk Kullanıcı Oluşturma

1. Uygulamaya gidin: `http://localhost:3000`
2. "Hesap Oluştur" butonuna tıklayın
3. Bilgilerinizi girin
4. 7 günlük ücretsiz deneme otomatik başlar

### API Dokümantasyonu

FastAPI otomatik dokümantasyon:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 📝 API Endpoints

### Authentication
```
POST /api/auth/register/     - Kullanıcı kaydı
POST /api/auth/login/        - Giriş
GET  /api/auth/subscription/ - Abonelik bilgisi
```

### Personnel
```
GET    /api/personnel/employees/              - Personel listesi
POST   /api/personnel/employees/              - Personel ekle
POST   /api/personnel/employees/{id}/toggle_active/ - Aktif/Pasif
GET    /api/personnel/attendance/             - Giriş-çıkış kayıtları
POST   /api/personnel/attendance/quick_entry/ - Hızlı giriş/çıkış
GET    /api/personnel/salaries/               - Maaşlar
POST   /api/personnel/salaries/{id}/mark_paid/ - Maaş ödendi
GET    /api/personnel/leaves/                 - İzinler
POST   /api/personnel/leaves/{id}/approve/    - İzin onayla
POST   /api/personnel/leaves/{id}/reject/     - İzin reddet
```

### Invoices
```
GET    /api/invoices/     - Fatura listesi
POST   /api/invoices/     - Fatura oluştur
PUT    /api/invoices/{id}/ - Fatura güncelle
DELETE /api/invoices/{id}/ - Fatura sil
```

## 🎨 Tasarım

### Renk Paleti
- **Primary**: Emerald Green (#059669)
- **Secondary**: Vibrant Orange (#f97316)
- **Background**: Slate tones

### Fontlar
- **Başlıklar**: Manrope (800 weight)
- **Metin**: Public Sans (400-600 weight)
- **Kod**: JetBrains Mono

## 🔐 Güvenlik

- JWT token-based authentication
- Bcrypt şifre hashleme
- CORS koruması
- SQL injection koruması (NoSQL)
- XSS koruması

## 📱 Responsive Tasarım

- Mobile-first yaklaşım
- Tablet ve desktop uyumlu
- Touch-friendly UI

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 İletişim

Proje Link: [https://github.com/yourusername/zenithar](https://github.com/yourusername/zenithar)

## 🙏 Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn/UI](https://ui.shadcn.com/)
- [MongoDB](https://www.mongodb.com/)

---

**ZENITHAR** - Muhasebenizi güçlü bir şekilde yönetin 🐺
