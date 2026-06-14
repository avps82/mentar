---
title: Mentar — Repository Architecture
version: v0.1 — Draft
last-updated: 2026-06-13
authority: This document + SPEC.md §8 + PHASE0.md W6.4
---

# Mentar — Repository Architecture

## 1. Purpose

This document defines the source-layout and module responsibilities for the Mentar repository so that Week 1 code does not become the de facto architecture by default (PHASE0.md W6.4). It is a navigational sketch, not a reference manual — detailed behavioural specs live in SPEC.md, SESSION_FSM.md, PROMPTS.md, and SAFETY.md. The layout is Python src-layout (`src/mentar/`) to keep the installable package separate from top-level data directories.

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
| `src/mentar/engine/` | KST prerequisite graph; pyBKT wiring and mastery estimates; outer-fringe selection; deterministic answer verifiers (fractions stdlib) | SPEC §10, §11, §15(2); W3.1–W3.4 |
| `src/mentar/dialogue/` | Session controller; FSM state machine (per SESSION_FSM.md); Help loop; probe trigger; interaction-pattern selection | SPEC §12, §13, §14; W6.1 |
| `src/mentar/safety/` | 6-layer safety implementation: input filter, output filter, escalation (`escalation.py`), age-mode enforcement, content-block rules | SPEC §16.0–16.3; W2.1–W2.4 |
| `src/mentar/inference/` | `generate()` abstraction layer; backend adapters (Ollama default, vLLM, Gemini, Claude opt-in); backend selection via env var / config | SPEC §20, §20.1; W1.5 |
| `src/mentar/eval/` | Eval harness code: dataset loader, numeric scorer, rubric scorer, safety scorer | SPEC §15; W1.2–W1.3; T1 suite |
| `src/mentar/db/` | SQLite store (single-file per-learner); schema migrations; query helpers | SPEC §16 L4; W3.6; T3.6 |
| `src/mentar/tools/` | CLI utilities: `validate_template.py` (DAG/schema validator), helper scripts | W3.1; T3.1 |
| `src/mentar/cli/` | `mentar` CLI entry point; subcommands: `serve`, `eval`, `validate-template` | PHASE0.md W6.4 |
| `curriculum/` | Markdown + YAML curriculum templates (country/grade); community contribution surface; NOT under `src/` (data, not code) | SPEC §9; W3.1–W3.2 |
| `prompts/` | Versioned prompt template files (≥10 files) + `PROMPTS.md` registry with per-file hash; NOT under `src/` (data, version-controlled) | SPEC §12, §13.2; W6.2; T4.6 |
| `eval/` | Eval DATA directory: `dataset_v1.jsonl`, `schema.json`, `models.yaml`, `responses/`, `scores_*.csv`, `rubric.md`; code lives at `src/mentar/eval/` | W1.2; T1.1–T1.5 |
| `docs/` | SPEC.md, PHASE0.md, TESTS.md, SAFETY.md, SESSION_FSM.md, ARCHITECTURE.md, PROMPTS.md (W6.2 registry), MODEL.md (post-W1.3), HARDWARE.md (W1.6), `research/` | All workstreams |
| `tests/` | pytest suite; mirrors `src/mentar/` layout (e.g. `tests/test_escalation.py`, `tests/test_session_fsm.py`) | TESTS.md §0; T2–T5 suites |
| `reports/` | Gitignored runtime output; `reports/<test-id>/result.json` per test; `reports/pilot/` for T6 protocols | TESTS.md §0 |
| `pyproject.toml` | Package metadata, dependencies, entry-point declarations | — |
| `pytest.ini` | Test discovery config; points at `tests/`; sets `MENTAR_ROOT` | TESTS.md §0 |
| `.gitignore` | Excludes: `reports/`, `.venv/`, `__pycache__/`, `*.pyc`, `*.db`, `.DS_Store` | — |

---

## 4. Entry Points

### CLI subcommands (via `mentar` after `pip install -e .`)

| Command | What it does |
|---------|--------------|
| `mentar serve` | Start a pilot tutoring session (spawns session controller, loads curriculum, attaches safety layer and inference backend) |
| `mentar eval` | Run the T1 eval harness over the dataset in `eval/` against model(s) listed in `eval/models.yaml` |
| `mentar validate-template <path>` | Run `src/mentar/tools/validate_template.py` against a curriculum template file; exits 0/1, prints cycle paths or unknown-id errors |

### Library import path

```python
from mentar.engine import KSTGraph, BKTTracker, fringe
from mentar.dialogue import SessionController
from mentar.safety import escalation
from mentar.inference import generate
from mentar.db import LearnerDB
```

---

## 5. Storage

**Per-learner SQLite database** (W3.6). Suggested location: `~/.mentar/learners/<learner-id>.db`. One file per learner — multi-learner namespacing is therefore a filesystem concern, not a database-schema concern (no cross-learner query surface, no accidental join risk).

Schema tables (W3.6): learner profile, per-skill BKT state, response log (timestamped, scored, hinted flag), Help events, probe events + class, escalation log, session transcripts (immutable via trigger).

**Export = file copy.** No extraction pipeline needed for the OSS edition; the file is the backup. Schema version tracked via `PRAGMA user_version` for future migrations.

---

## 6. Inference Abstraction

All LLM calls in Mentar route through a single function defined in `src/mentar/inference/`:

```python
generate(
    prompt: str,
    grounding_passages: list[str],
    constraints: dict,
) -> str
```

`grounding_passages` are injected as quoted data (never as instructions) to satisfy the W2.3 prompt-injection mitigation. `constraints` carry generation parameters (temperature, max tokens, modality tag) and age-mode flags for the backend. The active backend is selected via the `MENTAR_BACKEND` environment variable or the `inference.backend` config key — no code change is required to switch. Available backends: local Ollama / llama.cpp (default, offline-capable), parent-hosted vLLM cluster, Gemini API (opt-in, parent owns key), Claude API (opt-in, parent owns key). When a parent opts into a cloud backend they assume operator responsibility for data leaving the device (SPEC §20.1, §17.2).

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

**Recommended fix:** add a one-line "actual path = `src/mentar/<flat>`" note at the top of TESTS.md §0, keeping TESTS.md readable as a spec doc without requiring shim re-export files. Thin top-level shims (`tools/`, `safety/`) are the alternative but add indirection with no benefit. Do not change TESTS.md now — flag at W6.4 close.

---

## 8. Out of Scope for This Document

- **Session FSM details** — state/transition table, absorbing states, persistence contract → `docs/SESSION_FSM.md` (W6.1)
- **Prompt template registry** — file list, version hashes, per-template purpose → `prompts/PROMPTS.md` (W6.2)
- **Pilot interface** — chosen surface (TUI vs minimal web), view list, HTML structure → recorded in SPEC.md §23 (W6.3)
- **Model selection and hardware tiers** → `docs/MODEL.md` (W1.3) and `docs/HARDWARE.md` (W1.6)
- **Safety layer full spec** → `docs/SAFETY.md` (W2.1)
