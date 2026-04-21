from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# 🔐 CORE SETTINGS
# --------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# --------------------------------------------------
# 🧠 CUSTOM FLAGS (UNCHANGED)
# --------------------------------------------------
TEST_LOG = os.getenv("TEST_LOG", "false").lower() == "true"
BASIC_LOGS = os.getenv("TEST_LOG", "false").lower() == "true"

ALLOW_LIVE_TRADING = os.getenv("ALLOW_LIVE_TRADING", "False") == "True"

THRESHOLD_CHECK = True

# --------------------------------------------------
# 🍃 MONGO CONFIG (UNCHANGED)
# --------------------------------------------------
MONGO_URI = os.getenv("AUTH_MONGO_URI")
MONGO_DB_NAME = os.getenv("AUTH_DB_NAME", "trading")

# --------------------------------------------------
# 📡 WEBSOCKET CONFIG (UNCHANGED)
# --------------------------------------------------
WS_FEED_CONFIG = {
    "TEST_LOG": os.getenv("WS_TEST_LOG", "False") == "True",
    "SHOW_LTP": os.getenv("WS_SHOW_LTP", "False") == "True",
}

# --------------------------------------------------
# 📦 INSTALLED APPS
# --------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webhook_app",
    "ws_feed.apps.WsFeedConfig",
    "order_engine",
    "option_selector",
    "core",
]

# --------------------------------------------------
# 🧱 MIDDLEWARE (ADD WHITENOISE)
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ ADD
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
ROOT_URLCONF = "T_System.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "T_System.wsgi.application"

# --------------------------------------------------
# 🗄️ DATABASE (DUMMY SQLITE – REQUIRED BY DJANGO)
# --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 👉 You are NOT using it — just keeping Django happy

# --------------------------------------------------
# 🌍 INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# 📁 STATIC FILES
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# --------------------------------------------------
# 🔒 DEFAULT AUTO FIELD
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"