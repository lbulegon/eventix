import os
from pathlib import Path
from datetime import timedelta
# ============== BASE ==============
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---- Static files
STATIC_URL = "/static/"
# onde você guarda seus arquivos estáticos do projeto (css/js/imagens próprios)
STATICFILES_DIRS = [BASE_DIR / "static"]  # opcional, só se você tiver pasta /static no projeto
# onde o collectstatic vai juntar TUDO (use em produção)
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    # Arquivos de mídia enviados pelo usuário
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
        },
    },
    # Arquivos estáticos coletados (collectstatic)
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}



SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "False") == "True"

# Ajuste para seu domínio no Railway e uso local
ALLOWED_HOSTS = [
    "eventix-development.up.railway.app",  # seu domínio Railway
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://eventix-development.up.railway.app",
    # se for usar outro domínio custom depois, add aqui também
]

# ============ APPS ============
INSTALLED_APPS = [
    # Django padrão
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceiros
    "rest_framework",
    "rest_framework_simplejwt",
    # "corsheaders",  # opcional

    # Seus apps
    "app_eventos",
    "api_v01",
]

# IMPORTANTÍSSIMO: não remova os finders padrão
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",  # <- necessário para achar /admin
]

AUTH_USER_MODEL = "app_eventos.User"

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <- antes de CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "corsheaders.middleware.CorsMiddleware",  # se usar CORS, deixe antes de CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Middleware customizado para controle multi-empresas
    "app_eventos.middleware.EmpresaContratanteMiddleware",
    "app_eventos.middleware.EmpresaContextMiddleware",
]

# CORS (opcional)
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "setup.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # opcional
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

WSGI_APPLICATION = "setup.wsgi.application"
# ASGI_APPLICATION = "setup.asgi.application"  # se for usar channels

# ========== DATABASE ==========
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "eventix",
        "USER": "postgres",
        "PASSWORD": "MaHppemIkAJjTyCADpUGOIBqqOKtsVfS",
        "HOST": "trolley.proxy.rlwy.net",
        "PORT": "23534",
    }
}

# ========== AUTH / DRF / JWT ==========
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ========== I18N / TZ ==========
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ========== STATIC / MEDIA ==========
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"      # útil no Railway (collectstatic)
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========== LOGIN REDIRECTS ==========
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ========== LOGGING (dev) ==========
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'