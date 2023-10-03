"""
Django settings for prototype project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default='django-insecure-rij37)-oles^@_!o7elf$o-hrn5s%_d5&bw2t&a3b6-cngiqo4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=True)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

ALLOWED_HOSTS = ['*']

# Application definition

LOCAL_APPS = [
    'accounts.apps.AccountsConfig',
    'event.apps.EventConfig',
    'connectors.apps.ConnectorsConfig',
    'management.apps.ManagementConfig',
    'prototype.apps.PrototypeConfig',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'corsheaders',
    "djcelery_email"
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_prometheus',
    'django_celery_beat',
    'django.contrib.sites',
    'django.contrib.postgres',
    *LOCAL_APPS,
    *THIRD_PARTY_APPS,
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'prototype.middleware.RequestThreadLocalMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'prototype.urls'

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

WSGI_APPLICATION = 'prototype.wsgi.application'

_default_postgres_host = env.str('POSTGRES_HOST', default='127.0.0.1')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB', default='db'),
        'USER': env.str('POSTGRES_USER', default='user'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', default='pass'),
        'HOST': _default_postgres_host,
        'PORT': env.str('POSTGRES_PORT', default='5432'),
    },
    'replica1': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB', default='db'),
        'USER': env.str('POSTGRES_USER', default='user'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', default='pass'),
        'HOST': env.str('REPLICA1_POSTGRES_HOST', default=_default_postgres_host),
        'PORT': env.str('POSTGRES_PORT', default='5432'),
    },
    'clickhouse': {
        'ENGINE': 'clickhouse_backend.backend',
        'HOST': env.str("CLICKHOUSE_HOST", default='localhost'),
        'PORT': env.str("CLICKHOUSE_PORT", default='9000'),
        'USER': env.str("CLICKHOUSE_USERNAME", default='default'),
        'PASSWORD': env.str("CLICKHOUSE_PASSWORD", default=''),
        'OPTIONS': {
            'secure': env.bool("CLICKHOUSE_SECURE", default=True),
            'settings': {
                'allow_experimental_object_type': 1
            }
        }
    }
}

DATABASE_ROUTERS = ['prototype.db.router.DbRouter']

# Celery Configuration Options
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIME_ZONE = 'UTC'

# Celery Beat Configuration Options
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Redis Configuration
REDIS_URL = env.str('REDIS_URL', default='redis://localhost:6379')

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = "accounts.User"

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # },
    },
}

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8080', 'http://localhost']

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # We have disabled csrf checks here.
        'prototype.auth.CsrfExemptedSessionAuthentication',
    ),
}

SITE_ID = 1

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_VERIFICATION_URL = '/confirm-email/{}/'
ACCOUNT_USER_DISPLAY = 'accounts.authentication.user_display'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
ACCOUNT_ADAPTER = 'accounts.authentication.AccountAdapter'

REST_SESSION_LOGIN = True
REST_USE_JWT = True
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'accounts.serializer.AccountLoginSerializer'
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'accounts.serializer.AccountRegisterSerializer',
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh'

RESTRICT_EMAIL_DOMAIN = env.str("RESTRICT_EMAIL_DOMAIN", default='')

# For demo purposes only. Use a white list in the real world.
CORS_ORIGIN_ALLOW_ALL = True

LOGIN_URL = '/accounts/login/'
ALERT_PAGE_URL = '/alerts/{}'

# Email settings
EMAIL_USE_SITES = False
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'notification',
    'rate_limit': '50/m',  # * CELERY_EMAIL_CHUNK_SIZE (default: 10)
}

# Alert settings
ALERT_USE_SITE = True
ALERT_SITE_HTTP_PROTOCOL = 'http'

DELAYED_EVENT_TRIGGER_RESOLUTION_WINDOW_LOWER_BOUND_IN_SEC = int(env.str(
    'DELAYED_EVENT_TRIGGER_RESOLUTION_WINDOW_LOWER_BOUND_IN_SEC', default='60'))

ENTITY_PROCESSING_ENABLED = env.bool("ENTITY_PROCESSING_ENABLED", default=True)

RAW_EVENT_PROCESSING = {
    'async': env.bool("KAFKA_PRODUCER_RAW_EVENT_ENABLED", default=False),
    'producer': 'raw_events'
}

PROCESSED_EVENT_PROCESSING = {
    'async': env.bool("KAFKA_PRODUCER_PROCESSED_EVENT_ENABLED", default=False),
    'producer': 'processed_events'
}

RAW_MONITOR_TRANSACTION_PROCESSING = {
    'async': env.bool("KAFKA_PRODUCER_RAW_MONITOR_TRANSACTION_ENABLED", default=False),
    'producer': 'raw_monitor_transactions'
}

PROCESSED_MONITOR_TRANSACTION_PROCESSING = {
    'async': env.bool("KAFKA_PRODUCER_PROCESSED_MONITOR_TRANSACTION_ENABLED", default=False),
    'producer': 'processed_monitor_transactions'
}

KAFKA_PRODUCER_CONFIG = {
    'raw_events': {
        'enabled': env.bool("KAFKA_PRODUCER_RAW_EVENT_ENABLED", default=False),
        'topic': env.str("KAFKA_RAW_EVENT_TOPIC", default='raw-events'),
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'acks': 1,
        }
    },
    'raw_monitor_transactions': {
        'enabled': env.bool("KAFKA_PRODUCER_RAW_MONITOR_TRANSACTION_ENABLED", default=False),
        'topic': env.str("KAFKA_RAW_MONITOR_TRANSACTION_TOPIC", default='raw-monitor-transactions'),
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'acks': 1,
        }
    },
    'processed_events': {
        'enabled': env.bool("KAFKA_PRODUCER_PROCESSED_EVENT_ENABLED", default=False),
        'topic': env.str("KAFKA_PROCESSED_EVENT_TOPIC", default='processed-events'),
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'acks': 1,
        }
    },
    'processed_monitor_transactions': {
        'enabled': env.bool("KAFKA_PRODUCER_PROCESSED_MONITOR_TRANSACTION_ENABLED", default=False),
        'topic': env.str("KAFKA_PROCESSED_MONITOR_TRANSACTION_TOPIC", default='processed-monitor-transactions'),
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'acks': 1,
        }
    },
}

KAFKA_CONSUMER_CONFIG = {
    'raw_events': {
        'enabled': env.bool("KAFKA_CONSUMER_RAW_EVENT_ENABLED", default=True),
        'topic': env.str("KAFKA_RAW_EVENT_TOPIC", default='raw-events'),
        'processor': 'event.processors.raw_events_processor.RawEventProcessor',
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'auto.offset.reset': 'earliest'
        }
    },
    'raw_monitor_transactions': {
        'enabled': env.bool("KAFKA_CONSUMER_RAW_MONITOR_TRANSACTION_ENABLED", default=True),
        'topic': env.str("KAFKA_RAW_MONITOR_TRANSACTION_TOPIC", default='raw-monitor-transactions'),
        'processor': 'event.processors.raw_monitor_transactions_processor.RawMonitorTransactionProcessor',
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'auto.offset.reset': 'earliest'
        }
    },
    'processed_events_clickhouse': {
        'enabled': env.bool("KAFKA_CONSUMER_PROCESSED_EVENTS_CLICKHOUSE_ENABLED", default=True),
        'topic': env.str("KAFKA_PROCESSED_EVENT_TOPIC", default='processed-events'),
        'processor': 'event.processors.processed_events_processor.ProcessedEventClickhouseIngestProcessor',
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'auto.offset.reset': 'earliest'
        }
    },
    'processed_monitor_transactions_clickhouse': {
        'enabled': env.bool("KAFKA_CONSUMER_PROCESSED_MONITOR_TRANSACTIONS_CLICKHOUSE_ENABLED", default=True),
        'topic': env.str("KAFKA_PROCESSED_MONITOR_TRANSACTIONS_TOPIC", default='processed-monitor-transactions'),
        'processor': 'event.processors.processed_monitor_transaction_processor.ProcessedMonitorTransactionClickhouseIngestProcessor',
        'config': {
            'bootstrap.servers': env.str("KAFKA_BOOTSTRAP_SERVERS", default='localhost:9092'),
            'auto.offset.reset': 'earliest'
        }
    }
}

def get_cache_backend(alias='default'):
    if env.str("CACHE_BACKEND", default='locmem') == 'redis':
        return {
            alias: {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": env.str("REDIS_URL", default='redis://localhost:6379/1'),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            }
        }
    else:
        return {
            alias: {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }


CACHES = {
    **get_cache_backend('default'),
}

GLOBAL_EVENT_TYPE_CACHE = {
    'cache_key': env.str("EVENT_TYPE_CACHE_KEY", default='default'),
    'enabled': env.bool("EVENT_TYPE_CACHE_ENABLED", default=True),
}

GLOBAL_EVENT_KEY_CACHE = {
    'cache_key': env.str("EVENT_KEY_CACHE_KEY", default='default'),
    'enabled': env.bool("EVENT_KEY_CACHE_ENABLED", default=True),
}

GLOBAL_PANEL_CACHE = {
    'cache_key': env.str("PANEL_CACHE_KEY", default='default'),
    'enabled': env.bool("PANEL_CACHE_ENABLED", default=True),
}

GLOBAL_DASHBOARD_CACHE = {
    'cache_key': env.str("DASHBOARD_CACHE_KEY", default='default'),
    'enabled': env.bool("DASHBOARD_CACHE_ENABLED", default=True),
}

GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE = {
    'cache_key': env.str("GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE_KEY", default='default'),
    'enabled': env.bool("GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE_ENABLED", default=True),
}

GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE = {
    'cache_key': env.str("GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE_KEY", default='default'),
    'enabled': env.bool("GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE_ENABLED", default=True),
}

RECAPTCHA_SECRET_KEY = env.str("RECAPTCHA_SECRET_KEY", default='6LfGFpgmAAAAAL-caY9EiWPECwnbfaVPrjAUmaAJ')

GLOBAL_ACCOUNT_API_TOKEN_CACHE = {
    'cache_key': env.str("ACCOUNT_API_TOKEN_CACHE_KEY", default='default'),
    'enabled': env.bool("ACCOUNT_API_TOKEN_CACHE_ENABLED", default=True),
}

GLOBAL_ACCOUNT_CACHE = {
    'cache_key': env.str("ACCOUNT_CACHE_KEY", default='default'),
    'enabled': env.bool("ACCOUNT_CACHE_ENABLED", default=True),
}

GLOBAL_EXPORT_CONTEXT_CACHE = {
    'cache_key': env.str("EXPORT_CONTEXT_CACHE_KEY", default='default'),
    'enabled': env.bool("EXPORT_CONTEXT_CACHE_ENABLED", default=True),
}

ACCOUNT_DAILY_EVENT_QUOTA = env.int("ACCOUNT_DAILY_EVENT_QUOTA", default=10000)

CLICKHOUSE_CLIENT_CONFIG = {
    'host': env.str("CLICKHOUSE_HOST", default='localhost'),
    'port': env.int("CLICKHOUSE_PORT", default=8443),
    'username': env.str("CLICKHOUSE_USERNAME", default='default'),
    'password': env.str("CLICKHOUSE_PASSWORD", default=''),
}
