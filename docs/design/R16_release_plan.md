---
type: Mentar Design Doc
title: R16 — Release Wave (rendering contract, curriculum breadth, Singapore, OSS release)
description: Complete plan for the open bugs, the one-look-and-feel fix, full maths/science/English curriculum, the Singapore pack, and OSS release readiness. Planning only — nothing in here is built.
status: LIVE — plan + execution log (waves -1 through 2 and Y2 science shipped; see §H for per-item status)
timestamp: "2026-08-11T00:00:00Z"
---

# R16 — Release Wave

Started 2026-08-10 as a pure planning document; now also the execution log (statuses
updated in place as waves ship — see §F0-F2 and §H). File/line references were current at
the original read; sections marked ✅ describe what actually shipped.

Five workstreams — **A** rendering contract, **B** curriculum breadth, **C** Singapore,
**D** OSS release, **E** open bugs — plus **F**, which is not a workstream but the
local-LLM delegation policy that decides *who builds* each item in B and C.

---

## 0. What is actually wrong today (evidence, not impression)

### 0.1 The look-and-feel split has one root cause, not many

There are three rendering surfaces and only one of them can display a diagram correctly:

| Surface | Path | Font | Result |
|---|---|---|---|
| Question text | `_render_markdown_lite` → `.question-text` | **proportional** (`var(--font)`), `white-space: pre-wrap` | ASCII art misaligns |
| Explanation / feedback | `_render_markdown_lite` → `.msg-text` | **proportional**, `white-space: pre-wrap` | ASCII art misaligns |
| Arithmetic working | `render_steps_grid_lines` → `<pre class="steps-pre">` | **monospace**, `white-space: pre` | correct |

`_render_markdown_lite` (`src/mentar/web/app.py:833`) whitelists exactly four tags —
`<strong>`, `<em>`, `<ul>`, `<li>`. **It has no handling for fenced code blocks.**

Meanwhile **21 of the 24 files in `curriculum/visual_scaffolds/`** hand the LLM a fenced
ASCII diagram as the exemplar to imitate. So the model copies the pattern, emits a fence,
and the child sees literal ``` backticks wrapped around pipe-and-dash art rendered in a
proportional font. That is the whole "most are ascii text and some are html" complaint,
and it is one missing branch in one function — not a design taste problem.

The scaffold corpus also **contradicts itself**: `curriculum/visual_scaffolds/maths/fractions.md`
ends with *"Use emoji shapes (🟩 🟧 ⬜) for diagrams… instead of pipe-and-dash ASCII art"*,
while `curriculum/visual_scaffolds/english/parts_of_speech.md` ships three pipe-and-dash
ASCII blocks as its worked examples. 5 of 24 files push emoji, 21 push ASCII. Whichever
scaffold happens to keyword-match decides how that turn looks. That is why the app looks
different question to question.

Two supporting defects found while tracing it:

- `style.css:226` reads `font-family: var(--font-mono, monospace)` — **`--font-mono` is
  never defined** anywhere in the stylesheet. The one monospace surface in the app is
  running on the bare `monospace` fallback, i.e. whatever the browser feels like.
- There is an **uncommitted 62+/18− polish diff on `style.css`** in the working tree right
  now (layered shadows, gradient wordmark, pill trust-strip, hover transitions). It has to
  be landed or dropped before A starts, or A rebases onto a moving target.

### 0.2 Curriculum coverage is much thinner than the status doc implies

Every template in the tree, by subject and level:

| Pack | Maths | English | Science |
|---|---|---|---|
| `AU_ACARA` | Y2, Y3, Y4, Y5, Y6, Y7, Y8 | Y2, Y5, Y6 | — |
| `IN_GENERIC` | Class 3 | — | — |
| `_pilot` | fractions, arithmetic | — | `science.md` (`year_level: pilot`) |
| `practice` | sampler | sampler | — |

So: **no maths above Y8. No English at Y3, Y4, or Y7+. No year-levelled science at all** —
the single science template is unlevelled pilot content. Nothing for Singapore.

The cost driver is **not** the markdown. `curriculum/templates/AU_ACARA/year5_maths.md` is
131 lines / 7 nodes — a template is an afternoon. The cost is that every template names an
`item_source:` which must resolve in `engine/item_sources.py:46`, and each source is
**Python generators with a deterministic verifier**, because SPEC §14 forbids the LLM from
deciding correctness. 17 registry entries exist today. Full Y1–12 × 3 subjects × 3 packs is
where this stops being an afternoon.

### 0.3 The verifier ceiling blocks Y9+ before any authoring starts

Shipped answer types: `int`, `fraction`, `decimal` (R13), `mc_choice`. That set covers
primary maths, mc4 science, and mc4/cloze English. It **cannot express** Y9–12 algebra,
trigonometry, or calculus, where the correct answer is an expression and `2(x+3)` must
score equal to `2x+6`. No amount of curriculum authoring gets past this; it is a
prerequisite decision (see B0), not a step in the sequence.

---

## A — One rendering contract

**✅ SHIPPED 2026-08-10 (all of A0–A5, applied to the working tree, not committed).** See
the completion note at the end of this section for what actually happened, including one
real scope correction from the original estimate below (kept for the record — the "why"
still holds even though the "24 files" number turned out wrong).

**Goal:** every solution, explanation, and diagram in the app looks like it came from the
same product. One convention, enforced in one function and one CSS block.

The convention: **fenced monospace ASCII is the only diagram format.** Chosen over emoji
because 21/24 scaffolds and all four of the maintainer's own reference dumps
(`docs/design/year1_6_math_templates_reference.md`, `year7_12_math_...`,
`year1_12_science_...`, `year1_12_english_...`) already use it, and because it renders
identically at any font size on any device. Emoji stays as decoration inside prose, never
as diagram structure.

| # | Change | Where | Size |
|---|---|---|---|
| A0 | Land or drop the uncommitted `style.css` polish diff — decide first | working tree | decision |
| A1 | `_render_markdown_lite` gains fenced-block handling: content between ``` fences passes through escaped into `<pre class="ascii-art">`, never through the bold/italic/bullet regexes | `web/app.py:833` | ~15 lines |
| A2 | Define `--font-mono` (fixes the undefined var at `style.css:226`); merge `.steps-pre` and `.ascii-art` onto one shared "diagram box" rule — same surface, border, radius, `white-space: pre` | `static/style.css` | ~10 lines |
| A3 | Rewrite all 24 `visual_scaffolds/*.md` onto the single convention; delete the 5 emoji-diagram instructions | `curriculum/visual_scaffolds/` | 24 data files — **gemma** |
| A4 | State the contract once in the prompts: diagrams go in a fence, fences are used for nothing else | `prompts/system_prompt.md`, `prompts/help_visual.md` | ~4 lines |
| A5 | One golden-render test: fixture text with fence + bold + bullets → assert exactly one `<pre class="ascii-art">` and zero literal backticks in the output | `tests/web/` | one test |

**A1 is the root-cause fix.** Both proportional surfaces route through
`_render_markdown_lite`, so one branch there fixes the question, the explanation, and every
future surface that reuses it. Patching the scaffolds alone (A3 without A1) would leave the
fences rendering as literal backticks — symptom, not cause.

