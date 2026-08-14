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
    MENTAR_SESSION_ITEMS  R11 micro-session length  (default: 10 completed items; 0 = uncapped)
    SECRET_KEY            Flask session secret      (default: dev-only insecure key)
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from markupsafe import escape

from mentar.db.adapter import _DbStoreAdapter
from mentar.db.store import LearnerStore
from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.arithmetic_steps import render_steps_grid_lines
from mentar.engine.curriculum import (
    derive_subject_key,
    load_curriculum,
    load_template_meta,
    load_template_subject,
)
from mentar.engine.item_sources import build_registry
from mentar.engine.itembank import load_item_bank
from mentar.engine.itemgen import CompositeItemSource, ItemGenerator
from mentar.inference import (
    load_inference_config,
    make_llm_call,
    resolve_http_endpoint,
    upsert_dotenv_value,
    write_inference_config,
)
from mentar.tools.validate_template import validate_or_raise
from mentar.web.answer_modes import mode_for

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "mentar-dev-insecure-change-in-prod")

# ── Config ────────────────────────────────────────────────────────────────────

_REPO = Path(__file__).resolve().parents[3]  # src/mentar/web/app.py -> src -> repo root

LLM_BASE_URL = os.environ.get("MENTAR_LLM_BASE_URL", "http://localhost:11434/v1")
LLM_CRED     = os.environ.get("MENTAR_LLM_API_KEY") or "no-key"
LLM_MODEL    = os.environ.get("MENTAR_LLM_MODEL", "gemma2:9b")
DB_PATH      = os.environ.get("MENTAR_DB_PATH", str(_REPO / "mentar_pilot.db"))
PROMPT_DIR   = Path(os.environ.get("MENTAR_PROMPT_DIR", str(_REPO / "prompts")))
SCAFFOLD_DIR = Path(os.environ.get(
    "MENTAR_SCAFFOLD_DIR", str(_REPO / "curriculum" / "visual_scaffolds"),
))
CURRICULUM_PATH = Path(os.environ.get(
    "MENTAR_CURRICULUM",
    str(_REPO / "curriculum" / "templates" / "_pilot" / "fractions.md"),
))
# R11 micro-sessions: end each web session warmly after this many completed items
# (bite-sized by default; set 0 to disable the cap).
SESSION_ITEMS = int(os.environ.get("MENTAR_SESSION_ITEMS", "10") or 0)
ITEMBANK_PATH = Path(os.environ.get(
    "MENTAR_ITEMBANK",
    str(_REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl"),
))

# ── Subjects (R3.1: auto-discovered, not hand-registered) ───────────────────────
# Each subject = a curriculum template + its checkable-item source. The catalog is
# DERIVED by scanning curriculum/templates/**/*.md and reading each template's own
# front matter (label/icon/description/item_source) -- adding a year/subject is
# "drop a .md file in", not a code change here. Generators are code (can't live in
# YAML), so a template names its item source BY NAME (item_source:) and
# engine/item_sources.py's registry resolves the name -> actual generators/bank.
_TEMPLATES_DIR = _REPO / "curriculum" / "templates"
_ITEM_SOURCE_REGISTRY = build_registry(ITEMBANK_PATH)

# R8 (dormant as of R10): content-download for REMOTE packs -- content genuinely
# NOT in this repo. ONE pinned, hardcoded source, never user-supplied. Every
# authored pack now ships in-repo and is toggled locally instead (see R10 below),
# so packs.json is empty today; this machinery stays for a real future need
# (community packs, or a library too large to ship by default). A remote pack, if
# ever added, is fetched into curriculum/templates/<dir>/ (checksum-verified first).
_PACKS_BASE_URL = "https://raw.githubusercontent.com/avps82/mentar/main"
_PACKS_MANIFEST_PATH = _REPO / "curriculum" / "packs.json"

# R10: per-install curriculum enable/disable. A gitignored JSON file holds the
# set of subject keys a family has turned OFF -- so every in-repo pack ships
# discoverable (no download step for content already on disk) but a parent can
# hide the ones that don't apply to their child. Disabled packs are simply
# skipped during startup discovery, so the toggle is applied on the next
# restart (deliberate -- discovery is scan-once-at-startup; see R8's same note).
# Env-overridable (like MENTAR_DB_PATH) so a deployment can relocate it and tests
# can point it at a scratch file BEFORE discovery reads it.
_PACK_STATE_PATH = Path(
    os.environ.get("MENTAR_PACK_STATE", str(_REPO / "curriculum" / "pack_state.json"))
)


def _load_disabled_packs() -> set[str]:
    import json
    if not _PACK_STATE_PATH.exists():
        return set()
    try:
        data = json.loads(_PACK_STATE_PATH.read_text(encoding="utf-8"))
        return set(data.get("disabled", []))
    except Exception:
        return set()  # a corrupt state file must never break startup -- default to all-enabled


def _save_disabled_packs(disabled: set[str]) -> None:
    import json
    _PACK_STATE_PATH.write_text(
        json.dumps({"disabled": sorted(disabled)}, indent=2) + "\n", encoding="utf-8"
    )


def _discover_template_paths() -> list[Path]:
    # OKF reserved filenames (index.md, log.md) are bundle metadata, not templates.
    paths = sorted(p for p in _TEMPLATES_DIR.glob("**/*.md") if p.name not in ("index.md", "log.md"))
    # MENTAR_CURRICULUM env override (CLI/tests) replaces whichever discovered
    # path IS the default pilot fractions template -- preserves the existing
    # override point (tests/web/test_startup_validation.py points this at a
    # deliberately cyclic fixture to prove A16 validation still runs).
    default_fractions = (_TEMPLATES_DIR / "_pilot" / "fractions.md").resolve()
    return [CURRICULUM_PATH if p.resolve() == default_fractions else p for p in paths]


_DISABLED_PACKS = _load_disabled_packs()
SUBJECTS: dict[str, dict] = {}
for _path in _discover_template_paths():
    _meta = load_template_meta(_path)
    # derive_subject_key: fully automatic (directory = namespace) — no
    # per-template authoring step. See its docstring for the rule.
    _key = derive_subject_key(_path, _meta)
    if _key in _DISABLED_PACKS:
        continue  # R10: a family turned this curriculum off -- skip it entirely.
    # A16: validate BEFORE anything else touches this template — a cyclic/bad-
    # prereq template silently produces an empty fringe and a false "you've
    # mastered everything!" completion for the child. Fail loud at startup.
    validate_or_raise(_path)
    _source_name = _meta["item_source"]
    if _source_name not in _ITEM_SOURCE_REGISTRY:
        raise RuntimeError(
            f"template {_path} names item_source={_source_name!r}, which is not "
            f"in the registry ({sorted(_ITEM_SOURCE_REGISTRY)}) — add it to "
            "engine/item_sources.py or fix the template's item_source: field."
        )
    _source = _ITEM_SOURCE_REGISTRY[_source_name]
    SUBJECTS[_key] = {
        "label": _meta["label"] or _key,
        "icon": _meta["icon"] or "",
        "description": _meta["description"] or "",
        "year_level": _meta["year_level"],
        "country": _meta["country"],
        "curriculum": _path,
        "itembank": _source["itembank"],
        "generators": _source["generators"],
    }
DEFAULT_SUBJECT = "fractions"
_SUBJECT_CURRICULA = {k: load_curriculum(v["curriculum"]) for k, v in SUBJECTS.items()}
# A7: each subject's template `subject:` field, fed into the system prompt so a
# science session doesn't inherit the (formerly hardcoded) "fractions" text.
_SUBJECT_NAMES = {k: load_template_subject(v["curriculum"]) for k, v in SUBJECTS.items()}
# R6.2: one skill_id -> label lookup across EVERY loaded curriculum (safe to
# merge: R3.1's directory-namespace prefixing guarantees no id collisions
# across subjects). skill_id is a machine key, never shown to a human; every
# human-facing surface renders display_name, computed once via _display_name()
# below, never re-derived per-template (was 4 inconsistent strategies).
_ALL_NODE_LABELS = {
    nid: node.get("label", nid)
    for curriculum in _SUBJECT_CURRICULA.values()
    for nid, node in curriculum.items()
}


def _display_name(skill_id: str) -> str:
    return _ALL_NODE_LABELS.get(skill_id, skill_id)


def _subject_groups() -> list[tuple[str, list[str]]]:
    """R3.1: Year > Subject grouping for the picker/progress switcher (R3.2) —
    computed from the scan, not hand-maintained. Real years sort ascending;
    "pilot" (no fixed year level) sorts last as a "Try-out topics" group."""
    by_year: dict[str, list[str]] = {}
    for key, cfg in SUBJECTS.items():
        by_year.setdefault(cfg["year_level"] or "pilot", []).append(key)

    def _sort_key(year: str) -> tuple[int, str]:
        return (1, "") if year == "pilot" else (0, year)

    groups = []
    for year in sorted(by_year, key=_sort_key):
        keys = by_year[year]
        country = next((SUBJECTS[k]["country"] for k in keys if SUBJECTS[k]["country"]), None)
        label = "Try-out topics" if year == "pilot" else (f"{year} ({country})" if country else year)
        groups.append((label, keys))
    return groups


SUBJECT_GROUPS: list[tuple[str, list[str]]] = _subject_groups()
_learner_subject: dict[str, str] = {}   # learner_uuid -> active subject key

# Inference backend: prefer config/inference.yaml (the canonical, backend-agnostic
# source — llamacpp/vllm/ollama). Fall back to the legacy MENTAR_LLM_* env vars so an
# existing env-only setup keeps working (treated as an OpenAI-compatible endpoint).
_INFERENCE_CONFIG_PATH = _REPO / "config" / "inference.yaml"
_INFERENCE_CFG: dict = {}
_GROUNDING_CFG: dict = {}  # ZIM reader config (W7)
# The endpoint the app will ACTUALLY call (yaml or env fallback, local or remote) --
# the settings page's reachability check must test this, never a parallel default.
# None = in-process llamacpp (no HTTP endpoint to probe).
_LLM_STATUS_ENDPOINT: dict | None = None

# Built lazily: an in-process llama.cpp backend loads the GGUF on construction, so we
# defer it until the first turn (keeps `import mentar.web.app` cheap for tests/CLI reuse).
_llm_call_cached = None

# R9: setup gate. A missing OR unreachable backend redirects every route to /setup
# (see _require_setup below) instead of letting a family reach a picker that will
# just fail confusingly once they try to start a lesson. Cached briefly so the
# common (healthy backend) case doesn't add a live network probe to every request.
_SETUP_GATE_BYPASS = False  # tests set this True -- see tests/web/*.py _client()
_SETUP_GATE_CACHE: dict = {"ok": None, "checked_at": 0.0}
_SETUP_GATE_TTL_S = 30.0


def _reload_inference_config() -> None:
    """(Re-)read config/inference.yaml and reset every cached derivative.
    Called at import time AND after /setup writes a new config -- no
    restart needed either time, because _llm_call below is a stable
    indirection that lazily rebuilds _llm_call_cached from _INFERENCE_CFG
    on its NEXT call, and every session already holds a reference to
    _llm_call itself, never a snapshot of the config."""
    global _INFERENCE_CFG, _GROUNDING_CFG, _LLM_STATUS_ENDPOINT, _llm_call_cached
    # Explicit path, not load_inference_config()'s own no-arg default -- must
    # read the SAME file _setup_is_complete()/write_inference_config() use
    # (_INFERENCE_CONFIG_PATH), not a second, independently-computed default
    # that only coincidentally matches it in production. An explicit path
    # that doesn't exist raises, unlike the no-arg form -- guard it here.
    _INFERENCE_CFG = load_inference_config(_INFERENCE_CONFIG_PATH) if _INFERENCE_CONFIG_PATH.exists() else None
    if _INFERENCE_CFG is None:
        _INFERENCE_CFG = {
            "backend": "vllm",
            "vllm": {"base_url": LLM_BASE_URL, "api_key": LLM_CRED, "model": LLM_MODEL},
        }
    _GROUNDING_CFG = _INFERENCE_CFG.get("grounding", {})
    _LLM_STATUS_ENDPOINT = resolve_http_endpoint(_INFERENCE_CFG)
    _llm_call_cached = None
    _SETUP_GATE_CACHE["ok"] = None
    _SETUP_GATE_CACHE["checked_at"] = 0.0


_reload_inference_config()


def _llm_call(messages: list[dict]) -> str:
    global _llm_call_cached
    if _llm_call_cached is None:
        _llm_call_cached = make_llm_call(_INFERENCE_CFG)
    return _llm_call_cached(messages)


def _probe_llm_backend(endpoint: dict, deep: bool = False) -> tuple[bool, int, str | None]:
    """Probe an OpenAI-compatible endpoint. Deliberately a much shorter timeout
    than the app's own generation calls (see make_llm_call's config), so an
    unreachable backend can't hang a page load.

    Two depths, because the setup gate and the Settings status line are asking
    genuinely different questions:

    * shallow (default, the setup gate) -- `models.list()`: is there a server
      here at all? A routing decision on every request, so it must stay cheap.
    * deep (/settings/llm-status) -- a 1-token chat completion against the
      CONFIGURED model, exactly the call a lesson makes. 2026-08-14
      (maintainer): with the model unloaded the status line still showed green,
      because a gateway (llama-swap/llama.cpp server/LiteLLM) answers
      `models.list()` from its catalog whether or not anything is loaded. Only
      asking it to generate proves a lesson would work. Longer timeout: this
      request may trigger a cold model load (12-60s on the eval host).
    """
    import time as _time

    from openai import OpenAI

    start = _time.monotonic()
    try:
        client = OpenAI(
            base_url=endpoint["base_url"], api_key=endpoint["api_key"],
            timeout=60.0 if deep else 5.0,
        )
        client.models.list()
        if deep:
            resp = client.chat.completions.create(
                model=endpoint["model"],
                messages=[{"role": "user", "content": "Say OK."}],
                max_tokens=1,
            )
            if not resp.choices:
                raise RuntimeError(f"model {endpoint['model']} returned no choices")
        return True, round((_time.monotonic() - start) * 1000), None
    except Exception as exc:
        return False, round((_time.monotonic() - start) * 1000), str(exc)


def _setup_is_complete() -> bool:
    """Whether a working LLM backend is configured. False when
    config/inference.yaml doesn't exist at all (fresh install) OR when it
    exists but the backend fails the SAME reachability probe /settings/
    llm-status uses (an in-process llamacpp backend has no HTTP endpoint to
    probe, so its mere presence counts as configured). Cached for
    _SETUP_GATE_TTL_S -- a fresh install/broken backend is a real,
    persistent state, not something worth re-probing on every request."""
    if _SETUP_GATE_BYPASS:
        return True
    import time as _time
    now = _time.monotonic()
    if _SETUP_GATE_CACHE["ok"] is not None and now - _SETUP_GATE_CACHE["checked_at"] < _SETUP_GATE_TTL_S:
        return _SETUP_GATE_CACHE["ok"]

    ok = False
    if _INFERENCE_CONFIG_PATH.exists():
        if _LLM_STATUS_ENDPOINT is None:
            ok = True  # in-process backend -- no HTTP endpoint to probe, trust it
        else:
            ok, _latency, _error = _probe_llm_backend(_LLM_STATUS_ENDPOINT)
    _SETUP_GATE_CACHE["ok"] = ok
    _SETUP_GATE_CACHE["checked_at"] = now
    return ok


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
        # R-RES: a session a server-process restart interrupted is still "open"
        # (ended_at IS NULL) in the DB. Reuse its id + checkpoint ONLY when the
        # checkpointed node actually belongs to THIS subject's curriculum -- a
        # learner's open session could be for a different subject entirely (they
        # switched topics and never explicitly ended the old one), and reusing that
        # session_id here would wrongly mix two subjects' rows under one id.
        # NOTE: even pre-R-RES, switching subjects already discards/bypasses a frozen
        # SAME-PROCESS controller (the `_learner_subject` check above pops it) -- an
        # escalation freeze has always been per-subject, not global. Gating resume on
        # curriculum membership keeps that behaviour identical across a restart: a
        # frozen Maths session resumes frozen when Maths is reopened, but doesn't
        # block a family from opening English.
        resume_session_id, resume_checkpoint = None, None
        open_session = store.get_open_session(db_id)
        if open_session is not None and open_session["checkpoint_state"]:
            try:
                cp = json.loads(open_session["checkpoint_state"])
            except (ValueError, TypeError):
                cp = None
            if cp and cp.get("current_node_id") in _SUBJECT_CURRICULA[subject]:
                resume_session_id, resume_checkpoint = open_session["id"], cp
        _controllers[learner_uuid] = SessionController(
            llm_call=_llm_call,
            prompt_dir=PROMPT_DIR,
            scaffold_dir=SCAFFOLD_DIR,
            grounding_cfg=_GROUNDING_CFG,
            curriculum=_SUBJECT_CURRICULA[subject],
            db_store=_DbStoreAdapter(store, db_id),
            learner_id=learner_uuid,
            item_bank=item_source,
            subject=_SUBJECT_NAMES[subject],
            max_items=SESSION_ITEMS or None,
            session_id=resume_session_id,
            resume_checkpoint=resume_checkpoint,
        )
        _turn_logs[learner_uuid] = []
    return _controllers[learner_uuid]


# HTML templates live in src/mentar/web/templates/ (learner.html, done.html, parent.html).


# ── Routes ────────────────────────────────────────────────────────────────────

@app.before_request
def _require_setup():
    """R9: every route redirects to /setup while no working LLM backend is
    configured -- a family should never reach a picker that will just fail
    confusingly the moment they try to start a lesson."""
    if request.endpoint in ("setup", "setup_save", "static"):
        return None
    if not _setup_is_complete():
        return redirect(url_for("setup"))
    return None


@app.route("/setup")
def setup():
    """R9: the first-run gate's destination -- never itself gated."""
    return render_template("setup.html", result=None)


@app.route("/setup", methods=["POST"])
def setup_save():
    """R9: writes config/inference.yaml (+ a gitignored .env for a remote API
    key -- NEVER inlined in the yaml, same ${VAR} convention used everywhere
    else in this codebase), reloads live (no restart -- see
    _reload_inference_config), and immediately re-probes so the parent gets
    an instant answer instead of a guess."""
    import time

    backend = request.form.get("backend", "").strip()
    base_url = request.form.get("base_url", "").strip()
    model = request.form.get("model", "").strip()
    api_key = (request.form.get("api_key", "")).strip()

    if backend not in ("ollama", "vllm") or not base_url or not model:
        return render_template("setup.html", result={"ok": False, "error": "Please fill in all fields."})

    cfg: dict = {"backend": backend, backend: {"base_url": base_url, "model": model}}
    if backend == "vllm":
        if api_key:
            upsert_dotenv_value(_INFERENCE_CONFIG_PATH.parent / ".env", "MENTAR_VLLM_API_KEY", api_key)
            cfg["vllm"]["api_key"] = "${MENTAR_VLLM_API_KEY}"
        else:
            cfg["vllm"]["api_key"] = "no-key"

    write_inference_config(cfg, _INFERENCE_CONFIG_PATH)
    _reload_inference_config()

    if _LLM_STATUS_ENDPOINT is None:
        ok, error = True, None  # in-process backend -- nothing to probe, trust it
    else:
        ok, _latency, error = _probe_llm_backend(_LLM_STATUS_ENDPOINT)
    _SETUP_GATE_CACHE["ok"] = ok
    _SETUP_GATE_CACHE["checked_at"] = time.monotonic()

    if ok:
        return redirect(url_for("index"))
    return render_template("setup.html", result={"ok": False, "error": f"Saved, but couldn't connect: {error}"})


@app.route("/")
def index():
    """R4: picker-only, unconditionally -- no subject/controller logic here at
    all, so a long-lived cookie with a stale subject key (a past dev test, a
    prior day's session, or a server restart that wiped _controllers/_turn_logs
    while the cookie survived) can never silently resume into a quiz. The
    actual lesson view lives at /learn now."""
    learner_uuid = session.get("learner_uuid")
    if not learner_uuid:
        learner_uuid = str(uuid.uuid4())
        session["learner_uuid"] = learner_uuid
    return render_template(
        "subjects.html", subjects=SUBJECTS, subject_groups=SUBJECT_GROUPS,
        subjects_progress=_subjects_progress(learner_uuid),
    )


@app.route("/learn")
def learn():
    """R4: everything index() used to do AFTER the subject-chosen check,
    moved here unchanged. Reached only via /choose, /answer's non-htmx
    redirect, or /parent/ack's resume redirect -- never a bare picker miss."""
    learner_uuid = session.get("learner_uuid")
    if not learner_uuid:
        learner_uuid = str(uuid.uuid4())
        session["learner_uuid"] = learner_uuid

    subject = session.get("subject")
    if subject not in SUBJECTS:
        # No topic chosen (or a stale cookie) -- the picker is the only safe place to send this.
        return redirect(url_for("index"))

    ctrl = _get_or_create_controller(learner_uuid, subject)

    if ctrl.state == FSMState.ESCALATION_FREEZE.value:
        # Absorbing state — every child-facing render goes to the frozen page,
        # not just the turn that triggered it (A8).
        return redirect(url_for("frozen"))

    if ctrl.is_terminal:
        # A stale GET on an already-ended session (browser back after Stop, a
        # bookmarked /learn link, a plain refresh) previously fell straight
        # through to the live-turn render below with no question to show and
        # no answer to accept -- the goodbye message next to a still-live
        # input box + Help/Stop buttons a maintainer screenshot flagged
        # 2026-08-12. The done screen is the only sensible landing here; the
        # POST /answer and first-turn paths already redirect there the same
        # way on the turn that actually ends the session.
        _done_messages.setdefault(learner_uuid, _last_messages.get(learner_uuid) or "Session ended.")
        return redirect(url_for("done"))

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
    # R12-fix2: current_mastery now comes from _turn_context (inside the htmx
    # swap target) — no separate kwarg, or the two copies could disagree.
    return render_template(
        "learner.html", subject_label=SUBJECTS[subject]["label"],
        **_turn_context(learner_uuid, ctrl, is_first_turn=is_first_turn),
    )


@app.route("/choose", methods=["GET", "POST"])
def choose():
    """Subject picker: GET shows the topics, POST selects one and starts it."""
    if request.method == "POST":
        subject = request.form.get("subject")
        if subject in SUBJECTS:
            session["subject"] = subject
        return redirect(url_for("learn"))
    return render_template(
        "subjects.html", subjects=SUBJECTS, subject_groups=SUBJECT_GROUPS,
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

    ctrl = _controllers[learner_uuid]
    # R2.3: the answer-mode registry owns how the posted form composes into the
    # ONE string ctrl.step() accepts (e.g. fraction's num/den -> "n/d") — one
    # owned place instead of a type-specific if/elif here.
    answer_text = mode_for(ctrl.current_answer_type).compose(request.form)
    _log_turn(learner_uuid, "Child", answer_text)

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
    return redirect(url_for("learn"))


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
            "skills_touched": sorted(_display_name(sid) for sid in {r["skill_id"] for r in responses}),
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


@app.route("/settings")
def settings():
    """R5: voice picker + the relocated theme picker. Purely static -- the
    voice list is client-side only (speechSynthesis.getVoices() can't be
    queried server-side), so this route has no controller/session logic."""
    return render_template("settings.html")


# Theme names must match the [data-theme] blocks in style.css AND theme.js's
# THEMES registry. Only the gallery needs them server-side (the real picker
# renders from the JS registry), so this stays a plain list rather than a
# second source of truth: tests/web/test_theme_tokens.py checks the CSS side,
# and the gallery smoke test checks this list resolves.
_GALLERY_THEMES = ("light", "dark", "ocean", "space", "forest", "sunshine")


@app.route("/gallery")
def gallery():
    """DEV-ONLY theme gallery (2026-08-14): every component on one page so a
    theme review is one screenshot instead of five screens.

    Gated behind MENTAR_DEV_GALLERY=1 and 404s otherwise -- it is a design
    tool, and a family's install should never be able to reach a page full of
    fake questions and fake feedback. Read at request time (not import time)
    so a test can toggle it without reimporting the module.

    The theme comes from ?theme= and is stamped server-side by the template,
    so a headless screenshot needs no JS interaction. An unknown name falls
    back to light rather than rendering an unstyled page."""
    if os.environ.get("MENTAR_DEV_GALLERY") != "1":
        return ("Not found", 404)
    theme = request.args.get("theme", "light")
    if theme not in _GALLERY_THEMES:
        theme = "light"
    return render_template("gallery.html", theme=theme, theme_names=_GALLERY_THEMES)


@app.route("/settings/llm-status")
def settings_llm_status():
    """R7.2: a short-timeout reachability check against the SAME endpoint the
    app's own LLM calls resolve to (_LLM_STATUS_ENDPOINT, from
    config/inference.yaml or the env fallback -- local or remote, one config,
    one truth) -- via the same _probe_llm_backend the setup gate uses, so the
    two can never disagree about what "working" means."""
    if _LLM_STATUS_ENDPOINT is None:
        # In-process llamacpp (or an unprobeable backend): there is no HTTP
        # endpoint to check -- report that honestly instead of green/red.
        return jsonify({
            "ok": None,
            "model": None,
            "base_url": None,
            "latency_ms": 0,
            "error": "In-process model -- no HTTP endpoint to check.",
        })

    # deep=True: prove the configured MODEL generates, not just that a server
    # answers -- an unloaded model showed green before (2026-08-14).
    ok, latency_ms, error = _probe_llm_backend(_LLM_STATUS_ENDPOINT, deep=True)
    return jsonify({
        "ok": ok,
        "model": _LLM_STATUS_ENDPOINT["model"],
        "base_url": _LLM_STATUS_ENDPOINT["base_url"],
        "latency_ms": latency_ms,
        "error": error,
        "checked_at": time.strftime("%H:%M:%S"),
    })


def _load_packs_manifest() -> list[dict]:
    import json
    data = json.loads(_PACKS_MANIFEST_PATH.read_text(encoding="utf-8"))
    return data.get("packs", [])


def _is_safe_path_component(name: str) -> bool:
    """Defense in depth: pack "dir"/file "name" values come from packs.json (repo-
    controlled, not directly user-supplied), but they still end up in filesystem
    paths -- reject anything that isn't a plain single path segment before it's
    ever joined onto a real path, same discipline as the checksum verification
    below (never trust, always verify, even a source we mostly control)."""
    return bool(name) and "/" not in name and "\\" not in name and name not in (".", "..")


def _grade_sort_key(year_level: str | None) -> tuple[int, int | str]:
    """Numeric sort for a free-text year_level ("Year 10", "Class 2", "pilot").

    Plain string sort put "Year 10/11/12" before "Year 2" (lexicographic: "1" <
    "2") -- the exact bug a maintainer screenshot flagged 2026-08-12 on the
    Settings page. Extract the trailing number and sort on that; a non-numeric
    level (only "pilot" today, always under the "General" country group so it
    never collides with a real grade) sorts after every numbered grade.
    """
    if not year_level:
        return (1, "")
    digits = "".join(ch for ch in year_level if ch.isdigit())
    return (0, int(digits)) if digits else (1, year_level)


def _all_packs_with_state() -> list[dict]:
    """R10: every in-repo curriculum pack (discovered template), with its current
    on/off state -- INCLUDING disabled ones (which SUBJECTS excludes), so the
    Settings toggle list can show them for re-enabling. `enabled` reflects the
    live _DISABLED_PACKS set (updated on toggle); whether that state is actually
    APPLIED to the picker waits for the next restart (discovery is at startup).

    Sort is Country -> Grade -> Subject (maintainer ask 2026-08-12, matching how
    the Settings page groups them): country groups form at the JS layer, so the
    ordering here only needs grade-then-subject within a country.
    """
    out = []
    for path in _discover_template_paths():
        try:
            meta = load_template_meta(path)
            key = derive_subject_key(path, meta)
        except Exception:
            continue  # a malformed template shouldn't break the whole listing
        out.append({
            "key": key,
            "label": meta["label"] or key,
            "description": meta["description"] or "",
            "country": meta["country"],
            "year_level": meta["year_level"],
            "subject": meta["subject"] or "",
            "enabled": key not in _DISABLED_PACKS,
        })
    out.sort(key=lambda p: (p["country"] or "", _grade_sort_key(p["year_level"]), p["subject"], p["key"]))
    return out


@app.route("/settings/curricula")
def curricula_list():
    """R10: list every in-repo pack with its on/off state, for the Settings
    toggle UI. Local-disk only, no network."""
    return jsonify({"curricula": _all_packs_with_state()})


@app.route("/settings/curricula/<key>/<action>", methods=["POST"])
def curricula_toggle(key, action):
    """R10: enable/disable one in-repo pack. Updates the gitignored
    pack_state.json AND the in-memory _DISABLED_PACKS so the listing reflects
    it at once; the picker itself updates on the next restart (discovery is
    scan-once-at-startup -- same restart note R8 uses)."""
    if action not in ("enable", "disable"):
        return jsonify({"ok": False, "error": "unknown action"}), 404
    known = {p["key"] for p in _all_packs_with_state()}
    if key not in known:
        return jsonify({"ok": False, "error": "unknown curriculum"}), 404

    if action == "disable":
        _DISABLED_PACKS.add(key)
    else:
        _DISABLED_PACKS.discard(key)
    _save_disabled_packs(_DISABLED_PACKS)
    return jsonify({"ok": True, "enabled": key not in _DISABLED_PACKS, "restart_required": True})


@app.route("/settings/curricula/country/<country>/<action>", methods=["POST"])
def curricula_toggle_country(country, action):
    """The country-level master switch behind the Settings curriculum tabs
    (maintainer ask 2026-08-14: one tab per country, its on/off switch first,
    grades under it). Server-side because a country holds up to 25 packs --
    one call and ONE state-file write, not 25 POSTs and 25 writes from the
    browser. `country` is the group name the listing groups by, so the
    country-less pilot/practice packs are addressed as "General".
    """
    if action not in ("enable", "disable"):
        return jsonify({"ok": False, "error": "unknown action"}), 404
    keys = [p["key"] for p in _all_packs_with_state() if (p["country"] or "General") == country]
    if not keys:
        return jsonify({"ok": False, "error": "unknown country"}), 404

    if action == "disable":
        _DISABLED_PACKS.update(keys)
    else:
        _DISABLED_PACKS.difference_update(keys)
    _save_disabled_packs(_DISABLED_PACKS)
    return jsonify({
        "ok": True, "enabled": action == "enable", "count": len(keys), "restart_required": True,
    })


@app.route("/settings/curriculum-packs")
def curriculum_packs():
    """R8 (dormant): list downloadable REMOTE packs (curriculum/packs.json) with
    install status -- empty today (every authored pack ships in-repo and is
    toggled via /settings/curricula instead). Local-disk only, no network."""
    packs = []
    for p in _load_packs_manifest():
        if not _is_safe_path_component(p.get("dir", "")):
            continue
        installed = (_TEMPLATES_DIR / p["dir"]).exists()
        packs.append({
            "id": p["id"], "label": p["label"], "description": p["description"],
            "licence": p["licence"], "installed": installed,
        })
    return jsonify({"packs": packs})


@app.route("/settings/curriculum-packs/<pack_id>/install", methods=["POST"])
def install_curriculum_pack(pack_id):
    """R8: fetch every file for one pack over HTTPS from the ONE pinned base URL,
    verify EVERY file's sha256 against the manifest BEFORE any write happens
    (all-or-nothing -- a checksum mismatch on file 2 must not leave file 1
    written), then copy into curriculum/templates/<dir>/. Content is markdown/
    YAML template data, parsed by the existing yaml.safe_load path elsewhere --
    never executed. Restart is required for the new pack to appear in the
    picker (R3.1's auto-discovery scans once at startup, not per-request)."""
    import hashlib
    import urllib.request

    pack = next((p for p in _load_packs_manifest() if p.get("id") == pack_id), None)
    if pack is None:
        return jsonify({"ok": False, "error": "unknown pack"}), 404
    if not _is_safe_path_component(pack.get("dir", "")):
        return jsonify({"ok": False, "error": "invalid pack manifest entry"}), 500

    dest_dir = _TEMPLATES_DIR / pack["dir"]
    if dest_dir.exists():
        return jsonify({"ok": False, "error": "already installed"}), 400

    downloaded: dict[str, bytes] = {}
    for f in pack.get("files", []):
        if not _is_safe_path_component(f.get("name", "")):
            return jsonify({"ok": False, "error": "invalid pack manifest entry"}), 500
        url = f"{_PACKS_BASE_URL}/curriculum/remote_packs/{pack['dir']}/{f['name']}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310 -- pinned base, HTTPS only
                content = resp.read()
        except Exception as exc:
            return jsonify({"ok": False, "error": f"download failed for {f['name']}: {exc}"}), 502
        digest = hashlib.sha256(content).hexdigest()
        if digest != f["sha256"]:
            return jsonify({"ok": False, "error": f"checksum mismatch for {f['name']}"}), 502
        downloaded[f["name"]] = content

    # Every file verified -- now write. Nothing was written above; a failure at
    # any point before this line leaves the local filesystem untouched.
    dest_dir.mkdir(parents=True, exist_ok=True)
    for name, content in downloaded.items():
        (dest_dir / name).write_bytes(content)

    return jsonify({"ok": True, "restart_required": True})


@app.route("/settings/curriculum-packs/<pack_id>/uninstall", methods=["POST"])
def uninstall_curriculum_pack(pack_id):
    """R8: removes the pack's curriculum/templates/<dir>/ so it stops being
    discovered -- the child's skill_state DB rows for that pack's node ids are
    a SEPARATE table, keyed by skill_id, never touched by this (preserve-by-
    default, no code needed beyond simply not touching the DB). A future,
    separate, harder-to-reach "also erase this child's history" action is
    explicitly NOT built here (REMAINDER_PLAN.md R8.1)."""
    import shutil

    pack = next((p for p in _load_packs_manifest() if p.get("id") == pack_id), None)
    if pack is None:
        return jsonify({"ok": False, "error": "unknown pack"}), 404
    if not _is_safe_path_component(pack.get("dir", "")):
        return jsonify({"ok": False, "error": "invalid pack manifest entry"}), 500

    dest_dir = _TEMPLATES_DIR / pack["dir"]
    if not dest_dir.exists():
        return jsonify({"ok": False, "error": "not installed"}), 400

    shutil.rmtree(dest_dir)
    return jsonify({"ok": True, "restart_required": True})


_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"\*(.+?)\*")
# A workstream (2026-08-10): fenced ```...``` blocks are the ONE house convention for
# ASCII diagrams (curriculum/visual_scaffolds/*.md, help prompts) -- everything else in
# markdown-lite stays a 4-tag whitelist, but a fence's content must render in a
# monospace <pre>, not fall through to the proportional-font prose path (that was the
# actual root cause of "diagrams look broken" -- this function had no fence handling at
# all, so a model that copied a scaffold's fenced exemplar produced literal backticks
# wrapped around misaligned ASCII in the child's browser). Optional language tag after
# the opening ``` (e.g. "```text") is accepted and discarded, though nothing in this
# codebase's own scaffolds currently uses one.
_FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def _render_markdown_lite(text: str) -> str:
    """U-32: HTML-escape first (the security property), then insert ONLY 5
    whitelisted tags (<strong>/<em>/<ul>/<li>/<pre>) over the now-safe text --
    no third-party markdown lib, no other tag ever gets emitted. Fenced
    ```...``` blocks are extracted FIRST (before the per-line bullet/bold/
    italic pass, which must never run across a fence's own content) and
    rendered as a single <pre class="ascii-art"> block; everything outside a
    fence goes through the original line-by-line treatment. Bullet markers
    are stripped line-by-line BEFORE the bold/italic regexes run so a leading
    "* " (bullet) is never mistaken for an italic delimiter; bold (**x**) is
    substituted before italic (*x*) so a bold span's stars are consumed first.
    Segments are joined WITHOUT a "\\n" between block tags (<ul>/<li>/</ul>/
    <pre>) -- .question uses white-space:pre-wrap, so a raw newline next to a
    block element would render as a stray visible gap; "\\n" is only kept
    between two genuine prose lines, to preserve intentional line breaks.
    Safe to mark `| safe` in Jinja: every character that reaches an HTML tag
    boundary either came from escape() or from a literal string in this
    function, never from unescaped model/generator output -- fence content is
    already inside `escaped` (the whole input is escaped up front, before
    fence extraction), so wrapping it in <pre> needs no separate escaping."""
    escaped = str(escape(text))
    segments: list[tuple[bool, str]] = []  # (is_block_markup, content)
    in_list = False

    def _process_prose(chunk: str) -> None:
        nonlocal in_list
        for line in chunk.split("\n"):
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

    pos = 0
    for m in _FENCE_RE.finditer(escaped):
        _process_prose(escaped[pos:m.start()])
        if in_list:
            segments.append((True, "</ul>"))
            in_list = False
        fence_body = m.group(1).rstrip("\n")
        segments.append((True, f'<pre class="ascii-art">{fence_body}</pre>'))
        pos = m.end()
    _process_prose(escaped[pos:])
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


def _wrap_label(label: str, max_chars: int = 16, max_lines: int = 3) -> list[str]:
    """R2.4: greedy word-wrap for the concept-graph SVG labels -- never cuts a
    word mid-way (a longer-than-max_chars word gets its own line, kept whole).
    Truncates to max_lines with a trailing "…" only when words were actually
    dropped. The full label is still shown via the node's hover tooltip."""
    if not label or label.isspace():
        return [""]
    words = label.split()
    if not words:
        return [""]
    lines = []
    current_line = ""
    for word in words:
        if not current_line:
            current_line = word
        elif len(current_line) + 1 + len(word) <= max_chars:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    if len(lines) > max_lines:
        truncated = lines[:max_lines]
        last_line = truncated[-1]
        if not last_line.endswith("…"):
            truncated[-1] = last_line + "…"
        return truncated
    return lines


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
    base_height = max(n_levels * 26, 26)
    row_height = base_height / n_levels
    BOTTOM_MARGIN = 24  # circle radius (4) + up to 3 wrapped label lines (~16) + descender slack, so the last row's content never sits flush against the viewBox edge
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
            label = curriculum[node_id].get("label", node_id)
            nodes.append({
                "id": node_id,
                "label": label,
                "label_lines": _wrap_label(label),
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

    return {"nodes": nodes, "edges": edges, "height": base_height + BOTTOM_MARGIN}


@app.route("/progress")
def progress():
    """R3.2: a year/subject switcher (?subject=<key>) on top of the concept
    map + skill list -- the star-card list is now FILTERED to the selected
    subject's own node ids (was: every subject's skill_state rows mixed into
    one undifferentiated list, a real defect exposed once the AU templates
    added a second/third curriculum's worth of nodes)."""
    learner_uuid = session.get("learner_uuid", "")
    requested = request.args.get("subject")
    subject = requested if requested in SUBJECTS else (session.get("subject") or DEFAULT_SUBJECT)

    store, db_id = _store_and_id(learner_uuid)
    skill_states = store.all_skill_states(db_id) if (store and db_id is not None) else []
    curriculum = _SUBJECT_CURRICULA.get(subject, {})
    # Convert sqlite3.Row to plain dicts, filtered to THIS subject's nodes only.
    skills = [dict(r) for r in skill_states if r["skill_id"] in curriculum]
    for s in skills:
        s["display_name"] = _display_name(s["skill_id"])
    node_pct = {s["skill_id"]: int(s["p_mastery"] * 100) for s in skills}
    graph = _compute_graph_layout(curriculum, node_pct) if curriculum else None

    return render_template(
        "progress.html", skills=skills, graph=graph,
        subject=subject, subjects=SUBJECTS, subject_groups=SUBJECT_GROUPS,
        subjects_progress=_subjects_progress(learner_uuid),
    )


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
        for s in skill_states:
            s["display_name"] = _display_name(s["skill_id"])
        responses = store.session_responses(db_id, session_id)
        help_events = store.session_help_events(db_id, session_id)
        for r in responses:
            r["display_name"] = _display_name(r["skill_id"])
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
    return redirect(url_for("learn"))


# ── Helpers ───────────────────────────────────────────────────────────────────

# DB transcript role -> parent-facing display label.
_ROLE_DISPLAY = {"learner": "Child", "tutor": "Mentar", "system": "System"}


def _store_and_id(learner_uuid: str) -> tuple[LearnerStore | None, int | None]:
    return _stores.get(learner_uuid), _db_learner_ids.get(learner_uuid)


def _elaborate_display_lines(ctrl: SessionController) -> list[dict] | None:
    """"Show human working" (step grids) + explain-mode (method cards, 2026-08-12)
    render through the SAME `_arithmetic_steps.html` partial -- both are
    computed, non-LLM, line-oriented monospace content. A node is step-grid- or
    method-card-eligible, never both, so this is a plain either/or, not a merge.
    Method-card lines render at the normal size (is_annotation=False) but WRAP
    (steps_wrap below) -- they are prose, not aligned columns, and 2026-08-14
    showed a percentage card's question line clipped mid-word by the step
    grid's overflow-x:hidden."""
    if ctrl.elaborate_steps_grid is not None:
        return render_steps_grid_lines(ctrl.elaborate_steps_grid)
    if ctrl.elaborate_method_card is not None:
        return [{"text": line, "is_annotation": False} for line in ctrl.elaborate_method_card]
    return None


def _turn_context(learner_uuid: str, ctrl: SessionController, is_first_turn: bool = False) -> dict:
    """Template context for the _turn.html partial: the STRUCTURED message and
    question fields (TurnResult.message / .question — never string-split from
    prose), both rendered through the same markdown-lite (U-32), plus the
    answer-widget metadata driven by the R2.3 answer-mode registry."""
    message = _last_messages.get(learner_uuid, "")
    choices = ctrl.current_choices
    mode = mode_for(ctrl.current_answer_type)
    # R2.1 (now owned by the mode registry): a structured stem + no format-hint
    # mode (mc4) shows JUST the stem -- the radios make the answer shape
    # obvious. Anything else keeps the full question_display (unchanged).
    stem = ctrl.current_question_stem
    show_stem = choices and stem and not mode.show_format_hint
    question = (stem if show_stem else ctrl.question_display) or "Ready when you are!"
    return {
        "message_html": _render_markdown_lite(message) if message else "",
        "question_html": _render_markdown_lite(question),
        "is_first_turn": is_first_turn,
        "answer_type": ctrl.current_answer_type,
        "widget": mode.widget,
        "choices": choices,
        "choice_letters": ["A", "B", "C", "D"][: len(choices)] if choices else [],
        # R12.5: show the "💡 Explain more" button while an explanation is live.
        "can_elaborate": ctrl.can_elaborate,
        # "Show human working": deterministic step grid for step-eligible nodes
        # (add/sub/mult/div). None for anything else -- template shows nothing.
        # Rendered to plain monospace lines (2026-07-24/25) for a <pre> block --
        # replaces the earlier per-cell CSS Grid divs. steps_lines carries an
        # is_annotation tag per line so long "Middle Step"/scale-explanation
        # sentences render at a smaller font (fits on one line, no wrap/scroll)
        # while the numeric rows stay at the normal size.
        "steps_lines": _elaborate_display_lines(ctrl),
        # Step grids must never wrap (column alignment IS the meaning); method
        # cards must, or long sentences get clipped. See _elaborate_display_lines.
        "steps_wrap": ctrl.elaborate_steps_grid is None,
        # R12-fix2: mastery bar + session counter live INSIDE the swap target so
        # every htmx turn refreshes them (they froze at page-load state before).
        "current_mastery": _current_node_mastery(learner_uuid, ctrl),
        "session_progress": (
            {"n": ctrl.session_progress[0], "total": ctrl.session_progress[1]}
            if ctrl.session_progress else None
        ),
    }


def _render_turn_fragment(learner_uuid: str, ctrl: SessionController) -> str:
    return render_template("_turn.html", **_turn_context(learner_uuid, ctrl))


def _current_node_mastery(learner_uuid: str, ctrl: SessionController) -> dict | None:
    """U-34: a small per-skill mastery cue during the lesson (current node
    only). None before the first PRESENT or when there's nothing scored yet."""
    node_id = ctrl.current_node_id
    if not node_id:
        return None
    display_name = _display_name(node_id)
    store, db_id = _store_and_id(learner_uuid)
    if store is None or db_id is None:
        return {"skill_id": node_id, "display_name": display_name, "pct": 0}
    for row in store.all_skill_states(db_id):
        if row["skill_id"] == node_id:
            return {
                "skill_id": node_id, "display_name": display_name,
                "pct": int(row["p_mastery"] * 100),
            }
    return {"skill_id": node_id, "display_name": display_name, "pct": 0}


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
