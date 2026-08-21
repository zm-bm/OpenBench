# Private Workstation Deployment

These files are sanitized references for the private Latrunculi instance, not
an installer. Review paths and resource limits before copying them to a host.
Never place real secrets in this directory.

## Setup

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt -r Client/requirements.txt

mkdir -p ~/.config/openbench ~/.config/systemd/user
cp Deploy/openbench.env.example ~/.config/openbench/openbench.env
chmod 600 ~/.config/openbench/openbench.env
```

Replace every placeholder in the host environment. The worker username and
password must identify an enabled OpenBench account. Then initialize the server:

```bash
set -a
. ~/.config/openbench/openbench.env
set +a
PYTHONPATH="$PWD/Deploy:$PWD" .venv/bin/python manage.py migrate
PYTHONPATH="$PWD/Deploy:$PWD" .venv/bin/python manage.py collectstatic --noinput
PYTHONPATH="$PWD/Deploy:$PWD" .venv/bin/python manage.py createsuperuser
```

Copy the unit files, enable user lingering if needed, and start the services:

```bash
cp Deploy/openbench-*.service Deploy/openbench-backup.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now openbench-server openbench-worker openbench-backup.timer
```

The server uses SQLite and listens on loopback plus `OPENBENCH_BIND`. Keep port
8000 on a trusted private network. Database and PGN backups are written daily
under `~/.local/share/openbench/backups/`.

