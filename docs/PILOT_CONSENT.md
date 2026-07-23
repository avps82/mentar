---
type: Mentar Legal Doc
title: "Mentar — Pilot Parental Consent & Ethics Note"
version: v0.1 (template)
status: "Template — must be printed, completed, and signed BEFORE the first child session"
last-updated: 2026-06-14
sources: "PHASE0.md W2.5; SPEC §6.2 (parent-mediated mode), §16, §17.2; SAFETY.md §4.1–4.2, §4.3, Layer 3, Layer 5"
---

# Pilot Parental Consent & Ethics Note

**Gate (W2.5):** A completed, signed copy of this note must be **on file before the first
session with a real child**. No child session begins without it. This is a precondition of
the Phase-0 pilot, not paperwork after the fact.

> This is an informed-consent note for a small, supervised research pilot of an early
> prototype. It is **not** a commercial terms-of-service. The pilot runs local-only, with a
> parent/guardian physically present throughout.

---

## 1. What the pilot is

Mentar is an early prototype of a local-first AI tutor. This pilot tests a **fractions
(maths)** lesson flow with one child, to check that the tutoring engine, the Help loop, and
the safety layer work as intended. It is a prototype: it can make mistakes.

## 2. What is collected and where it lives

- All data stays **on the local device** — no cloud, no telemetry, no third party
  (SAFETY.md §4.1). Nothing about the child is transmitted off the device.
- Stored locally (SAFETY.md §4.3): learner profile (year-level, age-mode, curriculum),
  per-turn transcripts (child input + system response), BKT mastery state, Help/probe
  events, and any escalation-log entries.
- **You (the parent/guardian) can review every transcript and log** at any time, and can
  delete the data (SAFETY.md Layer 5).

## 3. Supervision

- The child is **under 13 → parent-mediated mode** (SPEC §6.2): a parent/guardian is
  **physically present for the entire session** and is the supervising adult.
- The pilot relies on the honor-system mechanism (parent present + full transcript logging
  + parent review); the PIN gate arrives in Phase 1 (SPEC §6.2).

## 4. Safety behaviour you should know about

- The safety layer is **active** during the pilot, as defined by SAFETY.md v0.1 (SPEC §23).
- If the child types something indicating distress or a safeguarding concern, Mentar will
  **freeze the lesson**, show a fixed, calm handoff message pointing the child to their
  grown-up, log the input verbatim for your review, and **raise an on-screen alert to you**.
  The lesson **will not resume** until you acknowledge it (SAFETY.md Layer 3).
- **Important interim limitation:** in this pilot, the only escalation route is **to you,
  the present parent** — there is no crisis-helpline signposting yet, and the handoff wording
  has not yet been reviewed by a safeguarding professional (SAFETY.md §3.5). **You are the
  safety net.** If any escalation flag appears, please intervene directly and immediately.
  Do not rely on the software to handle a distress disclosure on its own.

## 5. Your rights

- **You may stop the session at any time, for any reason, with no explanation.**
- You may review or delete any stored data at any time.
- Participation is voluntary; declining or withdrawing has no consequence.

---

## 6. Consent (to complete and sign)

By signing below, I confirm that I have read and understood the above, and I consent to my
child participating in the Mentar Phase-0 pilot under these conditions.

- Parent/guardian name: ____________________________
- Child's first name / identifier (no full name required): ____________________
- Child's age / year-level: ____________________
- [ ] I will be **physically present** for every session.
- [ ] I understand data stays local and I can review/delete it.
- [ ] I understand Mentar is a prototype and can make mistakes.
- [ ] I understand the escalation route is **to me**, and I will intervene if a flag appears.
- [ ] I understand I can stop the pilot at any time.

- Signature: ____________________________   Date: ______________

---

*File the completed, signed copy with the pilot records before session 1. Retain locally;
do not transmit. (W2.5)*
