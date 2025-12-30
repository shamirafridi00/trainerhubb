"""
Production settings for TrainerHub
Secure production configuration with environment variables.
"""
import os
from .base import *
from decouple import config, Csv

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = config('SECRET_KEY')

# ALLOWED HOSTS - Must be explicitly set in production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# HTTPS SETTINGS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# DATABASE - Production PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        }
    }
}

# STATIC FILES - Use S3 or CloudFront in production
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')

if AWS_STORAGE_BUCKET_NAME:
    # Use S3 for static files
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Fallback to local storage with CDN
    STATIC_URL = config('STATIC_URL', default='/static/')
    MEDIA_URL = config('MEDIA_URL', default='/media/')

# EMAIL - Production email service
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@trainerhubb.app')

# LOGGING - Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/trainerhub/django.log',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# CACHE - Redis for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'trainerhubb_prod',
        'TIMEOUT': 300,
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'trainerhubb_sessions_prod',
    },
}

# CELERY - Production configuration
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')
CELERY_TASK_ALWAYS_EAGER = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# MONITORING - Sentry error tracking
if config('SENTRY_DSN', default=''):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=1.0, cast=float),
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
        profiles_sample_rate=config('SENTRY_PROFILES_SAMPLE_RATE', default=1.0, cast=float),
        environment=config('ENVIRONMENT', default='production'),
        release=config('RELEASE_VERSION', default=''),
    )

# PERFORMANCE OPTIMIZATIONS
# Enable GZip compression
MIDDLEWARE.insert(0, 'django.middleware.gzip.GZipMiddleware')

# Enable cache middleware for public pages
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
] + MIDDLEWARE + [
    'django.middleware.cache.FetchFromCacheMiddleware',
]
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'trainerhubb_middleware_prod'

# Database optimizations
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['OPTIONS']['autocommit'] = True

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Admin settings
ADMIN_URL = config('ADMIN_URL', default='admin/')

# API rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_CACHE_PREFIX = 'rl:'

# Health check endpoint
HEALTH_CHECK_ENABLED = True
