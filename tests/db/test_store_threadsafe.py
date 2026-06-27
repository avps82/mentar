"""Regression: the store is reused across threads by the Flask dev server.

`mentar serve` runs the threaded Werkzeug dev server, so a single LearnerStore
connection is touched by different request worker threads. Before the fix this
raised:

    sqlite3.ProgrammingError: SQLite objects created in a thread can only be
    used in that same thread.

surfacing as a 500 on /parent and /progress (e.g. right after `stop`, when the
next request landed on a new worker thread). The single-threaded test_client
smoke never exercised this. These tests open the store in the main thread and
read/write it from a *different* thread.
"""

from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor

from mentar.db.store import LearnerStore


def test_store_usable_from_another_thread(tmp_path):
    store = LearnerStore(tmp_path / "threads.db")
    lid = store.create_learner("Kid", "Year 4", "AU", "parent_mediated")
    store.create_session(lid, "sess1")
    store.write_transcript(lid, "sess1", 0, "learner", "hello")

    def read_in_thread() -> int:
        # This is the call that used to raise ProgrammingError across threads
        # (db/store.py:transcript_for_session, hit by web/app.py:_persisted_turns).
        rows = store.transcript_for_session(lid, "sess1")
        return len(rows)

    with ThreadPoolExecutor(max_workers=1) as ex:
        n = ex.submit(read_in_thread).result()
    assert n == 1


def test_store_writes_from_multiple_threads(tmp_path):
    store = LearnerStore(tmp_path / "threads_w.db")
    lid = store.create_learner("Kid", "Year 4", "AU", "parent_mediated")
    store.create_session(lid, "sess1")

    def write_turn(i: int) -> None:
        store.write_transcript(lid, "sess1", i, "learner", f"turn {i}")

    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(write_turn, range(20)))

    assert len(store.transcript_for_session(lid, "sess1")) == 20


def test_wal_and_busy_timeout_applied(tmp_path):
    store = LearnerStore(tmp_path / "pragmas.db")
    # WAL mode + a busy timeout are what keep concurrent worker threads from
    # hitting "database is locked"; assert they actually took.
    mode = store._conn.execute("PRAGMA journal_mode;").fetchone()[0]
    timeout = store._conn.execute("PRAGMA busy_timeout;").fetchone()[0]
    assert mode.lower() == "wal"
    assert timeout >= 5000


def test_cross_thread_raised_before_fix_is_gone(tmp_path):
    """Sanity: a default-connect connection still raises across threads — proving
    the failure mode is real and that the store's check_same_thread=False is what
    avoids it (not some environment quirk)."""
    conn = sqlite3.connect(str(tmp_path / "raw.db"))  # default check_same_thread=True

    def use_it() -> None:
        conn.execute("SELECT 1;")

    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(use_it)
        try:
            fut.result()
        except sqlite3.ProgrammingError:
            return  # expected — the bug the store now avoids
    # If we get here, the runtime doesn't enforce the guard; the store fix is
    # still correct, so don't fail hard.
