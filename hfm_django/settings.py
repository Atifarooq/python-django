"""
settings.py — Django project configuration
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-hfm-change-this-in-production-use-env-var'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hfm_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'hfm_django.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'hfm.sqlite3',
    }
}

AUTH_USER_MODEL = 'auth.User'
AUTH_PASSWORD_VALIDATORS = []  # Custom validation handled in forms.py

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    # 'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # pip install bcrypt first
]

LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ── STATIC FILES ──────────────────────────────────────────────────────────────
#
# THE FIX FOR 404 on CSS/JS:
#
# Django's staticfiles app looks for static files in two places:
#   1. Inside each installed app's own  <app>/static/  subfolder
#   2. Any folders listed in STATICFILES_DIRS  ← this is what was missing
#
# Our static/ folder lives at the PROJECT ROOT (next to manage.py), not inside
# the accounts/ app. Without STATICFILES_DIRS, Django had no idea it existed,
# so every request to /static/css/style.css returned 404.
#
# STATICFILES_DIRS = [BASE_DIR / 'static']
#   BASE_DIR  →  /path/to/hfm_django/
#   / 'static' →  /path/to/hfm_django/static/
#   This tells Django: "also look here for static files"
#
# STATIC_URL   = the URL prefix  →  /static/css/style.css
# STATIC_ROOT  = where collectstatic copies files for production deployment
#                (not used during development)

STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # ← THE FIX: register root static/ folder
STATIC_ROOT      = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY    = True
