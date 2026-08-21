import os
import dj_database_url
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv("DEBUG", "0") == "1"

# A missing DJANGO_SECRET_KEY is only tolerable while DEBUG is on. Falling back
# to a checked-in key in production would make every issued JWT forgeable.
_DEV_SECRET_KEY = "safeconnect-dev-key-change-in-production-2026"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY must be set when DEBUG is off.")
    SECRET_KEY = _DEV_SECRET_KEY
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INSTALLED_APPS = ["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","corsheaders","rest_framework","rest_framework_simplejwt.token_blacklist","django_filters","moderation"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware","corsheaders.middleware.CorsMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF = "safeconnect.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "safeconnect.wsgi.application"
if os.getenv("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=600,conn_health_checks=True,ssl_require=not DEBUG)}
elif os.getenv("POSTGRES_DB"):
    DATABASES = {"default":{"ENGINE":"django.db.backends.postgresql","NAME":os.getenv("POSTGRES_DB"),"USER":os.getenv("POSTGRES_USER"),"PASSWORD":os.getenv("POSTGRES_PASSWORD"),"HOST":os.getenv("POSTGRES_HOST","db"),"PORT":os.getenv("POSTGRES_PORT","5432")}}
else:
    DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "moderation.User"
LANGUAGE_CODE="en-us"; TIME_ZONE="UTC"; USE_I18N=True; USE_TZ=True
STATIC_URL="static/"; DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES":["rest_framework_simplejwt.authentication.JWTAuthentication"],"DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"],"DEFAULT_FILTER_BACKENDS":["django_filters.rest_framework.DjangoFilterBackend","rest_framework.filters.SearchFilter","rest_framework.filters.OrderingFilter"],"DEFAULT_PAGINATION_CLASS":"rest_framework.pagination.PageNumberPagination","PAGE_SIZE":10,"DEFAULT_THROTTLE_CLASSES":["rest_framework.throttling.AnonRateThrottle","rest_framework.throttling.UserRateThrottle"],"DEFAULT_THROTTLE_RATES":{"anon":"30/min","user":"120/min"}}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME":timedelta(minutes=30),"REFRESH_TOKEN_LIFETIME":timedelta(days=7),"ROTATE_REFRESH_TOKENS":True,"BLACKLIST_AFTER_ROTATION":True}
REDIS_URL=os.getenv("REDIS_URL","")
CACHES={"default":{"BACKEND":"django.core.cache.backends.redis.RedisCache","LOCATION":REDIS_URL}} if REDIS_URL else {"default":{"BACKEND":"django.core.cache.backends.locmem.LocMemCache"}}
CELERY_BROKER_URL=REDIS_URL or "memory://"; CELERY_RESULT_BACKEND=REDIS_URL or "cache+memory://"

# Transport security, applied only outside DEBUG so local HTTP dev still works.
# SECURE_PROXY_SSL_HEADER must be paired with SECURE_SSL_REDIRECT here: Render
# terminates TLS at its edge and forwards over HTTP, so without it Django would
# see every request as insecure and redirect forever.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
