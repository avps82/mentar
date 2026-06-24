---
title: "Mentar — Remainder Build Plan (Phase 0 → G0 + go-public)"
version: living-doc
status: "Active"
created: 2026-06-24
---

# Remainder Build Plan

Prioritised, high-gain-first plan for the work left to reach **G0 (pilot-ready)** plus the
**go-public** track. This is the executable spec; it **supersedes the stale "Next batch" section**
of [PHASE0_STATUS.md](PHASE0_STATUS.md) (status doc stays the canonical task ledger — update it as
waves land).

## Execution model

- **Local-generate → verify** (standing default): `gemma4:12b` drafts grunt code/specs; **Opus/Sonnet
  verify every output**. Reuse `eval/run_candidates.py` + `judge_responses.py` where relevant.
- ⚠️ **`gemma4:12b` is eval-host-only** (12B will not fit the 4 GB build sandbox). It runs via the
  eval-host LiteLLM proxy → **needs `MENTAR_VLLM_BASE_URL` + `MENTAR_VLLM_API_KEY` exported in the
  session**. Until that's present, Gemma routing is blocked and Opus builds directly.
- **Per-task gate:** `pytest` green **and** `ruff check .` clean before a task counts as done.
- **Owner tags:** **[G]** Gemma-generates → Opus/Sonnet verifies · **[O]** Opus/me (design / safety /
  integration judgment) · **[M]** maintainer-only (eval-host run, real ZIMs, or a human decision).

## Reality check (what's already DONE, vs the stale "Next batch")

Built + verified since "Next batch" was written (350 tests pass): grounding reader (W7.1–3),
dialogue controller + FSM, web app, item bank + parametric generator, inference backend, `mentar`
CLI, escalation persistence, stale-mastery wiring, prompt-template loading. The "Sonnet wiring
follow-ups" are essentially closed **except the DB-logging gap (Task 1.1 below)**.

---

## Priority waves — high gain first

### Wave 0 — Unblock the critical path (tiny effort, unblocks everything else) · [M]

| # | Task | Spec / acceptance | Gain |
|---|------|-------------------|------|
| 0.1 | **Supply eval-host creds to the session** | Export `MENTAR_VLLM_BASE_URL` + `MENTAR_VLLM_API_KEY` (rotate the key if it was ever exposed). | Unblocks **both** Gemma routing **and** the model eval run. Hard prerequisite for [G] tasks + Wave 2. |
| 0.2 | **W5.6 thresholds** | Confirm the (c) distress threshold + optional (e) time/€ runway line in SPEC §25.1 — defaults already proposed; a yes / numbers reply closes it. | Clears a standing G0 blocker in one message. |
| 0.3 | **W1.2 → W1.3 model run + pick** | Run the eval host (orchestration spec in 2.1). | THE model decision the whole pilot assumes. Everything downstream is provisional until picked. |

### Wave 1 — Close the data + safety gaps (highest-gain build)

| # | Task | Spec / acceptance | Owner | Gain |
|---|------|-------------------|-------|------|
| 1.1 | **Wire DB logging** (gap found 2026-06-24) | Controller/web must call `write_transcript` (every turn, both roles, monotonic `turn_index`), `write_response` (each scored answer + `check_result` + `hinted`), `write_help_event`, `write_probe_event`. **Accept:** a scripted full session populates all 5 tables; `/parent` renders the real transcript; tests assert per-session row counts. | **[G]** | Parent oversight, the **immutable transcript (a SAFETY-layer feature)**, and P1–P5 metrics all depend on this — currently silently empty. |
| 1.2 | **W2.2 handoff-wording validation** | Build a validation harness/test asserting `HANDOFF_MESSAGE_PRIMARY/SUPPORT` meet the frozen criteria (age-appropriate, routes to present parent, no false promises); then route for professional review. | **[O]** build · **[M]** review | Load-bearing rollout guard (blocks rollout beyond single-family pilot + public). |
| 1.3 | **W2.2 emergency-services signposting** | Safeguarding **decision** (needs external input) on whether/what to display, esp. the residual "parent is the source of harm" hole; then build the display/routing once decided. | **[M]** decide · **[O]** build | The other load-bearing rollout guard; blocks unsupervised mode + public. |

