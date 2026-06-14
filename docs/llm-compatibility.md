# LLM Compatibility

⚠️ **TODO** — This document is a placeholder. Evaluation is an open task.

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
