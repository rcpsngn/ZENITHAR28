import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-change-this"

DEBUG = True

ALLOWED_HOSTS = []

# ======================
# APPLICATIONS
# ======================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "django_filters",

    # third party
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    # ERP MODÜLLERİ
    'apps.accounts',
    'apps.invoices',
    'apps.waybill',
    'apps.checks',
    'apps.current_accounts',
    'apps.personnel',
    'apps.help',
    'apps.settings_app',
]

# ======================
# MIDDLEWARE
# ======================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ======================
# URLS
# ======================

ROOT_URLCONF = "zenithar.urls"

# ======================
# TEMPLATES
# ======================

import os

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ======================
# WSGI
# ======================

WSGI_APPLICATION = "zenithar.wsgi.application"

# ======================
# DATABASE
# ======================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ======================
# PASSWORD VALIDATION
# ======================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# ======================
# LANGUAGE
# ======================

LANGUAGE_CODE = "tr-tr"

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True
USE_TZ = True

# ======================
# STATIC FILES
# ======================

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# ======================
# MEDIA FILES
# ======================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# ======================
# DEFAULT ID
# ======================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================
# CORS
# ======================

CORS_ALLOW_ALL_ORIGINS = True

# ======================
# DJANGO REST FRAMEWORK
# ======================

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    # Web arayüzü (Django template'leri) session tabanlı girişi kullanmaya devam eder;
    # /api/ altındaki uçlar (personel API'si dahil) artık JWT ile de çağrılabilir.
    # Sıra önemli: SessionAuthentication önce denenir (mevcut şablonlar bozulmasın diye),
    # JWTAuthentication ikinci sırada devreye girer.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# ======================
# SIMPLE JWT
# ======================
# NOT: Bu blok "Kimlik Doğrulama > Oturum" (JWT Login, Token Refresh, Logout)
# görevini gerçek koda bağlar. Önceki durum raporunda bu görev "Tamamlandı"
# olarak işaretlenmişti ama settings.py'de hiçbir JWT ayarı yoktu; bu artık
# düzeltildi. Uçlar için bkz. apps/accounts/urls.py (api/token/, api/token/refresh/,
# api/token/verify/, api/logout/).

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Refresh token her kullanıldığında yenisiyle değiştirilir ve eskisi
    # kara listeye (blacklist) alınır -> çalınmış bir refresh token'ın
    # tekrar tekrar kullanılmasının önüne geçer.
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ======================
# CUSTOM USER MODEL
# ======================

AUTH_USER_MODEL = "accounts.User"

# ======================
# DIŞ ENTEGRASYONLAR (VKN/GİB sorgulama, e-Fatura gönderimi vb.)
# ======================
# Şu an bilerek BOŞ/pasif bırakıldı -> apps/invoices/integrations.py
# simülasyon modunda çalışıyor.
#
# Gerçek bir GİB entegratörüyle (Foriba, Uyumsoft, Logo, Mikro vb.)
# anlaştığında, bu bilgileri BURAYA DEĞİL, .env dosyasına yaz ve
# os.environ.get(...) ile buraya çek. Aşağıdaki satırları o zaman
# yorumdan çıkar:
#
# GIB_INTEGRATION_PROVIDER = os.environ.get("GIB_INTEGRATION_PROVIDER")
# GIB_API_URL = os.environ.get("GIB_API_URL")
# GIB_API_KEY = os.environ.get("GIB_API_KEY")

GIB_INTEGRATION_PROVIDER = None
GIB_API_URL = None
GIB_API_KEY = None

# ======================
# E-POSTA (E-Arşiv bildirimleri için)
# ======================
# Geliştirmede varsayılan olarak e-postalar gerçekten gönderilmez, konsola
# yazdırılır (EMAIL_BACKEND=console). Üretimde .env'e gerçek SMTP bilgilerini
# girip EMAIL_BACKEND'i "django.core.mail.backends.smtp.EmailBackend" yapın.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@zenithar.local")

# ======================
# SMS (E-Arşiv bildirimleri için) — sağlayıcı seçilene kadar simülasyon
# ======================
# Netgsm/İletimerkezi/Twilio gibi bir sağlayıcı seçilince SMS_API_KEY/SMS_API_URL
# doldurulmalı; doldurulana kadar apps/invoices/notifications.py otomatik olarak
# simülasyon moduna düşer (bkz. o dosyadaki açıklama).
SMS_API_URL = os.environ.get("SMS_API_URL")
SMS_API_KEY = os.environ.get("SMS_API_KEY")

# ======================
# PORTAL ŞİFRELEME ANAHTARI (Genel Ayarlar > Portal için)
# ======================
# GİB / entegratör API şifresi DB'de bu anahtarla şifrelenip saklanır
# (bkz. apps/settings_app/crypto.py). Anahtarı ÜRETİMDE .env dosyasına yaz,
# koda GÖMME. Anahtar üretmek için:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
PORTAL_ENCRYPTION_KEY = os.environ.get("PORTAL_ENCRYPTION_KEY")

# ======================
# LOGIN / LOGOUT & SESSION CONFIG
# ======================

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/'

# Sadece bu satır kalsın (tarayıcı kapanınca oturumu kapatır, sistemi bozmaz)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True