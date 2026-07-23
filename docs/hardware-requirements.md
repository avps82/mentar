---
type: Mentar Audit Doc
title: Hardware Requirements
description: W1.4 hardware-tier mapping — what RAM/hardware runs which model tier. Partially validated against real eval-host runs.
tags: [hardware, eval, model-tiers]
timestamp: "2026-06-27T00:00:00Z"
---

# Hardware Requirements

W1.4 hardware-tier mapping. Partially validated (2026-06) against real runs; refine as more
models are benchmarked on the eval host.

---

## Goal

Define minimum CPU / RAM / storage needed to run Mentar locally at each hardware tier. Map compatible models to each tier so parents and contributors know what they can run.

---

## Tiers

| Tier | Target user | RAM | Storage | GPU | Model (Q4) | Example |
|---|---|---|---|---|---|---|
| Minimal | Budget / older laptop | 8 GB | 10 GB free | None (CPU) | 0.5B–3B | `qwen2.5:3b`, `phi3.5` |
| Standard | Modern laptop / desktop (incl. **MacBook Pro M1 16 GB**) | 16 GB | 20 GB free | Optional / Apple Metal | 7B–9B | `gemma2:9b` |
| Performance | Gaming PC / homelab | 32 GB+ | 50 GB free | Discrete GPU ≥ 10 GB VRAM | 12B+ (incl. reasoning) | `gemma4:12b` |

**RAM rule of thumb (Q4):** a model needs roughly **params × 0.6 GB** resident + ~1–2 GB
overhead. So a 12B Q4 ≈ 8–9 GB — it will **not** fit in 8 GB and is tight on 16 GB; a 9B ≈ 6 GB
fits comfortably on 16 GB.

---

## Validated data points (2026-06)

| Model | Where | Result |
|---|---|---|
| Qwen2.5-0.5B Q4 (in-process llama.cpp) | 2-core AMD A10-7800 (2014), 4 GB RAM, CPU-only | runs at **~7 tok/s**; loads in ~3 s |
| `gemma4:12b` (reasoning) | eval-host GPU via LiteLLM | ~14.6 s/item, full-GPU; **hangs on CPU-offload**; cannot run on 4 GB |

---

## Key constraints

- **Models must live on SSD** — HDD cold-start is unusable (minutes vs seconds on NVMe).
- **CPU instruction set:** stock `llama-cpp-python` / Ollama builds assume **AVX2**. On **pre-AVX2
  CPUs** (e.g. the AMD A10 above) they crash with `Illegal instruction` — build llama.cpp from
  source with `-DGGML_NATIVE=ON -DGGML_AVX2=OFF`. The Minimal tier must ship this fallback path.
- **Reasoning models** (e.g. `gemma4:12b`) need `think:false` (or a large token budget) or they
  return empty/truncated answers — see `config/inference.example.yaml`.
- CPU-only inference is viable at small sizes but slower; acceptable for single-child use.
- Quantisation (Q4/Q5) is assumed for all tiers; full precision is not a local-hardware target.

---

## Ollama as the recommended backend for non-technical parents

Ollama has the simplest local setup path (one install, `ollama pull <model>`). It is the recommended backend for the standard tier. Technical users can use llama.cpp directly for more control.

---

*Contributions welcome: benchmark a model on your hardware and add findings here.*
