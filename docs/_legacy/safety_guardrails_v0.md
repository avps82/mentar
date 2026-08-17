---
type: Mentar Design Doc
title: Safety guardrails (v0 draft, superseded)
description: Superseded v0 guardrail draft; content folded into SAFETY.md. Not authoritative.
---

# Guardrails Spec

These are non-negotiable. They ship in the safety layer from day one — not bolted on later.

---

## Hard blocks (no exceptions)

- **No sexual content involving minors.** Absolute block. No context or framing changes this.
- **No content that sexualises, grooms, or facilitates harm to children.**

---

## Content safety

- All model output is screened for age-appropriate language and topics before being returned to the child.
- The active curriculum template defines the topic scope. The dialogue framework does not follow a child off-topic into unsafe territory.
- Violent, disturbing, or adult content is blocked regardless of how the request is framed.

---

## Anti-manipulation (legal line — EU AI Act Article 5)

The following are prohibited. Under EU AI Act Article 5 (in force Feb 2025), AI that exploits vulnerabilities of age or uses compulsive/gamified mechanics on children can constitute a **prohibited practice** with fines up to €35M/7% of turnover. This is a legal line, not just an ethics preference.

- No dark patterns
- No compulsive gamification mechanics (streak pressure, loss aversion, reward loops designed to maximise session time)
- No nudging toward continued use beyond what's educationally beneficial
- No persuasion techniques that exploit children's developmental vulnerabilities

---

## Emotion recognition — prohibited in EU context

Inferring a child's mood or emotional state to adapt lessons is legally fraught in the EU (EU AI Act narrow exceptions apply). Mentar does not implement emotion recognition. Adaptive difficulty is based on academic performance signals only (e.g., answer correctness), not inferred emotional state.

---

## Age-mode enforcement

Enforced by the safety layer. See `safety/age-modes.md` for full detail.

- **Under-13:** parent-mediated mode. A parent is in the loop. The child never has an unsupervised ongoing conversation with the AI.
- **13+:** more independent, with parental oversight available.

Age-13 is the recurring regulatory threshold (COPPA, UNESCO guidance, most major GenAI platforms). This is the design choice.

---

## Transparency

- The system must be identifiable as an AI to the child. No impersonation of a human tutor.
- Explanations should be honest about what the AI does and does not know.

---

## What the safety layer does NOT do

- It does not collect, store, or transmit data about the child (OSS local edition).
- It does not profile the child for advertising or third-party purposes.
- It does not make consequential decisions (grading, gating access to education).
