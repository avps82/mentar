# Mentar

**OSS-first AI tutor for children that supplements — never replaces — school education.**

Local LLM hosting. Curriculum-templated by country and year level. Built-in kid safety from day one.

▶️ **Want to run it?** See **[docs/RUNNING.md](docs/RUNNING.md)** — a 6-step quick start for Windows, macOS (incl. MacBook Pro M1 16 GB) and Linux.

---

## What it is

Mentar is an open-source tutoring framework that lets parents run an AI tutor on their own hardware, with no data leaving the device and no per-seat API fees. The core is three components:

- **Template engine** — Markdown curriculum files per country + year/grade level, used as learning guidelines. Community-extensible.
- **Dialogue framework** — Scaffolds tutoring conversations within the bounds of the active curriculum template.
- **Safety layer** — Content guardrails and age-mode logic baked in, not bolted on. This is the non-negotiable bar the project must clear to justify existing.

---

## How this is built — an honesty note

Mentar is, candidly, **AI-built software**. The great majority of the code, tests, and docs in this
repo are written by AI agents working under a human maintainer's direction, decisions, and review —
**not hand-written by a person**. In that sense it is close to "vibe coding," even though it follows
deliberate engineering discipline: spec-first design, test-driven development (150+ tests gating
changes), design docs before code, versioned prompts, and code review. Those principles raise the
quality bar — but they don't change that underlying fact, and we'd rather be upfront about it.

What this means for you:

- **The human makes the decisions** (scope, safety thresholds, model choices, architecture); the AI
  executes and advises. Changes are test-gated and reviewed — but the author is AI.
- **It has not had a professional, independent audit.** In particular, the **child-safety** code and
  spec are AI-authored and reviewed by AI plus the maintainer — *not* by a qualified safeguarding,
  security, or child-development professional. The safety spec's own rollout guards
  ([`docs/SAFETY.md`](docs/SAFETY.md)) require that review **before** any use beyond a single,
  supervised pilot.
- Treat the project accordingly: carefully built and openly documented, but **not yet independently
  verified**. Read the code, run the tests, and do not put it in front of a real child outside a
  supervised pilot until the open safety items are closed.

---

## Why local-first

Two reasons:

1. **Privacy** — children's data never leaves the device. No operator collects it. This is also a major compliance advantage (see `compliance/`).
2. **Cost** — no per-seat API fees. A parent with a capable laptop or homelab machine pays nothing to run inference.

A paid hosted-inference tier (for non-technical parents) is a planned future bridge, but it carries its own heavier compliance obligations. The OSS local edition stays deliberately data-light by design.

---

## Architecture

The codebase uses a Python **src-layout** (`src/mentar/`); specs and the safety spec live
under `docs/` (not in a top-level `safety/`). See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
for the authoritative layout.

```
mentar/
├── curriculum/              # Markdown curriculum templates (concept graphs)
│   ├── _template.md         # Authoring format for new curricula
│   └── templates/
│       └── _pilot/          # Phase-0 fractions pilot graph (more to follow)
├── prompts/                 # Versioned prompt templates + prompts/README.md registry (W6.2)
├── src/mentar/              # Python package (src-layout)
│   ├── engine/              # Concept graph (KST), BKT mastery, fringe, probe classifier
│   ├── dialogue/            # Turn-loop controller (session state machine)
│   ├── safety/              # Safety-layer implementation (escalation, filters)
│   ├── inference/           # LLM abstraction layer (swappable backends)
│   ├── eval/                # Deterministic verifiers + model-eval harness
│   ├── db/                  # Local SQLite store (schema + access)
│   ├── tools/               # Template validator, etc.
│   └── cli/                 # Command-line entry points
├── tests/                   # Mirrors the src/ layout
├── docs/                    # SPEC, PHASE0(+_STATUS), SAFETY, SESSION_FSM, ARCHITECTURE,
│                            #   TESTS, CONTENT_LICENSES, PILOT_CONSENT, design/, research/
├── compliance/              # Compliance coverage-status map (points back to docs/)
└── eval/                    # Eval datasets/outputs (data is gitignored)
```

---

## Curriculum templates

Templates are simple Markdown files that define what topics a child at a given country + year level should be learning. They are **guidelines**, not scripts — the dialogue framework uses them to keep sessions on-topic and age-appropriate.

Anyone can add a new country or year-level template. See `curriculum/_template.md` for the format.

---

## Safety

Kid-safe content blocks and age-appropriate responses are non-negotiable and built in from the start. See [`docs/SAFETY.md`](docs/SAFETY.md) for the full 6-layer spec (implementation lives in `src/mentar/safety/`).

Key commitments:
- No dark patterns, no compulsive gamification mechanics (legal line under EU AI Act Article 5)
- No emotion recognition or mood inference
- Under-13: parent-mediated mode (parent in the loop, child never alone with AI)
- 13+: more independent with parental oversight available
- Hard block: model must never produce sexual content involving minors

---

## Compliance

The OSS local edition is data-light by design, which removes most direct developer exposure under COPPA, GDPR-K, and similar frameworks. However, obligations are real and documented.

See `compliance/README.md` for coverage status — what's mapped, what's incomplete, and where contributors can help.

---

## LLMs

Mentar is designed to work with smaller OSS models suited to educational dialogue. Low hallucination is critical for a children's tutor. The inference layer is abstracted so users can swap models.

Current evaluation status: see `docs/llm-compatibility.md`.

Hardware requirements: see `docs/hardware-requirements.md`.

---

## Documentation

Full index: **[`docs/README.md`](docs/README.md)**. Highlights:

- **[Spec](docs/SPEC.md)** · **[Live status](docs/PHASE0_STATUS.md)** · **[Architecture](docs/ARCHITECTURE.md)**
- **[Safety spec](docs/SAFETY.md)** (6-layer, non-negotiable) · **[Pilot consent](docs/PILOT_CONSENT.md)**
- **[Session state machine](docs/SESSION_FSM.md)** · **[Test plan](docs/TESTS.md)**
- Model evaluation — **[results, plain-language](docs/EVAL_RESULTS.md)** · **[roster & plan](docs/MODEL.md)** · **[eval tooling](eval/README.md)**
- **[Content licences](docs/CONTENT_LICENSES.md)** · **[Compliance status](compliance/README.md)** · **[Config & grounding sources](config/README.md)**

---

## Contributing

- Add or improve a curriculum template under `curriculum/templates/` (see `curriculum/_template.md` for the format)
- Improve the safety spec in `docs/SAFETY.md`
- Fill compliance gaps flagged in `compliance/README.md`
- Test and document model compatibility in `docs/llm-compatibility.md`

---

## Status

Early-stage, in active **Phase 0** (a single-subject fractions pilot). The architecture,
safety spec, session state machine, learner data model, and core engine pieces (concept
graph, BKT mastery, verifiers, escalation, prompt registry) are in place; the end-to-end
dialogue loop and the local model evaluation are the next milestones. Live status tracker:
[`docs/PHASE0_STATUS.md`](docs/PHASE0_STATUS.md).
