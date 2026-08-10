# CLAUDE.md

All project guidance is tool-neutral and lives in **[AGENTS.md](AGENTS.md)** — read that first
(setup, commands, src-layout, the pytest+ruff gate, and the protected-path RULES).

Claude-specific notes:
- **Memory is dual-located** — write to BOTH `~/.claude/projects/.../memory/` AND the repo's
  `.claude-memory/` on every memory change (the maintainer reviews via a network drive).
- **`gemma` skill** — delegate well-specified grunt coding to local `gemma4:12b`, then review its
  output (spec → gemma drafts → you verify). `gemma4:12b` is eval-host-only; it needs
  `MENTAR_VLLM_BASE_URL`/`MENTAR_VLLM_API_KEY` in the session.
- Commit trailer: `Co-Authored-By` only — **no `Claude-Session` URL trailer**.

---

## Local LLM delegation

A local LLM gateway is available. **Use it to conserve quota.** Delegate work
that fits the profile below, review the result, and never apply it unverified.

### Invoke

```bash
tools/llm.sh --rules <model> "<prompt>"        # code tasks: ALWAYS --rules
echo "<large spec>" | tools/llm.sh --rules <model>   # preferred for anything long
tools/llm.sh <model> "<quick question>"        # one-offs only
```

`--rules` prepends the delegation rules (grounding, no silent omission,
preserve-context, output blocks) as the system message. If your `llm.sh`
predates the flag, append the rules block below to the prompt manually
instead -- but update the script; manual appending gets forgotten.

Env comes from `.claude/settings.local.json`. Override `LLM_MAX_TOKENS`
(default 12000) if output truncates.

### Models and where they run

Two GPUs. **This determines what a model switch costs you.**

**GPU 0 — AMD Radeon AI PRO R9700, 32 GB — holds ONE of these at a time:**

| Model | Size loaded | Use for |
|---|---|---|
| `qwen3.6-27b-q5` | 19.5 GiB | **default.** general code, docs, batch work. Reasoning model. Cheapest KV, so it holds long context best |
| `devstral-24b-q5` | 20.6 GiB | multi-file / agentic edits. Smallest weights, most headroom |
| `gemma4-31b-q5` | ~24 GiB | second opinion — different family, so failures are uncorrelated |
| `skywork-swe-32b-q5` | ~26 GiB | SWE-specific. **16k context only** (BUG-11: spilled at 32k, ran 6x slow). Results non-comparable with the others above 16k |

**GPU 1 — NVIDIA RTX 3080, 10 GB — always resident, never swaps:**

| Model | Size loaded | Use for |
|---|---|---|
| `gemma4-12b-q4` | 7.4 GiB | small, fast, low-stakes. **No load penalty, ever** |

### What that costs you

Switching between any two GPU 0 models means **unload + cold load from disk:
12-60s**, every time. GPU 1 is a separate card, so `gemma4-12b-q4` never
competes and never waits.

Three rules follow:

1. **Batch your calls per model.** Ten calls to `qwen3.6-27b-q5` cost one cold
   load. Alternating ten times between two large models costs ten.
2. **A second opinion evicts your working model.** Calling `gemma4-31b-q5`
   while mid-session on `qwen3.6-27b-q5` unloads Qwen, and returning to it
   costs another cold load. Worth it for a genuine review pass; not worth it
   for a quick sanity check.
3. **For anything quick or throwaway, use `gemma4-12b-q4`.** It's on the other
   card, so it answers immediately *and* leaves your large model loaded.

Names use hyphens and a quant suffix. The old Ollama-style `gemma4:12b` is now
`gemma4-12b-q4`.

### DELEGATE these

- Boilerplate from a tight, complete spec
- Doc prose from a fact sheet
- Repetitive/batch transformations across many similar items
- Test scaffolding where the assertions are already decided
- First drafts that will be reviewed anyway
- Anything touching sensitive local data that shouldn't leave the LAN

### DO NOT delegate these

- Multi-step reasoning that spans several files
- Anything where complete ground truth can't be supplied in the prompt
- Final review or approval of correctness
- Security-sensitive logic
- Debugging that needs iterative tool use

The rule of thumb: **if you can write a complete spec, delegate it. If the task
is to work out what the spec should be, keep it.**

### Picking a model in practice

