#!/usr/bin/env bash
set -euo pipefail

source_dir=${OPENBENCH_SOURCE:-$(cd "$(dirname "$0")/.." && pwd)}
python=${OPENBENCH_PYTHON:-$source_dir/.venv/bin/python}
exec "$python" "$source_dir/Deploy/backup.py"
