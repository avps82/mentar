---
type: Mentar Audit Doc
title: LLM Compatibility
description: Superseded placeholder retained for its evaluation-criteria sketch. Real results live in EVAL_RESULTS.md and MODEL.md.
tags: [llm, compatibility, superseded]
timestamp: "2026-07-22T00:00:00Z"
---

# LLM Compatibility

> ⚠️ **Superseded — placeholder retained for its criteria sketch only.** Actual evaluation results
> live in **[EVAL_RESULTS.md](EVAL_RESULTS.md)** (first run 2026-06-16) and the candidate roster in
> **[MODEL.md](MODEL.md)**. The W1.3 pick was made 2026-06-27: **gemma2:9b**.

---

## Goal

Identify smaller OSS models suited to educational dialogue with **low hallucination**. Hallucination control is critical for a children's tutor — a model that confidently states incorrect facts undermines learning and erodes parent trust.

---

## Evaluation criteria

- Hallucination rate on factual questions (education domain)
- Age-appropriate language generation quality
- Instruction-following fidelity (follows curriculum scope, stays on topic)
- VRAM / RAM footprint at given quantisation levels
- Context window (enough for a multi-turn tutoring session)
- Any specific education/child-safety fine-tuning

---

## Models to evaluate

Priority candidates (smaller, OSS, education-plausible):

| Model | Size | Notes |
|---|---|---|
| Gemma 3 (4B / 12B) | 4B–12B | Google, strong instruction following, small footprint |
| Phi-4-mini | ~3.8B | Microsoft, optimised for reasoning/education tasks |
| Qwen2.5 (3B / 7B) | 3B–7B | Strong multilingual — relevant for non-English curricula |
| SmolLM2 | 1.7B | HuggingFace, very small — viable for low-end hardware |
| Llama 3.2 (3B / 8B) | 3B–8B | Meta, widely tested |

Models specifically trained/tuned for education or child safety: **research needed**.

---

## Hardware tiers

See `docs/hardware-requirements.md` for the hardware tiers these models map to.

---

## Abstraction layer

The inference abstraction in `src/inference/` should support:
- Ollama (recommended for non-technical parents — easiest local setup)
- llama.cpp / llama-server (for technical users, more control)
- Future: vLLM for hosted tier

The abstraction must be swappable — users should be able to change models without touching core code.

---

*Contributions welcome: test a model against the evaluation criteria above and add findings here.*
