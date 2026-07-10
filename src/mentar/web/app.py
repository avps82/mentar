"""Mentar pilot web app — minimal Flask, 4 views, localhost-only.

Spec: docs/design/W6.3_pilot_interface.md; SPEC §23.
Views: / (learner question) · /frozen (child-facing handoff during escalation) ·
       /parent (log + escalation ack; typed-URL only, never auto-navigated) ·
       /parent/ack (POST, requires a typed confirm word).

Run:
    MENTAR_LLM_BASE_URL=http://localhost:11434/v1 \
    MENTAR_LLM_MODEL=gemma2:9b \
    python3 -m mentar.web.app

Config via environment (never commit values):
    MENTAR_LLM_BASE_URL   LLM proxy base URL        (default: http://localhost:11434/v1)
    MENTAR_LLM_API_KEY    Bearer token              (default: no-key)
    MENTAR_LLM_MODEL      Model name                (default: gemma2:9b)
    MENTAR_DB_PATH        SQLite path               (default: mentar_pilot.db)
    MENTAR_PROMPT_DIR     prompts/ directory        (default: auto-detected from repo root)
    MENTAR_CURRICULUM     Curriculum YAML           (default: auto-detected pilot fractions.md)
    SECRET_KEY            Flask session secret      (default: dev-only insecure key)
"""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for
from markupsafe import escape

from mentar.db.adapter import _DbStoreAdapter
from mentar.db.store import LearnerStore
from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.curriculum import load_curriculum, load_template_subject
from mentar.engine.itembank import load_item_bank
from mentar.engine.itemgen import (
    ARITHMETIC_GENERATORS,
    DEFAULT_GENERATORS,
    CompositeItemSource,
    ItemGenerator,
)
from mentar.engine.science_items import SCIENCE_GENERATORS
from mentar.inference import load_inference_config, make_llm_call
from mentar.tools.validate_template import validate_or_raise

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "mentar-dev-insecure-change-in-prod")

# ── Config ────────────────────────────────────────────────────────────────────

_REPO = Path(__file__).resolve().parents[3]  # src/mentar/web/app.py -> src -> repo root

