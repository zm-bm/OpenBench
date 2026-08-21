"""Production overrides loaded from the untracked host environment."""

import os
from pathlib import Path

from OpenSite.settings import *  # noqa: F403


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("OPENBENCH_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

MIDDLEWARE = MIDDLEWARE.copy()  # noqa: F405
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATIC_ROOT = os.environ.get(
    "OPENBENCH_STATIC_ROOT",
    str(Path.home() / ".local/share/openbench/static"),
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

