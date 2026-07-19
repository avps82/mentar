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
    os.environ.pop("MENTAR_PACK_STATE", None)  # isolation: don't inherit a toggle test's state file
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    # Stub the LLM so tests never hit the network (auto-help on a wrong answer
    # would otherwise call the backend and hang on retries).
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    # R9: bypass the setup gate -- these tests aren't testing setup/first-run,
    # and a live reachability probe per test would be slow/flaky/network-bound.
    app_mod._SETUP_GATE_BYPASS = True
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
    learner_html = c.get("/learn").get_data(as_text=True)
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
    r = c.get("/learn")
    assert r.status_code == 200
    assert len(r.get_data(as_text=True)) > 100          # a question rendered

    r = c.post("/answer", data={"answer": "4"})
    assert r.status_code in (200, 302)                   # advanced (redirect or done page)

    assert c.get("/learn").status_code == 200
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
    c.get("/learn")
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

    # R4: / is picker-only, unconditionally -- re-visiting it while frozen
    # never leaks the trigger text or an ack control either.
    r2 = c.get("/")
    r2_html = r2.get_data(as_text=True)
    assert "I want to die" not in r2_html
    assert "confirm" not in r2_html.lower()

    # /learn (the actual former quiz route) still lands on /frozen while
    # still frozen (not just the triggering turn), never on the last
    # tutoring question or /parent.
    r3 = c.get("/learn", follow_redirects=True)
    r3_html = r3.get_data(as_text=True)
    assert "I want to die" not in r3_html
    assert "confirm" not in r3_html.lower()

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
    c1.get("/learn")
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
    app_mod._SETUP_GATE_BYPASS = True  # R9: reload resets this too -- not testing setup here
    c2 = app_mod.app.test_client()
    c2.set_cookie(domain="localhost", key="session", value=session_cookie.value)

    c2.post("/choose", data={"subject": "fractions"})
    c2.get("/learn")
    c2.post("/answer", data={"answer": "4"})

    db = sqlite3.connect(dbp)
    n_learners = db.execute("SELECT count(*) FROM learner_profile").fetchone()[0]
    learner_id_after = db.execute("SELECT id FROM learner_profile").fetchone()[0]
    n_responses = db.execute("SELECT count(*) FROM response_log").fetchone()[0]
    db.close()

    assert n_learners == 1, f"restart must reuse the learner row, not create a new one (got {n_learners})"
    assert learner_id_after == learner_id_before
    assert n_responses >= 2, "both pre- and post-restart answers should be under the same learner"


def test_session_resumes_same_topic_after_server_restart():
    """R-RES: a server-process restart (simulated via module reload, same pattern
    as A6's test above) must resume onto the SAME topic the child was on, with
    the session counters carried over -- not silently reset to a fresh session
    (the 'start from the last session end midway' gap, 2026-07-19 feedback)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import sqlite3

    app_mod, c1 = _client()
    dbp = os.environ["MENTAR_DB_PATH"]

    c1.post("/choose", data={"subject": "fractions"})
    c1.get("/learn")
    with c1.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl_before = app_mod._controllers[learner_uuid]
    node_before = ctrl_before.current_node_id
    session_id_before = ctrl_before.session_id
    assert node_before is not None

    session_cookie = c1.get_cookie("session")
    assert session_cookie is not None

    # Simulate a restart: reload the module (fresh _controllers/_stores/etc.) but
    # keep MENTAR_DB_PATH unchanged -- the checkpoint the first controller wrote
    # on its step(None) above is the only thing carrying context across the "gap".
    import importlib
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    app_mod._SETUP_GATE_BYPASS = True
    c2 = app_mod.app.test_client()
    c2.set_cookie(domain="localhost", key="session", value=session_cookie.value)

    c2.post("/choose", data={"subject": "fractions"})
    c2.get("/learn")
    with c2.session_transaction() as sess:
        learner_uuid2 = sess["learner_uuid"]
    ctrl_after = app_mod._controllers[learner_uuid2]

    assert ctrl_after.current_node_id == node_before, (
        "resume must land on the SAME topic, not wherever fresh NODE_SELECT would go"
    )
    assert ctrl_after.session_id == session_id_before, (
        "resume must reuse the original session_id so logging keeps accumulating under it"
    )

    db = sqlite3.connect(dbp)
    n_sessions = db.execute("SELECT count(*) FROM session").fetchone()[0]
    db.close()
    assert n_sessions == 1, "resume must NOT create a second session row"


def test_frozen_session_resumes_frozen_after_server_restart():
    """R-RES hard safety constraint: a session frozen when the process stopped
    must resume frozen -- never silently unfrozen by a restart."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c1 = _client()
    c1.post("/choose", data={"subject": "fractions"})
    c1.get("/learn")
    r = c1.post("/answer", data={"answer": "I want to die"}, headers={"HX-Request": "true"})
    assert r.headers.get("HX-Redirect") == "/frozen"

    session_cookie = c1.get_cookie("session")
    assert session_cookie is not None

    import importlib
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"
    app_mod._SETUP_GATE_BYPASS = True
    c2 = app_mod.app.test_client()
    c2.set_cookie(domain="localhost", key="session", value=session_cookie.value)

    # Reopening the SAME subject after the "restart" must land back on /frozen,
    # not a fresh, unfrozen question.
    c2.post("/choose", data={"subject": "fractions"})
    r3 = c2.get("/learn", follow_redirects=False)
    assert r3.status_code in (301, 302, 303, 307, 308)
    assert r3.headers.get("Location", "").endswith("/frozen")


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
    c.get("/learn")

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
    c.get("/learn")
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
    c.get("/learn")
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
    html = c.get("/learn").get_data(as_text=True)
    assert "Half means sharing" in html.split('<div class="feedback')[1].split("</div>")[0]
    assert "What is 1/2 of 8?" in html.split('<div class="question-text">')[1].split("</div>")[0]