```
Is it quick, small, or throwaway?
  -> gemma4-12b-q4        (GPU 1, instant, doesn't disturb anything)

Is it a normal grunt task?
  -> qwen3.6-27b-q5       (GPU 0, the default; keep using it for the whole batch)

Is it multi-file editing?
  -> devstral-24b-q5      (GPU 0, evicts qwen -- worth it for a run of edits)

Do I need a genuinely independent check on a local result?
  -> skywork-swe-32b-q5   (GPU 0, evicts qwen. PROVISIONAL: moved from
                           gemma4-31b on a 1-of-5 completion rate since
                           reattributed to gateway timeout/retry bugs, not
                           the model -- see docs/OPEN-BUGS-lifecycle-and-
                           timeouts.md. Re-test gemma after the fix; its one
                           completion held the round's sharpest analysis)
```

When in doubt, stay on the model already loaded. The swap usually costs more
than the model difference buys.

### Every delegated prompt must include

1. **Complete context** — paste real file contents, not summaries. Context
   window is not the constraint; 32k is comfortable.
2. **A sibling example** if the task is "follow the existing pattern."
   Saying "follow the existing pattern" without the pattern present is the
   single most reliable cause of fabricated identifiers.
3. **Explicit scope** — which files may change, which must not.
4. **The rules block below**, verbatim, appended to the prompt.

### Rules block — append to every delegated prompt

```
RULES:

1. GROUNDING. Every identifier you reference -- function, method, class, table,
   column, stored procedure, import, config key -- must appear verbatim in the
   context above. Do not invent, guess or infer names. If something you need is
   absent, list it under MISSING rather than proceeding.

2. NO SILENT OMISSION. If any requirement cannot be completed, do the rest and
   list what you skipped under NOT DONE with a one-line reason. Never quietly
   drop a requirement.

3. PRESERVE CONTEXT. When editing existing code, change only what was asked.
   Do not reformat, rename, reorder, refactor, or update unrelated comments.
   Every line you did not need to change must be byte-identical.

4. NO PREAMBLE. No explanation of your approach, no restating the task, no
   closing commentary. Output only the blocks below.

OUTPUT:

FILES
<one path per line: every file created or modified>

ARTIFACT
<for each file: a line "=== <path> ===" then its complete final content>

NOT DONE
<one line per skipped requirement and why, or "none">

MISSING
<identifiers or information needed but not given, or "none">
```

### After delegation

**Never apply local output unverified.** Expected failure modes, all measured
on this setup:

| Failure | How it shows up |
|---|---|
| Fabricated identifiers | plausible-looking function/table/param names that don't exist |
| Silent omission | a requirement quietly dropped; output looks complete |
| Unrelated edits | reformatting, renames, touched lines outside scope |
| Truncation | empty output, `finish_reason=length` — a budget failure, not a bad answer |

Read the blocks the model returns:

- **`FILES`** — feed to `check_diff_scope.sh --declared`. The model declared its
  own scope; hold it to that.
- **`ARTIFACT`** — feed to `check_identifiers.sh --generated`.
- **`NOT DONE` populated** — this is a **success**. It failed loudly rather than
  silently. Handle the gap yourself.
- **`MISSING` populated** — the spec was underspecified. Add the missing context
  and re-run; do not let it guess.

**An EMPTY `NOT DONE` / `MISSING` proves nothing.** Measured 2026-08-09: two of
three models falsely reported `NOT DONE: none` and `MISSING: none` — one had
shipped a no-op, the other had silently deleted a method that broke 25 of 43
tests. A populated block is signal; an empty one is not evidence of anything.
Verify with the harness regardless of what the model claims.

Then verify:

```bash
<local-llm-infra>/linux/harness/run_checks.sh --mode code \
  --declared <FILES block> --generated <path> --ground-truth ./src --lang python \
  --must-define <the thing you asked for> --min-lines 20 \
  --test-cmd "<test command>" --baseline-file .harness/test.count
```

**Always pass `--must-define` AND `--must-call` when the task names a
concrete deliverable.** Measured (qwen run 4): a defined-but-never-dispatched
method passes `--must-define` and silently returns wrong data -- only
`--must-call` catches the dead-code case.
Without it, a model that does nothing passes every check — nothing changed
means nothing broken. That is the failure mode hardest to spot in review,
because it looks exactly like a clean diff.

A caught failure costs a retry. An escaped one costs more than doing the work
here in the first place — which is the whole reason the harness exists.
