---
type: Mentar Architecture Doc
title: Mentar — Repository Architecture
version: v0.3
last-updated: 2026-07-22
authority: This document + SPEC.md §8 + PHASE0.md W6.4
---

# Mentar — Repository Architecture

## 1. Purpose

This document defines the source-layout and module responsibilities for the Mentar repository so that Week 1 code does not become the de facto architecture by default (PHASE0.md W6.4). It is a navigational sketch, not a reference manual — detailed behavioural specs live in SPEC.md, SESSION_FSM.md, prompts/README.md, and SAFETY.md. The layout is Python src-layout (`src/mentar/`) to keep the installable package separate from top-level data directories.

---

## 2. High-Level Data Flow

The diagram below maps onto SPEC.md §8 (4-layer model) and adds the runtime stores. Safety wraps every layer; inference is the bottom-most dependency.

```
┌────────────────────────────────────────────────────────────────────┐
│  SAFETY LAYER  src/mentar/safety/  (SPEC §16, 6 layers)            │
│  — input guard, output filter, escalation freeze, age-mode         │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐     │
│  │ curriculum/ │→  │ engine/      │→  │ dialogue/            │     │
│  │ YAML+MD     │   │ KST graph    │   │ session controller   │     │
│  │ (scope)     │   │ BKT mastery  │   │ FSM (W6.1)           │     │
│  │             │   │ fringe select│   │ Help loop (§13)      │     │
│  │             │   │ verifiers    │   │ probe trigger (§14)  │     │
│  └─────────────┘   └──────────────┘   └──────────────────────┘     │
│         │                 │                      │                  │
│         │         ┌───────┴──────┐       ┌───────┴──────┐          │
│         │         │  db/         │       │  prompts/    │          │
│         │         │  SQLite      │       │  versioned   │          │
│         │         │  per-learner │       │  templates   │          │
│         │         └──────────────┘       └──────────────┘          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  inference/  generate(prompt, grounding_passages,            │   │
│  │              constraints) → text                             │   │
│  │  ├─ Ollama / llama.cpp  (default, local)                    │   │
│  │  ├─ vLLM cluster        (parent-hosted)                     │   │
│  │  ├─ Gemini API          (opt-in, parent key)                │   │
│  │  └─ Claude / other API  (opt-in, parent key)               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

No network call crosses the data path in the default (local Ollama) backend. All generated output passes through the safety layer before reaching the child.

---

## 3. Module Map

| Path | Purpose | Defined by |
|------|---------|------------|
| `src/mentar/engine/` | KST prerequisite graph; Mentar's own deterministic BKT recurrence (`bkt.py` — **not** pyBKT in the hot path; pyBKT reserved for offline parameter fitting post-pilot per W3.3); outer-fringe selection (`fringe.py`); deterministic answer verifiers; item generators (see sub-modules below) | SPEC §10, §11, §15(2); W3.1–W3.4 |
| `src/mentar/engine/bkt.py` | Per-turn BKT update (`bkt_update()`), hinted-win discount, cold-start priors. pyBKT is NOT imported here. | SPEC §11; W3.3 |
| `src/mentar/engine/fringe.py` | Fringe selection policy: `select_next()` interleaves across unmastered nodes, injects spaced review of stale-mastered nodes (R11) | SPEC §11; R11 |
| `src/mentar/engine/curriculum.py` | Template discovery, `load_template_meta()`, country/authority namespace helpers | SPEC §9; R3.1; R-MC |
| `src/mentar/engine/item_sources.py` | Named item-source registry mapping `item_source:` keys to generator callables | R3.1 |
| `src/mentar/engine/itembank.py` | `ItemBank` — loads + caches static item JSON files for pre-authored question banks | R-option-A |
| `src/mentar/engine/itemgen.py` | `ItemGenerator` — parametric item generation (composite default, `mc_which_is` shared helper) | R-option-B |
| `src/mentar/engine/au_items.py` | AU_ACARA maths item generators (Year 2–8; per-year generator registries) | R14a; R15 |
| `src/mentar/engine/au_english_items.py` | AU_ACARA English item generators (Year 2/5/6) | R14a |
| `src/mentar/engine/in_generic_items.py` | India board-agnostic (IN_GENERIC) maths item generators (Class 3) | R8; R14b-deferred |
| `src/mentar/engine/science_items.py` | Science multiple-choice generators from curated fact tables (pilot `_pilot/science.md`) | 2026-06-29 |
| `src/mentar/engine/practice_items.py` | Country-agnostic practice-pack generators (times tables, English vocabulary; `curriculum/templates/practice/`) | R7.1 |
| `src/mentar/engine/arithmetic_steps.py` | Deterministic step-grid builder for column arithmetic (add/sub/mult/long-division with carry/borrow marks); wired into `HELP_ELABORATE` | R12-show-working |
| `src/mentar/engine/visual_scaffold.py` | LRU-cached loader for OKF visual scaffold files in `curriculum/visual_scaffolds/`; matched by `topic_keywords` | R12-explain |
| `src/mentar/engine/explain_check.py` | `has_verified_failure()` — arithmetic claim verifier for free-form explanation text; `realign_algebra_blocks()` — post-processor for aligned step blocks | A14; 2026-07-22 |
| `src/mentar/engine/probe_classify.py` | W3.4 false-confidence classifier; probe outcome → `false_confidence`/`slip_suspect`/`forgetting_suspect` | W3.4 |
| `src/mentar/dialogue/` | Session controller; FSM state machine (per SESSION_FSM.md); Help loop with 6 modalities + HELP_ELABORATE; probe trigger; interaction-pattern selection; session resume (R-RES) | SPEC §12, §13, §14; W6.1; R-RES |
| `src/mentar/safety/` | 6-layer safety implementation: input filter (`output_guard.py`), escalation (`escalation.py`), age-mode enforcement, credential scrubbing (`credential_guard.py`), handoff validation (`handoff_check.py`) | SPEC §16.0–16.3; W2.1–W2.4 |
| `src/mentar/safety/credential_guard.py` | Scrubs API keys / tokens from LLM output before it reaches the child | SPEC §16; A15 |
| `src/mentar/safety/handoff_check.py` | Validates fixed handoff message text against SAFETY §3.4 requirements | SAFETY §3.4; W2.2 |
| `src/mentar/inference/` | Backend abstraction (`backend.py`); Ollama/llama.app/vLLM/GGUF adapters; hardware-aware model autoselect (`autoselect.py`); `ggufparser.py` wrapper | SPEC §20, §20.1; W1.5; R9 |
| `src/mentar/eval/` | Deterministic verifiers (`verify_numeric.py`); eval harness: `run_candidates.py`, `judge_responses.py`, `build_dataset.py` | SPEC §15; W1.2–W1.3; T1 suite |
| `src/mentar/db/` | SQLite store (`store.py`); schema (`schema.sql`, v4 with `PRAGMA user_version`); `adapter.py` (LearnerStore ↔ SessionController bridge, A17) | SPEC §16 L4; W3.6; T3.6; R-RES |
| `src/mentar/grounding/` | ZIM reader (`reader.py`) + resolver (`resolve.py`) + source map (`source_map.py`) + sources downloader (`sources.py`) + LRU cache (`cache.py`) + data-wrapper (`wrapper.py`) | SPEC §15(1), §18.2; W7 |
| `src/mentar/web/` | Flask app (`app.py`): learner/parent views, answer-mode dispatch (`answer_modes.py`), session routing, curriculum toggles, setup gate, escalation freeze page | SPEC §23; W6.3; R9; R10 |
| `src/mentar/tools/` | CLI utilities: `validate_template.py` (DAG/schema validator) | W3.1; T3.1 |
| `src/mentar/cli/` | `mentar` CLI entry point (`__main__.py`); subcommands: `setup`, `serve`, `eval`, `validate-template` | PHASE0.md W6.4 |
| `curriculum/templates/` | Country/grade curriculum templates: `_pilot/` (fractions Phase-0), `AU_ACARA/` (Year 2–8 maths + English), `IN_GENERIC/` (Class 3 maths), `practice/` (country-agnostic) | SPEC §9; W3.1–W3.2; R14a; R15 |
| `curriculum/visual_scaffolds/` | OKF-format visual scaffold files matched by topic keywords and injected into Help explanations | R12-explain |
| `prompts/` | Versioned prompt templates + `prompts/README.md` registry with per-file SHA-256[:12] hashes | SPEC §12, §13.2; W6.2; T4.6 |
| `eval/` | Eval DATA: `dataset_v1.jsonl`, `schema.json`, `models.yaml`; code at `src/mentar/eval/` | W1.2; T1.1–T1.5 |
| `docs/` | SPEC.md, PHASE0.md, TESTS.md, SAFETY.md, SESSION_FSM.md, ARCHITECTURE.md, MODEL.md, REMAINDER_PLAN.md, PHASE0_STATUS.md, `design/`, `research/` | All workstreams |
| `tests/` | pytest suite (717 tests as of 2026-07-22); mirrors `src/mentar/` layout | TESTS.md §0; T2–T5 suites |
| `graphify-out/` | Graphify knowledge graph (`graph.json`, `GRAPH_REPORT.md`, `mentar_graph_overview.png`) — regenerated on major refactors | — |
| `pyproject.toml` | Package metadata, extras (`dev`, `web`, `grounding`), entry-point declarations | — |

---

## 4. Entry Points

### CLI subcommands (via `mentar` after `pip install -e .`)

| Command | What it does |
|---------|--------------|
| `mentar setup` | Detect hardware, auto-pick + download the best-fit vetted local model, write `config/inference.yaml` |
| `mentar run-session` | Drive a full tutoring session headlessly (no Flask) against the configured inference backend |
| `mentar serve` | Start a pilot tutoring session (spawns session controller, loads curriculum, attaches safety layer and inference backend) |
| `mentar eval` | Run the T1 eval harness over the dataset in `eval/` against model(s) listed in `eval/models.yaml` |
| `mentar validate-template <path>` | Run `src/mentar/tools/validate_template.py` against a curriculum template file; exits 0/1, prints cycle paths or unknown-id errors |

### Library import path

```python
from mentar.engine.bkt import bkt_update, BktParams
from mentar.engine.curriculum import load_template_meta
from mentar.engine.fringe import select_next
from mentar.dialogue.controller import SessionController
from mentar.safety.escalation import check_input
from mentar.inference.backend import LLMBackend
from mentar.db.store import LearnerStore
from mentar.db.adapter import LearnerStoreAdapter
```

---

## 5. Storage

**Per-learner SQLite database** (W3.6). Suggested location: `~/.mentar/learners/<learner-id>.db`. One file per learner — multi-learner namespacing is therefore a filesystem concern, not a database-schema concern (no cross-learner query surface, no accidental join risk).

Schema tables (W3.6): learner profile, per-skill BKT state, response log (timestamped, scored, hinted flag), Help events, probe events + class, escalation log, session transcripts (immutable via trigger).

**Export = file copy.** No extraction pipeline needed for the OSS edition; the file is the backup. Schema version tracked via `PRAGMA user_version` for future migrations.

---

## 6. Inference Abstraction

All LLM calls in Mentar route through `src/mentar/inference/backend.py` via a `LLMCall` object:

```python
# backend.py public API
llm = make_llm_call(cfg: dict) -> LLMCall
response: str = llm.call(messages: list[dict])

