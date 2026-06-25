"""Web app smoke test — full route + controller + DB cycle via Flask test_client.

Drives the learner flow without a live LLM: the item-bank path presents/scores deterministic
questions, so GET / and POST /answer exercise routes -> controller -> verifier -> DB with no
network. (The LLM-backed Help path is covered by the inference/backend + dialogue tests.)

Skips if Flask isn't installed (it's the optional `web` extra).

Inline smoke runner:
    python3 tests/web/test_app_smoke.py
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _client():
    # DB path is read at import time, so set it before importing the app.
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "web_smoke.db")
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    return app_mod, app_mod.app.test_client()


def test_web_learner_flow():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()

    r = c.get("/")
    assert r.status_code == 200
    assert len(r.get_data(as_text=True)) > 100          # a question rendered

    r = c.post("/answer", data={"answer": "4"})
    assert r.status_code in (200, 302)                   # advanced (redirect or done page)

    assert c.get("/").status_code == 200
    assert c.get("/parent").status_code == 200           # parent view renders

    import sqlite3
    db = sqlite3.connect(os.environ["MENTAR_DB_PATH"])
    assert db.execute("SELECT count(*) FROM learner_profile").fetchone()[0] == 1
    # an answer was scored and persisted through the web path
    assert db.execute("SELECT count(*) FROM skill_state").fetchone()[0] >= 1


def test_parent_view_reads_db_and_persists_ack():
    """A1: /parent renders the durable DB transcript; /parent/ack persists the
    parent's acknowledgement to escalation_log (SAFETY.md §3.3 Step 6)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import sqlite3

    app_mod, c = _client()  # noqa: F841
    dbp = os.environ["MENTAR_DB_PATH"]

    # A normal turn so the transcript + a scored response persist to the DB.
    c.get("/")
    c.post("/answer", data={"answer": "4"})

    db = sqlite3.connect(dbp)
    assert db.execute("SELECT count(*) FROM transcript").fetchone()[0] > 0  # write path
    db.close()

    # /parent renders (DB-backed) without error.
    assert c.get("/parent").status_code == 200

    # Trigger an escalation; it logs un-acknowledged.
    c.post("/answer", data={"answer": "I want to die"})
    db = sqlite3.connect(dbp)
    row = db.execute(
        "SELECT id, parent_ack_at, session_outcome FROM escalation_log"
    ).fetchone()
    db.close()
    assert row is not None, "escalation not logged"
    assert row[1] is None, "ack should be unset before the parent acks"

    # Parent acknowledges via the parent view.
    c.post("/parent/ack", data={"action": "end"})
    db = sqlite3.connect(dbp)
    ack_at, outcome = db.execute(
        "SELECT parent_ack_at, session_outcome FROM escalation_log"
    ).fetchone()
    db.close()
    assert ack_at is not None, "parent_ack_at not persisted"
    assert outcome == "acknowledged", f"session_outcome={outcome!r}"


if __name__ == "__main__":
    test_web_learner_flow()
    print("  ✓ test_web_learner_flow")
    test_parent_view_reads_db_and_persists_ack()
    print("  ✓ test_parent_view_reads_db_and_persists_ack")
