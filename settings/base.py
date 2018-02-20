import os

SETTINGS_ROOT = os.path.normpath(os.path.dirname(__file__).replace('\\', '/'))
PROJECT_ROOT = os.path.normpath(os.path.join(SETTINGS_ROOT, '..')).replace('/settings', '')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'buq2oul=@v^&y79i@mep1#1o&epi63&cf^&d_(g&lqdsy3+6%('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'tracking',
    'healthyminds',
    'console',
    'bleach',
    'pipeline',
    'ckeditor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'console.middleware.UMRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


AUTH_USER_MODEL = 'healthyminds.Account'

AUTHENTICATION_BACKENDS = ('console.backends.UMRemoteUserBackend','console.backends.EmailOrUsernameBackend',)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Detroit'

USE_I18N = True

USE_L10N = True

STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

MEDIA_URL = '/media/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{'verbose':{'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
                  },
    'filters': {
        'require_debug_false': {}
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter':'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'healthyminds':{
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'console':{
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'default':{
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    }
}


STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE = {
    'CSS_COMPRESSOR':'pipeline.compressors.yuglify.YuglifyCompressor',
    #'JS_COMPRESSOR':'pipeline.compressors.yuglify.YuglifyCompressor',
    'JS_COMPRESSOR':'pipeline.compressors.jsmin.JSMinCompressor',
    'COMPILERS': (
        'pipeline.compilers.less.LessCompiler',
        'pipeline.compilers.livescript.LiveScriptCompiler',
    ),
    'DISABLE_WRAPPER': True,
    'STYLESHEETS': {
        'healthyminds': {
            'source_filenames': (
                'css/libs/bootstrap-glyphicon.min.css',
                'css/libs/datatables.min.css',
                'less/healthyminds.less',
            ),
            'output_filename': 'css/healthyminds.min.css',
        },
    },
    'JAVASCRIPT': {
        'healthyminds': {
            'source_filenames': (
              'js/libs/fastclick.min.js',
              'js/libs/bootstrap.min.js',
              'js/healthyminds-scripts.js',
            ),
            'output_filename': 'js/healthyminds-scripts.min.js',
        },
    },
}

SERVER_EMAIL = 'django@healthyminds.miserver.it.umich.edu'
DEFAULT_FROM_EMAIL = 'HealthyMinds <healthyminds@healthyminds.miserver.it.umich.edu>'

#SESSION_COOKIE_AGE = (60 * 1 * 1)  # Development:  seconds in a minute * minutes in an hour * hours in a day
#SESSION_COOKIE_AGE = (60 * 20 * 1) # Production: seconds in a minute * minutes in an hour * hours in a day
SESSION_SAVE_EVERY_REQUEST = True

SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CKEDITOR_JQUERY_URL='https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'

CKEDITOR_CONFIGS = {
    'default': {
	'width' : '100%',
	'height' : 'auto',
    'enterMode': 1,
        'toolbar_Custom': [
	    {'name': 'format', 'items': ['Bold', 'Italic', 'Underline', 'Subscript', 'Superscript']},
	    {'name': 'font', 'items': ['Font', 'FontSize']},
	    {'name': 'lists', 'items': ['BulletedList', 'NumberedList']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'embed', 'items': ['Image', 'Table', 'Mathjax', 'CodeSnippet']},
        ],
        'toolbar': 'Custom',
        'mathJaxLib': '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS_HTML',
        'mathJaxClass': 'equation',
        'extraPlugins': ','.join(['mathjax','codesnippet']),
    },
}

WSGI_APPLICATION = 'apache.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

ALLOWED_HOSTS = ['localhost','127.0.0.1']
