"""Create and retain local OpenBench SQLite and media backups."""

import hashlib
import os
import sqlite3
import tarfile
from datetime import datetime, timezone
from pathlib import Path


os.umask(0o077)
root = Path(os.environ.get("OPENBENCH_STATE_DIR", "/var/lib/openbench"))
dest = Path(os.environ.get("OPENBENCH_BACKUP_DIR", root / "backups"))
dest.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
database_copy = dest / f"{stamp}.sqlite3"
archive = dest / f"openbench-{stamp}.tar.gz"

try:
    with sqlite3.connect(f"file:{root}/db.sqlite3?mode=ro", uri=True) as source:
        with sqlite3.connect(database_copy) as copy:
            source.backup(copy)
            if copy.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Database integrity check failed")

    with tarfile.open(archive, "w:gz") as output:
        output.add(database_copy, arcname="db.sqlite3")
        if (root / "Media").exists():
            output.add(root / "Media", arcname="Media")

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".gz.sha256").write_text(
        f"{digest}  {archive.name}\n", encoding="ascii"
    )

    for expired in sorted(dest.glob("openbench-*.tar.gz"))[:-14]:
        expired.unlink()
        expired.with_suffix(".gz.sha256").unlink(missing_ok=True)

    print(archive)
finally:
    database_copy.unlink(missing_ok=True)
