import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# Основные настройки
# ========================
SECRET_KEY = os.getenv("SECRET_KEY", "local-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ========================
# Installed Apps
# ========================
INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "kalkulacka",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ========================
# Middleware
# ========================
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Должен быть первым
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kalkulacka.middleware.RoleRedirectMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR.parent / "frontend" / "build",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ========================
# Database
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ========================
# Static & Media
# ========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR.parent / "frontend" / "build" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ========================
# Django REST Framework
# ========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ========================
# Authentication & Redirects
# ========================
MEAL_TOLERANCE = 0.9
LOGIN_REDIRECT_URL = "/profile/"
LOGOUT_REDIRECT_URL = "/login/"

# ========================
# CORS & CSRF
# ========================
FRONTEND_URL = "https://hubnuti-projekt-15.onrender.com"

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "https://hubnuti-projekt-17.onrender.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()
else:
    CORS_ALLOWED_ORIGINS = ["https://hubnuti-projekt-15.onrender.com"]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()