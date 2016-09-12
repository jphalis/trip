"""
Glossary of settings/prod.py:

- Hosting + Authentication
- Email
- SSL Security
- Installed applications
- Database
- Templates
- HTML minification
- Cache
- Staticfiles
- Logging
"""

import dj_database_url
from storages.backends.s3boto import S3BotoStorage
from .common import *

DEBUG = True

############################
# HOSTING + AUTHENTICATION #
############################
ADMINS = (
    # Uncomment lines below if you want email about server errors.
    # ("Kirk Sanderson", "kirksanderson1@gmail.com"),
)
MANAGERS = ADMINS
FULL_DOMAIN = 'transactionrisk.herokuapp.com'
ALLOWED_HOSTS = [
    '127.0.0.1',
]
FULL_DOMAIN = 'transactionrisk.herokuapp.com'
ALLOWED_HOSTS = [
    '127.0.0.1',
    '*{}'.format(FULL_DOMAIN),
    'wwww.{}'.format(FULL_DOMAIN),
    '*.{}'.format(FULL_DOMAIN)
]


#########
# EMAIL #
#########
DEFAULT_FROM_EMAIL = ''
DEFAULT_HR_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587


################
# SSL SECURITY #
################
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_SECONDS = 0
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


##########################
# INSTALLED APPLICATIONS #
##########################
INSTALLED_APPS += (
    'storages',
)


############
# DATABASE #
############
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}
DATABASES['default'] = dj_database_url.config()  # Heroku
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['NAME'] = 'ddnkqiaue2utva'
DATABASES['default']['USER'] = 'rcerpdvcjhyord'
DATABASES['default']['PASSWORD'] = 'O14XyRguW1NDnwssq8y6uSX7-m'
DATABASES['default']['HOST'] = 'ec2-54-221-234-118.compute-1.amazonaws.com'
DATABASES['default']['PORT'] = '5432'


##############
# MIDDLEWARE #
##############
MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)


#############
# TEMPLATES #
#############
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]


#####################
# HTML MINIFICATION #
#####################
KEEP_COMMENTS_ON_MINIFYING = False
EXCLUDE_FROM_MINIFYING = ('^hidden/secure/{}/admin/'.format(APP_NAME),)


#########
# CACHE #
#########
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': [
#             '127.0.0.1:11211',
#         ],
#         'TIMEOUT': 60,
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 12
# CACHE_MIDDLEWARE_KEY_PREFIX = ''


###############
# STATICFILES #
###############
USING_S3 = False
USING_CLOUDFRONT = False

if USING_S3:
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''
    S3_URL = '//{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)

    AWS_FILE_EXPIRE = 200
    AWS_PRELOAD_METADATA = True
    AWS_S3_SECURE_URLS = True
    S3DIRECT_REGION = 'us-east-1'

    STATICFILES_STORAGE = lambda: S3BotoStorage(location='static')
    STATIC_S3_PATH = 'media/'
    DEFAULT_FILE_STORAGE = lambda: S3BotoStorage(location='media')
    DEFAULT_S3_PATH = 'static/'

    if USING_CLOUDFRONT:
        AWS_CLOUDFRONT_DOMAIN = ''
        MEDIA_URL = '//{}/{}'.format(AWS_CLOUDFRONT_DOMAIN, STATIC_S3_PATH)
        STATIC_URL = '//{}/{}'.format(AWS_CLOUDFRONT_DOMAIN, DEFAULT_S3_PATH)
    else:
        MEDIA_URL = S3_URL + STATIC_S3_PATH
        STATIC_URL = S3_URL + DEFAULT_S3_PATH
        MEDIA_ROOT = '/home/ubuntu/{0}/{1}/static/media'.format(
            FULL_DOMAIN, APP_NAME)
        STATIC_ROOT = '/home/ubuntu/{0}/{1}/static/static'.format(
            FULL_DOMAIN, APP_NAME)

    STATICFILES_DIRS = (
        os.path.join(os.path.dirname(BASE_DIR), 'static', 'static_dirs'),
    )

    date_three_months_later = datetime.date.today() + datetime.timedelta(3 * 365 / 12)
    expires = date_three_months_later.strftime('%A, %d %B %Y 20:00:00 EST')
    AWS_HEADERS = {
        'Expires': expires,
        'Cache-Control': 'max-age=86400',
    }
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static', 'static')
    STATICFILES_DIRS = (
        os.path.join(os.path.dirname(BASE_DIR), 'static', 'static_dirs'),
    )
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static', 'media')


###########
# LOGGING #
###########
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}
