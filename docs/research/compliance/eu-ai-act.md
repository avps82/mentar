---
type: Mentar Compliance Research
title: EU AI Act
description: EU AI Act (Article 5 + Annex III) mapping for the OSS local edition. Not legal advice.
tags: [compliance, legal, eu-ai-act, eu]
timestamp: "2026-07-23T00:00:00Z"
---

# EU AI Act

**Jurisdiction:** European Union  
**Relevant provisions:** Article 5 (prohibited practices), Article 6 + Annex III (high-risk), Article 50 (transparency)  
**Article 5 in force:** 2 February 2025

---

## The OSS exemption — what it does and does NOT cover

Being open-source does NOT dissolve EU AI Act obligations. The Act's OSS exemption explicitly carves out:
- Article 5 (prohibited practices) — travels regardless of open-source status
- Article 6 / Annex III (high-risk classification) — travels regardless
- Article 50 (transparency obligations) — travels regardless

Classification is about **what the system does**, not how it's built or licensed.

---

## Article 5 — Prohibited practices (ABSOLUTE, no proportionality)

Fines up to **€35M or 7% of global annual turnover**.

Relevant prohibitions for Mentar:
1. **AI that exploits vulnerabilities of age** to distort behaviour in a way that causes harm. The Commission's July 2025 guidelines explicitly cite compulsive/gamified mechanics on children as potentially falling under this.
2. **Manipulation using subliminal techniques** below the threshold of consciousness.

**Design implication:** "No dark patterns / no compulsive gamification" is now a **legal line**, not just ethics. Streak pressure, loss-aversion mechanics, and reward loops designed to maximise session time are potentially Article 5 violations. See `docs/SAFETY.md` (the former `safety/guardrails.md` was folded into it).

---

## Annex III — High-risk classification (education)

Annex III classifies AI used in education as high-risk, triggering: risk-management system, technical documentation, human oversight, logging, accuracy/robustness requirements, and conformity assessment.

**Mentar's position (to verify before EU distribution):**

The high-risk education category centres on AI making **consequential decisions** — admissions, grading, evaluating learning outcomes, exam monitoring. Mentar:
- Does NOT grade
- Does NOT gate access to education
- Does NOT make formal educational decisions
- Positions as a supplementary home tutor only

This may place Mentar outside the strictest Annex III sub-categories. **This requires careful reading of Annex III + Article 6 criteria before committing to EU distribution.** ⚠️ Not yet verified with qualified legal review.

Additionally: purely local, non-commercial self-hosting may not constitute "placing on market / putting into service" — which is the trigger for provider obligations. Also to verify.

---

## Article 50 — Transparency

AI systems that interact with natural persons must disclose that the person is interacting with an AI. Mentar must not impersonate a human tutor.

**Design implication:** Already captured in `docs/SAFETY.md` (the former `safety/guardrails.md` was folded into it) — the system identifies itself as an AI.

---

## Emotion recognition — prohibited in education (EU)

EU AI Act prohibits emotion recognition systems in education contexts, with narrow exceptions. Mentar does not implement emotion recognition. Adaptive difficulty is based on academic performance signals only. See `docs/SAFETY.md` (the former `safety/guardrails.md` was folded into it).

---

## Launch sequencing recommendation

Given the compliance uncertainty around Annex III classification:
- **US / parental-consent-first rollout** is substantially lighter than EU.
- OSS local edition carries lower exposure than hosted tier regardless of jurisdiction.
- Get qualified EU AI Act legal review before any EU distribution of a hosted tier.

---

*Not legal advice. Verify before commercial deployment.*