### Wave 2 — Eval execution → model pick (high gain; needs 0.1)

| # | Task | Spec / acceptance | Owner | Gain |
|---|------|-------------------|-------|------|
| 2.1 | **Run the candidate eval** | Export env → `run_candidates.py` (full roster) → NIAH (`eval/niah/`) → `judge_responses.py` (Sonnet) → `score_*` → write `docs/MODEL.md` pick (W1.3) + W1.4 tier. Opus orchestrates + analyses; maintainer runs on the host. | **[M]** run · **[O]** analyse | Produces the model pick (0.3) + the latency/quality evidence. |
| 2.2 | **promptfoo red-team scaffold** | `eval/redteam/promptfooconfig.yaml` + README, **run-only / never vendored**, pointed at LiteLLM + Ollama, Sonnet grader, kids'-safety threats (jailbreak / prompt-injection / PII / harmful / emergency-signposting). **Use LOCAL attack-gen, not promptfoo cloud.** ⚠️ host needs **Node ≥20.20 / ≥22**; set `PROMPTFOO_DISABLE_TELEMETRY=1`. | **[G]** | Generated adversarial coverage for the Wave-1 safety gaps; complements the hand-authored suites. Spike-verified working (see backlog row). |

### Wave 3 — Grounding completion (medium gain; not a hard G0 blocker)

| # | Task | Spec / acceptance | Owner | Gain |
|---|------|-------------------|-------|------|
| 3.1 | **W7.4 real-ZIM verification** | Acquire pilot ZIMs (Vikidia + Simple-WP) to NAS; point `zim_dir`; verify the reader's path convention against a real modern ZIM (W7.4 contract step 2). | **[M]** | Lifts the pilot from degraded (empty passages) to genuinely grounded. |

### Wave 4 — Go-public prep (high gain for the public goal; G2-track, not G0)

| # | Task | Spec / acceptance | Owner | Gain |
|---|------|-------------------|-------|------|
| 4.1 | **W4.2 license + LICENSE file** | Decide commercial posture (earlier thread: **AGPL-3.0 + CLA** recommended to preserve optionality); add `LICENSE`, fix `pyproject` `license = TBD`. | **[M]** decide · **[O]** apply | The repo is "all rights reserved" until this lands — disqualifying for a public OSS repo. |
| 4.2 | **Dependency + content license audit** | Confirm no AGPL/NC **code or content** vendored (Hermit-AI ideas-only; MathTutorBench not pulled in; only synthetic ZIM committed); deps compatible with the chosen license. | **[O]** | The "commercial eval" prerequisite for going public. |
| 4.3 | **SECURITY.md + README disclaimer** | Research-preview / controlled-pilot-only / not-for-unsupervised-child-use, with the documented safety gaps (1.2/1.3) named. | **[G]** | Stops public readers deploying a half-safe build to real children. |
| 4.4 | **AGENTS.md + CONTRIBUTING.md** | Focused subset of the ai-repo-structure convention (keystone `AGENTS.md`, thin `CLAUDE.md` pointer, contributor guide, safety/protected-paths rules). Skip the sprawl. | **[G]** | Contributor on-ramp; "don't start from scratch." |

---

## Sequencing notes

- **0.1 and 0.3 gate the most** — without eval-host creds, neither Gemma nor the model run can proceed.
- **Wave 1 is the highest-gain *build*** and is mostly sandbox-doable now (1.1 fully; 1.2 the harness).
- Waves 2/4 carry the [G] grunt work best suited to Gemma once 0.1 lands.
- Backlog items (promptfoo, AI-repo-structure, private/public MCP) feed Waves 2 and 4; the two MCP
  tasks remain "needs a proper plan" and are **not** in G0 scope.
