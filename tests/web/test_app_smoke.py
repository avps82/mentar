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
    # Stub the LLM so tests never hit the network (auto-help on a wrong answer
    # would otherwise call the backend and hang on retries).
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    return app_mod, app_mod.app.test_client()


def test_trust_strip_on_child_and_parent_screens():
    """U-11: the offline/no-accounts trust strip is present on both the child-
    facing lesson screen and the parent dashboard."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    c.post("/choose", data={"subject": "fractions"})
    learner_html = c.get("/").get_data(as_text=True)
    parent_html = c.get("/parent").get_data(as_text=True)
    assert "Runs entirely on this device" in learner_html
    assert "Runs entirely on this device" in parent_html


def test_web_learner_flow():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()

    # No subject chosen yet -> the picker is shown.
    r = c.get("/")
    assert r.status_code == 200
    assert "Choose a topic" in r.get_data(as_text=True) or "learn today" in r.get_data(as_text=True)

    # Choose a subject, then a question is presented.
    c.post("/choose", data={"subject": "fractions"})
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
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    c.post("/answer", data={"answer": "4"})

    db = sqlite3.connect(dbp)
    assert db.execute("SELECT count(*) FROM transcript").fetchone()[0] > 0  # write path
    db.close()

    # /parent renders (DB-backed) without error, with the score header + per-answer table.
    parent_html = c.get("/parent").get_data(as_text=True)
    assert "correct out of" in parent_html          # session score (note 3)
    assert "Answers" in parent_html                 # per-answer correct/wrong/help table

    # Trigger an escalation; it logs un-acknowledged, and the CHILD's browser
    # (the redirect target of /answer) goes to /frozen, not /parent (A8).
    r = c.post("/answer", data={"answer": "I want to die"}, follow_redirects=True)
    frozen_html = r.get_data(as_text=True)
    assert "I want to die" not in frozen_html        # no verbatim trigger text
    assert "confirm" not in frozen_html.lower()       # no ack control on the child's screen
    assert "<a " not in frozen_html                  # U-60: zero navigation on the frozen screen
    assert "theme-toggle" not in frozen_html          # U-60: zero chrome, not just zero nav

    # Re-visiting / while still frozen (not just the triggering turn) also
    # lands on /frozen, never on the last tutoring question or /parent.
    r2 = c.get("/", follow_redirects=True)
    r2_html = r2.get_data(as_text=True)
    assert "I want to die" not in r2_html
    assert "confirm" not in r2_html.lower()

    db = sqlite3.connect(dbp)
    row = db.execute(
        "SELECT id, parent_ack_at, session_outcome FROM escalation_log"
    ).fetchone()
    db.close()
    assert row is not None, "escalation not logged"
    assert row[1] is None, "ack should be unset before the parent acks"

    # Wrong/missing confirm word is a no-op — no ack persisted.
    c.post("/parent/ack", data={"action": "end", "confirm": "nope"})
    db = sqlite3.connect(dbp)
    ack_at = db.execute("SELECT parent_ack_at FROM escalation_log").fetchone()[0]
    db.close()
    assert ack_at is None, "ack must not persist without the correct confirm word"

    # Parent acknowledges via the parent view, typing the confirm word.
    c.post("/parent/ack", data={"action": "end", "confirm": "RESUME"})
    db = sqlite3.connect(dbp)
    ack_at, outcome = db.execute(
        "SELECT parent_ack_at, session_outcome FROM escalation_log"
    ).fetchone()
    db.close()
    assert ack_at is not None, "parent_ack_at not persisted"
    assert outcome == "acknowledged", f"session_outcome={outcome!r}"


def test_learner_id_survives_server_restart():
    """A6: the flask-session cookie survives a server restart, but the in-memory
    _db_learner_ids map does not. Before the fix, every restart silently created
    a NEW learner_profile row (mastery/history reset). Simulate a restart by
    reloading mentar.web.app (fresh in-memory dicts) against the SAME db path
    and the SAME session cookie, and assert the learner id + mastery persist."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import sqlite3

    app_mod, c1 = _client()
    dbp = os.environ["MENTAR_DB_PATH"]  # fixed for both "processes" below

    c1.post("/choose", data={"subject": "fractions"})
    c1.get("/")
    c1.post("/answer", data={"answer": "4"})  # persists a learner + skill_state row

    db = sqlite3.connect(dbp)
    assert db.execute("SELECT count(*) FROM learner_profile").fetchone()[0] == 1
    learner_id_before = db.execute("SELECT id FROM learner_profile").fetchone()[0]
    db.close()

    # Grab the session cookie to carry over to the "restarted" process.
    session_cookie = c1.get_cookie("session")
    assert session_cookie is not None

    # Simulate a restart: reload the module (fresh _db_learner_ids/_stores/
    # _controllers) but keep MENTAR_DB_PATH unchanged (same on-disk DB file).
    import importlib
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    c2 = app_mod.app.test_client()
    c2.set_cookie(domain="localhost", key="session", value=session_cookie.value)

    c2.post("/choose", data={"subject": "fractions"})
    c2.get("/")
    c2.post("/answer", data={"answer": "4"})

    db = sqlite3.connect(dbp)
    n_learners = db.execute("SELECT count(*) FROM learner_profile").fetchone()[0]
    learner_id_after = db.execute("SELECT id FROM learner_profile").fetchone()[0]
    n_responses = db.execute("SELECT count(*) FROM response_log").fetchone()[0]
    db.close()

    assert n_learners == 1, f"restart must reuse the learner row, not create a new one (got {n_learners})"
    assert learner_id_after == learner_id_before
    assert n_responses >= 2, "both pre- and post-restart answers should be under the same learner"


