"""
Caching configuration for TrainerHub
"""
import os

# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'trainerhubb',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'templates': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'TIMEOUT': 3600,  # 1 hour for templates
        'KEY_PREFIX': 'trainerhubb_templates',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'TIMEOUT': 86400,  # 24 hours for sessions
        'KEY_PREFIX': 'trainerhubb_sessions',
    },
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Cache middleware
MIDDLEWARE_CACHE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Cache time settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'trainerhubb_middleware'

# Cache keys
CACHE_KEYS = {
    'TRAINER_PROFILE': 'trainer_profile_{id}',
    'SUBSCRIPTION': 'subscription_{trainer_id}',
    'FEATURE_LIMITS': 'feature_limits_{trainer_id}',
    'PAGE_TEMPLATES': 'page_templates_list',
    'PUBLIC_PAGE': 'public_page_{trainer_slug}_{page_slug}',
    'TRAINER_PAGES': 'trainer_pages_{trainer_id}',
    'WHITELABEL': 'whitelabel_{trainer_id}',
}

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'TRAINER_PROFILE': 3600,  # 1 hour
    'SUBSCRIPTION': 1800,  # 30 minutes
    'FEATURE_LIMITS': 1800,  # 30 minutes
    'PAGE_TEMPLATES': 86400,  # 24 hours
    'PUBLIC_PAGE': 600,  # 10 minutes
    'TRAINER_PAGES': 300,  # 5 minutes
    'WHITELABEL': 3600,  # 1 hour
}

