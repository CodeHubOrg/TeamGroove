""" Set up environment variables for Team Groove applications specific to production environment"""
import os

from .base import *

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="y1JCaLAyeDI0M48NZox7oDkGEs2979bLBd5P6J2e5FrqT24qS8PdIGNKsGkTc4Rt",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
