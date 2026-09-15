#!/usr/bin/env bash
set -euo pipefail

source_dir=${OPENBENCH_SOURCE:-$(cd "$(dirname "$0")/.." && pwd)}
state_dir=${OPENBENCH_STATE_DIR:-/var/lib/openbench}
python=${OPENBENCH_PYTHON:-$source_dir/.venv/bin/python}
gunicorn=${OPENBENCH_GUNICORN:-$source_dir/.venv/bin/gunicorn}
settings_dir=${OPENBENCH_SETTINGS_DIR:-$source_dir/Deploy}

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-openbench_settings}
export PYTHONPATH="$settings_dir:$source_dir${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

cd "$state_dir"
test -f db.sqlite3 || { echo "OpenBench database not found at $state_dir/db.sqlite3" >&2; exit 1; }
mkdir -p Media static Client
"$python" "$source_dir/manage.py" migrate --noinput
"$python" "$source_dir/manage.py" collectstatic --noinput
exec "$gunicorn" OpenSite.wsgi:application \
  --bind "${OPENBENCH_BIND:-127.0.0.1:8000}" \
  --workers 1 --timeout 120 --access-logfile - --error-logfile -