def test_answer_hx_request_returns_question_fragment():
    """U-90 plumbing: htmx (vendored static/htmx.min.js) sends HX-Request: true
    to get a bare HTML fragment swapped into hx-target=".question" (no page
    reload). Header absent = unchanged full-redirect behaviour (covered by
    test_web_learner_flow)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")

    r = c.post(
        "/answer",
        data={"answer": "4"},
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert "HX-Redirect" not in r.headers
    text = r.get_data(as_text=True)
    assert text.strip()  # a fragment, not a redirect/empty body


def test_answer_hx_fragment_escapes_html():
    """U-32: the htmx-swapped fragment must escape model/generator text in BOTH
    the message and the question areas -- htmx swaps via innerHTML, so unescaped
    HTML here would be a live XSS path into the child's browser."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    from mentar.dialogue.controller import TurnResult

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl._ctx.question_display = "<script>alert(1)</script>"
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="x", done=False, escalated=False,
        message="<script>alert(2)</script>", question=None,
    )

    r = c.post(
        "/answer",
        data={"answer": "4"},
        headers={"HX-Request": "true"},
    )
    body = r.get_data(as_text=True)
    assert "<script>alert" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body   # question area
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in body   # message area


def test_structured_turn_renders_message_and_question_separately():
    """The proper U-31 fix (maintainer review 2026-07-10): message and question
    come STRUCTURED from TurnResult.message/.question + ctrl.question_display —
    never string-split from prose. The old rfind-split misfired on the Help
    flow's "Q) {question}" recap (feedback box showed a bare "Q)", explanation
    landed in the question block)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    from mentar.dialogue.controller import TurnResult

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]

    # A Help-shaped turn: explanation prose + the SAME question still live.
    ctrl._ctx.question_display = "What is 1/2 of 8? (answer with a number)"
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="ignored-compat-field", done=False, escalated=False,
        message="Half means sharing into 2 equal parts.\n\nNow you try it! ✏️",
        question="What is 1/2 of 8? (answer with a number)",
    )
    frag = c.post("/answer", data={"answer": "help"},
                  headers={"HX-Request": "true"}).get_data(as_text=True)

    fb_div = frag.split('<div class="feedback')[1].split("</div>")[0]
    q_text = frag.split('<div class="question-text">')[1].split("</div>")[0]
    assert "Half means sharing" in fb_div            # explanation in the message area
    assert "What is 1/2 of 8?" not in fb_div         # question NOT duplicated into it
    assert "What is 1/2 of 8?" in q_text             # question in its own block
    assert "Half means sharing" not in q_text

    # Full-page GET / agrees with the fragment (same structured source).
    html = c.get("/").get_data(as_text=True)
    assert "Half means sharing" in html.split('<div class="feedback')[1].split("</div>")[0]
    assert "What is 1/2 of 8?" in html.split('<div class="question-text">')[1].split("</div>")[0]


def test_mc4_choices_render_as_radio_buttons():
    """mc4 items with structured choices render a native radio group (A-D),
    no JS required; fraction answers render numerator/denominator inputs that
    /answer composes server-side into the "n/d" the verifier accepts."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "science"})   # science = mc4 generators
    html = c.get("/").get_data(as_text=True)
    assert 'type="radio"' in html
    assert 'name="answer" value="A"' in html
    assert 'value="D"' in html
    assert "choice-option" in html

    # Answering via the radio value (a bare letter) works end-to-end.
    r = c.post("/answer", data={"answer": "A"})
    assert r.status_code in (200, 302)

    # Fraction widget path: unit_fractions is a fraction-answer node. Force it
    # via a fresh fractions session and check the current answer_type drives
    # the widget when it's a fraction question.
    c2 = app_mod.app.test_client()
    c2.post("/choose", data={"subject": "fractions"})
    body = c2.get("/").get_data(as_text=True)
    with c2.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    if ctrl.current_answer_type == "fraction":
        assert 'name="answer_num"' in body and 'name="answer_den"' in body
    else:
        assert 'name="answer"' in body  # int/free-text fall back to the text input


