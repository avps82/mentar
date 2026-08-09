---
type: Mentar Design Doc
title: R16 — Release Wave (rendering contract, curriculum breadth, Singapore, OSS release)
description: Complete plan for the open bugs, the one-look-and-feel fix, full maths/science/English curriculum, the Singapore pack, and OSS release readiness. Planning only — nothing in here is built.
status: PLAN ONLY — not started, nothing executed
timestamp: "2026-08-10T00:00:00Z"
---

# R16 — Release Wave

Planning document. **No code was changed to produce this.** Every claim below was read
out of the working tree on 2026-08-10; file/line references are current as of that read.

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

## F — What the local LLM builds

The standing default already applies (`feedback_local_generate_sonnet_verify`): **gemma4:12b
generates anything it can, Sonnet verifies.** This section is only the routing table for
this wave — the policy itself is settled and is not re-litigated here.

**Gemma-suitable** — high volume, schema-constrained, machine-checkable:

- A3: 24 scaffold rewrites onto one convention (mechanical transform, fixed target format)
- B1–B5: every curriculum template markdown (fixed front matter + node schema)
- B3: science fact tables (bulk authoring against a table shape)
- B2/B4: mc4 distractor lists for English and science

**Not gemma** — Sonnet or Opus, no delegation:

- B0's `expression` verifier and the strict pre-`sympify` regex gate (safety-critical, same
  class as the R13 decimal regex and the `verify_numeric.py` decimal safe-reject)
- A1's renderer change (a trust boundary — escape-first is the security property)
- C1's licence determination (a judgement call with legal consequences)
- Every acceptance gate and review

**Guardrails, learned the hard way:**

- In R14a, gemma placed `concepts:` **outside** the YAML front matter. The file would not
  have parsed. It was caught in review — so review is load-bearing, not ceremony.
- Every gemma-drafted template goes through `mentar validate` → 500-draw self-validate →
  live FSM round-trip **before** it is committed. Machine-check immediately after each
  draft, not in a batch at the end.
- `gemma4:12b` needs `generation.extra_body.think=false` or it burns the whole token budget
  on hidden reasoning and returns empty content.
- It is **eval-host only** — needs `MENTAR_VLLM_BASE_URL` / `MENTAR_VLLM_API_KEY` in the
  session. A 12B model will not run in the 4GB sandbox.
- One template per call, spec in / markdown out. Batching many templates into one call is
  where schema drift enters.

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

## G — Sequence

Dependency-ordered. The ordering is not cosmetic — three of these gates exist because doing
the work in the other order means redoing it.

| Wave | Contents | Why here |
|---|---|---|
| **0** | D1 licence field · D4 history sweep · A0 decide the uncommitted CSS diff | Hours of work; D1 blocks any public repo, A0 blocks A |
| **1** | **A — rendering contract** (A1–A5) | **Must precede B.** Content authored after A lands is authored once |
| **2** | **E — bug fixes** (E1, E2.1–E2.5, E3) | Cheap, root causes known, and E1/E2.2/E2.3 touch the same explain path A just changed |
| **3** | **B0 — verifier ceiling decision** (sympy or cap at Y8) | Gates every Y9+ item in B1/B4/B5. A decision, not a build |
| **4** | **B3 science** → B2 English → B1 maths Y9–12 → B4 India → **C Singapore** | Science first: entirely missing, proven generator shape, no new verifier. C is gated on C1's licence answer |
| **5** | **D — release** (D2 name reservation → D7 → D8 → publish) | Name reservation before publication, docs true before publication |
| **∞** | D3 safeguarding review | Maintainer-commissioned, runs in parallel, **gates rollout beyond the supervised pilot regardless of everything above** |

**The three real gates:** A before B (or you re-edit hundreds of files). B0 before Y9+ (or
you author curriculum no verifier can score). C1 before C3 (or you repeat NCERT).