def test_feedback_block_has_read_aloud_button():
    """R12.1 (maintainer feedback 2026-07-18, confirmed bug): explanations were
    not read-aloud-able — the 🔊 tts-btn existed only on the question block.
    The feedback block must now carry its own tts-btn + a .feedback-text wrapper
    (tts.js reads the clicked block's text)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    from mentar.dialogue.controller import TurnResult

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]

    ctrl._ctx.question_display = "What is 1/2 of 8? (answer with a number)"
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="x", done=False, escalated=False,
        message="Half means sharing into 2 equal parts.",
        question="What is 1/2 of 8? (answer with a number)",
    )
    frag = c.post("/answer", data={"answer": "help"},
                  headers={"HX-Request": "true"}).get_data(as_text=True)

    fb_block = frag.split('<div class="feedback')[1].split('<div class="question')[0]
    assert 'class="tts-btn"' in fb_block                 # the explanation's own 🔊
    assert 'class="msg-text"' in fb_block                # tts.js reads this wrapper
    # The question block keeps its own button too (two independent buttons).
    q_block = frag.split('<div class="question"')[1].split("</div>")[0]
    assert 'class="tts-btn"' in q_block

    # A message-less turn renders NO feedback block at all (unchanged).
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="x", done=False, escalated=False,
        message="", question="What is 1/2 of 8? (answer with a number)",
    )
    frag2 = c.post("/answer", data={"answer": "4"},
                   headers={"HX-Request": "true"}).get_data(as_text=True)
    assert '<div class="feedback' not in frag2


def test_mastery_bar_lives_inside_swap_fragment():
    """R12-fix2 (2026-07-19 hands-on): the per-topic mastery bar used to sit
    OUTSIDE #turn-area, so htmx turns never refreshed it — with R11's
    interleaving switching topics per question, the bar showed the wrong topic
    + a frozen % against every new question. It must render inside the /answer
    fragment (and carry the session-progress counter when a cap is set)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]

    ans = ctrl._ctx.current_item.answer if ctrl._ctx.current_item else "1/2"
    frag = c.post("/answer", data={"answer": ans},
                  headers={"HX-Request": "true"}).get_data(as_text=True)
    assert 'class="hint turn-mastery"' in frag          # bar IS in the fragment
    assert "bar-fill" in frag
    # And the full page renders it exactly once (via the same include).
    html = c.get("/learn").get_data(as_text=True)
    assert html.count('class="hint turn-mastery"') == 1


