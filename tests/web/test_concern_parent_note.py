"""CONCERN tier through the real web path: parent sees the note, child sees nothing.

    python3 -m pytest tests/web/test_concern_parent_note.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "web"))

from test_progress import _client

H = {"HX-Request": "true"}
CONCERN_TEXT = "i'm scared to go home"


def test_concern_reaches_the_parent_page_and_never_the_child():
    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")

    r = c.post("/answer", data={"answer": CONCERN_TEXT}, headers=H)
    child_view = r.get_data(as_text=True)

    # The child's page is a NORMAL turn: no freeze redirect, no handoff wording.
    assert r.status_code == 200
    assert "grown-up" not in child_view.lower()
    assert c.get("/learn").status_code == 200, "lesson must continue, not freeze"

    # The parent page carries the note, verbatim, labelled as a conversation
    # prompt rather than a paused-lesson alert.
    parent = c.get("/parent").get_data(as_text=True)
    # Jinja escapes the apostrophe (&#39;), so assert on the escape-free part.
    assert "scared to go home" in parent
    assert "worth a conversation" in parent


def test_second_concern_freezes_through_the_web_path():
    app_mod, c = _client()
    from mentar.dialogue.controller import FSMState
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    c.post("/answer", data={"answer": CONCERN_TEXT}, headers=H)
    c.post("/answer", data={"answer": "i havent eaten in two days"}, headers=H)
    with c.session_transaction() as s:
        uuid = s["learner_uuid"]
    assert app_mod._controllers[uuid].state == FSMState.ESCALATION_FREEZE.value
