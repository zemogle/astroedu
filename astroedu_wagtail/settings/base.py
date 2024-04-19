"""
Django settings for astroedu_wagtail project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
from django_storage_url import dsn_configured_storage_class

DEBUG = os.environ.get('DJANGO_DEBUG') == "True"

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-d9(ozf+uf_@y1%zq6)op0o$-v3)-_#mua%@y*ac9&*i(@%u=)8')

DIVIO_DOMAIN = os.environ.get('DOMAIN', '')

DIVIO_DOMAIN_ALIASES = [
    d.strip()
    for d in os.environ.get('DOMAIN_ALIASES', '').split(',')
    if d.strip()
]
DIVIO_DOMAIN_REDIRECTS = [
    d.strip()
    for d in os.environ.get('DOMAIN_REDIRECTS', '').split(',')
    if d.strip()
]

ALLOWED_HOSTS = [DIVIO_DOMAIN] + DIVIO_DOMAIN_ALIASES + DIVIO_DOMAIN_REDIRECTS

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'home',
    'search',
    'activities',

    'wagtail.contrib.forms',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail_localize',
    'wagtail_localize.locales',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    "wagtail.contrib.table_block",
    "wagtail.contrib.routable_page",

    'wagtail.api.v2',
    'rest_framework',

    'modelcluster',
    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tagsinspector',
    'wagtail.contrib.styleguide'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'astroedu_wagtail.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(BASE_DIR, 'activities','templates'),
        ],
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

WSGI_APPLICATION = 'astroedu_wagtail.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite://:memory:')
DATABASES = {'default': dj_database_url.config()}

DEFAULT_STORAGE_DSN = os.environ.get('DEFAULT_STORAGE_DSN')

DefaultStorageClass = dsn_configured_storage_class('DEFAULT_STORAGE_DSN')

# Django's DEFAULT_FILE_STORAGE requires the class name
DEFAULT_FILE_STORAGE = 'astroedu_wagtail.settings.DefaultStorageClass'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTH_USER_MODEL = 'home.Person'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True
WAGTAIL_I18N_ENABLED = True

USE_L10N = True

USE_TZ = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
    ('it', "Italian"),
    ('es', "Spanish"),
]

LIVE_LANGUAGES = [
    ('en', "English"),
    ('it', "Italian"),
]


LOCALE_PATHS = [ os.path.join(PROJECT_DIR, 'locale'),
                os.path.join(PROJECT_DIR, 'activities/locale')]

# Static files

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# read the setting value from the environment variable
DEFAULT_STORAGE_DSN = os.environ.get('DEFAULT_STORAGE_DSN')

# dsn_configured_storage_class() requires the name of the setting
DefaultStorageClass = dsn_configured_storage_class('DEFAULT_STORAGE_DSN')

# Django's DEFAULT_FILE_STORAGE requires the class name
DEFAULT_FILE_STORAGE = 'astroedu_wagtail.settings.base.DefaultStorageClass'

THUMBNAIL_DEFAULT_STORAGE  = DEFAULT_FILE_STORAGE

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join('/data/media/')

# Wagtail settings

WAGTAIL_SITE_NAME = "astroEDU"
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'http://example.com'
