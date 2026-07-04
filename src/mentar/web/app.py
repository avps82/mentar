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
import uuid
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from mentar.db.adapter import _DbStoreAdapter
from mentar.db.store import LearnerStore
from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.curriculum import load_curriculum
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
        "curriculum": CURRICULUM_PATH,
        "itembank": ITEMBANK_PATH,
        "generators": DEFAULT_GENERATORS,
    },
    "arithmetic": {
        "label": "Maths: + − × 🔢",
        "curriculum": _TPL / "arithmetic.md",
        "itembank": None,
        "generators": ARITHMETIC_GENERATORS,
    },
    "science": {
        "label": "Science 🔬",
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


def _get_or_create_controller(learner_uuid: str, subject: str) -> SessionController:
    # Switching subject starts a fresh session for that subject (new controller +
    # turn log + session_id). The DB store/learner is shared (skill_state is keyed
    # by node id, which is distinct across subjects, so there's no collision).
    if _learner_subject.get(learner_uuid) != subject:
        _controllers.pop(learner_uuid, None)
        _turn_logs[learner_uuid] = []
        _learner_subject[learner_uuid] = subject

    if learner_uuid not in _controllers:
        store = _stores.get(learner_uuid)
        if store is None:
            store = LearnerStore(DB_PATH)
            _stores[learner_uuid] = store
            _db_learner_ids[learner_uuid] = store.create_learner(
                name=f"pilot-{learner_uuid[:8]}",
                year_level="pilot",
                country="GB",
                age_mode="parent_mediated",  # SPEC §6.2 pilot default
            )
        db_id = _db_learner_ids[learner_uuid]
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
        return render_template("subjects.html", subjects=SUBJECTS)

    ctrl = _get_or_create_controller(learner_uuid, subject)

    if ctrl.state == FSMState.ESCALATION_FREEZE.value:
        # Absorbing state — every child-facing render goes to the frozen page,
        # not just the turn that triggered it (A8).
        return redirect(url_for("frozen"))

    # Only call step(None) to initialise — subsequent renders just show the last question.
    if ctrl.state == FSMState.SESSION_START.value:
        result = ctrl.step(None)
        _log_turn(learner_uuid, "Mentar", result.text)
        if result.done:
            return render_template("done.html", message=result.text or "All done!")
        if result.escalated:
            return redirect(url_for("frozen"))

    # Re-display the last Mentar question from the log (don't call step again).
    question = _last_mentar_text(learner_uuid) or "Ready when you are!"
    return render_template(
        "learner.html", question=question, subject_label=SUBJECTS[subject]["label"]
    )


@app.route("/choose", methods=["GET", "POST"])
def choose():
    """Subject picker: GET shows the topics, POST selects one and starts it."""
    if request.method == "POST":
        subject = request.form.get("subject")
        if subject in SUBJECTS:
            session["subject"] = subject
        return redirect(url_for("index"))
    return render_template("subjects.html", subjects=SUBJECTS)


@app.route("/answer", methods=["POST"])
def answer():
    learner_uuid = session.get("learner_uuid")
    if not learner_uuid or learner_uuid not in _controllers:
        return redirect(url_for("index"))

    answer_text = request.form.get("answer", "").strip()
    _log_turn(learner_uuid, "Child", answer_text)

    ctrl = _controllers[learner_uuid]
    result = ctrl.step(answer_text)
    if result.text:
        _log_turn(learner_uuid, "Mentar", result.text)

    if result.escalated:
        return redirect(url_for("frozen"))
    if result.done:
        return render_template("done.html", message=result.text or "Well done — session complete!")
    return redirect(url_for("index"))


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


@app.route("/progress")
def progress():
    learner_uuid = session.get("learner_uuid", "")
    store, db_id = _store_and_id(learner_uuid)
    skill_states = store.all_skill_states(db_id) if (store and db_id is not None) else []
    # Convert sqlite3.Row to plain dicts for the template.
    skills = [dict(r) for r in skill_states]
    return render_template("progress.html", skills=skills)


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
        if result.done:
            return render_template("done.html", message=result.text or "Session ended.")
    return redirect(url_for("index"))


# ── Helpers ───────────────────────────────────────────────────────────────────

# DB transcript role -> parent-facing display label.
_ROLE_DISPLAY = {"learner": "Child", "tutor": "Mentar", "system": "System"}


def _store_and_id(learner_uuid: str) -> tuple[LearnerStore | None, int | None]:
    return _stores.get(learner_uuid), _db_learner_ids.get(learner_uuid)


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