def test_elaborate_form_uses_hidden_input():
    """R12-fix2: the ELABORATE word must ride a hidden input (the Help/Stop
    quick-action pattern), never the submit button's name/value — a button
    value is only submitted where event.submitter is supported, and when it
    was dropped the POST arrived empty and 'Explain more' silently did
    nothing (the reported live bug)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    frag = c.post("/answer", data={"answer": "no idea"},
                  headers={"HX-Request": "true"}).get_data(as_text=True)
    assert "Explain more" in frag
    form = frag.split('class="elaborate-form"')[1].split("</form>")[0]
    assert '<input type="hidden" name="answer" value="more">' in form
    assert 'name="answer"' not in form.split("<button")[1]  # nothing on the button


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
    html = c.get("/learn").get_data(as_text=True)
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
    body = c2.get("/learn").get_data(as_text=True)
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
    html = c.get("/learn").get_data(as_text=True)
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
    "n/d" server-side -- verified through the real controller scoring path.
    R2.3: composition is scoped to the CURRENT question's actual answer_type
    via the answer-mode registry (not attempted unconditionally whenever the
    "answer" field is blank, unlike the pre-R2.3 code) -- force a fraction
    node so this test doesn't depend on which node fringe-selection picks
    first for the "fractions" subject (that's not always a fraction node)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl._ctx.current_node_id = "unit_fractions"  # a real fraction-type node
    ctrl._ctx.current_item = None
    assert ctrl.current_answer_type == "fraction"

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
    c.get("/learn")
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
    c.get("/learn")

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
    c.get("/learn")

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
    c.get("/learn")
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
    c.get("/learn")

    # No fallback file yet -> no banner.
    assert "Durable logging degraded" not in c.get("/parent").get_data(as_text=True)

    fallback = pathlib.Path(dbp).parent / "escalation_fallback.log"
    fallback.write_text('{"iso_ts": "t", "trigger_class": "harm_to_self", '
                         '"severity": "critical", "verbatim_text": "x"}\n')

    assert "Durable logging degraded" in c.get("/parent").get_data(as_text=True)


def test_r4_stale_cookie_index_shows_picker_never_a_question():
    """R4 regression: a long-lived cookie with session["subject"] ALREADY set
    to a valid key (simulating a stale cookie from a past dev test, a prior
    day's session, or a server restart that wiped _controllers/_turn_logs
    while the cookie survived) used to make GET / silently resume straight
    into a quiz question. / must now ALWAYS show the picker, unconditionally."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")  # starts a real session, subject now set in the cookie

    r = c.get("/")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "Choose a topic" in body or "learn today" in body
    assert '<div class="question-text">' not in body  # never a quiz question


def test_r4_learn_route_renders_quiz_with_subject_chosen():
    """R4: GET /learn (the relocated former index() body) still renders the
    quiz once a subject is chosen -- existing behaviour, just at a new URL."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    r = c.get("/learn")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert '<div class="question-text">' in body


def test_r4_choose_post_redirects_to_learn():
    """R4: /choose's POST redirect target moved from index to learn."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    r = c.post("/choose", data={"subject": "fractions"})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/learn")


def test_r4_no_js_answer_loop_stays_on_learn_never_bounces_to_picker():
    """R4: the JS-disabled (no HX-Request header) answer loop must keep
    redirecting through /learn after every submitted answer, never bounce
    back to the picker mid-quiz."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")

    for _ in range(3):
        r = c.post("/answer", data={"answer": "4"})
        assert r.status_code == 302
        # Either advances to /learn (next question) or completes to /done --
        # never back to / (the picker).
        assert r.headers["Location"].endswith("/learn") or r.headers["Location"].endswith("/done")
        if r.headers["Location"].endswith("/done"):
            break
        c.get(r.headers["Location"])  # follow, to keep answering


def test_r4_brand_link_from_any_screen_lands_on_picker():
    """R4 follow-up (maintainer, 2026-07-11): clicking the Mentar brand icon
    from ANY screen, including mid-quiz, must land on the picker. The brand
    link in _base.html already points at "/" -- R4 makes "/" picker-only, so
    this needs no separate code change, just this explicit proof."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    learn_html = c.get("/learn").get_data(as_text=True)
    assert '<a href="/" class="brand">' in learn_html  # the brand link mid-quiz

    picker_html = c.get("/").get_data(as_text=True)
    assert "Choose a topic" in picker_html or "learn today" in picker_html


