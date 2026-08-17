---
type: Mentar Architecture Doc
title: Architecture (v0 draft, superseded)
description: Superseded v0 architecture draft, kept for history. Not authoritative — see docs/ARCHITECTURE.md.
---

# Architecture

## Core principles

**Local-first.** Inference runs on the user's hardware. No data leaves the device in the OSS edition. This is both a privacy design choice and a compliance advantage — when no operator collects data, most of the heavy COPPA/GDPR-K machinery doesn't attach.

**Supplement, not replace.** Mentar assists with learning within school curriculum boundaries. It does not grade, does not gate access to education, and does not make consequential educational decisions. This positioning is load-bearing: it keeps the system outside the EU AI Act's strictest Annex III high-risk education sub-categories.

**Safety baked in.** The safety layer is not an add-on. It ships as a first-class component alongside the template engine and dialogue framework.

---

## Three-component OSS core

### 1. Template engine

Reads curriculum Markdown files (country + year/grade level) and provides the dialogue framework with scoped learning context: topics, expected knowledge level, age-appropriate vocabulary bounds.

### 2. Dialogue framework

Manages tutoring sessions. Uses the active curriculum template to keep conversations on-topic and at the right level. Feeds every exchange through the safety layer before returning a response to the child.

### 3. Safety layer

Applies guardrails to model output and session behaviour. See `safety/guardrails.md` for the full spec. Key responsibilities:
- Content filtering (age-appropriate output)
- Age-mode enforcement (under-13 parent-mediated vs 13+ independent)
- Anti-manipulation enforcement (no dark patterns, no compulsive mechanics)
- Hard blocks (no sexual content involving minors under any circumstance)

---

## Inference abstraction

The inference layer is an abstraction over local LLM backends (Ollama, llama.cpp, etc.). Users can swap models without touching the core. The abstraction interface is defined in `src/inference/`.

See `docs/llm-compatibility.md` for tested model recommendations and `docs/hardware-requirements.md` for minimum hardware tiers.

---

## Tier separation

| | OSS local edition | Paid hosted tier (future) |
|---|---|---|
| Inference | On-device | Cloud |
| Data collection | None by design | Full COPPA/GDPR-K machinery required |
| Compliance exposure | Low | Heavy |
| Cost to user | Hardware only | Subscription |

The paid hosted tier is a planned future bridge for non-technical parents. It requires a separate, full compliance implementation. The OSS core stays data-light deliberately.

---

## Data flow (OSS local edition)

```
Parent sets up session
        ↓
Template engine loads country/year curriculum
        ↓
Child inputs question / response
        ↓
Dialogue framework builds prompt with curriculum context
        ↓
Safety layer pre-screens prompt
        ↓
Local LLM inference (on-device)
        ↓
Safety layer post-screens model output
        ↓
Age-mode check (parent-mediated if under-13)
        ↓
Response returned to child
```

No network call in the data path.
