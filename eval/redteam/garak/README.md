# Garak — LLM vulnerability scanner (run-only)

[Garak](https://github.com/NVIDIA/garak) (NVIDIA, Apache-2.0) probes a model for prompt injection,
jailbreaks, encoding attacks, and prompt/data leakage. We adopt it the **same way as promptfoo /
MathTutorBench / NIAH: run-only, never vendored, kept out of `pyproject.toml`.** It complements the
hand-authored `eval/dataset_v1.jsonl` (adversarial/sycophancy suites) and `prompt_injection.jsonl`.

## What it tests (and what it does NOT)

Garak probes the **raw model**. Mentar's shipped safety is the **FSM + deterministic verifier +
escalation classifier** wrapper — so a Garak finding is a **defence-in-depth signal** (what would
happen if the wrapper failed), **not** a shipped-behaviour bug on its own. Use it to:
- stress the model behind the tutor (the same endpoint the app calls), and
- mine new attack patterns to fold into `safety/escalation.py` + `prompt_injection.jsonl`.

## Install (separate env — NOT a Mentar dependency)

```bash
python3 -m venv .garak && source .garak/bin/activate
pip install garak            # heavy deps; keep out of Mentar's venv
```

## Run against Mentar's endpoint (OpenAI-compatible: LiteLLM / vLLM / Ollama)

Garak's `openai` generator uses the `openai` client, which reads **`OPENAI_BASE_URL`** (same gotcha
as NIAH — `base_url` env, not a flag). Point it at the proxy/Ollama and use Mentar's token:

```bash
export OPENAI_BASE_URL="http://<host>:4000/v1"      # your LiteLLM/vLLM, or http://localhost:11434/v1 for Ollama
export OPENAI_API_KEY="$MENTAR_VLLM_API_KEY"        # from config/.env / your environment
export GARAK_TELEMETRY=0                              # do not phone home (verify before running)

garak --model_type openai --model_name gemma2:9b \
      --probes promptinject,dan,encoding,latentinjection,leakreplay \
      --report_prefix mentar_garak
```

**Probe focus for a kids' tutor:**
- `promptinject` — direct prompt injection / instruction override
- `dan` — DAN / persona jailbreaks
- `encoding` — base64 / rot13 / other encoded-payload injection
- `latentinjection` — indirect injection (the **grounding** surface — our primary LLM risk)
- `leakreplay` — system-prompt / training-data leakage

## Posture / caveats

- **Run-only, never vendored**; nothing added to `pyproject.toml`.
- **Data egress:** Garak can report telemetry — set `GARAK_TELEMETRY=0` and verify no phone-home;
  the run also sends prompts to whatever endpoint you target (use the eval host / local Ollama, not
  a cloud you don't control — and never with real child data).
- Findings → triage into `safety/escalation.py` patterns + `eval/redteam/prompt_injection.jsonl`,
  and judge against the **wrapper** (FSM), not the raw model alone.
- See `../README.md` (promptfoo) and `../prompt_injection.jsonl` for the owned complements.
