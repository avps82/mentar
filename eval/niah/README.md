# eval/niah/ — Needle-In-A-Haystack (retrieval/grounding faithfulness)

NIAH is **adopted as the retrieval-faithfulness instrument** of W1.2 — it does NOT cover
hallucination/correctness or safety (those are our own T1 harness). Full assessment +
verdict: [`docs/design/W1.2_eval_tooling.md`](../../docs/design/W1.2_eval_tooling.md).

Verified 2026-06-15: clones, `pip install -e ".[dev]"` clean on py3.13, `niah demo --fake`
runs end-to-end, 209 tests pass, and the `openai` provider targets a local vLLM via
`base_url_env`.

## Run against local vLLM

```bash
pip install needlehaystack
export MENTAR_VLLM_BASE_URL="http://localhost:8000/v1"
export MENTAR_VLLM_API_KEY="dummy"          # vLLM usually accepts any token
# edit models/vllm.example.yaml: set id + request.model to the served model
niah run --config <a run config referencing models/vllm.example.yaml>
```

`niah validate ...` checks a config without calling the model; `niah reconstruct results.jsonl
--row N` replays the exact context a given cell sent. Scoring is deterministic
(`exact_match` / uuid needles) — no LLM judge required.

Run **each W1.2 candidate** (Qwen2.5-7B, Llama-3.1-8B, Gemma-2-9B, Phi-4-mini, …); poor
retrieval at our working context lengths is a disqualifier — a tutor that loses the grounding
passage will hallucinate to a child.

> Secrets: endpoint + key are read from ENV, never written to these files (config/README.md).
> `eval/responses/` and `eval/dataset_*.jsonl` / `eval/scores_*.csv` stay gitignored.
