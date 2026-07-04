# Security & Safety

## Status: research preview — supervised single-family pilot only

Mentar is **pre-1.0 and in a controlled Phase-0 pilot.** It is **not** ready for unsupervised use
with real children. Do not deploy it as an independent/unattended tutor. Use it only with a
**parent or carer physically present** for the whole session, as a research/evaluation build.

This is a children's product, so we state the **known safety gaps openly** (full detail in
[`docs/SAFETY.md`](docs/SAFETY.md)):

- **No emergency-services signposting.** On a distress/safety trigger the child is routed to the
  **physically-present parent**, not to crisis numbers. This deliberately leaves a hole when *the
  parent is the source of harm* — signposting with safeguarding-professional input is required
  before any unsupervised mode. (W2.2 §6.1)
- **Handoff wording not yet professionally reviewed.** The fixed handoff messages pass an
  automated wording harness (`src/mentar/safety/handoff_check.py`) but still require sign-off by a
  safeguarding / child-communication professional. (W2.2 §6.2)
- **No PIN gate on parent mediation.** Parent-mediated mode is honour-based for the pilot; there is
  no authentication separating the child from parent controls. (SAFETY.md L5)
- **Distress auto-stop thresholds pending.** No automatic session-halt on distress yet; the
  present parent's judgement governs in the interim. (W5.6)

> **Rollout guard.** Mentar MUST NOT move beyond the supervised single-family pilot — in
> particular MUST NOT enable independent/unsupervised mode — until both W2.2 guards
> (emergency-services signposting **and** professional handoff-wording review) are closed.

## Data & privacy posture

- **Local-first:** the tutor runs on the operator's own hardware; no learner data leaves the
  device by design.
- **Immutable transcript:** session transcripts are append-only (enforced by DB triggers) for
  parental review.
- **Retention:** the pilot retains all data — no automatic purge/rolling-window mechanism
  exists. Deletion = delete the `.db` file (see SAFETY.md §4.6 for the ratified rationale and
  the transcript-immutability constraint that motivates it).

## Content licensing note

The grounding reader consumes **user-supplied** content (ZIM files the operator downloads). Some
sources (e.g. Khan Academy, CC BY-NC-SA) are **non-commercial**; do not use them in a commercial or
hosted deployment. See [`docs/LICENSE_AUDIT.md`](docs/LICENSE_AUDIT.md).

## Reporting a vulnerability

Please report security or child-safety issues **privately** — do **not** open a public issue:

- Use **GitHub → Security → "Report a vulnerability"** (private advisory) on this repository, or
- contact the maintainer listed in `pyproject.toml`.

We aim to acknowledge reports promptly. Given the child-safety domain, safety reports are
prioritised over feature work.