LLM_BASE_URL = os.environ.get("MENTAR_LLM_BASE_URL", "http://localhost:11434/v1")
LLM_CRED     = os.environ.get("MENTAR_LLM_API_KEY") or "no-key"
LLM_MODEL    = os.environ.get("MENTAR_LLM_MODEL", "gemma2:9b")
DB_PATH      = os.environ.get("MENTAR_DB_PATH", str(_REPO / "mentar_pilot.db"))
PROMPT_DIR   = Path(os.environ.get("MENTAR_PROMPT_DIR", str(_REPO / "prompts")))
CURRICULUM_PATH = Path(os.environ.get(
    "MENTAR_CURRICULUM",
    str(_REPO / "curriculum" / "templates" / "_pilot" / "fractions.md"),
))
ITEMBANK_PATH = Path(os.environ.get(
    "MENTAR_ITEMBANK",
    str(_REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl"),
))

# ── Subjects (multi-topic testing) ──────────────────────────────────────────────
# Each subject = a curriculum template + its checkable-item source. Fractions keeps
# the authored bank (Option A); the new subjects are fully generator-driven.
_TPL = _REPO / "curriculum" / "templates" / "_pilot"
SUBJECTS: dict[str, dict] = {
    "fractions": {
        "label": "Fractions 🍕",
        "icon": "🍕",
        "description": "Slices, halves, and sharing things fairly.",
        "curriculum": CURRICULUM_PATH,
        "itembank": ITEMBANK_PATH,
        "generators": DEFAULT_GENERATORS,
    },
    "arithmetic": {
        "label": "Maths: + − × 🔢",
        "icon": "🔢",
        "description": "Adding, subtracting, and multiplying numbers.",
        "curriculum": _TPL / "arithmetic.md",
        "itembank": None,
        "generators": ARITHMETIC_GENERATORS,
    },
    "science": {
        "label": "Science 🔬",
        "icon": "🔬",
        "description": "How the world around us works.",
        "curriculum": _TPL / "science.md",
        "itembank": None,
        "generators": SCIENCE_GENERATORS,
    },
}
DEFAULT_SUBJECT = "fractions"
# A16: validate every subject's template before loading — a cyclic/bad-prereq
# template silently produces an empty fringe and a false "you've mastered
# everything!" completion for the child. Fail loud at startup instead.
for _subj_key, _subj_cfg in SUBJECTS.items():
    validate_or_raise(_subj_cfg["curriculum"])
_SUBJECT_CURRICULA = {k: load_curriculum(v["curriculum"]) for k, v in SUBJECTS.items()}
# A7: each subject's template `subject:` field, fed into the system prompt so a
# science session doesn't inherit the (formerly hardcoded) "fractions" text.
_SUBJECT_NAMES = {k: load_template_subject(v["curriculum"]) for k, v in SUBJECTS.items()}
_learner_subject: dict[str, str] = {}   # learner_uuid -> active subject key

# Inference backend: prefer config/inference.yaml (the canonical, backend-agnostic
# source — llamacpp/vllm/ollama). Fall back to the legacy MENTAR_LLM_* env vars so an
# existing env-only setup keeps working (treated as an OpenAI-compatible endpoint).
_INFERENCE_CFG = load_inference_config()
if _INFERENCE_CFG is None:
    _INFERENCE_CFG = {
        "backend": "vllm",
        "vllm": {"base_url": LLM_BASE_URL, "api_key": LLM_CRED, "model": LLM_MODEL},
    }
_GROUNDING_CFG: dict = _INFERENCE_CFG.get("grounding", {})  # ZIM reader config (W7)

# Built lazily: an in-process llama.cpp backend loads the GGUF on construction, so we
# defer it until the first turn (keeps `import mentar.web.app` cheap for tests/CLI reuse).
_llm_call_cached = None


def _llm_call(messages: list[dict]) -> str:
    global _llm_call_cached
    if _llm_call_cached is None:
        _llm_call_cached = make_llm_call(_INFERENCE_CFG)
    return _llm_call_cached(messages)


# Per-learner controller instances and turn logs.
_controllers: dict[str, SessionController] = {}
_turn_logs: dict[str, list[dict]] = {}      # learner_id -> [{role, text}]
_stores: dict[str, LearnerStore] = {}
_db_learner_ids: dict[str, int] = {}        # flask-session learner_uuid -> DB int id
_done_messages: dict[str, str] = {}         # learner_uuid -> final completion text
_last_messages: dict[str, str] = {}         # learner_uuid -> last TurnResult.message (transient prose)


def _get_or_create_controller(learner_uuid: str, subject: str) -> SessionController:
    # Switching subject starts a fresh session for that subject (new controller +
    # turn log + session_id). The DB store/learner is shared (skill_state is keyed
    # by node id, which is distinct across subjects, so there's no collision).
    if _learner_subject.get(learner_uuid) != subject:
        _controllers.pop(learner_uuid, None)
        _turn_logs[learner_uuid] = []
        _last_messages.pop(learner_uuid, None)
        _learner_subject[learner_uuid] = subject

    if learner_uuid not in _controllers:
        store = _stores.get(learner_uuid)
        if store is None:
            store = LearnerStore(DB_PATH)
            _stores[learner_uuid] = store
            # A6: reuse the existing learner_profile row across server restarts —
            # _db_learner_ids is in-memory and clears on restart, but the Flask
            # session cookie (and so learner_uuid) survives; without this, every
            # restart silently created a new learner and reset mastery/history.
            learner_name = f"pilot-{learner_uuid[:8]}"
            existing = store.get_learner_by_name(learner_name)
            _db_learner_ids[learner_uuid] = existing["id"] if existing else store.create_learner(
                name=learner_name,
                year_level="pilot",
                country="GB",
                age_mode="parent_mediated",  # SPEC §6.2 pilot default
            )
        db_id = _db_learner_ids[learner_uuid]
        # A19: pilot scope is parent_mediated only — a clear error, not a silent
        # unsupervised session, if a learner row is ever anything else.
        store.assert_parent_mediated(db_id)
        subj = SUBJECTS[subject]
        bank = (
            load_item_bank(subj["itembank"])
            if subj["itembank"] and Path(subj["itembank"]).exists()
            else None
        )
        item_source = CompositeItemSource(ItemGenerator(generators=subj["generators"]), bank)
        _controllers[learner_uuid] = SessionController(
            llm_call=_llm_call,
            prompt_dir=PROMPT_DIR,
            grounding_cfg=_GROUNDING_CFG,
            curriculum=_SUBJECT_CURRICULA[subject],
            db_store=_DbStoreAdapter(store, db_id),
            learner_id=learner_uuid,
            item_bank=item_source,
            subject=_SUBJECT_NAMES[subject],
        )
        _turn_logs[learner_uuid] = []
    return _controllers[learner_uuid]


# HTML templates live in src/mentar/web/templates/ (learner.html, done.html, parent.html).


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    learner_uuid = session.get("learner_uuid")
    if not learner_uuid:
        learner_uuid = str(uuid.uuid4())
        session["learner_uuid"] = learner_uuid

    subject = session.get("subject")
    if subject not in SUBJECTS:
        # No topic chosen yet — show the picker.
        return render_template(
            "subjects.html", subjects=SUBJECTS, subjects_progress=_subjects_progress(learner_uuid)
        )

    ctrl = _get_or_create_controller(learner_uuid, subject)

    if ctrl.state == FSMState.ESCALATION_FREEZE.value:
        # Absorbing state — every child-facing render goes to the frozen page,
        # not just the turn that triggered it (A8).
        return redirect(url_for("frozen"))

    # U-35: the assent/transparency lines only ever appear on this first turn
    # (session.py bundles them into the SESSION_START->PRESENT text) -- flag it
    # so the template can give them distinct visual treatment.
    is_first_turn = ctrl.state == FSMState.SESSION_START.value

    # Only call step(None) to initialise — subsequent renders just show the last question.
    if is_first_turn:
        result = ctrl.step(None)
        _log_turn(learner_uuid, "Mentar", result.text)
        _last_messages[learner_uuid] = result.message
        if result.done:
            _done_messages[learner_uuid] = result.text or "All done!"
            return redirect(url_for("done"))
        if result.escalated:
            return redirect(url_for("frozen"))

    # Re-display the last Mentar turn from the log (don't call step again).
    return render_template(
        "learner.html", subject_label=SUBJECTS[subject]["label"],
        current_mastery=_current_node_mastery(learner_uuid, ctrl),
        **_turn_context(learner_uuid, ctrl, is_first_turn=is_first_turn),
    )


@app.route("/choose", methods=["GET", "POST"])
def choose():
    """Subject picker: GET shows the topics, POST selects one and starts it."""
    if request.method == "POST":
        subject = request.form.get("subject")
        if subject in SUBJECTS:
            session["subject"] = subject
        return redirect(url_for("index"))
    return render_template(
        "subjects.html", subjects=SUBJECTS,
        subjects_progress=_subjects_progress(session.get("learner_uuid", "")),
    )


@app.route("/answer", methods=["POST"])
def answer():
    # U-90: htmx (static/htmx.min.js, vendored) drives every submit of this
    # form. "HX-Request: true" marks an htmx-issued request; a normal browser
    # POST (JS disabled) carries no such header and gets the classic redirect
    # response instead — same routes/behaviour either way (U-14).
    hx = request.headers.get("HX-Request") == "true"

    learner_uuid = session.get("learner_uuid")
    if not learner_uuid or learner_uuid not in _controllers:
        if hx:
            return "", 200, {"HX-Redirect": url_for("index")}
        return redirect(url_for("index"))

    answer_text = request.form.get("answer", "").strip()
    if not answer_text:
        # Fraction widget: two structured inputs (numerator / denominator) compose
        # server-side into the "n/d" string the verifier already accepts — no
        # client JS involved, works identically with JS disabled.
        num = request.form.get("answer_num", "").strip()
        den = request.form.get("answer_den", "").strip()
        if num and den:
            answer_text = f"{num}/{den}"
    _log_turn(learner_uuid, "Child", answer_text)

    ctrl = _controllers[learner_uuid]
    result = ctrl.step(answer_text)
    if result.text:
        _log_turn(learner_uuid, "Mentar", result.text)
    _last_messages[learner_uuid] = result.message

    if result.escalated:
        if hx:
            return "", 200, {"HX-Redirect": url_for("frozen")}
        return redirect(url_for("frozen"))
    if result.done:
        _done_messages[learner_uuid] = result.text or "Well done — session complete!"
        if hx:
            return "", 200, {"HX-Redirect": url_for("done")}
        return redirect(url_for("done"))

    # Advancing: htmx swaps this fragment straight into hx-target="#turn-area"
    # (no page reload); a non-JS browser gets the usual full redirect+reload.
    # Same _turn.html partial as the full-page path (U-31 feedback/question
    # split + U-32 markdown-lite), so the two never visually disagree.
    if hx:
        return _render_turn_fragment(learner_uuid, ctrl)
    return redirect(url_for("index"))


@app.route("/done")
def done():
    """U-70: celebration + a simple recap (questions tried, skills touched).
    Same store/session_responses shape already used by /parent -- no new
    store methods, no controller changes."""
    learner_uuid = session.get("learner_uuid", "")
    message = _done_messages.get(learner_uuid, "All done!")
    ctrl = _controllers.get(learner_uuid)
    store, db_id = _store_and_id(learner_uuid)
    recap = None
    if store and db_id is not None and ctrl is not None:
        responses = store.session_responses(db_id, ctrl.session_id)
        help_events = store.session_help_events(db_id, ctrl.session_id)
        recap = {
            "n_responses": len(responses),
            "n_correct": sum(1 for r in responses if r.get("scored") == 1),
            "n_help": len(help_events),
            "skills_touched": sorted({r["skill_id"] for r in responses}),
        }
    return render_template("done.html", message=message, recap=recap)


@app.route("/frozen")
def frozen():
    """Child-facing view during ESCALATION_FREEZE (A8): the two fixed handoff
    messages ONLY — no verbatim trigger text, no resume/ack control. The parent
    resumes via /parent (typed URL only, never auto-navigated here) + /parent/ack
    (gated behind a typed confirm word)."""
    from mentar.safety.escalation import HANDOFF_MESSAGE_PRIMARY, HANDOFF_MESSAGE_SUPPORT

    learner_uuid = session.get("learner_uuid", "")
    ctrl = _controllers.get(learner_uuid)
    if ctrl is None or ctrl.state != FSMState.ESCALATION_FREEZE.value:
        return redirect(url_for("index"))
    return render_template(
        "frozen.html",
        handoff_primary=HANDOFF_MESSAGE_PRIMARY,
        handoff_support=HANDOFF_MESSAGE_SUPPORT,
    )


_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"\*(.+?)\*")


