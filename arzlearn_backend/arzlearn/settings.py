"""
تنظیمات اصلی پروژه ارزلرن (Arzlearn)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-dev-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_ckeditor_5',

    'accounts',
    'articles',
    'comments',
    'prices',
    'socials',
    'exchanges',
    'economic_calendar',
    'topbanner',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arzlearn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'arzlearn.wsgi.application'
ASGI_APPLICATION = 'arzlearn.asgi.application'

# --------------------------------------------------------------------------
# Django Channels - برای پخش لحظه‌ای قیمت‌ها از طریق WebSocket
# --------------------------------------------------------------------------
# نیازمند یک سرور Redis در حال اجرا (بصورت پیش‌فرض روی 127.0.0.1:6379).
# دلیل استفاده از Redis (و نه InMemoryChannelLayer): دستور بروزرسانی قیمت‌ها
# (`update_prices`) در یک پراسس جدا از سرور اصلی اجرا می‌شود، پس باید پیام‌ها
# از طریق یک message broker مشترک (Redis) بین دو پراسس رد و بدل شوند.
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'arzlearn_db'),
        'USER': os.environ.get('DB_USER', 'mmdreza'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Mr13841384'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'accounts.validators.ComplexPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------------------------------
# آدرس عمومی فرانت‌اند - برای ساخت لینک مقالات در Sitemap، Schema.org و پیام‌های تلگرام
# --------------------------------------------------------------------------
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'http://localhost:3000')

# آدرس عمومی خودِ بک‌اند - برای ساخت لینک کامل عکس‌ها (مثلاً در Sitemap یا تلگرام)
BACKEND_BASE_URL = os.environ.get('BACKEND_BASE_URL', 'http://127.0.0.1:8000')

# --------------------------------------------------------------------------
# تلگرام - برای پست خودکار مقالات در کانال
# --------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID', '')
# اگر تلگرام از شبکه‌ی سرور فیلتر است، آدرس یک پروکسی HTTP/SOCKS5 اینجا بدهید
# مثال: http://127.0.0.1:10809  یا  socks5h://127.0.0.1:1080
TELEGRAM_PROXY_URL = os.environ.get('TELEGRAM_PROXY_URL', '')

# --------------------------------------------------------------------------
# داده‌های اقتصادی - کلید API سرویس تقویم اقتصادی (قابل تعویض)
# --------------------------------------------------------------------------
ECONOMIC_CALENDAR_API_KEY = os.environ.get('ECONOMIC_CALENDAR_API_KEY', '')
ECONOMIC_CALENDAR_API_BASE_URL = os.environ.get(
    'ECONOMIC_CALENDAR_API_BASE_URL', 'https://api.forex-calendar.pro'
)

# --------------------------------------------------------------------------
# BrsApi.ir - کلید اختصاصی برای قیمت دلار و طلا
# --------------------------------------------------------------------------
BRSAPI_KEY = os.environ.get('BRSAPI_KEY', '')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    # محدودسازی نرخ درخواست - دفاع در برابر brute-force روی ورود/ثبت‌نام
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/min',
        'register': '5/min',
    },
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_CONFIGS = {
    'default': {
        'language': 'fa',
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'imageUpload', 'insertTable', 'mediaEmbed', '|',
            'undo', 'redo',
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:full', 'imageStyle:side',
            ],
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells'],
        },
    },
}

# --------------------------------------------------------------------------
# لاگ‌ها - بدون این تنظیم، پیام‌های logger.info/warning در سرویس‌های پروژه
# (مثل prices, articles.telegram, economic_calendar) توی کنسول دیده نمی‌شدند
# و مشکلات (مثل خالی بودن تنظیمات تلگرام) بی‌صدا رد می‌شدند.
# --------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# --------------------------------------------------------------------------
# محدودیت حجم آپلود - جلوگیری از حمله‌ی DoS با آپلود فایل‌های خیلی بزرگ
# --------------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # ۵ مگابایت
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # ۵ مگابایت

# --------------------------------------------------------------------------
# سخت‌سازی امنیتی - فقط در پروداکشن فعال می‌شود (DEBUG=False)
# چون بعضی از این تنظیمات (مثل SECURE_SSL_REDIRECT) در محیط توسعه‌ی محلی
# (http://127.0.0.1) باعث خرابی می‌شوند.
# --------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
