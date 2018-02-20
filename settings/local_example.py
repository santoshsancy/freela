from settings.base import *
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.local_example'

DEBUG = True
SITE_ID = 1

SOUTH_TESTS_MIGRATE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    },
}

INSTALLED_APPS += (
    "django_extensions",
)

INTERNAL_IPS = (
    '127.0.0.1',
) 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

USE_HTTPS = False
SESSION_COOKIE_SECURE = USE_HTTPS