def _render_markdown_lite(text: str) -> str:
    """U-32: HTML-escape first (the security property), then insert ONLY 4
    whitelisted tags (<strong>/<em>/<ul>/<li>) over the now-safe text -- no
    third-party markdown lib, no other tag ever gets emitted. Bullet markers
    are stripped line-by-line BEFORE the bold/italic regexes run so a leading
    "* " (bullet) is never mistaken for an italic delimiter; bold (**x**) is
    substituted before italic (*x*) so a bold span's stars are consumed first.
    Segments are joined WITHOUT a "\\n" between block tags (<ul>/<li>/</ul>) --
    .question uses white-space:pre-wrap, so a raw newline next to a block
    element would render as a stray visible gap; "\\n" is only kept between
    two genuine prose lines, to preserve intentional line breaks.
    Safe to mark `| safe` in Jinja: every character that reaches an HTML tag
    boundary either came from escape() or from a literal string in this
    function, never from unescaped model/generator output."""
    escaped = str(escape(text))
    segments: list[tuple[bool, str]] = []  # (is_block_markup, content)
    in_list = False
    for line in escaped.split("\n"):
        stripped = line.strip()
        is_bullet = stripped.startswith("* ") or stripped.startswith("- ")
        content = stripped[2:] if is_bullet else line
        content = _MD_BOLD_RE.sub(r"<strong>\1</strong>", content)
        content = _MD_ITALIC_RE.sub(r"<em>\1</em>", content)
        if is_bullet:
            if not in_list:
                segments.append((True, "<ul>"))
                in_list = True
            segments.append((True, f"<li>{content}</li>"))
        else:
            if in_list:
                segments.append((True, "</ul>"))
                in_list = False
            segments.append((False, content))
    if in_list:
        segments.append((True, "</ul>"))

    result = ""
    prev_is_block = None
    for is_block, s in segments:
        if result and not is_block and prev_is_block is False:
            result += "\n"
        result += s
        prev_is_block = is_block
    return result


