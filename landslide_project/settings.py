"""
Django settings for Landslide Detection Project
landslide_project/settings.py
"""

from pathlib import Path
import os
from celery.schedules import crontab

# BASE_DIR must be defined before anything that uses it
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (dotenv first, then django-environ for typed access)
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

try:
    import environ
    env = environ.Env()
    environ.Env.read_env(BASE_DIR / '.env')
    _HAS_ENVIRON = True
except Exception:
    _HAS_ENVIRON = False

def _env(key, default=''):
    """Safe env reader — works with or without django-environ installed."""
    if _HAS_ENVIRON:
        return env(key, default=default)
    return os.environ.get(key, default)


# ── Core ─────────────────────────────────────────────────────────────────────

SECRET_KEY = 'django-insecure-landslide-detection-change-this-in-production-2024'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# ── Apps ──────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'corsheaders',
    'predictions',
    'alerts',
    'channels',
    'django_celery_beat',
]

# Add these only after installing: pip install channels django-celery-beat


# ── Middleware ────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ── Templates ─────────────────────────────────────────────────────────────────

ROOT_URLCONF = 'landslide_project.urls'

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

WSGI_APPLICATION = 'landslide_project.wsgi.application'


# ── Database ──────────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

USE_TZ = False
USE_I18N = True
USE_L10N = True

# ── Static & Media ────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Only add STATICFILES_DIRS entry if the folder actually exists
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ── ML Model path ─────────────────────────────────────────────────────────────

ML_REPO_PATH = os.environ.get(
    'ML_REPO_PATH',
    str(BASE_DIR.parent.parent / 'landslides_detection')
)


# ── CORS ──────────────────────────────────────────────────────────────────────

CORS_ALLOW_ALL_ORIGINS = True


# ── REST Framework ────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}


# ── File upload limits (50 MB) ────────────────────────────────────────────────

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800


# ── Channels (WebSockets) — only active when channels is installed ────────────

if 'channels' in INSTALLED_APPS:
    ASGI_APPLICATION = 'landslide_project.asgi.application'
    try:
        import channels_redis  # noqa
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
            }
        }
    except ImportError:
        # Fall back to in-memory layer if channels_redis not yet installed
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            }
        }


# ── Celery ────────────────────────────────────────────────────────────────────

CELERY_BROKER_URL     = _env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = _env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_TIMEZONE       = 'Asia/Kolkata'

#if 'django_celery_beat' in INSTALLED_APPS:
    #CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

try:
    from celery.schedules import crontab
    CELERY_BEAT_SCHEDULE = {
        'auto-prediction-every-30min': {
            'task':     'alerts.tasks.auto_run_prediction',
            'schedule': crontab(minute='*/30'),
        },
    }
except ImportError:
    pass


# ── Twilio SMS ────────────────────────────────────────────────────────────────

TWILIO_ACCOUNT_SID = _env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN  = _env('TWILIO_AUTH_TOKEN',  default='')
TWILIO_FROM_NUMBER = _env('TWILIO_FROM_NUMBER', default='')


# ── Email (Gmail SMTP) ────────────────────────────────────────────────────────

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = _env('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = _env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = _env('DEFAULT_FROM_EMAIL',  default='alerts@landslideai.in')


# ── Alert thresholds ──────────────────────────────────────────────────────────

ALERT_THRESHOLDS = {
    'low':      0.25,
    'moderate': 0.50,
    'high':     0.75,
    'critical': 0.90,
}

# Test phone numbers for SMS (comma-separated in .env)
_phones_raw = _env('ALERT_TEST_PHONES', default='')
ALERT_TEST_PHONES = [p.strip() for p in _phones_raw.split(',') if p.strip()]
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']