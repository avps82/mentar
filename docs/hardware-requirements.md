# Hardware Requirements

⚠️ **TODO** — This document is a placeholder. Minimum requirements are an open task pending LLM evaluation.

---

## Goal

Define minimum CPU / RAM / storage needed to run Mentar locally at each hardware tier. Map compatible models to each tier so parents and contributors know what they can run.

---

## Proposed tiers (to be validated)

| Tier | Target user | RAM | Storage | GPU | Expected model |
|---|---|---|---|---|---|
| Minimal | Budget laptop, older hardware | 8GB | 10GB free | None (CPU only) | 1.7B–3B model |
| Standard | Modern laptop / desktop | 16GB | 20GB free | Optional | 3B–7B model |
| Performance | Gaming PC / homelab | 32GB+ | 50GB free | Discrete GPU | 7B–12B model |

---

## Key constraints

- **Models must live on SSD** — HDD load times make cold-start unusable (minutes per load vs seconds on NVMe)
- CPU-only inference is viable at small model sizes but noticeably slower. Acceptable for single-child use case.
- Quantisation (Q4/Q5) is assumed for all tiers. Full precision is not a target for local consumer hardware.

---

## Ollama as the recommended backend for non-technical parents

Ollama has the simplest local setup path (one install, `ollama pull <model>`). It is the recommended backend for the standard tier. Technical users can use llama.cpp directly for more control.

---

*Contributions welcome: benchmark a model on your hardware and add findings here.*
