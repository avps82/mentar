---
okf_version: "0.2"
---

# Mentar documentation index

Start with the [project README](../README.md). This page maps everything under `docs/`.

## Start here
| Doc | What it is |
|-----|-----------|
| [SPEC.md](SPEC.md) | The full product specification (the authoritative source of truth). |
| [PHASE0_STATUS.md](PHASE0_STATUS.md) | **Live status tracker** — what's done, in progress, and blocked. |
| [PHASE0.md](PHASE0.md) | The Phase-0 entry plan + task list (W1–W7, P1–P5 pilot tasks). |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Repo layout + module map (Python src-layout). |
| [REMAINDER_PLAN.md](REMAINDER_PLAN.md) | The post-G0 release-wave build plan (R2–R15, R-RES, R-MC). |
| [DOC_AUDIT.md](DOC_AUDIT.md) | Documentation staleness audit register + fix log. |
| [EXPLAIN_METHOD_AUDIT.md](EXPLAIN_METHOD_AUDIT.md) | Node-by-node audit of every curriculum concept's explain output (ASCII step-grid vs. LLM prose vs. LLM prose + visual scaffold) — subject × category × explain-type, with 5 real findings. |

## Safety
| Doc | What it is |
|-----|-----------|
| [SAFETY.md](SAFETY.md) | The 6-layer child-safety specification (non-negotiable). |
| [PILOT_CONSENT.md](PILOT_CONSENT.md) | Signable consent template — required before any pilot session. |
| [PILOT_RUNBOOK.md](PILOT_RUNBOOK.md) | Operational runbook for running a supervised pilot session. |

## Pedagogy & runtime
| Doc | What it is |
|-----|-----------|
| [SESSION_FSM.md](SESSION_FSM.md) | The tutoring turn-loop as an explicit state machine. |
| [TESTS.md](TESTS.md) | The test plan (T1.x–T7.x), incl. the model-eval tests. |
| [TESTING_NOTES.md](TESTING_NOTES.md) | Raw, unprocessed maintainer testing notes (triage log). |
| [RUNNING.md](RUNNING.md) | Cross-platform quick-start guide (Windows/macOS/Linux). |

## Model evaluation (W1)
| Doc | What it is |
|-----|-----------|
| [EVAL_RESULTS.md](EVAL_RESULTS.md) | **Plain-language results** — why/how/what we found. |
| [MODEL.md](MODEL.md) | Candidate roster, roles, run plan, and the W1.3 pick (`gemma2:9b`). |
| [llm-compatibility.md](llm-compatibility.md) | Model compatibility notes (superseded by EVAL_RESULTS.md/MODEL.md). |
| [hardware-requirements.md](hardware-requirements.md) | What hardware runs which model tier. |
| [`../eval/README.md`](../eval/README.md) | The eval **tooling** (how to run the tests). |

## Licensing
| Doc | What it is |
|-----|-----------|
| [LICENSE_AUDIT.md](LICENSE_AUDIT.md) | Dependency + bundled-content license audit (informs the W4.2 OSS-license decision). |
| [CONTENT_LICENSES.md](CONTENT_LICENSES.md) | Licences of the grounding content sources (Vikidia, Wikipedia, Khan Academy, …). |

## Subdirectories
* [design](design/index.md) — Deeper design decisions and build contracts behind specific workstreams.
* [research/compliance](research/compliance/index.md) — Regulatory background research (COPPA, GDPR-K, EU AI Act, UK AADC). Not legal advice.

## Other folder docs
- [`../config/README.md`](../config/README.md) — runtime config + grounding/ZIM sources + secret safeguards.
- [`../curriculum/README.md`](../curriculum/README.md) — how curriculum templates work.
- [`../prompts/README.md`](../prompts/README.md) — the versioned prompt-template registry.

## Archived
- `_legacy/` — superseded v0 drafts, kept for history (not authoritative).