# Autoselect: pick + download the best-fit vetted model for this hardware
selection: Selection = autoselect.select(roster_path)
```

Grounding passages are injected by the dialogue controller into the message list as quoted data (never as instructions) to satisfy the W2.3 prompt-injection mitigation. The active backend is determined by `config/inference.yaml` (`backend:` key), switchable live via `mentar setup` or `POST /setup` with no restart required (R9). Available backends: local Ollama (default, offline), local llama.app/llama.cpp (GGUF, R9.1), parent-hosted vLLM/OpenAI-compatible API (opt-in, `backend: vllm`). When a parent opts into a remote backend they assume operator responsibility for data leaving the device (SPEC §20.1, §17.2).

---

## 7. TESTS.md Path Reconciliation

TESTS.md (§0 and throughout) uses flat paths that predate the src-layout decision:

| TESTS.md flat path | Actual src-layout path |
|--------------------|----------------------|
| `safety/escalation.py` | `src/mentar/safety/escalation.py` |
| `tools/validate_template.py` | `src/mentar/tools/validate_template.py` |
| `eval/verify_numeric.py` | `src/mentar/eval/verify_numeric.py` |
| `db/schema.sql` | `src/mentar/db/schema.sql` |

**Data paths are unchanged** — `eval/dataset_v1.jsonl`, `eval/responses/*.jsonl`, `eval/scores_*.csv`, and `eval/rubric.md` remain at the top-level `eval/` directory (data, not code).

**Status (2026-07-22):** the path table above is the reconciliation. TESTS.md still uses flat paths in its prose (historical, for readability as a spec doc) — the actual test files live at `tests/<module>/test_*.py` mirroring the src layout. No shims needed.

---

## 7b. Dependency philosophy (build vs import)

*Added 2026-06-15 (the maintainer).* Default to **importing well-maintained open-source libraries
to reduce maintenance** — don't hand-roll what a focused, healthy lib already does well. We
**own only**: (1) the thin *glue* wiring libs together, and (2) the **safety-critical and
differentiating** logic (curriculum/pedagogy engine, safety layer, the scope/data-wrapping
around retrieval, the deterministic verifier).

The distinction that matters is **shape, not "third-party vs ours":**
- ✅ **Import a focused library** that does one hard thing well — e.g. `libzim` (ZIM reading +
  search), `llama-cpp-python`/llama.cpp (local inference), `needlehaystack` (retrieval eval).
- ⛔ **Don't adopt a heavyweight framework/server whose architecture is the wrong shape** for
  Mentar's controlled, local, child-safety loop just to reach the library inside it — e.g.
  running the OpenZIM **MCP server** when we only need its `libzim` layer
  (`docs/design/grounding_zim_reference_hermit.md`).

"Build it ourselves" therefore never means reinventing a solved primitive; it means owning
the thin glue + the parts that *are* the product. The grounding/ZIM reader is the canonical
example: **depend on `libzim`, own the safety wrapper, skip the server.**

---

## 8. Out of Scope for This Document

- **Session FSM details** — state/transition table, absorbing states, persistence contract → `docs/SESSION_FSM.md` (W6.1)
- **Prompt template registry** — file list, version hashes, per-template purpose → `prompts/README.md` (W6.2)
- **Pilot interface** — chosen surface (TUI vs minimal web), view list, HTML structure → recorded in SPEC.md §23 (W6.3)
- **Model selection and hardware tiers** → `docs/MODEL.md` (W1.3) and `docs/hardware-requirements.md` (W1.6)
- **Safety layer full spec** → `docs/SAFETY.md` (W2.1)
