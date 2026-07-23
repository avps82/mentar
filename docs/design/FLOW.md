---
type: Mentar Design Doc
title: Mentar — Interaction Flow
description: How a session flows across subject selection, child learning loop, and parent oversight view, with safety as a cross-cutting pre-empt. Mermaid diagrams grounded in dialogue/controller.py and web/app.py.
tags: [design, flow, fsm, safety]
timestamp: "2026-07-23T00:00:00Z"
---

# Mentar — interaction flow

How a session actually flows, separated into **subject selection**, the **child** learning loop,
and the **parent** oversight view, with **safety** as a cross-cutting pre-empt. Grounded in
`dialogue/controller.py` (the FSM) and `web/app.py` (routes). Diagrams are Mermaid (render on
GitHub / most viewers).

Key invariants the flow guarantees:
- **The deterministic verifier scores answers — never the LLM** (`eval/verify_numeric.py`).
- **Safety classification runs first** on every child input and pre-empts everything.
- **One question at a time** is live for the child.
- The **LLM only generates inside bounded states** (present / explain), never open chat.

---

## 1. System overview — subjects, child, parent

```mermaid
flowchart TD
  Start(["Child opens Mentar"]) --> Pick{"Subject chosen?"}
  Pick -- "no" --> Picker["Subject picker (/choose)"]
  Picker --> Pick
  Pick -- "yes" --> Child["Child learning loop (FSM)"]

  Child -- "writes" --> DB[("SQLite store: mastery, transcript, responses, escalations")]
  DB -- "reads" --> Parent["Parent view (/parent)"]
  Child -- "safety trigger" --> Freeze["Escalation freeze + handoff"]
  Freeze --> Parent
  Parent -- "resume / end" --> Child

  subgraph Subjects["Subjects: curriculum + item source"]
    F["Fractions: authored bank + generators"]
    M["Maths plus minus times: parametric generators"]
    S["Science: multiple-choice from curated fact tables"]
  end
  Pick -. "binds session to one" .-> Subjects
```

| Subject | Answer types | Item source | Scored by |
|---|---|---|---|
| **Fractions** | int, fraction, mc4 | authored item bank + parametric generators | `int_exact` / `fraction_equiv` / `mc_choice` |
| **Maths +−×** | int | parametric generators (computed answers) | `int_exact` |
| **Science** | mc4 | generated MC from curated fact tables (ground truth = the table) | `mc_choice` |

Switching subject starts a **fresh session** (new controller + `session_id`); `skill_state` is
keyed by concept id, which is distinct across subjects, so there is no cross-subject collision.

---

## 2. Child learning loop (the FSM)

```mermaid
flowchart TD
  SS(["SESSION_START"]) --> NS["NODE_SELECT: pick next unmastered concept"]
  NS -- "all mastered" --> DONE(["SESSION_END_COMPLETE"])
  NS --> PS["PATTERN_SELECT"] --> PR["PRESENT a question"]
  PR --> AW{"AWAIT_ANSWER"}

  AW -- "stop" --> ENDL(["SESSION_END_BY_LEARNER"])
  AW -- "? / help" --> HM["HELP_MODALITY_SELECT"]
  AW -- "unreadable (gibberish/blank)" --> REASK["Re-ask SAME question + guidance"]
  REASK --> AW
  AW -- "an answer" --> SC["SCORE (deterministic verifier)"]

  SC -- "correct" --> FBp["Praise"] --> BK["BKT_UPDATE"]
  SC -- "wrong" --> FBw["Not quite — feedback"] --> BKw["BKT_UPDATE"]
  BKw --> HM

  BK --> BR{"BRANCH_DECISION"}
  BR -- "probe due" --> PP["PROBE_PRESENT"]
  BR -- "else" --> NS

  HM --> HE["HELP_EXPLAIN: show the question + a worked example to its answer"]
  HE --> HRP["HELP_RECHECK_PRESENT: re-try the SAME question"]
  HRP --> HRA{"HELP_RECHECK_AWAIT"}
  HRA -- "? / help" --> HM
  HRA -- "answer" --> HSC["HELP_RECHECK_SCORE"] --> HBK["BKT_UPDATE (hinted)"] --> HRD{"HELP_RETRY_DECISION"}
  HRD -- "correct" --> BR
  HRD -- "wrong, retries left" --> HM
  HRD -- "wrong, cap reached" --> LB["LINK_BACK: encourage, move on"] --> BR

  PP --> PA{"PROBE_AWAIT_ANSWER"}
  PA -- "? / help" --> HM
  PA -- "answer" --> PSC["PROBE_SCORE"] --> PC{"PROBE_CLASSIFY"}
  PC -- "clean pass" --> NS
  PC -- "slip suspect (one retry)" --> PP
  PC -- "mastery overestimated" --> DEM["Demote mastery below threshold"] --> NS
```

