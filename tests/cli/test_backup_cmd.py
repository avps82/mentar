"""D6 — `mentar backup`: checkpoint + copy + verify the DB file.

Real DB file I/O (no mocking of LearnerStore/sqlite3) -- this command's whole
point is a genuine on-disk copy, so the tests exercise the real thing.

Inline smoke runner:
    python3 tests/cli/test_backup_cmd.py
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
import tempfile
import uuid
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import mentar.cli.__main__ as CLI  # noqa: E402
from mentar.db.store import LearnerStore  # noqa: E402


def _seeded_db(tmp_path: pathlib.Path) -> pathlib.Path:
    db_path = tmp_path / "seed.db"
    store = LearnerStore(str(db_path))
    learner_id = store.create_learner(
        name="test-learner", year_level="pilot", country="GB", age_mode="parent_mediated",
    )
    store.create_session(learner_id, str(uuid.uuid4()))
    store.close()
    return db_path


def test_backup_missing_source_fails():
    with tempfile.TemporaryDirectory() as td:
        args = SimpleNamespace(db=str(pathlib.Path(td) / "nope.db"), dest=None)
        assert CLI._backup(args) == 1


def test_backup_copies_and_verifies():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = pathlib.Path(td)
        db_path = _seeded_db(tmp_path)
        dest = tmp_path / "out.db"
        args = SimpleNamespace(db=str(db_path), dest=str(dest))

        assert CLI._backup(args) == 0
        assert dest.exists()

        conn = sqlite3.connect(str(dest))
        assert conn.execute("PRAGMA integrity_check").fetchone()[0].lower() == "ok"
        assert conn.execute("SELECT count(*) FROM session").fetchone()[0] == 1
        conn.close()


def test_backup_default_dest_name_and_refuses_overwrite():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = pathlib.Path(td)
        db_path = _seeded_db(tmp_path)
        args = SimpleNamespace(db=str(db_path), dest=None)

        assert CLI._backup(args) == 0
        backups = list(tmp_path.glob("seed.db.backup-*"))
        assert len(backups) == 1

        # A second run with the SAME explicit dest must refuse, not overwrite.
        args2 = SimpleNamespace(db=str(db_path), dest=str(backups[0]))
        assert CLI._backup(args2) == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} backup-cmd tests passed.")
