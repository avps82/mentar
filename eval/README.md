# `eval/` — model evaluation harness

Welcome to the `eval/` folder! This is where we put candidate AI tutor models through their paces
before choosing the best one for a child. We create a set of maths questions, ask each model to
answer them, and then carefully score how **correct** the maths is, how **clearly** it explains for
a child, and how **safely** it behaves. Think of it as a fair, repeatable test to find the smartest
*and* friendliest tutor. *(This folder is the W1.2 / W1.3 workstream — see `docs/MODEL.md`.)*

➡️ **Human-readable results: [`docs/EVAL_RESULTS.md`](../docs/EVAL_RESULTS.md).**
Test specs (T1.1–T1.6): [`docs/TESTS.md`](../docs/TESTS.md).

## What's here

| File | What it does |
|------|--------------|
| `build_dataset.py` | Authored source of the question set → generates `dataset_v1.jsonl` (deterministic). |
| `dataset_v1.jsonl` | The 101 questions: 50 *explain*, 31 *transfer* (checkable maths), 20 *adversarial* (safety). **Git-ignored** — regenerate it; pinned by `dataset_v1.sha256`. |
| `schema.json` | The shape of one dataset item. |
| `validate_dataset.py` | Checks the dataset against the T1.1 rules → `reports/T1.1/result.json`. |
| `models.yaml` | The candidate roster + roles (candidate / ceiling / judge). |
| `run_candidates.py` | Asks each model every question and records answers + latency. `--system-prompt` runs the **full safety pipeline**. |
| `score_responses.py` | Scores **maths correctness** (transfer suite) with the deterministic verifier → `reports/T1.3/`. |
| `score_safety.py` | Quick keyword **safety** pre-screen of the adversarial answers → `reports/T1.5/`. |
| `judge_responses.py` | Uses a strong **judge model** (Sonnet) to grade explanation quality + confirm safety → `reports/T1.4/`. |
| `rubric.md` | The 0/1 criteria the judge applies. |
| `niah/` | "Needle-in-a-haystack" retrieval-faithfulness test (separate, adopted tool). |

## Quickstart

```bash
# 1. build + validate the question set (the .jsonl is git-ignored; this regenerates it)
python3 eval/build_dataset.py && python3 eval/validate_dataset.py

# 2. point at your local model endpoint (token via env — never commit it)
export MENTAR_VLLM_BASE_URL="http://192.168.xx.xxx:4000/v1"
export MENTAR_VLLM_API_KEY="<token>"

# 3. generate answers + score
python3 eval/run_candidates.py                       # all candidates (bare model)
python3 eval/run_candidates.py --system-prompt prompts/system_prompt.md --suite adversarial   # full safety pipeline
python3 eval/score_responses.py                      # maths correctness
python3 eval/score_safety.py                         # quick safety heuristic
python3 eval/judge_responses.py --model gemma2:9b    # judge-graded quality + safety
```

## Where results go

Raw per-model answers (`eval/responses/`) and scores (`reports/`) are **git-ignored on purpose** —
they can be large and the safety answers contain unsafe model text we don't commit. The committed,
readable summary is [`docs/EVAL_RESULTS.md`](../docs/EVAL_RESULTS.md). Tests for this harness live in
`tests/eval/` (all green).

## Important

These tools produce an **early signal, not the final pick**. Safety must be judged on the **full
pipeline** (model + `prompts/system_prompt.md`), not the bare model; a sample of judge grades needs
human review; and the final model decision (W1.3) is recorded in `docs/MODEL.md`.
