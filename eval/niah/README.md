# eval/niah/ — Needle-In-A-Haystack (retrieval/grounding faithfulness)

NIAH is **adopted as the retrieval-faithfulness instrument** of W1.2 — it does NOT cover
hallucination/correctness or safety (those are our own T1 harness). Full assessment +
verdict: [`docs/design/W1.2_eval_tooling.md`](../../docs/design/W1.2_eval_tooling.md).

Verified 2026-06-15: clones, `pip install -e ".[dev]"` clean on py3.13, `niah demo --fake`
runs end-to-end, 209 tests pass, and the `openai` provider targets a local vLLM via
`base_url_env`.

## Run against local vLLM / the LiteLLM proxy

```bash
pip install needlehaystack
# 1. model config: cp models/vllm.example.yaml models/<stem>.yaml — set request.model to the
#    served id (e.g. gemma2:9b). NOTE: `niah run` resolves `model:` by FILENAME stem, not the
#    `id:` field, and --model-dir points at the dir.
# 2. ⚠️ GOTCHA: needlehaystack's openai provider reads api_key_env but IGNORES base_url_env —
#    it calls AsyncOpenAI(api_key=...) with no base_url, defaulting to api.openai.com. Route it
#    to the proxy via the SDK env var instead:
export MENTAR_VLLM_BASE_URL="http://<eval-host>:4000/v1"
export MENTAR_VLLM_API_KEY="<token>"
export OPENAI_BASE_URL="$MENTAR_VLLM_BASE_URL"   # <-- the fix; without it, calls hit OpenAI (401)
export OPENAI_API_KEY="$MENTAR_VLLM_API_KEY"
niah run <run.yaml> --model-dir models           # add --dry-run first to validate
```

Minimal run YAML (`task: uuid`, `haystack: text`; `model:` = the model-config filename stem):
```yaml
run_name: mentar-niah
model: gemma2                 # resolves models/gemma2.yaml
task: {type: uuid}
haystack: {type: text, text: "...filler sentence repeated to length... "}
sweep: {context_lengths: [1000, 2000, 4000], depth_percents: [10, 50, 90]}
store: {type: jsonl, path: /tmp/niah_results.jsonl}
```

**First result (2026-06-27, `gemma2:9b`):** **9/9 cells score 1.00** (perfect retrieval) across
1k/2k/4k context × 10/50/90% depth — no grounding-passage loss at pilot context lengths. ✅

`niah validate ...` checks a config without calling the model; `niah reconstruct results.jsonl
--row N` replays the exact context a given cell sent. Scoring is deterministic
(`exact_match` / uuid needles) — no LLM judge required.

Run **each W1.2 candidate** (Qwen2.5-7B, Llama-3.1-8B, Gemma-2-9B, Phi-4-mini, …); poor
retrieval at our working context lengths is a disqualifier — a tutor that loses the grounding
passage will hallucinate to a child.

> Secrets: endpoint + key are read from ENV, never written to these files (config/README.md).
> `eval/responses/` and `eval/dataset_*.jsonl` / `eval/scores_*.csv` stay gitignored.