def test_mc4_question_box_shows_stem_only_not_options_thrice():
    """R2.1: an mc4 question used to render its options THREE times (inline
    "A) ... B) ..." text, the "(answer with a letter...)" format hint, AND the
    radios) -- and TTS read them twice. The question box must now show only
    the stem; the options appear exactly once, as radios."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "science"})
    html = c.get("/").get_data(as_text=True)
    q_text = html.split('<div class="question-text">')[1].split("</div>")[0]

    assert "A)" not in q_text and "B)" not in q_text
    assert "answer with a letter" not in q_text.lower()
    assert html.count('type="radio"') == 4  # options appear exactly once, as radios

    # The full inline "A) ..." form still exists for surfaces without radios
    # (CLI/transcript) -- composed centrally, not lost.
    c.post("/answer", data={"answer": "A"})
    parent_html = c.get("/parent").get_data(as_text=True)
    assert "A)" in parent_html and "Answer with the letter" in parent_html


def test_fraction_inputs_compose_server_side():
    """POST /answer with answer_num/answer_den (and no answer field) composes
    "n/d" server-side -- verified through the real controller scoring path."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]

    captured = {}
    real_step = ctrl.step
    def capturing_step(answer_text):
        captured["answer"] = answer_text
        return real_step(answer_text)
    ctrl.step = capturing_step

    c.post("/answer", data={"answer_num": "3", "answer_den": "4"})
    assert captured["answer"] == "3/4"


