"""Back up the SQLite database and retained server PGNs."""

import hashlib
import os
import sqlite3
import tarfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(
    os.environ.get("OPENBENCH_ROOT", Path.home() / "code/tools/OpenBench")
).expanduser()
BACKUP_DIR = Path(
    os.environ.get(
        "OPENBENCH_BACKUP_DIR", Path.home() / ".local/share/openbench/backups"
    )
).expanduser()
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
database_copy = BACKUP_DIR / f"openbench-{stamp}.sqlite3"
archive = BACKUP_DIR / f"openbench-{stamp}.tar.gz"

os.umask(0o077)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(ROOT / "db.sqlite3") as source:
    with sqlite3.connect(database_copy) as destination:
        source.backup(destination)

with tarfile.open(archive, "w:gz") as output:
    output.add(database_copy, arcname="db.sqlite3")
    pgn_dir = ROOT / "Media/PGNs"
    if pgn_dir.exists():
        output.add(pgn_dir, arcname="Media/PGNs")

database_copy.unlink()
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix(archive.suffix + ".sha256").write_text(
    f"{digest}  {archive.name}\n", encoding="ascii"
)
print(archive)