def _compute_graph_layout(curriculum: dict, node_pct: dict[str, int]) -> dict:
    """U-40/U-41: an owned layered layout for the concept-graph map -- no
    graph library. Works for any curriculum (node count/edges not hardcoded):
    level(n) = 0 if no prereqs, else 1 + max(level(prereq)); nodes in the same
    level are spread evenly across a 0-100 x-axis so the SVG (viewBox 0 0 100
    H) scales responsively. Percentage coordinates keep this pure/testable."""
    levels: dict[str, int] = {}

    def _level(nid: str, seen: frozenset[str] = frozenset()) -> int:
        if nid in levels:
            return levels[nid]
        if nid in seen:  # a cycle would infinite-loop; validate_or_raise already
            return 0     # rejects cyclic templates at startup, this is a safety net
        prereqs = [p for p in curriculum.get(nid, {}).get("prerequisites", []) if p in curriculum]
        lvl = 0 if not prereqs else 1 + max(_level(p, seen | {nid}) for p in prereqs)
        levels[nid] = lvl
        return lvl

    for node_id in curriculum:
        _level(node_id)

    by_level: dict[int, list[str]] = {}
    for node_id, lvl in levels.items():
        by_level.setdefault(lvl, []).append(node_id)
    for row in by_level.values():
        row.sort()

    n_levels = max(by_level, default=0) + 1
    row_height = 100 / max(n_levels, 1)
    pos: dict[str, tuple[float, float]] = {}
    nodes = []
    for lvl in sorted(by_level):
        row = by_level[lvl]
        for i, node_id in enumerate(row):
            x = (i + 1) / (len(row) + 1) * 100
            y = lvl * row_height + row_height / 2
            pos[node_id] = (x, y)
            pct = node_pct.get(node_id)
            status = "not_started" if pct is None else ("mastered" if pct >= 85 else "learning")
            nodes.append({
                "id": node_id,
                "label": curriculum[node_id].get("concept", node_id),
                "x": round(x, 1), "y": round(y, 1),
                "pct": pct or 0, "status": status,
            })

    edges = []
    for node_id, node in curriculum.items():
        x2, y2 = pos[node_id]
        for prereq in node.get("prerequisites", []):
            if prereq not in pos:
                continue
            x1, y1 = pos[prereq]
            edges.append({"x1": round(x1, 1), "y1": round(y1, 1), "x2": round(x2, 1), "y2": round(y2, 1)})

    return {"nodes": nodes, "edges": edges, "height": max(n_levels * 22, 22)}


