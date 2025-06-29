"""
Django test settings for convenience store management system.
This configuration uses SQLite with SpatiaLite for faster test execution.
"""

from backend.settings import *
import os

# Test database configuration using PostgreSQL with PostGIS
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'convenience_store_test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres123',
        'HOST': 'localhost',
        'PORT': '5433',
        'TEST': {
            'NAME': 'convenience_store_test_db',
        },
    }
}

# Disable cache during testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable CORS during testing
CORS_ALLOW_ALL_ORIGINS = True

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests unless needed for debugging
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
        'level': 'ERROR',  # Only show errors during tests
    },
}

# Test-specific settings
SECRET_KEY = 'test-secret-key-for-testing-only'
DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Disable migrations for faster tests (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Uncomment the following line to disable migrations during tests
# MIGRATION_MODULES = DisableMigrations()

# PostGIS configuration - no additional library paths needed
# PostGIS is handled natively by the PostgreSQL backend 