def test_r5_settings_route_renders_voice_select_and_theme_toggle():
    """R5: GET /settings is a plain static page containing the voice-picker
    <select> and the theme toggle button, RELOCATED here from the shared
    header (not duplicated)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()
    r = c.get("/settings")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert '<select id="voice-select">' in body
    assert 'id="test-voice-btn"' in body
    assert 'class="theme-toggle"' in body


def test_r5_theme_toggle_moved_out_of_shared_header_not_duplicated():
    """R5: the shared header (_base.html) no longer contains .theme-toggle on
    any page using the default header block -- it lives ONLY on /settings
    now, replaced in the header by a Settings link."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})

    for path in ("/", "/learn", "/progress"):
        body = c.get(path).get_data(as_text=True)
        assert 'class="theme-toggle"' not in body, f"{path} still has the header theme toggle"
        assert 'class="settings-link"' in body, f"{path} is missing the Settings header link"

    settings_body = c.get("/settings").get_data(as_text=True)
    assert settings_body.count('class="theme-toggle"') == 1  # present exactly once, not duplicated


def test_r5_footer_settings_link_on_learner_and_progress_not_frozen_or_parent():
    """R5: a '⚙️ Settings' footer link is added to learner.html and
    progress.html, but deliberately NOT frozen.html (U-60 zero-chrome
    invariant) or parent.html (its existing minimal-header design call)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})

    learn_html = c.get("/learn").get_data(as_text=True)
    assert 'href="/settings"' in learn_html

    progress_html = c.get("/progress").get_data(as_text=True)
    assert 'href="/settings"' in progress_html

    parent_html = c.get("/parent").get_data(as_text=True)
    assert 'href="/settings"' not in parent_html
    assert "Settings" not in parent_html

    # Trigger the frozen screen and confirm no settings link/chrome leaks in.
    r = c.post("/answer", data={"answer": "I want to die"}, follow_redirects=True)
    frozen_html = r.get_data(as_text=True)
    assert 'href="/settings"' not in frozen_html
    assert "theme-toggle" not in frozen_html
    assert "settings-link" not in frozen_html


def test_llm_status_reports_ok_when_backend_reachable():
    """The /settings/llm-status endpoint is a short-timeout reachability
    check -- mocked here (no real network in tests) to cover both outcomes.
    It must test the endpoint the app ACTUALLY resolved (config/inference.yaml
    or the env fallback -- app_mod._LLM_STATUS_ENDPOINT), never the raw
    MENTAR_LLM_* env defaults (the original bug: with a yaml present it pinged
    localhost:11434 while the app was really configured for a remote proxy)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    from unittest.mock import MagicMock, patch

    app_mod, c = _client()
    assert app_mod._LLM_STATUS_ENDPOINT is not None  # sandbox/CI configs are HTTP-backed
    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.models.list.return_value = []

        r = c.get("/settings/llm-status")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["model"] == app_mod._LLM_STATUS_ENDPOINT["model"]
        assert data["base_url"] == app_mod._LLM_STATUS_ENDPOINT["base_url"]
        assert data["error"] is None
        assert isinstance(data["latency_ms"], int)
        # The client was constructed against the RESOLVED endpoint.
        assert mock_openai_cls.call_args.kwargs["base_url"] == app_mod._LLM_STATUS_ENDPOINT["base_url"]


def test_llm_status_reports_info_for_in_process_backend():
    """In-process llamacpp has no HTTP endpoint -- the check must say so
    honestly (ok: null) instead of a false green/red."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    from unittest.mock import patch

    app_mod, c = _client()
    with patch.object(app_mod, "_LLM_STATUS_ENDPOINT", None):
        r = c.get("/settings/llm-status")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is None
        assert "no HTTP endpoint" in data["error"]


def test_settings_links_to_setup_page_for_ongoing_backend_switching():
    """R9 follow-up: /setup is reachable voluntarily at any time (not just as
    the gate's forced destination when something's broken) -- Settings must
    link to it so a family can find their way back to reconfigure without
    needing to remember the URL."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    body = c.get("/settings").get_data(as_text=True)
    assert 'href="/setup"' in body

    # And /setup itself must actually be reachable (not redirected away) even
    # though the test client's backend is "working" (bypassed, but the point
    # is the route itself never blocks a voluntary visit).
    r = c.get("/setup")
    assert r.status_code == 200


