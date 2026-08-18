"""No file holding child data can be staged by an ordinary `git add -A`.

The learner DB holds verbatim transcripts and escalation disclosures. `.gitignore`
covers `*.db` — but SQLite's sidecars and this CLI's own backups do NOT end in
`.db`, so none of them matched:

  * `<db>-wal` / `<db>-shm` — the DB runs in WAL mode (store.py sets
    `journal_mode = WAL`), so this pair exists on disk the whole time the app is
    running. A `git add -A` from a second terminal during a lesson would stage
    recent writes.
  * `<db>.backup-<UTC timestamp>` — the DEFAULT destination of `mentar backup`.
    Running it from the repo root (its default `--db` is a bare relative path,
    so that is the normal case) left an untracked, unignored copy of the whole
    learner DB in the repo. Found 2026-08-18 by running the command.

Mentar is private today and planned to go public, which makes an accidentally
committed learner DB unrecoverable in the way that matters — history is public
even after a later delete.

`.gitignore` twice before shipped a pattern that was wrong in the OTHER direction
(over-broad, silently excluding tracked source), so this also pins that real
source files stay stageable.

    python3 -m pytest tests/test_gitignore_child_data.py
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

MUST_BE_IGNORED = [
    "mentar_pilot.db",
    "mentar_pilot.db-wal",
    "mentar_pilot.db-shm",
    "mentar_pilot.db.backup-20260818T004521Z",
    "data.sqlite",
    "data.sqlite-wal",
    "data.sqlite-shm",
    "subdir/learner.db-wal",
]

# The other direction: a pattern broad enough to catch the above must not start
# swallowing tracked files. Both of these are real tracked paths.
MUST_NOT_BE_IGNORED = [
    "src/mentar/db/store.py",
    "tests/test_gitignore_child_data.py",
]


def _is_ignored(path: str) -> bool:
    """git's own verdict — asserting on the real tool, not on a re-implementation
    of its matching rules, which is where a hand-rolled check would drift."""
    return subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", path],
        cwd=REPO_ROOT, capture_output=True,
    ).returncode == 0


@pytest.mark.parametrize("path", MUST_BE_IGNORED)
def test_child_data_files_are_ignored(path):
    assert _is_ignored(path), (
        f"{path} is NOT gitignored — it holds child transcript data and one "
        f"`git add -A` would stage it into a repo intended to go public"
    )


@pytest.mark.parametrize("path", MUST_NOT_BE_IGNORED)
def test_tracked_source_is_still_stageable(path):
    assert (REPO_ROOT / path).exists(), f"precondition: {path} should exist"
    assert not _is_ignored(path), (
        f"{path} is a tracked source file but .gitignore now excludes it — a new "
        f"file added beside it would silently refuse to stage"
    )