Notes:
- **Auto-help on wrong:** a wrong *unaided* answer gives feedback (without revealing the answer)
  and routes into the Help loop, rather than advancing.
- **Help = one question:** the explanation shows `Q) <the question>` + a worked example *to its
  answer*; the child re-tries the **same** question ("Now you try it!"). Any extra question the
  model appends is stripped.
- **Probes confirm then advance:** a clean probe advances (the mastered node leaves the fringe); a
  failed probe demotes mastery so the node returns to **normal feedback practice** (this fixed the
  endless-silent-probe bug).
- **Open modelling decisions** (see PHASE0_STATUS): mastery rising after wrong answers; broader
  child-intent recognition ("I don't know", clarify, off-topic) — `design/INTERACTION_SCOPE.md`.

---

## 3. Safety pre-empt (cross-cutting)

Runs first on **every** child input, in every awaiting state, before any scoring or help.

```mermaid
flowchart TD
  IN(["Child input (any state)"]) --> CLS{"Deterministic safety classifier"}
  CLS -- "harm / danger / distress / abuse / secrecy / jailbreak" --> FR["ESCALATION_FREEZE"]
  CLS -- "none" --> NORMAL["Normal handling (answer / help / stop)"]
  FR --> LOG[("Log escalation (verbatim)")]
  FR --> HO["Show handoff message; absorb further child input"]
  HO --> PAW{"PARENT_ACK_WAIT (parent only)"}
  PAW -- "resume" --> RES["Back to the lesson"]
  PAW -- "end" --> ENDP(["SESSION_END_BY_PARENT"])
```

The freeze is **absorbing for child input** — a child can never unfreeze a session by typing; only
the parent control plane (`/parent/ack`) transitions out of it.

---

## 4. Parent view (oversight)

```mermaid
flowchart TD
  P(["Parent opens /parent"]) --> V["Reads durable DB: mastery % per skill, session score (X correct of Y), per-answer correct/wrong/help, session log, escalations"]
  V --> E{"Escalation pending?"}
  E -- "yes" --> ACK["Handoff message + Resume / End"]
  ACK -- "resume" --> RES["parent_acknowledge('resume') -> next question"]
  ACK -- "end" --> ENDP(["SESSION_END_BY_PARENT"])
  E -- "no" --> BACK["Back to the lesson"]
```

The parent view is **read-mostly** (durable transcript + mastery from the DB); its only write is
acknowledging an escalation (resume/end). It does not drive the tutoring FSM otherwise.

---

## 5. Where to look in the code

| Flow piece | Code |
|---|---|
| Child FSM (all states) | `src/mentar/dialogue/controller.py` |
| Scoring (deterministic) | `src/mentar/eval/verify_numeric.py` |
| Mastery (BKT) | `src/mentar/engine/bkt.py` |
| Item sources / generators | `src/mentar/engine/itembank.py`, `itemgen.py`, `science_items.py` |
| Safety classifier + handoff | `src/mentar/safety/escalation.py` |
| Web routes, subject picker, parent view | `src/mentar/web/app.py`, `templates/` |
| Curricula | `curriculum/templates/_pilot/*.md` |
