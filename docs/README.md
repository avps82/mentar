# Mentar documentation index

Start with the [project README](../README.md). This page maps everything under `docs/`.

## Start here
| Doc | What it is |
|-----|-----------|
| [SPEC.md](SPEC.md) | The full product specification (the authoritative source of truth). |
| [PHASE0_STATUS.md](PHASE0_STATUS.md) | **Live status tracker** — what's done, in progress, and blocked. |
| [PHASE0.md](PHASE0.md) | The Phase-0 entry plan + task list (W1–W7, P1–P5 pilot tasks). |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Repo layout + module map (Python src-layout). |

## Safety
| Doc | What it is |
|-----|-----------|
| [SAFETY.md](SAFETY.md) | The 6-layer child-safety specification (non-negotiable). |
| [PILOT_CONSENT.md](PILOT_CONSENT.md) | Signable consent template — required before any pilot session. |

## Pedagogy & runtime
| Doc | What it is |
|-----|-----------|
| [SESSION_FSM.md](SESSION_FSM.md) | The tutoring turn-loop as an explicit state machine. |
| [TESTS.md](TESTS.md) | The test plan (T1.x–T7.x), incl. the model-eval tests. |

## Model evaluation (W1)
| Doc | What it is |
|-----|-----------|
| [EVAL_RESULTS.md](EVAL_RESULTS.md) | **Plain-language results** — why/how/what we found. |
| [MODEL.md](MODEL.md) | Candidate roster, roles, run plan, and the W1.3 pick (TBD). |
| [llm-compatibility.md](llm-compatibility.md) | Model compatibility notes. |
| [hardware-requirements.md](hardware-requirements.md) | What hardware runs which model tier. |
| [`../eval/README.md`](../eval/README.md) | The eval **tooling** (how to run the tests). |

## Licensing
| Doc | What it is |
|-----|-----------|
| [CONTENT_LICENSES.md](CONTENT_LICENSES.md) | Licences of the grounding content sources (Vikidia, Wikipedia, …). |

## Design notes (`docs/design/`)
Deeper design decisions behind specific workstreams:
- [W1.2_eval_tooling.md](design/W1.2_eval_tooling.md) — eval tooling scan (NIAH adoption).
- [W2.2_escalation.md](design/W2.2_escalation.md) — safety escalation module contract.
- [W3.3_bkt.md](design/W3.3_bkt.md) — BKT mastery model.
- [W3.5_build_vs_adopt.md](design/W3.5_build_vs_adopt.md) — Open-TutorAI build-vs-adopt verdict.
- [W6.3_pilot_interface.md](design/W6.3_pilot_interface.md) — pilot interface decision.
- [W7_grounding_reader.md](design/W7_grounding_reader.md) — grounding / ZIM-reader contract.
- [grounding_zim_reference_hermit.md](design/grounding_zim_reference_hermit.md) — grounding reference scan.
- [media_and_interactivity.md](design/media_and_interactivity.md) — media/interactivity decision (W6.5/W7.6).

## Compliance research (`docs/research/compliance/`)
Background research, not legal advice — see [research/compliance/README.md](research/compliance/README.md):
- [coppa.md](research/compliance/coppa.md) · [gdpr-k.md](research/compliance/gdpr-k.md) ·
  [eu-ai-act.md](research/compliance/eu-ai-act.md) · [uk-aadc.md](research/compliance/uk-aadc.md)

(The mapped coverage status lives in [`../compliance/README.md`](../compliance/README.md).)

## Other folder docs
- [`../config/README.md`](../config/README.md) — runtime config + grounding/ZIM sources + secret safeguards.
- [`../curriculum/README.md`](../curriculum/README.md) — how curriculum templates work.
- [`../prompts/README.md`](../prompts/README.md) — the versioned prompt-template registry.

## Archived
- `_legacy/` — superseded v0 drafts, kept for history (not authoritative).
