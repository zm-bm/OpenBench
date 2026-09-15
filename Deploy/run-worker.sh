#!/usr/bin/env bash
set -euo pipefail

source_dir=${OPENBENCH_SOURCE:-$(cd "$(dirname "$0")/.." && pwd)}
state_dir=${OPENBENCH_STATE_DIR:-/var/lib/openbench}
python=${OPENBENCH_PYTHON:-$source_dir/.venv/bin/python}
client_dir=$state_dir/Client

mkdir -p "$client_dir"
cp --no-preserve=mode "$source_dir"/Client/*.py "$client_dir"/
cd "$client_dir"

client_flags=()
if [[ -n ${OPENBENCH_FASTCHESS:-} ]]; then
  install -m 700 "$OPENBENCH_FASTCHESS" fastchess-ob
  client_flags+=(--no-client-downloads)
fi

exec "$python" client.py "${client_flags[@]}" \
  --threads "${OPENBENCH_WORKER_THREADS:-1}" \
  --nsockets "${OPENBENCH_WORKER_SOCKETS:-1}" \
  --identity "${OPENBENCH_WORKER_IDENTITY:-$(hostname)}" \
  --focus "${OPENBENCH_WORKER_FOCUS:-Latrunculi}"
