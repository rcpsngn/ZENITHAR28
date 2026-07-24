import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-this")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

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

# Aşama 43: whitenoise KURULUYSA statik dosya middleware'i devreye girer.
# Kurulu değilse (ör. requirements.txt henüz güncellenmemişse) sunucu
# ImproperlyConfigured hatasıyla çökmek yerine sessizce atlar — geliştirme
# ortamında Django'nun kendi statik dosya sunumu zaten yeterlidir.
# Üretimde (Docker) whitenoise requirements.txt'te olduğu için sorun olmaz;
# sadece yerel ortamda `pip install -r requirements.txt` çalıştırmayı unutursanız
# bu koruma devreye girer.
try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")
    WHITENOISE_INSTALLED = True
except ImportError:
    WHITENOISE_INSTALLED = False

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

# Aşama 43: Docker'da `collectstatic` sonrası dosyaları sıkıştırıp
# hash'leyerek sunar (nginx/CDN olmadan da production-ready statik sunum).
#
# ÖNEMLİ: ManifestStaticFilesStorage bir "staticfiles.json" manifest dosyası
# gerektirir; bu dosya yalnızca `collectstatic` çalıştırıldıktan SONRA var
# olur. Geliştirme ortamında ve `manage.py test` çalıştırırken collectstatic
# hiç çalışmaz — bu yüzden Manifest sürümü SADECE üretimde (DEBUG=False)
# kullanılır. DEBUG=True iken (dev/test) manifest gerektirmeyen, sıkıştırma
# yapan ama hash'lemeyen basit whitenoise storage'ı kullanılır.
if WHITENOISE_INSTALLED and not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
elif WHITENOISE_INSTALLED:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

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
# GİB / E-Fatura Entegratör Ayarları (fallback — asıl kaynak PortalSettings)
# ======================
# Bu üçü artık .env'den okunuyor. Öncelik sırası apps/invoices/integrations.py
# > _get_gib_credentials() içinde belirleniyor: önce kullanıcının Genel Ayarlar
# > Portal sayfasında kaydettiği (şifreli) bilgi denenir, o boşsa buradaki
# ortam değişkenlerine düşülür, o da boşsa sistem simülasyon moduna geçer.
GIB_INTEGRATION_PROVIDER = os.environ.get("GIB_INTEGRATION_PROVIDER")
GIB_API_URL = os.environ.get("GIB_API_URL")
GIB_API_KEY = os.environ.get("GIB_API_KEY")

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
# CACHE (Aşama 42 - Final: Performans)
# ======================
# Varsayılan: LocMemCache (ek bağımlılık/servis gerektirmez, tek-process
# geliştirme/küçük dağıtımlar için yeterli). Birden fazla worker/sunucu ile
# üretime çıkarken CACHE_BACKEND=redis ve REDIS_URL ortam değişkenlerini
# ayarlayın; Django 4.0+ 'redis' python paketi kuruluysa yerleşik
# RedisCache backend'ini kullanabilir (requirements.txt'e 'redis' eklenmeli).
if os.environ.get("CACHE_BACKEND") == "redis":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "zenithar-locmem-cache",
        }
    }

# ======================
# PORTAL ŞİFRELEME ANAHTARI (Genel Ayarlar > Portal için)
# ======================
# GİB / entegratör API şifresi DB'de bu anahtarla şifrelenip saklanır
# (bkz. apps/settings_app/crypto.py). Anahtarı ÜRETİMDE .env dosyasına yaz,
# koda GÖMME. Anahtar üretmek için:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
PORTAL_ENCRYPTION_KEY = os.environ.get(
    "PORTAL_ENCRYPTION_KEY",
    # UYARI: Bu, yalnızca .env ayarlanmamışsa (geliştirme/test ortamı) devreye
    # giren GÜVENSİZ bir varsayılan anahtardır — SECRET_KEY'deki
    # "django-insecure-change-this" ile aynı mantık. ÜRETİMDE mutlaka .env'e
    # kendi anahtarınızı yazın; aksi halde şifreli veriler bu bilinen anahtarla
    # çözülebilir hale gelir.
    "ffFA3TDVrkhzfbb3vDsRPgVCWCFtwcl2M9-nfD4xCnc=",
)

# ======================
# LOGIN / LOGOUT & SESSION CONFIG
# ======================

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/'

# Sadece bu satır kalsın (tarayıcı kapanınca oturumu kapatır, sistemi bozmaz)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True