@app.route("/progress")
def progress():
    learner_uuid = session.get("learner_uuid", "")
    store, db_id = _store_and_id(learner_uuid)
    skill_states = store.all_skill_states(db_id) if (store and db_id is not None) else []
    # Convert sqlite3.Row to plain dicts for the template.
    skills = [dict(r) for r in skill_states]
    node_pct = {s["skill_id"]: int(s["p_mastery"] * 100) for s in skills}
    subject = session.get("subject") or DEFAULT_SUBJECT
    curriculum = _SUBJECT_CURRICULA.get(subject, {})
    graph = _compute_graph_layout(curriculum, node_pct) if curriculum else None
    return render_template("progress.html", skills=skills, graph=graph)


@app.route("/parent")
def parent():
    learner_uuid = session.get("learner_uuid", "")
    ctrl = _controllers.get(learner_uuid)
    escalated = ctrl is not None and ctrl.state == FSMState.ESCALATION_FREEZE.value
    from mentar.safety.escalation import HANDOFF_MESSAGE_PRIMARY

    # Prefer the durable transcript from the DB (survives restarts); fall back to
    # the in-memory live log only if the store has nothing yet.
    turns = _persisted_turns(learner_uuid)
    if turns is None:
        turns = _turn_logs.get(learner_uuid, [])

    # Session summary counts from the DB.
    store, db_id = _store_and_id(learner_uuid)
    session_id = ctrl.session_id if ctrl is not None else None
    skill_states: list[dict] = []
    session_summary: dict = {}
    answers: list[dict] = []
    if store and db_id is not None and session_id:
        skill_states = [dict(r) for r in store.all_skill_states(db_id)]
        responses = store.session_responses(db_id, session_id)
        help_events = store.session_help_events(db_id, session_id)
        answers = responses
        n_correct = sum(1 for r in responses if r.get("scored") == 1)
        session_summary = {
            "n_responses": len(responses),
            "n_correct": n_correct,
            "n_help": len(help_events),
        }

    return render_template(
        "parent.html",
        escalated=escalated,
        handoff_msg=HANDOFF_MESSAGE_PRIMARY,
        turns=turns,
        escalations=_persisted_escalations(learner_uuid),
        skill_states=skill_states,
        session_summary=session_summary,
        answers=answers,
        logging_degraded=_escalation_fallback_log_nonempty(),
    )


