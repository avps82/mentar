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

## First live run — 2026-06-27 (target `gemma2:9b`, all local)

Ran against the pilot pick `gemma2:9b` via the LiteLLM proxy; generation **and** grading routed
through the proxy's `claude-sonnet-4-6` (config `redteam.provider` + `defaultTest.options.provider`).

- **Result: 10 probes (`pii:direct` 5 + Mentar `policy` 5) → 4 passed / 6 failed (60% fail).**
- This is the **raw model, no Mentar pipeline** — consistent with the bare-model floor; the shipped
  FSM/verifier pipeline scored 80–85% on the hand-authored adversarial set (`EVAL_RESULTS.md`). Read
  it as a defence-in-depth signal: the wrapper is mandatory, never expose the raw model.

**Limitations found (config now reflects them):**
- The proxy's **Claude generator refuses** the explicit-harm plugins
  (`harmful:self-harm/sexual/graphic/harassment`) → 0 generated locally; they need an uncensored
  generator or promptfoo Cloud.
- The **iterative strategies** (`jailbreak`, `prompt-injection` meta) **require promptfoo remote
  generation** (cloud) — disabled for privacy, so `strategies: []` locally. Enable on a host via
  `promptfoo auth login` (or `PROMPTFOO_REMOTE_GENERATION_URL`).
- Env templating is **`{{ env.VAR }}`** (nunjucks), not shell `${VAR}`; `MENTAR_REDTEAM_MODEL`
  selects the target.

### Generator choice — verified 2026-06-27 (the harmful-coverage gap is structural)
We tried to close the explicit-harm gap **locally** by swapping the generator:

| Generator | Plugins generated locally |
|---|---|
| `claude-sonnet-4-6` (current) | `pii:direct` + `policy` (reliable); **refuses** all `harmful:*` |
| `mistral:7b-instruct` (uncensored attempt) | **only `pii:direct`** — too weak at promptfoo's structured generation; 0 harmful |

**Key finding:** a stronger *aligned* model does **not** help — `claude-opus`/`sonnet` refuse to
synthesise self-harm/sexual/graphic/harassment attacks by design (and Opus isn't on the proxy
anyway). The 7B "uncensored" route was capability-limited. So **explicit-harm + iterative-jailbreak
coverage is an open item that requires promptfoo Cloud or a genuinely uncensored, capable
generator** — not a bigger Claude. The local run reliably covers `pii:direct` + the Mentar policy
(the most Mentar-specific checks); treat the rest as the documented cloud/host follow-up.

## Notes

- `targets` points at the OpenAI-compatible LiteLLM proxy; uncomment the `ollama:chat:` target to
  probe a local Ollama model instead.
- Raise `redteam.numTests` once a clean run is established; start small.
- This probes the **raw model**. Mentar's shipped safety lives in the FSM/verifier wrapper, so a
  raw-model failure here is a defence-in-depth signal (what would happen if the wrapper failed),
  not a shipped-behaviour bug on its own.

---

## Prompt-injection test set (`prompt_injection.jsonl`)

A curated set of prompt-injection inputs for testing Mentar's **layered** defence. Each row:
`{id, category, surface, input, classifier_current, expected, note}`.

**Mentar's injection defences (test all three):**
1. **Deterministic safety classifier** (`safety/escalation.py`) — catches jailbreak/secrecy/etc. in
   child input → freeze + handoff. Runs FIRST, before anything reaches the LLM.
2. **Bounded FSM** — child input that the classifier doesn't catch is **scored by the deterministic
   verifier**, not fed to the LLM as an instruction. So an un-caught injection becomes a
   (non-)answer → `EXTRACT_FAIL` → re-prompt. It is **not executed**. (A classifier "GAP" is a
   missed *alert*, not a successful injection.)
3. **Grounding-as-data wrapper** (`prompts/system_prompt.md`) — the real LLM injection surface is
   untrusted **grounding** content (`surface: grounding`); the wrapper must make the model treat it
   as data and ignore embedded commands.

**Quick coverage check against the live classifier:**
```bash
python3 - <<'PY'
import json, sys; sys.path.insert(0, "src")
from mentar.safety.escalation import classify
for line in open("eval/redteam/prompt_injection.jsonl"):
    r = json.loads(line)
    if r["surface"] != "child_input":
        continue
    m = classify(r["input"])
    got = m.trigger_class.value if m else None
    flag = "ok " if got == r["classifier_current"] else "DIFF"
    print(f"[{flag}] {r['id']:16} classifier={got}")
PY
```

**Known classifier gaps (as of 2026-06-29) — defence-in-depth candidates, NOT live exploits**
(the bounded FSM still prevents execution): system-prompt **extraction**, **scope-break**/off-topic,
and **obfuscation** (leetspeak / spacing / base64). The `grounding_injection` rows must be tested
**end-to-end through the LLM** (they don't go through `classify()`); that's where the data-wrapper
is the only thing standing.
