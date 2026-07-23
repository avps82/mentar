---
type: Mentar Compliance Research
title: Compliance Overview
description: Cross-jurisdiction compliance posture mapping (COPPA, GDPR-K, EU AI Act, UK AADC) for the OSS local edition. Not legal advice.
tags: [compliance, legal, coppa, gdpr-k, eu-ai-act, uk-aadc]
timestamp: "2026-07-23T00:00:00Z"
---

# Compliance Overview

This folder documents Mentar's legal and regulatory compliance posture. Because Mentar is OSS, coverage status is documented here openly so contributors can see what's mapped, what's incomplete, and where they can help.

---

## The architecture advantage

The OSS local edition is **local-first and data-light by design**. This is not just a technical choice — it's a compliance strategy.

When data never leaves the device and no operator collects it:
- Most COPPA operator obligations don't attach (no operator collecting children's data)
- GDPR-K controller/processor roles likely don't apply (household-activity exemption may cover parent home use)
- EU AI Act "placing on market / putting into service" obligations may not apply to purely local non-commercial self-hosting

**Obligations concentrate in the paid hosted tier** (future). That tier will require full COPPA/GDPR-K consent machinery, data retention limits, security program, and potentially EU AI Act conformity assessment. Those obligations are NOT in scope here.

---

## Framework coverage

| Framework | Region | Status | File |
|---|---|---|---|
| COPPA (2025 amendments) | US | Mapped | `coppa.md` |
| GDPR-K | EU | Mapped | `gdpr-k.md` |
| EU AI Act (Article 5 + Annex III) | EU | Mapped | `eu-ai-act.md` |
| UK Age Appropriate Design Code | UK | Mapped | `uk-aadc.md` |
| California AADC | US (CA) | Partial — see `uk-aadc.md` | — |
| Australia Online Safety Act | AU | Partial | `australia.md` ⚠️ TODO |
| UNESCO GenAI in Education guidance | International | Applied (design decisions) | — |
| UNICEF AI and Children guidance | International | Applied (design decisions) | — |

**Contributors welcome:** if you know a jurisdiction not listed, add a file following the format of `coppa.md`.

---

## Cross-jurisdiction through-lines

These principles appear across every framework and are baked into Mentar's design:

- Verifiable parental consent for under-13
- Data minimisation + purpose limitation + retention limits
- Privacy by default and by design
- Best interests of the child as primary design lens (UNCRC-grounded)
- No profiling, no targeted ads, no detrimental use, no dark patterns
- Age-appropriate transparency
- Written security program (applies to hosted tier)
- Voice/biometric/device data treated as personal information

---

## What this folder is NOT

This is not legal advice. It is a good-faith mapping of frameworks for OSS contributor awareness. Before commercial deployment (especially hosted tier or EU distribution), get qualified legal review.
