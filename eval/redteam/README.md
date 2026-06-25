# Mentar red-team (promptfoo) — run-only

Generated adversarial probing of a candidate tutor model, as **defence-in-depth behind**
Mentar's real guardrails (the FSM escalation freeze + the deterministic verifier). It
complements the hand-authored `adversarial`/`sycophancy` items in `eval/dataset_v1.jsonl`
with promptfoo's *generated* attacks (jailbreak, prompt-injection, PII, harmful content,
plus a Mentar-specific distress/defer-to-adult policy).

> **Posture:** promptfoo is **run-only** — invoked via `npx`, **never vendored**, and **never
> added to `pyproject.toml`** (same arrangement as MathTutorBench). It is a dev/CI tool, not a
> Mentar runtime dependency.

## Prerequisites

- **Node ≥ 20.20.0 / ≥ 22** — promptfoo *refuses to run* below this (it's a hard gate, not a
  warning). The build sandbox ships 20.19.2, which is too old; use the eval host or CI.
- The eval-host **LiteLLM** endpoint + token, exported (never committed):
  ```bash
  export MENTAR_VLLM_BASE_URL="http://<eval-host>:4000/v1"
  export MENTAR_VLLM_API_KEY="<token>"        # rotate if ever exposed
  export MENTAR_REDTEAM_MODEL="gemma2:9b"     # the candidate to probe
  ```

## Privacy / telemetry (required)

- promptfoo bundles `posthog-node`; the "no telemetry" claim is conditional. **Always** run with:
  ```bash
  export PROMPTFOO_DISABLE_TELEMETRY=1
  ```
- **Generate attacks locally, not via promptfoo's cloud** (no child-adjacent prompts leave the
  host):
  ```bash
  export PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true
  ```

## Verify the config (do this first)

The schema/plugin ids in `promptfooconfig.yaml` were authored from the promptfoo docs and were
**not** run in the sandbox (Node too old). Before relying on it, validate on the host:

```bash
cd eval/redteam
npx -y promptfoo@latest validate -c promptfooconfig.yaml
# If a plugin/strategy id has drifted, refresh the catalog:
npx -y promptfoo@latest redteam plugins
```

## Run

```bash
cd eval/redteam
PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true \
  npx -y promptfoo@latest redteam run -c promptfooconfig.yaml
npx -y promptfoo@latest redteam report      # view the findings dashboard (local)
```

## Notes

- `targets` points at the OpenAI-compatible LiteLLM proxy; uncomment the `ollama:chat:` target to
  probe a local Ollama model instead.
- Raise `redteam.numTests` once a clean run is established; start small.
- This probes the **raw model**. Mentar's shipped safety lives in the FSM/verifier wrapper, so a
  raw-model failure here is a defence-in-depth signal (what would happen if the wrapper failed),
  not a shipped-behaviour bug on its own.
