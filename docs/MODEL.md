---
title: "Mentar — Model Selection & Eval Plan (W1.2 / W1.3)"
version: living-doc (pre-decision)
status: "Candidate roster live on the eval host (2026-06-15). Eval run pending. W1.3 pick fills the Decision section."
last-updated: 2026-06-15
owner: Opus
refs: "SPEC §20 (local LLM), §20.3 (eval host), §15 (RAG/quality), docs/design/W1.2_eval_tooling.md, eval/niah/, docs/PHASE0_STATUS.md (W1)"
---

# Model Selection & Eval Plan

The pilot tutor must be a **local OSS model** (SPEC §20 — local-first; closed cloud models can be
opt-in only, never the default). This doc is the canonical eval roster + run plan; **W1.3 writes the
final pick into the Decision section** below.

## Eval host (W1.1 — connection details, supplied 2026-06-15)

- **Endpoint:** `http://192.168.1.191:4000/v1` — an **OpenAI-compatible LiteLLM proxy** on Pradeep's
  gaming PC, fronting all candidate models (≤14B run on the 10GB-vRAM GPU; larger ones CPU-offload).
- **Auth:** bearer token via env — **never commit it**. Set:
  ```bash
  export MENTAR_VLLM_BASE_URL="http://192.168.1.191:4000/v1"
  export MENTAR_VLLM_API_KEY="<token>"      # rotate the value pasted in chat on 2026-06-15
  ```
  (The NIAH harness reads these via `base_url_env`/`api_key_env`; see `eval/niah/models/vllm.example.yaml`.)
- **Verified 2026-06-15:** `llama3.1:8b`, `gemma2:9b`, `phi4-mini` all return `finish=stop` on a
  `say hello` chat-completion. Endpoint reachable from the build sandbox.

## Candidate roster

| Served id | Family | ~Size | Tier (W1.4) | Role | Notes |
|-----------|--------|-------|-------------|------|-------|
| `phi4-mini` | Phi | ~3.8B | low-end / broad-HW | **candidate** | strong small model |
| `qwen3.5:2b` | Qwen | ~2B | low-end / broad-HW | **candidate** | smallest; confirm exact base+quant |
| `llama3.1:8b` | Llama | 8B | mid (broad-HW default story) | **candidate** | best-supported on llama.cpp |
| `gemma2:9b` | Gemma | 9B | mid | **candidate** | |
| `qwen3.5:9b` | Qwen | ~9B | mid | **candidate** | confirm exact base+quant |
| `qwen3:14b` | Qwen | 14B (9.3GB) | capable-GPU | **candidate** | just fits 10GB vRAM |
| `mistral-small3.1` | Mistral | ~24B (15GB) | — (CPU-offload) | **CEILING, not candidate** | quality upper-bound; too big/slow for the pilot deployment envelope — do **not** pick as the tutor |
| `claude-sonnet-4-6` | Anthropic (cloud) | — | n/a | **judge / oracle** | grades candidate outputs; Phase-2 LLM-as-judge |
| `claude-haiku-4-5` | Anthropic (cloud) | — | n/a | **dev / cheap judge** | not a tutor candidate |

**Roles (keep distinct):** **A** local pilot candidate · **B** LLM-judge/oracle (Sonnet) · **C**
dev/agent (Claude Code) · **D** opt-in cloud backend (parent owns key, never default).

## Eval dimensions

Model quality directly gates pedagogical quality (SPEC §15). Score every candidate on:

1. **Hallucination** (own T1 dataset) — biggest risk; wrong facts to a child = safety failure.
2. **Correctness** (STEM/checkable; pairs with the deterministic verifier).
3. **Retrieval-faithfulness** — **NIAH** (adopted; `eval/niah/`) — does it answer *from* the grounded passage?
4. **Safety / refusal behaviour** (own T1 safety fixtures).
5. **Instruction-following / pedagogy** (pattern + Help-modality adherence).
6. **Latency = tokens/sec on representative hardware** — a model that aces quality but is too slow on a
   modest box fails the local-first bar. Record per candidate per tier (esp. CPU-offloaded ones).