def _escalation_fallback_log_nonempty() -> bool:
    """A15 — true when the escalation DB-write fallback sink has entries, meaning
    at least one escalation failed to persist to the DB and was only captured in
    the append-only escalation_fallback.log next to the DB file."""
    path = Path(DB_PATH).parent / "escalation_fallback.log"
    return path.exists() and path.stat().st_size > 0


# A8: the parent must type this word to acknowledge/resume — an honor-system-compatible
# minimum gate against an un-gated resume button (PIN gate is Phase 1, out of pilot scope).
PARENT_ACK_CONFIRM_WORD = "RESUME"


@app.route("/parent/ack", methods=["POST"])
def parent_ack():
    learner_uuid = session.get("learner_uuid", "")
    action = request.form.get("action", "resume")  # "resume" or "end"
    confirm = request.form.get("confirm", "").strip().upper()
    if confirm != PARENT_ACK_CONFIRM_WORD:
        # No-op: wrong/missing confirm word acknowledges nothing and changes no state.
        return redirect(url_for("parent"))
    # Persist the parent's acknowledgement against the latest open escalation
    # (SAFETY.md §3.3 Step 6) before resuming/ending the session.
    _ack_latest_escalation(learner_uuid)
    if learner_uuid in _controllers:
        ctrl = _controllers[learner_uuid]
        # Parent control plane — transitions out of the escalation freeze (child
        # input via /answer cannot). See SessionController.parent_acknowledge.
        result = ctrl.parent_acknowledge(action)
        if result.text:
            _log_turn(learner_uuid, "Mentar", result.text)
        _last_messages[learner_uuid] = result.message or result.text
        if result.done:
            return render_template("done.html", message=result.text or "Session ended.")
    return redirect(url_for("index"))


# ── Helpers ───────────────────────────────────────────────────────────────────

# DB transcript role -> parent-facing display label.
_ROLE_DISPLAY = {"learner": "Child", "tutor": "Mentar", "system": "System"}


def _store_and_id(learner_uuid: str) -> tuple[LearnerStore | None, int | None]:
    return _stores.get(learner_uuid), _db_learner_ids.get(learner_uuid)


