# Overnight status — 2026-06-15 ~16:23 UTC (02:23 Brisbane)

## TL;DR
The T1.1 eval-dataset build **did not run**. The background build agent failed
**immediately on a usage/session limit** (`resets 1:40am Brisbane`) — 0 tokens, 0 tool calls.
**Nothing was built or committed for T1.1.** No half-finished state to clean up.

A scheduled **cloud** job was *not* set up because cloud routines can't reach this private
repo (`auto_disabled_repo_access`) **and** can't reach the LAN eval host `192.168.xx.xxx:4000`.

## What IS done and pushed (earlier today)
- W1.1 eval host recorded: LiteLLM OpenAI-compatible proxy `http://192.168.xx.xxx:4000/v1`
  (token via env, never committed). `llama3.1:8b`/`gemma2:9b`/`phi4-mini` verified responding.
- `docs/MODEL.md` — candidate roster, roles A–D, size→tier map, eval dimensions, run plan.
- Grounding (W7) reader + NAS/Samba + structured-source/auto-latest + config docs — all green.

## What's NOT done
- **T1.1 dataset** (`eval/dataset_v1.jsonl` + `eval/schema.json` + validator + `eval/models.yaml`
  + `eval/run_candidates.py` + `tests/eval/`). Fully specified, just not built (rate-limited).
- The eval **run** (T1.2) and scoring (T1.3–T1.6).

## Morning runbook
1. **Re-run the T1.1 build** (fresh Claude session after the limit resets). The complete contract
   is in `docs/TESTS.md` §T1.1 + `docs/MODEL.md`. (Ask Claude: "build T1.1 per docs/TESTS.md and
   the MODEL.md roster"; it's a self-contained Sonnet grunt task that self-commits when green.)
2. **Start testing** (needs your token in this box's env — that's why it can't be automated):
   ```bash
   export MENTAR_VLLM_BASE_URL="http://192.168.xx.xxx:4000/v1"
   export MENTAR_VLLM_API_KEY="<your token>"   # rotate the one pasted in chat
   python3 eval/run_candidates.py              # → eval/responses/{model}.jsonl (+latency)
   ```
3. **Score** — correctness via the existing `src/mentar/eval/verify_numeric.py`; rubric/safety
   per T1.4/T1.5; then W1.3 pick → fill the Decision section of `docs/MODEL.md`.

## Notes
- Rotate the eval token pasted in chat on 2026-06-15.
- Confirm exact Qwen base+quant for the `:9b`/`:2b` tags (no known "Qwen3.5" release).

_This file is a transient handoff — safe to delete once T1.1 is built._
