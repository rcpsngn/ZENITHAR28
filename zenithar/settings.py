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
    ]
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
# LOGIN / LOGOUT & SESSION CONFIG
# ======================

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/'

# Sadece bu satır kalsın (tarayıcı kapanınca oturumu kapatır, sistemi bozmaz)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True