## What needs to happen (run plan)

- [x] **T1.1 dataset** — BUILT 2026-06-16: 101 items (50 reexplain / 31 transfer / 20 adversarial).
      Source = `eval/build_dataset.py` (deterministic); the `.jsonl` is gitignored (regenerate with
      `python3 eval/build_dataset.py`) and **pinned** by `eval/dataset_v1.sha256`
      (`ba653976…eb7d069`). `eval/schema.json` + `eval/validate_dataset.py` (PASS) + `eval/models.yaml`
      + `eval/run_candidates.py`; `tests/eval/test_dataset_v1.py` green (regenerates if absent).
- [ ] **Env** — export `MENTAR_VLLM_BASE_URL` + `MENTAR_VLLM_API_KEY` (above).
- [ ] **Generate responses (T1.2)** — `python3 eval/run_candidates.py` → `eval/responses/{model}.jsonl`
      (101 prompts × 6 candidates; latency recorded). Runner built + dry-run verified.
- [ ] **NIAH pass** — run retrieval-faithfulness per candidate against the proxy (`eval/niah/`).
- [~] **Numeric correctness (T1.3)** — `python3 eval/score_responses.py` scores the transfer suite
      via `verify_numeric.py` per model (pass-rate + outcome breakdown + median latency →
      `reports/T1.3/scores.csv`). Built + tested; works on partial/complete `eval/responses/`.
- [ ] **Hallucination / safety / rubric (T1.4–T1.5)** — judge-graded; **Sonnet as judge/oracle**
      (no human-in-loop for every output). Not yet built.
- [ ] **Latency** — record tok/s per candidate (note CPU-offload for `mistral-small3.1`, big Qwen).
- [ ] **Score + pick (W1.3)** — fill the Decision section; map sizes → hardware tiers (W1.4).
- [ ] *(2nd pass, optional)* confirm Qwen `:9b`/`:2b` exact base+quant for reproducibility.

## T1.3 first-pass results — transfer numeric correctness (2026-06-16)

**ONE dimension only** — numeric correctness on the 31 checkable transfer items, via
`verify_numeric.py`. This is an early signal, **NOT** the W1.3 decision (NIAH retrieval,
hallucination, safety, and instruction-following are still pending). Latency = median seconds
per item over all 101 prompts, as served by the eval-host proxy (includes model-load/queue).

| Model | transfer pass | rate | median latency |
|-------|---------------|------|----------------|
| `gemma2:9b` | 31/31 | **1.00** | 7.5s |
| `qwen3.5:2b` | 19/31 | 0.61 | 2.6s |
| `qwen3.5:9b` | 19/31 | 0.61 | 13.7s |
| `llama3.1:8b` | 18/31 | 0.58 | 1.1s |
| `phi4-mini` | 15/31 | 0.48 | 1.0s |
| `qwen3:14b` | _(run still completing)_ | — | ~31s/item (partial) |

Observations (preliminary):
- Only **`gemma2:9b`** clears the T1.6 numeric gate (≥95%) — perfect on transfer, but ~7.5s/item.
- The others fail on **correctness alone** (≤0.61), before any other dimension.
- Latency spread is wide: `qwen3.5:9b` (13.7s) and `qwen3:14b` (~31s) look too slow for the
  broad-hardware envelope; `phi4-mini`/`llama3.1:8b` are sub-1.5s but weaker on correctness.
- `qwen3:14b` is slow enough that its run is still finishing; it had not reached the transfer
  items when scored. Re-score on completion.

Raw: `eval/responses/*.jsonl`; scores: `reports/T1.3/scores.csv`.

## Decision (W1.3) — TBD

_Pending the eval run. Records: chosen pilot model(s) per hardware tier, the scores that justified it,
and the kill-criteria check (SPEC §25.1(a): if no candidate passes the T1.6 quality gates, raise the
size ceiling once, then pause)._
