import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ============== BASE ==============
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

# ================== STATIC / MEDIA ==================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"

# Configuração para produção
if not DEBUG:
    # Configurações específicas para produção
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Hosts e CSRF - Configuração fixa para funcionar em qualquer ambiente
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'eventix-development.up.railway.app',
    'railway.app',
    '*.railway.app',  # Permite qualquer subdomínio do Railway
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
   
    'http://eventix-development.up.railway.app',
    'https://*.railway.app',  # Permite qualquer subdomínio HTTPS do Railway
   
]

# Configurações aplicadas

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
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # Seus apps
    "app_eventos",
    "api_v01",
    "api_mobile",
    "api_desktop",
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
    "corsheaders.middleware.CorsMiddleware",  # CORS antes de CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Middleware customizado para controle multi-empresas
    "app_eventos.middleware_dashboard.DashboardRedirectMiddleware",
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
        "DIRS": [BASE_DIR / "templates", BASE_DIR / "app_eventos" / "templates"],  # inclui templates do app
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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'ItkhFBExHXIbdgfkxekghWeGzRElxQQa',
        'HOST': 'yamanote.proxy.rlwy.net',
        'PORT': '28520',
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
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    # Paginação padrão
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
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

# ========== STATIC / MEDIA (final) ==========
# WhiteNoise storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ========== LOGIN REDIRECTS ==========
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ========== LOGGING (dev) ==========
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# CORS - Configuração fixa para funcionar em qualquer ambiente
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://eventix-development.up.railway.app',
        'http://eventix-development.up.railway.app',
        'https://*.railway.app',
        'http://*.railway.app',
    ]

CORS_ALLOW_CREDENTIALS = True

# Integrações
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")  # do painel Mercado Pago