#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 OUTPUT_DIRECTORY" >&2
  exit 2
fi

deploy_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source_dir=${OPENBENCH_SOURCE:-$(cd "$deploy_dir/.." && pwd)}
service_user=${OPENBENCH_SERVICE_USER:-openbench}
service_group=${OPENBENCH_SERVICE_GROUP:-openbench}
state_dir=${OPENBENCH_STATE_DIR:-/var/lib/openbench}
environment_file=${OPENBENCH_ENVIRONMENT_FILE:-/etc/openbench/openbench.env}
bash=${OPENBENCH_BASH:-/bin/bash}
output_dir=$1

escape_sed_replacement() {
  printf '%s' "$1" | sed 's/[\\&|]/\\&/g'
}

service_user=$(escape_sed_replacement "$service_user")
service_group=$(escape_sed_replacement "$service_group")
state_dir=$(escape_sed_replacement "$state_dir")
environment_file=$(escape_sed_replacement "$environment_file")
source_dir=$(escape_sed_replacement "$source_dir")
bash=$(escape_sed_replacement "$bash")

render_dir=$(mktemp -d)
trap 'rm -rf "$render_dir"' EXIT

for unit in openbench-server openbench-worker openbench-backup; do
  sed \
    -e "s|@service_user@|$service_user|g" \
    -e "s|@service_group@|$service_group|g" \
    -e "s|@state_dir@|$state_dir|g" \
    -e "s|@environment_file@|$environment_file|g" \
    -e "s|@source_dir@|$source_dir|g" \
    -e "s|@bash@|$bash|g" \
    "$deploy_dir/$unit.service.in" > "$render_dir/$unit.service"
done

if grep -En '@[[:alnum:]_]+@' "$render_dir"/*.service; then
  echo "Unresolved placeholder in rendered OpenBench service" >&2
  exit 1
fi

install -d -m 0755 "$output_dir"
install -m 0644 "$render_dir"/*.service "$deploy_dir/openbench-backup.timer" "$output_dir/"