def test_llm_status_reports_not_ok_when_backend_unreachable():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    from unittest.mock import patch

    app_mod, c = _client()  # noqa: F841
    with patch("openai.OpenAI", side_effect=ConnectionError("Connection refused")):
        r = c.get("/settings/llm-status")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is False
        assert "Connection refused" in data["error"]
        assert isinstance(data["latency_ms"], int)


def _fake_response(content: bytes):
    """A urllib.request.urlopen(...) context-manager stand-in (no real network)."""
    from unittest.mock import MagicMock
    resp = MagicMock()
    resp.read.return_value = content
    resp.__enter__.return_value = resp
    return resp


# R10: packs.json ships EMPTY (every authored pack is now an in-repo toggle, not a
# download). The R8 download machinery is kept dormant for genuine future remote
# packs, so these tests exercise it against a SYNTHETIC one-pack manifest rather
# than a real in-repo entry -- which is the correct way to test dormant machinery.
_SYNTH_CONTENT = b"# synthetic remote pack content\n"


def _synthetic_manifest():
    import hashlib
    digest = hashlib.sha256(_SYNTH_CONTENT).hexdigest()
    return [{
        "id": "test_pack", "dir": "TEST_PACK",
        "label": "Test Pack", "description": "synthetic", "licence": "synthetic-licence",
        "files": [{"name": "content.md", "sha256": digest}],
    }]


def test_shipped_packs_json_is_empty_dormant():
    """R10: the download manifest ships EMPTY -- every authored pack is now an
    in-repo toggle, nothing is download-gated. Guards against a real pack
    accidentally being re-added to the download path."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    assert app_mod._load_packs_manifest() == []
    r = c.get("/settings/curriculum-packs")
    assert r.status_code == 200
    assert r.get_json()["packs"] == []


def test_curriculum_pack_install_verifies_checksum_and_writes_files():
    """R8 (dormant machinery): a successful install fetches every file, checks
    its sha256 against the manifest, and only then writes to
    curriculum/templates/<dir>/. Tested against a SYNTHETIC manifest since no
    real pack is download-gated anymore."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import pathlib
    import tempfile
    from unittest.mock import patch

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp())
    with patch.object(app_mod, "_TEMPLATES_DIR", scratch), \
         patch.object(app_mod, "_load_packs_manifest", return_value=_synthetic_manifest()):
        with patch("urllib.request.urlopen", return_value=_fake_response(_SYNTH_CONTENT)):
            r = c.post("/settings/curriculum-packs/test_pack/install")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["restart_required"] is True

        installed = scratch / "TEST_PACK" / "content.md"
        assert installed.exists()
        assert installed.read_bytes() == _SYNTH_CONTENT

        listing = c.get("/settings/curriculum-packs").get_json()
        packs = {p["id"]: p for p in listing["packs"]}
        assert packs["test_pack"]["installed"] is True


