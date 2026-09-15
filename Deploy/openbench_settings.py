"""Production settings backed by an external environment and state directory."""

import os
from pathlib import Path

import OpenSite.settings as upstream_settings
from OpenSite.settings import *  # noqa: F403


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("OPENBENCH_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
public_host = os.environ.get("OPENBENCH_PUBLIC_HOST")
if public_host:
    if public_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(public_host)
    CSRF_TRUSTED_ORIGINS = [f"https://{public_host}"]
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

state_root = Path(os.environ.get("OPENBENCH_STATE_DIR", "/var/lib/openbench"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": state_root / "db.sqlite3",
    }
}
MEDIA_ROOT = state_root / "Media"
# This OpenBench revision imports MEDIA_ROOT directly from the upstream module.
upstream_settings.MEDIA_ROOT = MEDIA_ROOT
STATIC_ROOT = state_root / "static"

MIDDLEWARE = MIDDLEWARE.copy()  # noqa: F405
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