def test_markdown_lite_renders_bold_italic_and_bullets():
    """U-32: the owned markdown-lite subset actually renders bold/italic/
    bullets (not just escapes) -- and stays safe on a mixed malicious+markdown
    input. Checked directly against _render_markdown_lite, and once through
    the live /answer fragment path for the wiring."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()

    md = app_mod._render_markdown_lite
    assert md("**Great job!**") == "<strong>Great job!</strong>"
    assert md("Try *this* next") == "Try <em>this</em> next"
    assert md("* first\n* second") == "<ul><li>first</li><li>second</li></ul>"
    # Bold consumed before italic: no stray single-star <em> inside a **bold** span.
    assert md("**bold**") == "<strong>bold</strong>"
    # Escaping still wins over markdown syntax embedded in unsafe input.
    mixed = md("**<script>alert(1)</script>**")
    assert "<script>" not in mixed
    assert mixed == "<strong>&lt;script&gt;alert(1)&lt;/script&gt;</strong>"

    from mentar.dialogue.controller import TurnResult

    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="x", done=False, escalated=False,
        message="**Nice work!**\n* Step one\n* Step two", question=None,
    )
    r = c.post("/answer", data={"answer": "4"}, headers={"HX-Request": "true"})
    body = r.get_data(as_text=True)
    assert "<strong>Nice work!</strong>" in body
    assert "<li>Step one</li>" in body


def test_answer_hx_request_on_escalation_sends_hx_redirect():
    """Escalated htmx turns get an HX-Redirect to /frozen (empty body), never
    the verbatim trigger text anywhere in the response (mirrors A8)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")

    r = c.post(
        "/answer",
        data={"answer": "I want to die"},
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert r.headers.get("HX-Redirect") == "/frozen"
    assert "die" not in r.get_data(as_text=True)


def test_done_route_shows_final_message_and_is_directly_navigable():
    """U-90: completion now goes through a real GET /done route (htmx's
    HX-Redirect needs a URL to target) instead of being inline-rendered from
    the POST /answer body. /done must show the session's real final message
    and survive a plain re-GET (e.g. a refresh)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")

    # Force a done outcome without depending on real lesson-completion length:
    # stub the controller's step() to return a done TurnResult directly.
    from mentar.dialogue.controller import TurnResult

    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="Great work today — session complete!", done=True, escalated=False
    )

    r = c.post("/answer", data={"answer": "4"})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/done")

    r2 = c.get("/done")
    assert "Great work today" in r2.get_data(as_text=True)
    # Re-GET (refresh) still shows the same message, not a generic fallback.
    r3 = c.get("/done")
    assert "Great work today" in r3.get_data(as_text=True)


def test_done_recap_shows_questions_and_skills():
    """U-70: the done screen's recap reflects the session's real responses
    (question count, skills touched), sourced the same way /parent already
    reads them -- no new store methods, no controller change."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    from mentar.dialogue.controller import TurnResult

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    c.post("/answer", data={"answer": "4"})  # a real scored response first

    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="All done!", done=True, escalated=False
    )
    c.post("/answer", data={"answer": "4"})

    body = c.get("/done").get_data(as_text=True)
    assert "correct out of" in body
    assert "See my progress map" in body


def test_parent_view_shows_degraded_banner_when_fallback_log_present():
    """A15: /parent shows a warning banner when escalation_fallback.log has
    content (a prior escalation failed to persist to the DB) — and not otherwise."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    dbp = os.environ["MENTAR_DB_PATH"]

    c.post("/choose", data={"subject": "fractions"})
    c.get("/")

    # No fallback file yet -> no banner.
    assert "Durable logging degraded" not in c.get("/parent").get_data(as_text=True)

    fallback = pathlib.Path(dbp).parent / "escalation_fallback.log"
    fallback.write_text('{"iso_ts": "t", "trigger_class": "harm_to_self", '
                         '"severity": "critical", "verbatim_text": "x"}\n')

    assert "Durable logging degraded" in c.get("/parent").get_data(as_text=True)


if __name__ == "__main__":
    test_trust_strip_on_child_and_parent_screens()
    print("  ✓ test_trust_strip_on_child_and_parent_screens")
    test_web_learner_flow()
    print("  ✓ test_web_learner_flow")
    test_parent_view_reads_db_and_persists_ack()
    print("  ✓ test_parent_view_reads_db_and_persists_ack")
    test_answer_hx_request_returns_question_fragment()
    print("  ✓ test_answer_hx_request_returns_question_fragment")
    test_answer_hx_fragment_escapes_html()
    print("  ✓ test_answer_hx_fragment_escapes_html")
    test_markdown_lite_renders_bold_italic_and_bullets()
    print("  ✓ test_markdown_lite_renders_bold_italic_and_bullets")
    test_structured_turn_renders_message_and_question_separately()
    print("  ✓ test_structured_turn_renders_message_and_question_separately")
    test_mc4_choices_render_as_radio_buttons()
    print("  ✓ test_mc4_choices_render_as_radio_buttons")
    test_fraction_inputs_compose_server_side()
    print("  ✓ test_fraction_inputs_compose_server_side")
    test_answer_hx_request_on_escalation_sends_hx_redirect()
    print("  ✓ test_answer_hx_request_on_escalation_sends_hx_redirect")
    test_done_route_shows_final_message_and_is_directly_navigable()
    print("  ✓ test_done_route_shows_final_message_and_is_directly_navigable")
    test_done_recap_shows_questions_and_skills()
    print("  ✓ test_done_recap_shows_questions_and_skills")
    test_parent_view_shows_degraded_banner_when_fallback_log_present()
    print("  ✓ test_parent_view_shows_degraded_banner_when_fallback_log_present")
    test_learner_id_survives_server_restart()
    print("  ✓ test_learner_id_survives_server_restart")
