"""Mentar pilot web app — minimal Flask, 4 views, localhost-only.

Spec: docs/design/W6.3_pilot_interface.md; SPEC §23.
Views: / (learner question) · /parent (log + escalation ack) · /parent/ack (POST).

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

import yaml
from flask import Flask, redirect, render_template, request, session, url_for

from mentar.db.store import LearnerStore
from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.itembank import load_item_bank
from mentar.engine.itemgen import build_item_source
from mentar.inference import load_inference_config, make_llm_call

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

# ── One-time startup ──────────────────────────────────────────────────────────

def _load_curriculum(path: Path) -> dict:
    """Convert the pilot fractions.md YAML into the controller's curriculum dict."""
    # The file is a YAML block followed by Markdown narrative (after a --- divider).
    # Extract only the first YAML document (everything before the second ---).
    text = path.read_text(encoding="utf-8")
    parts = text.split("\n---\n", maxsplit=1)
    raw = yaml.safe_load(parts[0])
    curriculum = {}
    for node in raw.get("concepts", []):
        nid = node["id"]
        verifier = node.get("verifier", {})
        seeds = node.get("transfer_seeds", [])
        curriculum[nid] = {
            "concept": node.get("label", nid),
            "answer_type": verifier.get("answer_type", "free_text"),
            "checker": verifier.get("checker", "none"),
            "expected_answer": seeds[0] if seeds else "",
            "grounding": node.get("grounding", {}),
            "prerequisites": node.get("prereqs", []),
            "bkt_priors": node.get("bkt_priors"),
        }
    return curriculum


_CURRICULUM = _load_curriculum(CURRICULUM_PATH)

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


def _get_or_create_controller(learner_uuid: str) -> SessionController:
    if learner_uuid not in _controllers:
        store = LearnerStore(DB_PATH)
        _stores[learner_uuid] = store
        db_id = store.create_learner(
            name=f"pilot-{learner_uuid[:8]}",
            year_level="pilot",
            country="GB",
            age_mode="parent_mediated",  # SPEC §6.2 pilot default
        )
        _db_learner_ids[learner_uuid] = db_id
        bank = load_item_bank(ITEMBANK_PATH) if ITEMBANK_PATH.exists() else None
        # item_source: composite (default, generator+bank) | generator | bank
        item_bank = build_item_source(_INFERENCE_CFG.get("item_source", "composite"), bank=bank)
        _controllers[learner_uuid] = SessionController(
            llm_call=_llm_call,
            prompt_dir=PROMPT_DIR,
            grounding_cfg=_GROUNDING_CFG,
            curriculum=_CURRICULUM,
            db_store=_DbStoreAdapter(store, db_id),
            learner_id=learner_uuid,
            item_bank=item_bank,
        )
        _turn_logs[learner_uuid] = []
    return _controllers[learner_uuid]


class _DbStoreAdapter:
    """Adapts LearnerStore (int learner_id) to the controller's expected interface."""

    def __init__(self, store: LearnerStore, db_id: int) -> None:
        self._store = store
        self._db_id = db_id

    def get_skill_state(self, learner_id: str, node_id: str):
        return self._store.get_skill_state(self._db_id, node_id)

    def update_skill_state(self, learner_id: str, node_id: str, p: float) -> None:
        self._store.update_skill_state(
            learner_id=self._db_id,
            skill_id=node_id,
            p_mastery=p,
            priors_used=True,  # pilot uses cold-start priors (W3.3: fitted only at N>=100)
        )

    def write_escalation(self, learner_id: str, trigger_class: str, trigger_text_verbatim: str) -> int:
        # Verbatim text stored untruncated (SAFETY §3.3 Step 2).
        return self._store.write_escalation(
            learner_id=self._db_id,
            trigger_class=trigger_class,
            trigger_text_verbatim=trigger_text_verbatim,
        )

    # ── Durable session logging (controller calls these best-effort) ──────────

    def create_session(self, session_id: str) -> None:
        self._store.create_session(self._db_id, session_id)

    def end_session(self, session_id: str, ended_reason: str) -> None:
        self._store.end_session(self._db_id, session_id, ended_reason)

    def write_transcript(self, session_id: str, turn_index: int, role: str, text: str) -> int:
        return self._store.write_transcript(self._db_id, session_id, turn_index, role, text)

    def write_response(
        self, session_id: str, skill_id: str, prompt_ref: str, answer: str,
        scored: int, hinted: int, check_result: str | None,
    ) -> int:
        return self._store.write_response(
            self._db_id, session_id, skill_id, prompt_ref, answer, scored, hinted, check_result,
        )

    def write_help_event(
        self, session_id: str, skill_id: str, modality: str, response_log_id: int,
    ) -> int:
        return self._store.write_help_event(
            self._db_id, session_id, skill_id, modality, response_log_id,
        )

    def write_probe_event(
        self, session_id: str, skill_id: str, response_log_id: int,
        retry_response_log_id: int | None, class_: str,
    ) -> int:
        return self._store.write_probe_event(
            self._db_id, session_id, skill_id, response_log_id, retry_response_log_id, class_,
        )


# HTML templates live in src/mentar/web/templates/ (learner.html, done.html, parent.html).


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    learner_uuid = session.get("learner_uuid")
    if not learner_uuid:
        learner_uuid = str(uuid.uuid4())
        session["learner_uuid"] = learner_uuid

    ctrl = _get_or_create_controller(learner_uuid)

    # Only call step(None) to initialise — subsequent renders just show the last question.
    if ctrl.state == FSMState.SESSION_START.value:
        result = ctrl.step(None)
        _log_turn(learner_uuid, "Mentar", result.text)
        if result.done:
            return render_template("done.html", message=result.text or "All done!")
        if result.escalated:
            return redirect(url_for("parent"))

    # Re-display the last Mentar question from the log (don't call step again).
    question = _last_mentar_text(learner_uuid) or "Ready when you are!"
    return render_template("learner.html", question=question)


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
        return redirect(url_for("parent"))
    if result.done:
        return render_template("done.html", message=result.text or "Well done — session complete!")
    return redirect(url_for("index"))


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
    )


@app.route("/parent/ack", methods=["POST"])
def parent_ack():
    learner_uuid = session.get("learner_uuid", "")
    action = request.form.get("action", "resume")  # "resume" or "end"
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
