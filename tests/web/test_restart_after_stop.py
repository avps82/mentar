"""Ending a session must be undoable — /restart (2026-08-15, maintainer-reported).

    "When stopped... I can see progress but can't start again."

The Done page's "Start again" pointed at /learn. But Stop leaves the finished
controller CACHED, and /learn redirects any terminal session to /done — so the
button looped onto its own page. The only accidental escape was choosing a
DIFFERENT subject, the one case that discards the controller; choosing the same
one kept the dead session forever.

These tests drive the real routes, because the loop is a property of how the
routes hand off to each other and would be invisible in any single one of them.
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))


def _skip_if_no_flask():
    pytest.importorskip("flask")


def _client():
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "restart.db")
    # isolation: the root conftest already points MENTAR_PACK_STATE at a
    # scratch path. Popping it did the OPPOSITE -- see conftest.py.
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    app_mod._SETUP_GATE_BYPASS = True
    return app_mod, app_mod.app.test_client()


def _start_a_lesson(app_mod, c):
    subject = next(iter(app_mod.SUBJECTS))
    c.post("/choose", data={"subject": subject})
    assert c.get("/learn").status_code == 200
    return subject


def test_stop_then_start_again_actually_starts_again():
    """The reported bug, end to end."""
    _skip_if_no_flask()
    app_mod, c = _client()
    _start_a_lesson(app_mod, c)

    c.post("/answer", data={"answer": "stop"})
    # /learn now bounces to /done -- that part is correct and stays.
    assert c.get("/learn").headers["Location"].endswith("/done")

    r = c.post("/restart")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/learn"), "restart must send them to a lesson"
    # ...and the lesson must actually RENDER, not bounce back to /done again.
    again = c.get("/learn")
    assert again.status_code == 200, "the whole point: a live lesson, not another redirect"


def test_the_done_page_offers_a_way_out_that_is_not_a_loop():
    _skip_if_no_flask()
    app_mod, c = _client()
    _start_a_lesson(app_mod, c)
    c.post("/answer", data={"answer": "stop"})

    body = c.get("/done").get_data(as_text=True)
    assert 'action="/restart"' in body, "Start again must POST /restart, not link to /learn"
    assert 'href="/"' in body, "and a way to pick a different topic"


def test_restart_does_not_release_an_escalation_freeze():
    """A freeze is the parent's to clear (SAFETY §3.3). If /restart cleared it, the
    child would have a one-click escape from the exact state that exists to stop
    them carrying on alone -- the most dangerous possible reading of "start again"."""
    _skip_if_no_flask()
    app_mod, c = _client()
    _start_a_lesson(app_mod, c)

    c.post("/answer", data={"answer": "someone at home hits me"})
    learner = next(iter(app_mod._controllers))
    ctrl = app_mod._controllers[learner]
    assert ctrl.state == app_mod.FSMState.ESCALATION_FREEZE.value, "test needs a real freeze"

    r = c.post("/restart")
    assert r.headers["Location"].endswith("/frozen"), "must not restart out of a freeze"
    assert app_mod._controllers.get(learner) is ctrl, "the frozen controller must survive"
    assert ctrl.state == app_mod.FSMState.ESCALATION_FREEZE.value


def test_restart_without_a_session_goes_to_the_picker():
    _skip_if_no_flask()
    _app_mod, c = _client()
    r = c.post("/restart")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")


def test_progress_page_offers_the_picker_not_only_a_dead_lesson_link():
    """Progress is where a child lands after stopping, so its only exit must not be
    the link that bounces them back to /done."""
    _skip_if_no_flask()
    app_mod, c = _client()
    _start_a_lesson(app_mod, c)
    c.post("/answer", data={"answer": "stop"})
    body = c.get("/progress").get_data(as_text=True)
    assert 'href="/"' in body


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
