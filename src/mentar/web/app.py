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
from openai import OpenAI

from mentar.db.store import LearnerStore
from mentar.dialogue.controller import FSMState, SessionController

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
_GROUNDING_CFG: dict = {}  # populated from config/inference.yaml if present

_openai_client = OpenAI(api_key=LLM_CRED, base_url=LLM_BASE_URL)


def _llm_call(messages: list[dict]) -> str:
    resp = _openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=400,
        temperature=0.3,
    )
    return resp.choices[0].message.content or ""


# Per-learner controller instances and turn logs.
_controllers: dict[str, SessionController] = {}
_turn_logs: dict[str, list[dict]] = {}      # learner_id -> [{role, text}]
_stores: dict[str, LearnerStore] = {}
_db_learner_ids: dict[str, int] = {}        # flask-session learner_uuid -> DB int id


def _get_or_create_controller(learner_uuid: str) -> SessionController:
    if learner_uuid not in _controllers:
        store = LearnerStore(DB_PATH)
        _stores[learner_uuid] = store
        db_id = store.create_learner(name=f"pilot-{learner_uuid[:8]}", year_level="pilot")
        _db_learner_ids[learner_uuid] = db_id
        _controllers[learner_uuid] = SessionController(
            llm_call=_llm_call,
            prompt_dir=PROMPT_DIR,
            grounding_cfg=_GROUNDING_CFG,
            curriculum=_CURRICULUM,
            db_store=_DbStoreAdapter(store, db_id),
            learner_id=learner_uuid,
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


@app.route("/parent")
def parent():
    learner_uuid = session.get("learner_uuid", "")
    escalated = (
        learner_uuid in _controllers
        and _controllers[learner_uuid].state == FSMState.ESCALATION_FREEZE.value
    )
    from mentar.safety.escalation import HANDOFF_MESSAGE_PRIMARY
    turns = _turn_logs.get(learner_uuid, [])
    return render_template(
        "parent.html",
        escalated=escalated,
        handoff_msg=HANDOFF_MESSAGE_PRIMARY,
        turns=turns,
    )


@app.route("/parent/ack", methods=["POST"])
def parent_ack():
    learner_uuid = session.get("learner_uuid", "")
    action = request.form.get("action", "resume")  # "resume" or "end"
    if learner_uuid in _controllers:
        ctrl = _controllers[learner_uuid]
        result = ctrl.step(action)
        if result.text:
            _log_turn(learner_uuid, "Mentar", result.text)
        if result.done:
            return render_template("done.html", message=result.text or "Session ended.")
    return redirect(url_for("index"))


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    print(f"Mentar pilot — http://localhost:5000")
    print(f"  LLM:  {LLM_BASE_URL}  model={LLM_MODEL}")
    print(f"  DB:   {DB_PATH}")
    print(f"  curriculum: {CURRICULUM_PATH}")
    app.run(host="127.0.0.1", port=5000, debug=False)
