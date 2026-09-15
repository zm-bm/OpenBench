# System service deployment

This directory contains application-owned systemd templates and launch helpers for a
small OpenBench installation. The templates intentionally leave host paths and the
service account to the installer.

## Install

The example below uses `/opt/OpenBench` for the checkout, `/var/lib/openbench` for
mutable state, and `/etc/openbench/openbench.env` for secrets.

```bash
sudo useradd --system --home-dir /var/lib/openbench --create-home openbench
sudo git clone https://github.com/zm-bm/OpenBench.git /opt/OpenBench
sudo python3.11 -m venv /opt/OpenBench/.venv
sudo /opt/OpenBench/.venv/bin/pip install \
  -r /opt/OpenBench/requirements.txt \
  -r /opt/OpenBench/Client/requirements.txt

sudo install -d -m 0750 -o root -g openbench /etc/openbench
sudo install -m 0640 -o root -g openbench \
  /opt/OpenBench/Deploy/openbench.env.example \
  /etc/openbench/openbench.env
sudo install -m 0600 -o openbench -g openbench /dev/null \
  /var/lib/openbench/db.sqlite3
```

Edit `/etc/openbench/openbench.env`, replacing the secret and host placeholders.
Render the services using the documented default paths, then start the server and
backup timer:

```bash
sudo /opt/OpenBench/Deploy/render-systemd-units.sh /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable --now openbench-server openbench-backup.timer
```

Create the initial administrator using the same settings as the service:

```bash
sudo -u openbench -g openbench bash -c '
  set -a
  source /etc/openbench/openbench.env
  set +a
  export OPENBENCH_SOURCE=/opt/OpenBench
  export OPENBENCH_STATE_DIR=/var/lib/openbench
  export PYTHONPATH=/opt/OpenBench/Deploy:/opt/OpenBench
  cd /var/lib/openbench
  /opt/OpenBench/.venv/bin/python /opt/OpenBench/manage.py createsuperuser
'
```

Finally, put the credentials for that administrator (or another enabled account)
in `OPENBENCH_USERNAME` and `OPENBENCH_PASSWORD`, then start the worker:

```bash
sudo systemctl enable --now openbench-worker
```

The server launcher applies database migrations and collects static files before
starting Gunicorn. By default it listens only on `127.0.0.1:8000`; expose it through
a reverse proxy or private network as appropriate.

## Configuration

The environment file controls hosts, binding, worker credentials, and worker capacity.
Set `OPENBENCH_PUBLIC_HOST` when HTTPS terminates at a reverse proxy; this also enables
secure cookies and trusts that host for CSRF checks.

The renderer defaults to the paths and account used above. Packagers may override
them with `OPENBENCH_SERVICE_USER`, `OPENBENCH_SERVICE_GROUP`,
`OPENBENCH_STATE_DIR`, `OPENBENCH_ENVIRONMENT_FILE`, `OPENBENCH_SOURCE`, and
`OPENBENCH_BASH`.

The launchers normally use `/opt/OpenBench/.venv`. Packagers may additionally
provide `OPENBENCH_PYTHON`, `OPENBENCH_GUNICORN`, `OPENBENCH_SETTINGS_DIR`, and
`OPENBENCH_FASTCHESS` directly in the rendered service or an environment file.

Check the deployment with:

```bash
systemctl status openbench-server openbench-worker openbench-backup.timer
curl --fail http://127.0.0.1:8000/
```

Backups are stored under `/var/lib/openbench/backups`; the newest 14 are retained.
