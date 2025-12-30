"""
Django settings for development environment.
"""

import os
from .base import *

DEBUG = True

# Development allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'trainerhubb.local',
    'app.trainerhubb.local',
    'trainerhubb.app',
    'app.trainerhubb.app',
    '192.168.100.182',  # For network access
]

# Development database (SQLite for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development email backend (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://localhost:3003',
    'http://localhost:3004',
    'http://localhost:3005',
    'http://localhost:3006',
    'http://localhost:3007',
    'http://localhost:3008',
    'http://localhost:3009',
    'http://localhost:3010',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3002',
    'http://127.0.0.1:3003',
    'http://127.0.0.1:3004',
    'http://127.0.0.1:3005',
    'http://127.0.0.1:3006',
    'http://127.0.0.1:3007',
    'http://127.0.0.1:3008',
    'http://127.0.0.1:3009',
    'http://127.0.0.1:3010',
    'http://192.168.100.182:3000',
    'http://192.168.100.182:3001',
    'http://192.168.100.182:3002',
    'http://192.168.100.182:3003',
    'http://192.168.100.182:3004',
    'http://192.168.100.182:3005',
    'http://192.168.100.182:3006',
    'http://192.168.100.182:3007',
    'http://192.168.100.182:3008',
    'http://192.168.100.182:3009',
    'http://192.168.100.182:3010',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://trainerhubb.local:8000',
    'http://app.trainerhubb.local:8000',
]

# Development logging (more verbose)
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
            'filename': '/home/shamir/trainerhubb/logs/trainerhub_dev.log',
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
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
