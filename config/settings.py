"""
Django settings for TrainerHub project.
Configured to work with Supabase PostgreSQL and Authentication.
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'admin_interface',  # Must be before django.contrib.admin
    'colorfield',  # Required by admin_interface
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'apps.users',
    'apps.trainers',
    'apps.clients',
    'apps.availability',
    'apps.bookings',
    'apps.packages',
    'apps.payments',
    'apps.notifications',
    'apps.analytics',
    'apps.frontend',
    'apps.admin_panel',
    'apps.pages',
    'apps.workflows',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'apps.pages.middleware.SubdomainMiddleware',  # Subdomain/custom domain detection
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.payments.middleware.SubscriptionMiddleware',  # Subscription status checking
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.frontend.middleware.UserInteractionLoggerMiddleware',  # User interaction logging
    'apps.core.middleware.RequestLoggingMiddleware',  # Request logging and monitoring
    'apps.core.middleware.HealthCheckMiddleware',  # Health check enhancements
    'apps.core.middleware.SecurityHeadersMiddleware',  # Security headers
    'apps.core.middleware.PerformanceMonitoringMiddleware',  # Performance monitoring
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Add PostgreSQL-specific options only when using PostgreSQL
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 10,
    }

# Supabase Configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY', default='')
SUPABASE_PROJECT_ID = config('SUPABASE_PROJECT_ID', default='')

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Caching configuration - use Redis if available, otherwise fallback to locmem
REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')

def get_cache_backend(redis_url, timeout=300, prefix='trainerhubb'):
    """Get cache backend, falling back to locmem if Redis is unavailable."""
    try:
        # Test Redis connection
        import redis
        client = redis.from_url(redis_url)
        client.ping()
        return {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': prefix,
            'TIMEOUT': timeout,
        }
    except (ImportError, redis.ConnectionError):
        # Fallback to local memory cache
        return {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': f'{prefix}_cache',
            'TIMEOUT': timeout,
        }

CACHES = {
    'default': get_cache_backend(REDIS_URL, timeout=300, prefix='trainerhubb'),
    'templates': get_cache_backend(f'{REDIS_URL.rsplit("/", 1)[0]}/1', timeout=3600, prefix='trainerhubb_templates'),
    'sessions': get_cache_backend(f'{REDIS_URL.rsplit("/", 1)[0]}/2', timeout=86400, prefix='trainerhubb_sessions'),
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://localhost:3003',
    'http://localhost:3004',
    'http://localhost:3005',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3002',
    'http://127.0.0.1:3003',
    'http://127.0.0.1:3004',
    'http://127.0.0.1:3005',
    'http://127.0.0.1:8000',
    'http://192.168.100.182:3000',
    'http://192.168.100.182:3001',
    'http://192.168.100.182:3002',
    'http://192.168.100.182:3003',
    'http://192.168.100.182:3004',
    'http://192.168.100.182:3005',
]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Fail fast if Redis is unavailable (prevent slow retries)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = False
CELERY_BROKER_CONNECTION_RETRY = False
CELERY_BROKER_CONNECTION_MAX_RETRIES = 1
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_connections': 10,
    'socket_connect_timeout': 2,  # 2 second timeout
    'socket_timeout': 2,
    'retry_on_timeout': False,
}

# Email Configuration (SendGrid)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Payment Configuration (Paddle)
PADDLE_VENDOR_ID = config('PADDLE_VENDOR_ID', default='')
PADDLE_API_KEY = config('PADDLE_API_KEY', default='')
PADDLE_WEBHOOK_SECRET = config('PADDLE_WEBHOOK_SECRET', default='')
PADDLE_PRODUCT_ID = config('PADDLE_PRODUCT_ID', default='')
PADDLE_NOTIFICATION_SET_ID = config('PADDLE_NOTIFICATION_SET_ID', default='')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'trainerhub.log',
            'formatter': 'verbose',
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
        'apps.bookings': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.payments': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.notifications': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.analytics': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