**Do A before B.** Every template and scaffold authored after A lands is authored against
the final convention. Authoring first means re-editing hundreds of files later.

**Verification is visual, not just green tests.** The house rule from
`project_r12_followup_bugs_2026-07-19` applies: reproduce through a real `mentar serve`
request path. "Code reads correct" is not evidence for a rendering change.

**Completion note (2026-08-10):** all done directly, not delegated — A1 is a trust-boundary
change (escape-first is the security property) and A2–A5 turned out small enough that
writing a delegation spec would have cost more than doing the work.

- **A1**: implemented exactly as scoped (fence extraction before the per-line bullet/bold/
  italic pass, wrapped in `<pre class="ascii-art">`). Verified against real, pre-existing
  content, not just synthetic fixtures — `curriculum/visual_scaffolds/science/
  states_of_matter.md`'s actual fenced table now renders as a genuine `<pre>` block with
  zero literal backticks, through the real `load_visual_scaffold` → `_render_markdown_lite`
  pipeline.
- **A2**: `--font-mono` defined; `.steps-pre`/`.ascii-art` share one "diagram box" rule.
  One deliberate divergence from the original estimate: `.ascii-art` gets `overflow-x: auto`
  (not `.steps-pre`'s `hidden`) — free-form scaffold content has no width guarantee the way
  the computed arithmetic step grid does, so clipping would silently reintroduce the exact
  misalignment this workstream exists to fix.
- **A3**: the "24 files, rewrite all of them" estimate was wrong — **21 of 24 already used
  fences correctly** and needed no content change once A1 landed; only the 4 files that
  actively told the model to prefer emoji *instead of* the fence needed fixing (a 5th
  emoji mention, in `algebra_equations.md`, turned out to already be decoration-only
  guidance, not a contradiction — checked before editing it, left alone). Fixed directly
  (one line each), not delegated — the actual fix was smaller than a delegation spec would
  have been.
- **A4**: found a second contradiction not in the original plan while implementing this —
  `prompts/help_visual.md` explicitly instructed emoji-shape diagrams
  ("🟩🟩⬜⬜ shows 2/4"), directly opposing the fence-only decision. Fixed, plus a new
  "Diagrams" section in `system_prompt.md` stating the convention once. Both are in the
  hash-gated prompt registry (T4.6/T7.3) — versions recomputed and `prompts/README.md`
  updated to match; verified via `test_prompt_registry.py`, not just eyeballed.
- **A5**: `test_markdown_lite_renders_fenced_ascii_diagrams` added to
  `tests/web/test_app_smoke.py` — fence rendering, bold/italic/bullet syntax correctly
  NOT processed inside a fence, and XSS-safety inside a fence (escaping is not a separate
  trust boundary from the rest of the function).
- **A0 still open, not resolved by this pass**: the pre-existing uncommitted `style.css`
  polish diff (gradient wordmark, layered shadows, hover states) is still sitting in the
  working tree, now with A2's changes layered on top of it with no conflicts. Whether to
  keep or drop that polish work is a product/taste call for the maintainer, not something
  to decide unilaterally while fixing the rendering contract.

Full suite: 739 passed (up from 738 — A5 adds one test). Nothing committed.

---

## B — Full curriculum: maths, science, English

### B0 — Prerequisite decision: the verifier ceiling (blocks B1, B4, B5 at Y9+)

Y9–12 maths needs expression equality. Two options:

- **Adopt `sympy`** — `simplify(a - b) == 0` is the whole verifier. Well-maintained OSS,
  focused library shape, matches the ratified dependency philosophy. Adds a real dependency
  to a project that currently has few.
- **Cap the curriculum at Y8** and ship Y9–12 as a later wave.

**Recommendation: adopt sympy.** Hand-rolling expression equality is writing a CAS badly,
and the alternative is telling a Y10 student the app has nothing for them. New answer type
`expression`, additive only — zero edits to the `int`/`fraction`/`decimal` paths, exactly
the shape R13 used for `decimal`. The R13 safety lesson carries over: a **strict regex gate
before `sympify()`**, because `sympify` on unrestricted input is an eval-shaped surface.
That gate is safety-critical and is **not** gemma work.

### B1–B5 — The build-out

| # | Scope | New templates | New generators | Notes |
|---|---|---|---|---|
| B1 | AU maths Y9–Y12 | 4 | 4 sets, `expression` type | Gated on B0 |
| B2 | AU English Y3, Y4, Y7–Y12 | 9 | 9 sets | Reuses the mc4/cloze shape in `au_english_items.py` |
| B3 | **Science Y2–Y12** — new subject | 11 | 11 fact tables | Extends `science_items.py`'s curated-fact-table shape; the *tables* are the work, the code is 59 lines today |
| B4 | `IN_GENERIC` Classes 1–12, all three subjects | ~30 | ~30 | Board-agnostic — forced by the NCERT/CBSE/ICSE licence findings, not a design choice |
| B5 | Singapore | see C | see C | Gated on the C1 licence check |

**Per-year acceptance gate** (already the house pattern from R14a/R15, do not skip):
`mentar validate` on the template → **500-draw self-validate** on the generators → **live
FSM round-trip** through a real serve process. A year is not done until all three pass.

**Ordering inside B:** B3 (science) first. It is the only entirely missing subject, its
generator shape already exists and is proven, and mc4 fact tables need no new verifier — so
it delivers the most visible breadth for the least risk while B0 is still being decided.

**Known coupling to flag, not fix here:** grounding is wired to **zero** non-pilot
curriculum (`decision_hybrid_content_architecture`, 2026-07-25). Every year added widens
that gap. B does not close it; the ratified retrieve-extract-verify-freeze pipeline does,
and that is a separate wave. Say so in the release notes rather than letting it look solved.

---

## C — Singapore

### C1 — Licence check FIRST (hard gate on everything else in C)

This is the NCERT lesson. India cost a full authoring plan before anyone read the licence,
and the answer was "no derivatives" — which is why `IN_GENERIC` exists instead of
`IN_NCERT`. `docs/design/MULTI_COUNTRY.md:75` already records that Singapore MOE publishes
**prose syllabus documents with no enumerated code scheme**, so per-node codes are simply
omitted (the schema already supports this — it was one of the two conventions the
multi-country stress test *confirmed*, not invented).

What is **not** yet known is the copyright position. Expect `© MOE, all rights reserved`
with no open licence — the common case for national education ministries, and the same
position as all three Indian boards.

Do this before authoring a single node: two independent searches of moe.gov.sg terms and
copyright pages, log the finding in `docs/CONTENT_LICENSES.md` §2b with the date and the
quoted text, then decide:

- **Open licence found** (unlikely) → `SG_MOE`, claimed alignment, codes omitted.
- **All rights reserved / permission required** (expected) → **`SG_GENERIC`** — a
  board-agnostic pack that teaches the same concepts at the same levels without claiming
  alignment or reproducing syllabus text. Identical strategy to `IN_GENERIC`, already
  proven through R8 and R10.

### C2 — "Downloaded": what that actually means here

Two things sit behind the word, and they resolve differently:

- **The syllabus PDFs** (reference material for authoring) — a `scripts/fetch_sg_syllabus.sh`
  following the house rule that repeated manual command sequences get wrapped in `scripts/`,
  never left as doc prose. **The sandbox will block this fetch.** The auto-mode classifier
  denies any agent-chosen external fetch regardless of prior verbal approval; only the
  maintainer's own typed `!` command clears it. Plan on the maintainer running it. Do not
  retry-loop.
- **The curriculum pack itself** — this is **not** a download. R10 settled it: shipped packs
  are in-repo on/off toggles in Settings, not downloads. `SG_GENERIC` ships in
  `curriculum/templates/` and appears as a toggle. The dormant R8 fetch path stays dormant.

### C3 — Authoring

Primary 1–6 and Secondary 1–4 maths first (10 templates + 10 generator sets), science and
English following only if C1 clears them. `year_level` stays free text — `"Primary 3"`,
`"Secondary 2"` — never parsed, never split into (stage, year). The UK stress test in
MULTI_COUNTRY.md §2 already confirmed that requirement.

### C4 — The pack-card mess

`PHASE0_STATUS.md:418` has an open maintainer complaint: *"in curricular card it is still a
mess .. need proper separation btw countries."* Adding Singapore as a third country makes a
known-messy screen worse. Group the cards by country with a header per country — this is
the natural moment, and it is a template change, not an architecture change.

---

## D — OSS release readiness

| # | Item | State | Notes |
|---|---|---|---|
| D1 | `pyproject.toml` → `license = { text = "TBD" }` | **Open — hard blocker** | W4.2 ratified **AGPL-3.0-only** and it was never applied. One line. Flagged at `docs/DOC_AUDIT.md:51`. Do this first. |
| D2 | Name reservation on npm + PyPI | **Open** | `docs/SPEC.md:69` (W4.1): publish placeholders to claim `mentar` *before* the repo is public. Ordering matters — after publication it is a race. |
| D3 | W2.2 professional safeguarding review | **Open — maintainer-gated** | Handoff wording + emergency-services signposting. `SAFEGUARDING_REVIEW_PACKET.md` is prepared and hands straight to a professional. **Not autonomous work.** Blocks anything past the supervised pilot; the README must say so plainly at release. |
| D4 | Secret + history sweep | **Not done** | `.gitignore` is sane (`*.db`, `reports/`, `dist/`, eval data all excluded) and no DB or model is tracked. Two things to settle: scan **git history** for the eval-host LiteLLM token, and decide whether `graphify-out/` (tracked: `graph.json`, `cost.json`, a PNG) belongs in a public repo — dev artifact, probably drop. |
| D5 | CI installs `[dev,web,grounding]` | Known gotcha | Not just `dev,web`, or libzim tests fail. Confirm before the release build. |
| D6 | Cloud-routine repo access | Blocked, may self-resolve | `auto_disabled_repo_access` because the repo is private. Going public may unblock it. Do not build anything that depends on it. |
| D7 | Attribution + obligations pass | Partly done | `CONTENT_LICENSES.md` is thorough. The one that must be surfaced, not buried: **Khan Academy is CC BY-NC-SA** — the NC clause is a live blocker against any paid hosted tier (§3, "Phase-3 blocker"). State it in the README, not only in the audit doc. |
| D8 | Doc truth pass | **Open** | The overnight sweep of 2026-07-13 found **4 stale `🔭` rows in `PHASE0_STATUS.md` that had actually shipped**. Never trust a `🔭` marker without verifying against the tree. Reconcile `PHASE0_STATUS.md`, `DOC_AUDIT.md`, and `REMAINDER_PLAN.md` before publishing. |

---

## E — Open bugs and issues

Everything currently known to be broken or unfinished, with the source it came from.

| # | Issue | Source | Assessment |
|---|---|---|---|
| E1 | **5 explain-method findings, none fixed** — 2 scaffold-routing bugs, 2 draw-dependent step-grid eligibility bugs, 1 where decimal-mult is almost never eligible | `docs/EXPLAIN_METHOD_AUDIT.md` (2026-07-25, audit-only) | Real. The decimal-mult one was caught **only by running real draws** — fix the same way, don't reason from the code |
| E2 | Restart button | `project_r12_followup_bugs` | Last unfixed of the original 5 |
| E3 | `--font-mono` undefined | `style.css:226` | One line; folded into A2 |
| E4 | No fenced-block handling in markdown-lite | `web/app.py:833` | The root cause; **is** A1 |
| E5 | Pack cards don't separate countries | `PHASE0_STATUS.md:418` | Folded into C4 |
| E6 | Settings toggle for step-grid display style | `PHASE0_STATUS.md:417` | Idea only. **Skip** — A gives one house style; a toggle to switch between styles is the opposite of the goal |
| E7 | Grounding wired to zero non-pilot curriculum | `decision_hybrid_content_architecture` | Not a bug — the unbuilt half of a ratified architecture. Disclose, don't paper over |
| E8 | T1.6 rubric `overall_pass` below the 90% gate | `PHASE0_STATUS.md` known defects | Open, prompt-iteration follow-up |
| E9 | htmx 4 migration | `docs/design/htmx4_migration_plan.md` | htmx 4 is beta. **Monitoring only — do not start.** Migrating a beta dependency during a release wave is gratuitous risk |

**Skipped deliberately:** E6 (a display-style toggle contradicts A), E9 (beta dependency,
wrong wave). Add E6 if families actually ask for it after A ships; start E9 when htmx 4 is
stable.

---

## F0 — Local-LLM infra: what was verified and fixed (2026-08-10)

Superseded: the old `gemma4:12b`-via-`MENTAR_VLLM_*` eval-host path referenced below in F's
prior version. A new gateway (`local-llm-infra`, `<local-llm-infra>`, source of
truth over any pasted copy) is now set up in this project — `tools/llm.sh`, five named
models across two GPUs, and a verification harness
(`local-llm-infra/linux/harness/run_checks.sh`). Before revising the delegation plan against
it, every piece was actually exercised, not assumed working:

| Checked | Result |
|---|---|
| `CLAUDE.md` local-LLM section, `tools/llm.sh`, `.claude/settings.local.json` env | All present, JSON valid, script executable |
| Bare call (`tools/llm.sh gemma4-12b-q4 "reply with OK"`) | ✅ Works, instant |
| `--rules` (mandatory for all code delegation per the standing rules) | ❌ Failed outright — `prompts/system-grunt.md` doesn't exist in this project. **Root cause**: this project's `prompts/` is a spec-gated dialogue-template registry (`tests/test_prompt_registry.py`, T4.6/T7.3) that globs every `*.md` under it and demands versioned front matter + a README hash entry. Confirmed by dropping the file there directly: 3 tests failed immediately. **Fixed**: `system-grunt.md` copied to `tools/system-grunt.md` instead (outside the registry, git-excluded alongside its sibling `llm.sh`); `llm.sh` patched with a one-line `${LLM_SYSTEM_GRUNT_PATH:-...}` override (falls back to upstream's default path when unset, so the vendored script's own behaviour is unchanged for any project that doesn't need the override) wired via `.claude/settings.local.json`. Verified: `--rules` now returns correctly-formatted `FILES`/`ARTIFACT`/`NOT DONE`/`MISSING` blocks |
| `gemma4-12b-q4` + `--rules` on a real artifact-shaped task | ❌ Failed twice — `finish_reason=length`, empty content, then `Context size has been exceeded` even at `LLM_MAX_TOKENS=4000`. **Root cause**: this is `local-llm-infra`'s own already-documented **BUG-4** (`docs/OPEN-BUGS-lifecycle-and-timeouts.md`) — `gemma4-12b-q4` is a reasoning model that burns its entire budget on hidden `reasoning_content`; `think:false` is silently ignored (an Ollama-ism llama.cpp doesn't know) and `reasoning_effort:"none"` is rejected by LiteLLM. The one thing BUG-4 measured as working — `chat_template_kwargs: {enable_thinking: false}` — is **not sent by the shipped `llm.sh`**, and the script's own on-failure advice ("raise `LLM_MAX_TOKENS`") is the *wrong* fix per BUG-4: this model has a hard `-c 16384` ceiling (BUG-12, its 10 GB card), so more budget just means more silent thinking, not an answer. **Fixed**: `llm.sh` patched to send `chat_template_kwargs: {enable_thinking: false}`, scoped to `gemma4-12b-q4` only (the only model with measured evidence either way). Verified: the same artifact task that failed twice now returns clean, correctly-formatted output |
| Model registry (`GET /v1/models`) | ✅ All 5 documented names present, no drift |
| Harness (`run_checks.sh --help`) | ✅ Runs, interface matches the `CLAUDE.md` block exactly (no doc drift) |
| `tools/ask-local.sh` (pre-existing, not part of this setup) | ⚠️ **Stale, not fixed** — a parallel, older tool for the same purpose. Different env var names (`LITELLM_URL`/`LITELLM_KEY`, neither set in `.claude/settings.local.json`) so it fails outright on its own env guard; hardcodes the same `system-grunt.md` path with no override; no reasoning-suppression fix. Left alone (wasn't asked to remove it) but flagged — two tools claiming the same job, one working and one silently broken, is a maintenance trap. Recommend deleting it or pointing it at `llm.sh`. |

**Both `llm.sh` fixes are deliberate, commented deviations from the vendored copy**, not
silent forks — each cites the reason (project-specific registry collision; upstream BUG-4)
so a future re-sync from `local-llm-infra` doesn't blindly overwrite them and reintroduce
either failure. Consider upstreaming both (the env-var override is generically useful for
any project with an incompatible `prompts/`-shaped directory; the `chat_template_kwargs` fix
is a correctness fix, not a Mentar-specific choice) — not done here since `local-llm-infra`
is a shared repo outside this task's scope.

**Measured capability evidence worth carrying into the routing below**
(`local-llm-infra/docs/2026-08-09-capability-validation.md`, one real multi-file task,
43 tests, temperature 0): `qwen3.6-27b-q5` was the *only* model of the four GPU-0 options
that shipped genuinely correct, working functionality. `devstral-24b-q5` completed fast
(318s) but silently built stub objects and never fetched them — 0 records, no error.
`skywork-swe-32b-q5` completed but re-fetched the wrong node 3× and returned duplicated
data. `gemma4-31b-q5` timed out entirely even at a raised 2400s ceiling. **"Completed
without error" is not evidence of correctness for any of these models** — devstral and
skywork's failures look exactly like clean diffs. This is the concrete case for why the
harness gate below is mandatory regardless of which model produced the output, not a
formality for the less-trusted ones.

---

## F — What the local LLM builds

The standing default (`feedback_local_generate_sonnet_verify`) still applies — **local
model generates, Sonnet/Opus verifies** — retargeted onto the new roster and pushed further:
with a 27B reasoning model and a 24B agentic model now available (not just a 12B), more of
this wave's grunt work can move off Sonnet/Opus quota than the original plan assumed.

### F1 — Calibration pilot: E2.2 delegated to `qwen3.6-27b-q5`, measured (2026-08-10)

Before trusting the routing table below on real curriculum work, one real advisory-judgment
task was run end to end to get a measured data point instead of a guess: **E2.2**, the
`explain_check.py` false-positive on division-with-remainder claims (`"12 ÷ 5 = 2 R 2"`
wrongly flagged as verified-wrong — see E2 above). Chosen because it satisfies the
advisory-judgment test above: the desired behavior reduces to a small truth table
(does `a == q×b + r` with `0 ≤ r < b`?) plus a pre-existing 16-test regression suite, so
verifying the result doesn't require re-deriving the fix myself. E2.3 (decimal claims,
same file) was deliberately left out of scope — see the "Not delegated" note above.

**Task spec sent to qwen:** complete file contents of `explain_check.py` and its test file,
the exact bug trace (already fully diagnosed in E2), a 7-row truth table of required
in/out behavior, explicit file scope (may edit the implementation file; may only *append*
new tests to the test file, never modify existing ones), and the `--rules` block.

**Result:** `tools/llm.sh --rules qwen3.6-27b-q5` — 9m36s wall time (mostly cold load; GPU 0
had nothing resident). Output: correctly-formed `FILES`/`ARTIFACT`/`NOT DONE: none`/
`MISSING: none`.

**Verification actually run** (not just re-running qwen's own claims):
1. Manual diff against HEAD — exactly 3 changed lines in the implementation (the regex, the
   tuple-unpack, one new branch) plus 1 trailing blank line; the test file diff was a pure
   append of 3 new test functions. Zero reformatting, zero renamed/reordered anything —
   clean PRESERVE CONTEXT compliance.
2. Applied, ran `pytest tests/engine/test_explain_check.py` — 19/19 pass (16 original + 3
   new, 0 changed, 0 removed).
3. **7 adversarial cases I wrote myself, not qwen's** — including a non-canonical-remainder
   case (`"12 ÷ 5 = 1 R 7"`, arithmetically self-consistent but `7 ≥ divisor`, must be
   WRONG) that wasn't in my own spec's truth table. qwen's fix rejected it correctly anyway
   (the `0 ≤ r < b` range check it added handles this on its own) — a genuine positive
   signal, not just spec-compliance. One of my own hand-checked cases had an arithmetic
   error in my prediction; the code's actual output was right and caught it.
4. Full suite: 735 → 738 passed (exactly +3, 0 regressions). `ruff check` clean.
5. `run_checks.sh --mode code --must-preserve ... --must-call normalise_fraction --json`:
   `check_preserved` passed once I fixed my own flag misuse (`--must-preserve` means
   *byte-identical to HEAD* — I'd wrongly listed `find_claims`, the function that was
   *supposed* to change; removing it from the list was the correct fix, not a harness bug).
   `check_diff_scope` reported a false "out-of-scope" failure — caused by unrelated
   pre-existing uncommitted changes already sitting in this working tree from earlier in
   the session (`CLAUDE.md`, this plan doc, `style.css`), not by qwen's edit. Confirmed via
   a direct `git diff --name-only` cross-check. **Operational lesson for future runs:**
   `check_diff_scope` needs a clean or task-isolated working tree (stash first, or a git
   worktree per delegated task) to be meaningful — running it against a tree with other
   in-flight work produces misleading collateral-damage failures unrelated to the task
   actually being checked.

**Verdict: qwen3.6-27b-q5 produced a correct, well-scoped, properly-tested fix for a
moderately subtle regex/judgment bug on the first attempt.** Not committed yet — applied to
the working tree, pending the same commit decision as everything else this session. This is
one data point, not a pattern — but it's real evidence advisory-judgment delegation to this
model is worth doing more of, at the E2.2 risk tier (bounded file, existing regression
suite, checkable truth table), not yet at the E2.4/E2.5 tier reclassified above.

### F2 — First production slice: B3 science, AU_ACARA Year 2 sound (2026-08-10)

Not another calibration pilot — the first real wave-4 deliverable, run to prove the
two-model split on actual content rather than a bug fix. Narrowed from the plan's original
"B3: Y2-12 science, 11 fact tables" down to ONE topic (sound/vibration, ACARA `AC9S2U02`)
for a concrete reason found while scoping, not caution for its own sake: the other two
natural Y2 topics had real, structural problems —
- **Solar system (`AC9S2U01`)**: the natural {planet, star, moon} fact-table shape breaks
  `mc_which_is`'s `rng.sample(pool, 3)` — targeting "planet" (5 members) leaves only
  star+moon (1+1=2) in the distractor pool, which crashes at runtime for a real child
  session, not at authoring time.
- **Materials change (`AC9S2U03`)**: bending/twisting/stretching/breaking don't cleanly
  partition into an unambiguous disjoint-classes MC shape at this reading level (a
  "twisted pipe cleaner" is arguably also bent) — content-design risk, not a coding one.

Shipping one structurally-sound node beats three where two have unresolved design risk.

**Split, applying the advisory/binding distinction from F1 directly:** the fact table
itself (is "a guitar string vibrates to make sound" true?) is binding judgment — cheap
for Opus to verify against general knowledge, so authored directly rather than delegated.
Writing the generator function/registry entry AND the template markdown against an
already-fact-checked table is advisory — delegated.

- **Template** (`curriculum/templates/AU_ACARA/year2_science.md`) → `gemma4-12b-q4`,
  16s. One real defect: it copied the sibling template's `engine/au_items.py
  AU_YEAR2_GENERATORS` comment line verbatim even though this template's items come from
  `engine/science_items.py`/`SCIENCE_GENERATORS` — my own spec gave explicit values for
  every field but that one connective comment line, so it fell back to copying the
  sibling unchanged rather than flagging the gap under `MISSING` as instructed. Caught on
  read-through, fixed directly (one line) rather than re-delegated. A second, unrelated
  typo ("ACAR" → "ACARA") also fixed directly.
- **Generator** (`engine/science_items.py`, new `_gen_sound_vibration` + registry entry)
  → `qwen3.6-27b-q5`, 3m30s. Clean — diff was a pure 3-block insertion, zero touched
  existing lines, matched the existing `_gen_states_of_matter` pattern exactly.
- **Registry wiring** (`item_sources.py`, one new entry pointing both `"science"` and
  `"au_science_year2"` at the same growing `SCIENCE_GENERATORS` dict) — done directly,
  not delegated. One dict entry with zero design freedom isn't worth a round-trip.
- **Visual scaffold** (`curriculum/visual_scaffolds/science/sound.md`) — done directly,
  not delegated. `tests/engine/test_scaffold_coverage.py` failed on the first full-suite
  run because the new node had no matching scaffold (a real, generically-useful gate this
  project already had — not something either model was asked about, since I hadn't
  scoped it into either task spec). Authored in workstream A's target rendering
  convention (fenced ASCII, no emoji-diagram instruction) even though A itself hasn't
  landed yet — costs nothing extra now and means this one file won't need touching again
  once A ships.

**Verification, all four layers, not just "tests passed":**
1. `mentar validate` on the template — pass, 1 concept, correctly identified as root+leaf.
2. 500-draw self-validate on the generator — zero crashes; every draw's marked-correct
   option independently re-derived and confirmed a member of the target category AND
   confirmed absent from the other category (disjointness holds every time, not just in
   qwen's own untested claim).
3. Full suite — 738/738 (same count as F1; this run added no new tests, just content).
   Two failures on the first pass, both real and both fixed directly: the golden-list
   catalog test (`test_template_catalog.py`) needed the new template added to `_EXPECTED`
   — expected maintenance, the test's whole documented purpose; and the scaffold-coverage
   gap above.
4. **Live FSM round-trip through a real `SessionController`** — not a stub. First attempt
   at this had a bug in the verification script itself (a stateful `ItemGenerator` reused
   across four supposedly-independent sessions, so each "answer attempt" silently drew a
   different random question instead of testing one question four ways) — caught before
   trusting the result, fixed with a freshly-seeded generator per session. Re-run: the
   same question, answered all four ways, produced exactly one PASS and three
   correctly-routed-to-Help responses, the wrong-answer fallback pulling a second,
   independently-correct worked example from the same fact table.

**Verdict:** the two-model split works on real content, not just a bug fix. The one real
defect (the copied sibling-reference line) was a spec gap on my side, not a model failure,
and was exactly the kind of thing the read-before-apply step exists to catch. Not
committed — applied to the working tree.

**Round 2 (same session): the remaining two Y2 topics, shipped.** Solar system
(`AC9S2U01`) and materials (`AC9S2U03`) needed their fact-table shapes redesigned first —
done directly (binding judgment, see the "Advisory vs. binding" split below), landing on
a 2-category `{is a planet / is not a planet}` split (avoids the earlier 3-category
`mc_which_is` pool-size crash) and a `{flexible / rigid}` materials split (avoids the
earlier bend/twist/stretch ambiguity). Same two-model split as round 1: `qwen3.6-27b-q5`
extended `science_items.py` with both generators in one batched call (5m56s, clean
insertion, zero touched lines); `gemma4-12b-q4` extended the template from 1 to 3 nodes
and flipped every "partial coverage" field to "complete" (22s) — one real defect this
time, a dropped digit in a re-typed ACARA code (`AC9S2U1` for `AC9S2U01`), caught on
read-through and fixed directly, same pattern as round 1's defect. Two new scaffolds
(`solar_system.md`, `materials_change.md`) authored directly, same reasoning as round 1.
Template now covers all 3 planned Year 2 Science topics — no longer partial.

**A verification-script bug worth recording, since it cost real debugging time:** the
live FSM round-trip initially appeared to fail — some answer attempts showed zero
correct letters, and the node presented seemed to change between what should have been
identical repeated attempts. Chased for a while (checked whether prior `random.Random`
construction could leak into a later one — confirmed via direct test it cannot; checked
whether the item generator's fact-table draw was non-deterministic — confirmed via direct
inspection it was not). **Root cause was in the check script, not the delegated code**:
`PRAISE_VARIANTS` has 5 randomly-chosen phrasings (`"Yes, that's it — great job!"` among
them), and the verification script's substring keyword list didn't cover all 5 — a
genuinely correct PASS was being misread as unrecognized/failing. Fixed by matching
against the exact `PRAISE_VARIANTS`/`WRONG_VARIANTS` lists imported from
`controller.py` instead of guessing keywords. Re-run: all 3 nodes correctly produce
exactly one PASS letter each. **The lesson generalizes**: a verification script is code
too, and an unverified verification script can manufacture a false failure as easily as
an unverified delegation can manufacture a false pass — don't stop debugging at "the
model must be wrong" without checking the checker first.

Remaining Y2 ACARA science content beyond these 3 topics (if any — this was scoped as
"the natural Year 2 slice," not audited against the full syllabus) is out of scope for
this session; Y3+ science and the other subjects' remaining year gaps are still the B1–B5
backlog in §B.

### Model routing per workstream

| Task | Model | Why |
|---|---|---|
| A3 — 24 scaffold rewrites onto one convention | `gemma4-12b-q4` | Mechanical, fixed target format, short per-file — its grunt-tier ceiling (BUG-12) is not a constraint here; GPU 1, free to interleave with anything else running on GPU 0 |
| B1–B5, C3 — curriculum template markdown (fixed front matter + node schema) | `gemma4-12b-q4` | Same shape as A3 — short, schema-constrained, high volume |
| B3 — science fact tables | `gemma4-12b-q4` | Bulk authoring against a table shape, verified against the curated source separately |
| B2/B4 — mc4 distractor lists | `gemma4-12b-q4` | Same |
| B1/B4/C3 — the **generator Python** behind each template (the actual checkable-answer code, `engine/*_items.py`-shaped) | `qwen3.6-27b-q5` | Real control-flow code needs correctness, not just schema conformance — this is the model the capability-validation round measured actually working, not just completing |
| Wiring a new pack into `item_sources.py` / multi-file registry changes | `devstral-24b-q5` | Multi-file/agentic shape fits its design intent — **but its own measured failure mode is a silent stub that never does the real work**, so treat its output with the same suspicion as any other, not more trust for being "the agentic one" |
| A genuinely independent second check on a risky local result | `skywork-swe-32b-q5` or `gemma4-31b-q5` | Evicts the GPU-0 working model — worth it for a real review pass (e.g. sanity-checking B0's sympy verifier design before it goes to Sonnet), not for routine work |
| D7/D8 — doc prose from a fact sheet (attribution paragraphs, status-doc corrections) | `gemma4-12b-q4` or `qwen3.6-27b-q5` | "Doc prose from a fact sheet" is explicitly in the DELEGATE list; the underlying facts (licence findings, stale-row list) are already nailed down in this plan, so it's transcription, not judgement |

**Batching note, corrected from the naive "batch per model" version of this rule:**
`gemma4-12b-q4` sits on GPU 1 and is always resident — it never evicts anything and costs
nothing to interleave. The cold-load cost is specifically GPU-0-to-GPU-0 switching. So: run
all the `gemma4-12b-q4` scaffold/template/fact-table calls for a wave in one batch (fast
regardless of interleaving), and separately batch every `qwen3.6-27b-q5` generator-code
call for that same wave together — don't ping-pong between `qwen` and `devstral` mid-wave.

### Advisory judgment vs. binding judgment (maintainer framing, 2026-08-10)

The routing table above is necessary but not sufficient — model *capability* is not the
only variable. The real split is:

- **Advisory judgment** — qwen produces a claim or draft whose correctness reduces to a
  small set of checkable facts: a truth table, an existing regression suite, a harness
  pass/fail. Verifying it costs a read of the diff plus running the checks — cheap,
  regardless of how much reasoning qwen did to get there. **This is delegable.**
- **Binding judgment** — the decision itself is what ships, and checking it means
  re-deriving the same reasoning chain qwen used, because there's no independent ground
  truth to check against (or checking it exhaustively would take as long as doing it).
  **This stays with Opus, regardless of qwen's raw ability on the task.**

The trap is scoping a task as "delegate because qwen can probably do it" without asking
whether *verifying* the output is actually cheaper than doing it. A task can be well
within qwen's capability and still belong on the Opus side of this line if confirming
correctness requires the same depth of reasoning as authoring it.

Reclassifying two items from the original routing pass under this lens:

- **E2.4** (the SAFE_REJECT/EXTRACT_FAIL asymmetry fix, 3 call sites in `controller.py`)
  — moved to **binding, keep with Opus**. Confirming the refactor changed *only* the
  intended branch at each of the three sites means tracing FSM state transitions by hand;
  there's no truth table that substitutes for that, so verification cost ≈ authoring cost.
- **E2.5** (the `escalation.py` jailbreak-exemption regex) — moved to **binding, keep
  with Opus**. The specific fixture (`"you are now a tutor"`) is cheap to check, but the
  real question — does the new pattern introduce a false negative somewhere in the safety
  classifier's much larger attack surface that the existing 20+20 fixtures don't cover —
  is not answerable by re-running the fixtures. That question requires the same reasoning
  as writing the fix.

### Not delegated — Sonnet or Opus, no local model, at any tier

- B0's `expression` verifier and the strict pre-`sympify` regex gate (safety-critical, same
  class as the R13 decimal regex and the `verify_numeric.py` decimal safe-reject)
- A1's renderer change (a trust boundary — escape-first is the security property)
- C1's licence determination (a judgement call with legal consequences)
- E2.3 (the decimal-claim fix) — not a precision-work exclusion like the original draft of
  this list said (E2.2 disproved that framing — see F1). The real reason: fixing it means
  deliberately overturning `test_decimal_claim_is_unparseable_not_a_failure`'s *asserted
  intent*, which requires reading why that test was written that way (pre-R13, before
  decimal answer types existed) and deciding it's now stale rather than a deliberate scope
  boundary. That's a binding judgment call about spec intent, not a checkable claim.
- E2.4, E2.5 — see the reclassification above
- Every acceptance gate and review, regardless of which model produced the draft

### Guardrails, learned the hard way (R14a + this setup pass)

- In R14a, gemma placed `concepts:` **outside** the YAML front matter. The file would not
  have parsed. It was caught in review — so review is load-bearing, not ceremony.
- Every delegated template/generator goes through **two** verification layers before it's
  committed, in this order:
  1. `local-llm-infra/linux/harness/run_checks.sh --mode code` with `--must-define` **and**
     `--must-call` for every named deliverable, `--must-preserve` for every frozen symbol,
     `--json > verdict.json` — catches fabricated identifiers, silent omission, and
     out-of-scope edits generically, regardless of content domain.
  2. Mentar's own domain gate, unchanged from the original plan: `mentar validate` → 500-draw
     self-validate → live FSM round-trip. The harness above doesn't know what a curriculum
     node or a BKT prior is; this is what catches a schema-valid-but-pedagogically-wrong
     template.
  An empty `NOT DONE`/`MISSING` block from either layer proves nothing — always run the
  harness regardless of what the model claims.
- `gemma4-12b-q4` needs `chat_template_kwargs: {enable_thinking: false}` or it burns the
  whole budget on hidden reasoning (BUG-4, now patched into this project's `tools/llm.sh` —
  see F0). It is also grunt-tier only on this rig (BUG-12, hard `-c 16384` ceiling) — fine
  for A3/B/C's template and fact-table work, wrong choice for the generator Python.
- One template (or one generator file) per call, spec in / markdown or code out. Batching
  many templates into one call is where schema drift enters.
- `--rules` is mandatory for every code-shaped delegation call in this project now that it
  actually works (F0) — it wasn't functional before this pass, so nothing in the earlier
  release-backlog work used it; don't assume prior local-model output went through it.

---

## E2 — Bugs found by reading the code (2026-08-10, new — not in the original doc-derived list)

The first pass of this plan was built from status docs and greps. This pass reads the
actual logic — `dialogue/controller.py` (1573 lines), `eval/verify_numeric.py` (safety-
critical verifier), `engine/explain_check.py`, `safety/escalation.py`, `engine/bkt.py`,
`engine/fringe.py`, `engine/arithmetic_steps.py` — end to end. Five real defects, each
reproduced directly (regex traced by hand or run), not inferred from a docstring.

| # | Bug | Where | Reproduction |
|---|---|---|---|
| E2.1 | Session-complete message hardcodes **"fractions"** regardless of the active subject | `controller.py:841` — `"Well done — you've mastered all the fractions concepts for today!"` | A21/`_SUBJECT_NAMES` (A7) already fixed this exact class of bug for the system prompt; this one line was missed. A science or English session ends by congratulating the child on "fractions" |
| E2.2 | `explain_check.py`'s arithmetic-claim verifier has no notion of remainder notation, so a **correct** division-with-remainder explanation gets flagged as verified-WRONG | `explain_check.py:23-32` (`_NUM`/`_CLAIM_RE`) | Traced by hand and confirms: `"12 ÷ 5 = 2 R 2"` matches the claim regex as `12 ÷ 5 = 2` (the `R 2` isn't recognized, doesn't block the match), computes `12/5 ≠ 2`, returns `ok=False`. `has_verified_failure` then discards the explanation and regenerates (`controller.py:1207`) — up to 2 attempts, then degrades to the generic fallback hint. "Remainder" is `build_long_division_steps`'s **default** ending, so this fires on ordinary division content |
| E2.3 | Same file: decimal arithmetic claims are never checked at all — `_NUM` has no `.` handling, so a claim like `"3.5 + 2.1 = 5.6"` fails to match the claim regex entirely and passes through **unverified** | `explain_check.py:23` | Traced by hand: the decimal point breaks the number token before the `=` can match, so the whole claim silently falls outside `_CLAIM_RE`. Not a false-positive like E2.2 — the opposite failure: SAFETY §6.2 Level 2's "verify numeric steps, discard on failure" guard is silently inert for every decimal claim, and R13 already shipped decimal content this applies to |
| E2.4 | SAFE_REJECT/EXTRACT_FAIL handling is asymmetric: `_do_score` re-prompts a garbled/unreadable answer without penalizing (`controller.py:934-957`), but `_do_help_recheck_score` and `_do_probe_score` don't have that branch at all — any non-PASS result, including an unreadable one, gets scored flatly WRONG | `controller.py:1289-1311` (recheck), `1398-1419` (probe) | Read directly: both call `check()` and set `..._scored_correct = (outcome.result is CheckResult.PASS)` with no branch for `SAFE_REJECT`/`EXTRACT_FAIL`. A malformed answer during a Help re-check or a proactive probe silently counts as a wrong answer against mastery/retry-count, instead of getting the same "couldn't read that, try again" nudge the first ask gets. No test in the suite exercises SAFE_REJECT at either of these two call sites |
| E2.5 | The adversarial-jailbreak pattern's own inline exemption for benign role statements doesn't work — `"you are now a tutor"` fires as a jailbreak match despite `"a tutor"` being explicitly listed as exempt | `safety/escalation.py:191` | Reproduced directly: `(a |an )?` is optional and greedy, so it consumes `"a "` *before* the negative lookahead `(?!a tutor|helping|assisting)` runs; the lookahead then checks for the literal `"a tutor"` at a position where `"a "` is already gone, so it never blocks. `pattern.search("you are now a tutor")` → matches. LOW severity (logged-only, not frozen), so no child-facing freeze, but it defeats the pattern's documented intent and pollutes the escalation log with false positives the 20+20 fixture set doesn't cover |

**Fixes are all small, root-cause, single-location changes** — consistent with the rest of
this plan's ladder-first approach:

- E2.1: `f"Well done — you've mastered all the {self._subject} concepts for today! Great work."` — one line, `self._subject` already exists on the controller.
- E2.2/E2.3: extend `_NUM` to accept a decimal component, and extend `_CLAIM_RE`'s trailing lookahead (or add a dedicated branch) to recognize `R <n>` as a valid claim terminator rather than an ambiguous trailing token. Needs a couple of new unit cases in the existing `find_claims` test file — this is exactly the kind of regex-precision work that wants a human check, not gemma.
- E2.4: root-cause fix is one shared helper — factor `_do_score`'s SAFE_REJECT/EXTRACT_FAIL branch out (it's currently inlined) and call it from all three scoring sites (`_do_score`, `_do_help_recheck_score`, `_do_probe_score`), per the house rule of fixing shared logic once rather than patching each caller.
- E2.5: reorder the pattern so the exemption is checked before the optional article is consumed, e.g. `(?:a |an )?(?!(?:a |an )?(?:tutor|helping|assisting))` — needs a regression test asserting `"you are now a tutor"` does **not** fire, since nothing in the current fixture set would have caught this.

None of these are fixed yet — this is a review pass, consistent with the "plan only, no
execution" instruction for this document. Add E2.1–E2.5 to wave 2 alongside E1–E3 in the
sequence below; they're comparably small and share the same root-cause-not-symptom shape.

---

## H — Complete missing-items inventory (2026-08-10 overnight pass)

Maintainer asked for a complete plan of everything still open, then autonomous execution
("keep doing all the task until completed"). This section is that inventory — every open
item, its disposition, and the reason. Statuses updated in place as the overnight pass
executes; each ✅ below was verified (tests + targeted checks), not just written.

### Executable tonight (in order)

| # | Item | Status | Notes |
|---|---|---|---|
| H1 | E2.1 — hardcoded "fractions" in session-complete message (`controller.py:841`) | ✅ done + regression test | One line, `self._subject` exists |
| H2 | E2.5 — jailbreak-pattern exemption broken (`escalation.py:191`) | ✅ done — BOTH the primary pattern and the despaced de-obfuscation fallback needed the exemption (the fallback re-fired on "youarenowatutor" after the primary was fixed; caught by the new regression test, 72 safety tests green) | Regex reorder + regression test the fixture set lacks |
| H3 | E2.3 — decimal claims never verified (`explain_check.py`) | ✅ done — `_NUM` gained decimals (exact Fraction arithmetic, so `0.1 + 0.2 = 0.3` passes where float math would fail); lookbehind extended to `(?<![\d./])` after adversarial checks found phantom mid-token claims ("3.5/7 + 1.5 = 2" must not verify a "7 + 1.5 = 2" nobody claimed); stale pre-R13 test overturned with documented rationale | **Binding judgment resolved**: `test_decimal_claim_is_unparseable_not_a_failure`'s rationale ("decimals out of pilot scope") is pre-R13 and stale — R13 shipped decimal answer types, Y5-8 decimal content is live, so SAFETY §6.2's verify-or-discard guard MUST cover decimal claims. The old test gets rewritten to assert the new behaviour, with a comment recording the overturn |
| H4 | E2.4 — SAFE_REJECT/EXTRACT_FAIL asymmetry (recheck + probe scoring) | ✅ done — shared `_handle_unreadable` helper, state assignments inline (T3.7 AST constraint), 4 new SESSION_FSM.md §3 rows, 2 regression tests. Two pre-existing tests used the literal string "wrong" as an incorrect answer — which only ever scored wrong BECAUSE of this bug (no extractable number); updated to a readable-but-wrong "999", preserving their real intent | Shared classification helper; `ctx.state` assignments stay inline in handlers (T3.7 AST test walks handler bodies); `SESSION_FSM.md` §3 table gains the two re-ask transitions |
| H5 | E1 Findings 1+2 — scaffold routing bugs | ✅ done — most-keywords-matched-wins in `visual_scaffold.py`; new `place_value.md` (gemma-drafted, 9s; applied after fixing its misaligned column table + one wrong guideline line on review); `decimals.md` keyword narrowed. All 7 routing cases verified through the real matcher + locked in a regression test | Root cause is shared: first-match-wins on alphabetical filename scan. Fix: **most-keywords-matched wins** in `visual_scaffold.py` (a more specific scaffold matches more of the label), plus a new `place_value.md` whole-number scaffold, plus `decimals.md`'s bare `"place value"` keyword narrowed to `"decimal place value"` |
| H6 | D1 — licence field | ✅ was ALREADY `AGPL-3.0-only` — `DOC_AUDIT.md` item 7 was itself stale (the exact D8 problem); DOC_AUDIT corrected instead | W4.2 ratified it 2026-06-27; one line |
| H7 | B0 — verifier ceiling decision | ✅ decided: **cap at Y8 for now** (sympy not installed; sandbox denies agent pip installs — adding the dependency is a maintainer action, design unchanged) | **Decided tonight: cap at Y8.** Not a change of recommendation — sympy is simply not installed and the sandbox denies agent-chosen `pip install` (`feedback_sandbox_blocks_agent_binary_exec`); adding the dependency is a maintainer action (add to `pyproject.toml` + install). The `expression` answer-type design stays as specced in B0; build resumes when sympy is present. Y9-12 maths authoring stays blocked behind it |
| H8 | C1 — Singapore MOE licence check | ✅ done — moe.gov.sg Terms of Use fetched directly + independent search 2026-08-11: all rights reserved, modifications prohibited, no open licence. **`SG_GENERIC` confirmed** (IN_GENERIC pattern); logged in CONTENT_LICENSES.md §2b with verbatim quotes | Two web searches + a dated `CONTENT_LICENSES.md` §2b entry; expected outcome `SG_GENERIC` |
| H9 | Commit + push in logical chunks | ✅ done (see git log) | Per `project_git_github_workflow` — SSH push to main works; maintainer asleep, so nothing left uncommitted overnight |
| H10 | Doc truth pass | ✅ done — PHASE0_STATUS changelog entry + DOC_AUDIT stale item 7 corrected | Avoid creating the exact stale-🔭 problem D8 exists to fix |
| H11 | Memory dual-write | ✅ done | Both memory locations per house rule |

### Explicitly deferred tonight (with reasons — not silently dropped)

| Item | Why deferred |
|---|---|
| E1 Findings 3+5 — draw-dependent step-grid eligibility (`au7_integers_add_sub` 21%, `au8_negative_multiplication` 23%, `au6_mult_decimals` 13%, `au7_mult_decimal_by_decimal` 1%) | The audit itself classified these as design-accepted: the exclusions are individually correct (signed/decimal arithmetic ≠ the unsigned column method), the inconsistency needs either a signed-number step-grid method or a decimal place-value method — each a real design+build the size of the original "show human working" phases. Not a tonight-sized item; needs its own plan |
| E1 Finding 4 — `au6_fraction_decimal_equiv` scaffold is "debatable, not wrong" | Audit's own words; building a dual-representation scaffold is polish, YAGNI until a real complaint |
| Restart-the-app button (R12 follow-up item 4) | `PHASE0_STATUS.md` already records it as "needs a design call (no in-process restart for a WSGI dev server)" — a design decision, not an overnight fix |
| A0 — pre-existing `style.css` polish diff | Maintainer taste call, explicitly left to them (see A's completion note) |
| B1 maths Y9-12, B2 English breadth, B4 India, B5/C3 Singapore authoring, science Y3-12 | Each slice = fact-table/content design (binding, mine) + delegation round + full verification ≈ 1-2h per slice. The pattern is proven (F1/F2); executing the full breadth is a multi-session effort, not an overnight one. **Next-session starting point: Y3 science (extend the proven Y2 shape), then English Y3/Y4** |
| D2 name reservation, D3 safeguarding, D4 history sweep, D6 cloud routines | D2/D3 are maintainer actions (publishing packages, commissioning a professional). D4's history sweep is worth doing carefully with the maintainer present (a found secret would need immediate rotation — not something to discover at 3am with nobody to rotate it). D6 self-resolves on going public |
| htmx 4 migration (E9) | Still beta, still monitoring-only |

## G — Sequence

Dependency-ordered. The ordering is not cosmetic — three of these gates exist because doing
the work in the other order means redoing it.

| Wave | Contents | Why here |
|---|---|---|
| **-1** | ✅ **DONE 2026-08-10** — local-LLM infra verified + 2 real bugs fixed (F0) | Prerequisite for delegating anything below with confidence |
| **0** | D1 licence field · D4 history sweep · A0 decide the uncommitted CSS diff | Hours of work; D1 blocks any public repo, A0 blocks A |
| **1** | ✅ **DONE 2026-08-10** — **A — rendering contract** (A1–A5; A0 still open) | Done directly, not delegated — A1 is a trust boundary, A2–A5 turned out smaller than a delegation spec. A3 was 4 files, not 24 (21 already used fences) |
| **2** | E2.2 ✅ **DONE**; E1, E2.1, E2.3–E2.5, E3 still open | Cheap, root causes known, and E1/E2.3 touch the same explain path A just changed. Not delegated — precision/binding-judgment work, see F's "Not delegated" list |
| **3** | **B0 — verifier ceiling decision** (sympy or cap at Y8) | Gates every Y9+ item in B1/B4/B5. A decision, not a build — not delegated. **Still open** |
| **4** | **B3 science: AU_ACARA Y2 ✅ DONE** (sound, solar system, materials — all 3 topics) → Y3–12 still open → B2 English → B1 maths Y9–12 → B4 India → **C Singapore** | Y2 proved the two-model split on real content twice (F1/F2). Templates/fact-tables → `gemma4-12b-q4`; generator Python → `qwen3.6-27b-q5`; fact-table design itself stays with Opus (binding judgment) |
| **5** | **D — release** (D2 name reservation → D7 → D8 → publish) | Name reservation before publication, docs true before publication. D7/D8 doc prose can delegate to `gemma4-12b-q4`/`qwen3.6-27b-q5` per F |
| **∞** | D3 safeguarding review | Maintainer-commissioned, runs in parallel, **gates rollout beyond the supervised pilot regardless of everything above** |

**The three real gates:** A before B (or you re-edit hundreds of files). B0 before Y9+ (or
you author curriculum no verifier can score). C1 before C3 (or you repeat NCERT). Local-LLM
delegation (F) rides inside waves 1 and 4–5 wherever the routing table says so; it doesn't
change the gate order, only who drafts the work inside each wave.
