from datetime import timedelta
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG") != "False"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "rest_framework_simplejwt",
    "rest_framework",
    "django_celery_beat",
    "django_extensions",
    "debug_toolbar",
    "templated_email",
    "drf_spectacular",
    "rosetta",
    
    "books_service.apps.BooksServiceConfig",
    "user",
    "borrowing_service",
    "payments_service",    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "library_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "library_project.wsgi.application"

# For local usage:
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ["POSTGRES_HOST"],
        "NAME": os.environ["POSTGRES_NAME"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "user.User"

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
    ("uk", _("Ukrainian")),
]

STATIC_URL = "static/"
MEDIA_URL = "/media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media") // for local usage
MEDIA_ROOT = "/vol/web/media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = [
    "127.0.0.1",
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 25,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
}

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

STRIPE_SECRET = os.environ.get("STRIPE_SECRET")

SPECTACULAR_SETTINGS = {
    "TITLE": "Library Service API",
    "DESCRIPTION": "Manage books, borrowings and payments for library",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelRendering": "model",
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
    },
}

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "check_overdue_borrowings": {
        "task": "borrowing_service.tasks.check_overdue_borrowings",
        "schedule": crontab(minute=0, hour=7),
    },
    "check_expired_payments": {
        "task": "payments_service.tasks.check_expired_payments",
        "schedule": crontab(minute="*")
    }
}

CELERY_BROKER_URL = "redis://localhost"

CELERY_RESULT_BACKEND = "redis://localhost"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "verbose": {
            "format": (
                "[%(asctime)s] %(levelname)s "
                "[%(name)s:%(lineno)s] -> %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "(%(name)s:%(lineno)s) %(message)s"},
        "extended": {
            "format": "%(levelname)s:%(name)s: %(message)s "
            "(%(asctime)s; %(filename)s:%(lineno)d)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "main": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/debug.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "trash_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/trash_error.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "books_service_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/books_service_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "borrowing_service_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/borrowing_service_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "payments_service_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/payment_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "tg_bot_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/tg_bot_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "stripe_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/stripe_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "celery_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/stripe_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
        "users_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/user_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "extended",
        },
    },
    "loggers": {
        "PIL": {
            "handlers": ["main", "error"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "urllib3": {
            "handlers": ["main", "error"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "django.db": {
            "handlers": ["null"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["trash_error"],
            "propagate": False,
        },
        "": {
            "handlers": ["main", "debug", "error"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.user": {
            "handlers": ["debug", "error", "users_file"],
            "level": "INFO",
            "propagate": False,
        },
        "borrowing_service": {
            "handlers": ["borrowing_service_file", "debug", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "books_service": {
            "handlers": ["books_service_file", "debug", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "payments_service": {
            "handlers": ["payments_service_file", "debug", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "tg_bot": {
            "handlers": ["tg_bot_file", "debug", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "stripe": {
            "handlers": ["stripe_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

FINE_MULTIPLIER = 2

EMAIL_BACKEND = "django_smtp_ssl.SSLEmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 465
EMAIL_TIMEOUT = 10

TEMPLATED_EMAIL_FILE_EXTENSION = "html"