def test_curriculum_pack_install_rejects_checksum_mismatch_writes_nothing():
    """R8: a corrupted/tampered download must be rejected BEFORE anything is
    written to disk -- verify-then-write, never write-then-verify."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import pathlib
    import tempfile
    from unittest.mock import patch

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp())
    with patch.object(app_mod, "_TEMPLATES_DIR", scratch), \
         patch.object(app_mod, "_load_packs_manifest", return_value=_synthetic_manifest()):
        with patch("urllib.request.urlopen", return_value=_fake_response(b"corrupted content")):
            r = c.post("/settings/curriculum-packs/test_pack/install")
        assert r.status_code == 502
        data = r.get_json()
        assert data["ok"] is False
        assert "checksum mismatch" in data["error"]
        assert not (scratch / "TEST_PACK").exists()


def test_curriculum_pack_install_rejects_unknown_pack_id():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()  # noqa: F841
    r = c.post("/settings/curriculum-packs/not_a_real_pack/install")
    assert r.status_code == 404


def test_curriculum_pack_install_rejects_already_installed():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import pathlib
    import tempfile
    from unittest.mock import patch

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp())
    (scratch / "TEST_PACK").mkdir(parents=True)
    with patch.object(app_mod, "_TEMPLATES_DIR", scratch), \
         patch.object(app_mod, "_load_packs_manifest", return_value=_synthetic_manifest()):
        r = c.post("/settings/curriculum-packs/test_pack/install")
        assert r.status_code == 400
        assert "already installed" in r.get_json()["error"]


def test_curriculum_pack_uninstall_removes_directory():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import pathlib
    import tempfile
    from unittest.mock import patch

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp())
    (scratch / "TEST_PACK").mkdir(parents=True)
    (scratch / "TEST_PACK" / "content.md").write_text("x", encoding="utf-8")
    with patch.object(app_mod, "_TEMPLATES_DIR", scratch), \
         patch.object(app_mod, "_load_packs_manifest", return_value=_synthetic_manifest()):
        r = c.post("/settings/curriculum-packs/test_pack/uninstall")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["restart_required"] is True
        assert not (scratch / "TEST_PACK").exists()


def test_curriculum_pack_uninstall_rejects_not_installed():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import pathlib
    import tempfile
    from unittest.mock import patch

    app_mod, c = _client()
    scratch = pathlib.Path(tempfile.mkdtemp())
    with patch.object(app_mod, "_TEMPLATES_DIR", scratch), \
         patch.object(app_mod, "_load_packs_manifest", return_value=_synthetic_manifest()):
        r = c.post("/settings/curriculum-packs/test_pack/uninstall")
        assert r.status_code == 400
        assert "not installed" in r.get_json()["error"]


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
    test_r4_stale_cookie_index_shows_picker_never_a_question()
    print("  ✓ test_r4_stale_cookie_index_shows_picker_never_a_question")
    test_r4_learn_route_renders_quiz_with_subject_chosen()
    print("  ✓ test_r4_learn_route_renders_quiz_with_subject_chosen")
    test_r4_choose_post_redirects_to_learn()
    print("  ✓ test_r4_choose_post_redirects_to_learn")
    test_r4_no_js_answer_loop_stays_on_learn_never_bounces_to_picker()
    print("  ✓ test_r4_no_js_answer_loop_stays_on_learn_never_bounces_to_picker")
    test_r4_brand_link_from_any_screen_lands_on_picker()
    print("  ✓ test_r4_brand_link_from_any_screen_lands_on_picker")
    test_r5_settings_route_renders_voice_select_and_theme_toggle()
    print("  ✓ test_r5_settings_route_renders_voice_select_and_theme_toggle")
    test_r5_theme_toggle_moved_out_of_shared_header_not_duplicated()
    print("  ✓ test_r5_theme_toggle_moved_out_of_shared_header_not_duplicated")
    test_r5_footer_settings_link_on_learner_and_progress_not_frozen_or_parent()
    print("  ✓ test_r5_footer_settings_link_on_learner_and_progress_not_frozen_or_parent")
    test_llm_status_reports_ok_when_backend_reachable()
    print("  ✓ test_llm_status_reports_ok_when_backend_reachable")
    test_llm_status_reports_not_ok_when_backend_unreachable()
    print("  ✓ test_llm_status_reports_not_ok_when_backend_unreachable")
    test_llm_status_reports_info_for_in_process_backend()
    print("  ✓ test_llm_status_reports_info_for_in_process_backend")
    test_settings_links_to_setup_page_for_ongoing_backend_switching()
    print("  ✓ test_settings_links_to_setup_page_for_ongoing_backend_switching")
    test_shipped_packs_json_is_empty_dormant()
    print("  ✓ test_shipped_packs_json_is_empty_dormant")
    test_curriculum_pack_install_verifies_checksum_and_writes_files()
    print("  ✓ test_curriculum_pack_install_verifies_checksum_and_writes_files")
    test_curriculum_pack_install_rejects_checksum_mismatch_writes_nothing()
    print("  ✓ test_curriculum_pack_install_rejects_checksum_mismatch_writes_nothing")
    test_curriculum_pack_install_rejects_unknown_pack_id()
    print("  ✓ test_curriculum_pack_install_rejects_unknown_pack_id")
    test_curriculum_pack_install_rejects_already_installed()
    print("  ✓ test_curriculum_pack_install_rejects_already_installed")
    test_curriculum_pack_uninstall_removes_directory()
    print("  ✓ test_curriculum_pack_uninstall_removes_directory")
    test_curriculum_pack_uninstall_rejects_not_installed()
    print("  ✓ test_curriculum_pack_uninstall_rejects_not_installed")
