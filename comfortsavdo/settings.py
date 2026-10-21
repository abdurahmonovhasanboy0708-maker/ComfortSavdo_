import os
from os.path import join
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-u6iq@a8iq%747@o-l5gl9&=lfico7472k-4f%7ez02ke(_4f!f',
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'apps',
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

ROOT_URLCONF = 'comfortsavdo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'comfortsavdo.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
MEDIA_ROOT = join(BASE_DIR, 'media/')


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_USER_MODEL = 'apps.User'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'