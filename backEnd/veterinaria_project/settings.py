"""
Configuración del proyecto veterinaria_project (Clínica «Huellitas» · G02).
Las credenciales se leen desde el archivo .env (nunca se suben al repositorio).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if SECRET_KEY == "":
    raise RuntimeError("Falta DJANGO_SECRET_KEY en el archivo .env")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros (rest_framework, authtoken y corsheaders se agregan en la semana 3)
    # Negocio
    "veterinaria",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "veterinaria_project.urls"

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

WSGI_APPLICATION = "veterinaria_project.wsgi.application"

# ---------------------------------------------------------------------
# Dos bases de datos:
#   default -> SQLite (usuarios, permisos, tokens, admin, sesiones)
#   negocio -> Oracle FreeSQL (tablas de la clínica)
# ---------------------------------------------------------------------
# FreeSQL exige TLS en el puerto 2484 (protocolo tcps); sin TLS el servidor
# cierra la conexión (DPY-4011). Si no se indica ORACLE_PROTOCOL, se usa tcps
# para el puerto 2484 y tcp para cualquier otro.
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521").strip()
ORACLE_PROTOCOL = os.getenv("ORACLE_PROTOCOL", "").strip().lower()
if ORACLE_PROTOCOL == "":
    ORACLE_PROTOCOL = "tcps" if ORACLE_PORT == "2484" else "tcp"

ORACLE_DSN = "{}://{}:{}/{}".format(
    ORACLE_PROTOCOL,
    os.getenv("ORACLE_HOST", "").strip(),
    ORACLE_PORT,
    os.getenv("ORACLE_SERVICE", "").strip(),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "negocio": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": ORACLE_DSN,
        "USER": os.getenv("ORACLE_USER", ""),
        "PASSWORD": os.getenv("ORACLE_PASSWORD", ""),
    },
}

DATABASE_ROUTERS = ["veterinaria_project.db_router.NegocioRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Idioma y zona horaria de Chile. En la base se guarda UTC.
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
