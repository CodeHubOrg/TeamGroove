""" Set up environment variables for Team Groove applications specific to production environment"""
import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", ""),
    }
}

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)s %(module)s %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "ERROR", "handlers": ["console"]},
}