def _turn_context(learner_uuid: str, ctrl: SessionController, is_first_turn: bool = False) -> dict:
    """Template context for the _turn.html partial: the STRUCTURED message and
    question fields (TurnResult.message / .question — never string-split from
    prose), both rendered through the same markdown-lite (U-32), plus the
    answer-widget metadata (mc4 radio choices / fraction inputs)."""
    message = _last_messages.get(learner_uuid, "")
    question = ctrl.question_display or "Ready when you are!"
    choices = ctrl.current_choices
    return {
        "message_html": _render_markdown_lite(message) if message else "",
        "question_html": _render_markdown_lite(question),
        "is_first_turn": is_first_turn,
        "answer_type": ctrl.current_answer_type,
        "choices": choices,
        "choice_letters": ["A", "B", "C", "D"][: len(choices)] if choices else [],
    }


def _render_turn_fragment(learner_uuid: str, ctrl: SessionController) -> str:
    return render_template("_turn.html", **_turn_context(learner_uuid, ctrl))


def _current_node_mastery(learner_uuid: str, ctrl: SessionController) -> dict | None:
    """U-34: a small per-skill mastery cue during the lesson (current node
    only). None before the first PRESENT or when there's nothing scored yet."""
    node_id = ctrl.current_node_id
    if not node_id:
        return None
    store, db_id = _store_and_id(learner_uuid)
    if store is None or db_id is None:
        return {"skill_id": node_id, "pct": 0}
    for row in store.all_skill_states(db_id):
        if row["skill_id"] == node_id:
            return {"skill_id": node_id, "pct": int(row["p_mastery"] * 100)}
    return {"skill_id": node_id, "pct": 0}


def _subjects_progress(learner_uuid: str) -> dict[str, dict]:
    """U-20 progress cue on the subject picker: {subject_key: {mastered, total}},
    only for subjects with an existing store (a learner who has played before
    this server process started up) -- never triggers a fresh DB connection
    just to render the picker."""
    store, db_id = _store_and_id(learner_uuid)
    if store is None or db_id is None:
        return {}
    mastered_ids = {
        r["skill_id"] for r in store.all_skill_states(db_id) if r["p_mastery"] >= 0.85
    }
    out = {}
    for key, curriculum in _SUBJECT_CURRICULA.items():
        total = len(curriculum)
        if total:
            out[key] = {"mastered": len(mastered_ids & curriculum.keys()), "total": total}
    return out


def _persisted_turns(learner_uuid: str) -> list[dict] | None:
    """The durable transcript for this learner's live session, or None if unavailable."""
    store, db_id = _store_and_id(learner_uuid)
    ctrl = _controllers.get(learner_uuid)
    if store is None or db_id is None or ctrl is None:
        return None
    rows = store.transcript_for_session(db_id, ctrl.session_id)
    if not rows:
        return None
    return [{"role": _ROLE_DISPLAY.get(r["role"], r["role"]), "text": r["text"]} for r in rows]


def _persisted_escalations(learner_uuid: str) -> list[dict]:
    store, db_id = _store_and_id(learner_uuid)
    if store is None or db_id is None:
        return []
    return store.learner_escalations(db_id)


def _ack_latest_escalation(learner_uuid: str) -> None:
    """Mark the most recent un-acknowledged escalation as acknowledged by the parent."""
    store, db_id = _store_and_id(learner_uuid)
    if store is None or db_id is None:
        return
    open_escs = [e for e in store.learner_escalations(db_id) if not e.get("parent_ack_at")]
    if open_escs:
        store.parent_ack_escalation(open_escs[-1]["id"])


def _log_turn(learner_uuid: str, role: str, text: str) -> None:
    if text:
        _turn_logs.setdefault(learner_uuid, []).append({"role": role, "text": text})


def _last_mentar_text(learner_uuid: str) -> str | None:
    for entry in reversed(_turn_logs.get(learner_uuid, [])):
        if entry["role"] == "Mentar":
            return entry["text"]
    return None


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Mentar pilot — http://localhost:5000")
    print(f"  LLM:  backend={_INFERENCE_CFG.get('backend')}")
    print(f"  DB:   {DB_PATH}")
    print(f"  curriculum: {CURRICULUM_PATH}")
    app.run(host="127.0.0.1", port=5000, debug=False)
