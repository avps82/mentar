---
type: Mentar Status Doc
title: "Mentar — Remainder Build Plan v2 (post-G0-validation)"
version: living-doc
status: "Active"
updated: 2026-07-22
---

# Release Wave — pilot-ready main (status as of 2026-07-22)

**A1–A21 + B1 + B2 are ALL merged to `main`** (PRs #55–#74, all human-reviewed and merged by
the maintainer). B1 (re-pointed pilot grounding to Khan Academy — see B1's row below) merged
as **PR #73**; the small unrelated docs aside (README "Author's Funny Thoughts") merged as
**PR #74**. The entire release wave is closed — nothing from A1–A21/B1/B2 is outstanding.
Post-wave work (D-tasks: doc-truth fixes, `mentar backup`, explain_check division support,
this pilot runbook, the UI rebuild) tracked separately, not part of this wave.

A CI bug was found and fixed mid-wave: a job-level `permissions:` block in `.github/workflows/
ci.yml` was silently dropping `contents: read` (GitHub Actions `permissions:` *replaces*
defaults, it doesn't add to them) — fixed by adding `contents: read` alongside the job's
`pull-requests: write`.

**Goal (met):** close every codeable safety/correctness defect from the 2026-07-03 review
(A3–A19), plus A1/A2/B1/B2 and 2 new ratified tasks (A20/A21), so `main` is pilot-ready. Repo
stays private; going public is a separate later step. Maintainer-only C-rows (AGPL text paste,
token rotation, safeguarding review, consent signing) are OUT of this wave — see section C.

**Next actions for whoever picks this up:** (1) review/merge PR #73 (B1) and PR #74 (README
aside); (2) after that, this wave's local backlog is exhausted — remaining work is either
maintainer-only (section C) or post-pilot (see `PHASE0_STATUS.md`'s backlog section).

**Full plan (wave grouping, execution model, key-files map, research checkpoints) is at**
`<local-plan-file>` **on this machine** — that path is
NOT repo-tracked, so if it's gone, this section + the task table below is the source of truth;
re-derive the plan file from the Wave table if you want it back in that format.

## 3 maintainer decisions ratified 2026-07-04 (apply in this wave, not yet built)

1. **BKT Option B** — gate the `learns` transition on non-wrong observations only (a wrong
   unaided answer conditions/drops mastery, never adds `learns` credit). Fixes the
   counterintuitive "mastery % rises after wrong answers" behaviour documented in
   PHASE0_STATUS.md's 2026-06-29 modeling-decision note. Task **A20** below.
2. **Retention = option (ii)** — pilot retains everything; deletion = delete the `.db` file. No
   purge mechanism gets built this wave; docs reworded to say this plainly (folds into A4).
   90-day rolling purge design deferred to Phase 1 (kept as a C-row).
3. **Interaction-scope v0 (minimal subset)** — deterministic routing for "I don't know"-type
   input and question-shaped input (child asking a clarifying question) into the existing Help
   loop, unscored — same guard pattern as `_is_help_request`. The FULL taxonomy in
   `docs/design/INTERACTION_SCOPE.md` stays deferred/unbuilt; only this narrow slice ships. Task
   **A21** below.

## Wave order (do NOT reorder without reason — dependencies noted)

| Wave | Tasks | Status | Notes |
|------|-------|--------|-------|
| **0 — rails** | A12 | ✅ **DONE** (2026-07-04, PR #54, merged `b544978`) | CI matrix py3.11-3.13 + gitleaks CLI (MIT, pinned v8.30.1 — NOT gitleaks-action, which is commercial-licensed since v2). **Gotcha found + fixed:** `pip install -e ".[dev,web]"` is not enough — grounding tests need `libzim`, which lives behind its own `grounding` extra (spotty cross-platform wheels, so deliberately not in `dev`/`web`). CI installs `.[dev,web,grounding]`; manylinux wheels exist for cp311-313 on ubuntu-latest so this is safe. First run failed on this, second run (483630c) passed. |
| **1 — safety-critical, Opus-led, in order** | A3 → A15 → A8 → A13 → A14 | ✅ **Wave 1 ALL DONE + MERGED** — A3 (#55), A15 (#56), A8 (#57), A13 (#58), A14 (#59) | A3 (schema v2) unblocks A13's incident-row home + A19's session-row rng_seed column — do it first. Branches were stacked (same files touched across tasks); merged in stack order #55→#59. |
| **2 — correctness, Gemma-drafted/Opus-verified** | A17 → A16 → A5 → A6 → A9 → A7 → A20 → A21 | ✅ **Wave 2 ALL DONE + MERGED** — A17 (#60), A16 (#61), A5 (#62), A6 (#63), A9 (#64), A7 (#65), A20 (#66), A21 (#67) | A17 before A16 (layering clean-up first makes A16's startup hook land in one place). A20/A21 are the new ratified tasks — specs below. |
| **3 — assent/docs/hygiene** | A1 → A4 → A18 → A19 → A2 → A11 | ✅ **Wave 3 ALL DONE + MERGED** — A1 + A2 found **already shipped** (`e664658` / `a277b73`, doc drift corrected), A4 (#68), A18 (#69), A19 (#70), A11 (#71) | A1 before A4 (same controller preamble). A11 (FSM conformance test) runs **after** waves 1–2 since A9/A14/A21 add new FSM transitions the doc needs to capture. A18's own re-run caught + fixed a real eval-harness bug (see docs/MODEL.md 2026-07-05 note) — the A7 prompt change itself was confirmed safe (20/20, no regression). A19 bumped schema to v3 (`session.rng_seed`). A2's `run.example.yaml` re-verified `--dry-run` clean on this host. A11 removed the dead `PARENT_ACK_WAIT` state and fixed 2 stale transition-table edges the new T3.7 test caught. |
| **4 — QA + doc close-out** | B1 → B2 → close-out | ✅ **Wave 4 ALL DONE + MERGED** — B1 + B2 (#72, bundled), B1's final Khan Academy re-point (#73) | B1's "skipped" status was corrected: the maintainer pointed out `/mnt/zim` was always readable — the real gap was narrower (that mount holds Wikipedia/KhanAcademy/gutenberg/StackExchange, never Vikidia/Simple-WP), resolved by re-pointing to Khan Academy rather than waiting on a NAS upload. B2 (doc-drift sweep) ran last so it reflected the post-wave state. **Every A/B task in this backlog is built and merged.** |

**Execution model (unchanged from plan):** one branch + PR per task; gate = `pytest tests/ -q`
green (398 baseline, will grow) + `ruff check .` clean + the task's own Accept criteria (specs
below / already in this file for A3–A19). `[G]` tasks → `gemma` skill (spec → gemma4:12b drafts →
Opus reviews); `[O]` tasks → Opus direct (safety-critical). Research checkpoints (don't guess):
CI tooling / blocklist sourcing / BKT-variant literature / COPPA-GDPR-K wording — verify live via
WebSearch/Context7 at execution time, not from training-data memory (maintainer directive
2026-07-04).

**Environment notes for next session:**
- `eval/.creds.env` holds `MENTAR_VLLM_BASE_URL`/`MENTAR_VLLM_API_KEY` — source it before
  `tools/llm.sh`/gemma calls; not in the shell env by default.
- The sandbox's auto-mode permission classifier blocks agent-downloaded-and-executed external
  binaries (hit this trying to dry-run the gitleaks CLI locally for A12) — such steps must
  either go through an existing declared dependency/tool or be verified via the actual CI run
  instead of a local smoke test.
- `git branch -a` currently shows several stale-looking remote branches unrelated to this wave
  (`batch-session`, `docs/backlog-*`, `eval/niah-*`, `feat/credential-guard`, `feat/w5.6-assent`)
  — pre-existing, not touched this session, not this wave's concern unless the maintainer flags
  them.

## New task specs (A20, A21 — not yet in the A3–A19 table below)

### A20 — BKT Option B: gate `learns` on non-wrong observations `[O]`
- **Why:** ratified 2026-07-04 (see above). Current recurrence applies `learns` credit after
  *every* attempt (SPEC §11 / W3.3), so wrong answers from a low prior still raise mastery
  (verified: 10%→21%→22%, plateaus, never false-masters — but counterintuitive for a
  parent-facing %). REVIEW/PHASE0_STATUS 2026-06-29 note recommends Option B.
- **Spec:** in `src/mentar/engine/bkt.py`, apply the learning transition
  `P(L') = P(L|obs) + (1−P(L|obs))·learns` only when the observation is NOT a wrong
  attempt; a wrong answer only runs the conditioning step (posterior drops via slip/guess), no
  `learns` term added. Correct observations — hinted or not — and probes still get the `learns`
  credit as before.
  **(Amended 2026-08-16.** This said "NOT a bare-wrong (unaided incorrect) attempt" and listed
  "Hinted-win" as still earning credit, which contradicted this task's own Accept line below.
  The implementation followed the narrower wording, so the ~22% plateau the task exists to remove
  survived on the hinted path — the path the Help loop actually drives. Body now matches the
  title and the Accept criterion.) Add a literature reference in
  `docs/design/W3.3_bkt.md` for the "no-learning-on-incorrect" BKT variant (research the term
  before writing — don't assert a citation from memory). Update SPEC §11 to reflect the deviation
  from classic BKT.
- **Files:** `src/mentar/engine/bkt.py`, `docs/design/W3.3_bkt.md`, `docs/SPEC.md` §11,
  `tests/engine/test_bkt.py`.
- **Accept:** new invariant test — a wrong-answer streak from cold start never raises mastery
  above the prior (was: rises then plateaus ~22%; should now: stays flat or drops); existing
  7 W3.3 invariants still verified; hinted-win / correct-answer paths unchanged (regression).

### A21 — interaction-scope v0: don't-know + question-shaped input → Help, unscored `[G]` draft, `[O]` verify
- **Why:** ratified 2026-07-04, minimal slice of the deferred `INTERACTION_SCOPE.md` design.
  Currently every non-answer input is force-scored as an answer (corrupts BKT) unless it matches
  the narrow `_is_help_request`/`_is_stop` guards. "I don't know" and clarifying questions are
  common enough child input to warrant a deterministic carve-out now, without building the full
  taxonomy.
- **Spec:** add `_is_dont_know(text)` (case-insensitive match on "i don't know", "idk", "no idea",
  "dunno", "i dont know") and reuse/extend a question-shaped check (starts with
  what/how/why/when/where/who/can/is/does, OR ends in `?`) as a new guard in the answer-await
  states (mirrors `_is_help_request`'s wiring — same states, same routing target: the Help loop,
  unscored, no BKT update). Safety classifier (Bucket D) still runs first, unchanged. Check
  `docs/design/INTERACTION_SCOPE.md` for any existing phrase inventory before inventing one from
  scratch. Note in that doc that this v0 slice shipped; full taxonomy still deferred/needs
  maintainer ratification.
- **Files:** `src/mentar/dialogue/controller.py`, `tests/dialogue/test_controller.py`,
  `docs/design/INTERACTION_SCOPE.md` (status note only).
- **Accept:** "I don't know" and "what does numerator mean?" both route to Help unscored (no
  response_log row, no BKT update, matches `_is_help_request` test pattern); a genuine numeric
  answer is unaffected; existing help/stop guards unaffected.

---

# UI review round 2 (R2) — tight specs, gemma-executable

Maintainer's second hands-on review (2026-07-10, after review round 1 shipped). Two
findings, both `[G]` (route through the `gemma` skill: spec → gemma4:12b drafts → Sonnet/Opus
verifies; needs `MENTAR_VLLM_*` from `eval/.creds.env`; remember `think:false` is handled by
`tools/llm.sh`). **Do R2.1 first** — it changes what the TTS reads, so R2.2's audio behaviour
depends on it. Per-task gate unchanged: `pytest tests/ -q` green + `ruff check .` clean +
Accept criteria; one commit per task.

## R2.1 — MCQ shows its options THREE times; web should show stem + radios only  `[G]` ✅ DONE 2026-07-11 (commit e264652)

- **Why (maintainer finding, verbatim symptom):** an mc4 question renders as
  *"Which of these is a non-living thing? A) a tree  B) a flower  C) a fish  D) a spoon.
  Answer with the letter. (answer with a letter: A, B, C or D)"* **and** the same four
  options again as radio buttons — the options appear in the inline text, the format hint
  repeats the letters, and the radios repeat the options. The TTS also reads the options
  twice (once from the question text, once from the radio labels).
- **Design (structure at the source, same principle as the R1 turn-payload fix — never
  string-strip the options back out):** mc generators return the question **stem** and the
  options separately; ONE central place composes the inline "A) …" text for surfaces that
  need plain text (CLI, transcript, parent view); the web learner view renders stem + radios
  only, with **no format hint** (the radios make the answer shape obvious).
- **Spec:**
  1. `src/mentar/engine/itembank.py` — `Item` gains `stem: str | None = None` (after
     `choices`; same comment style: the question WITHOUT the inline options, for surfaces
     that render choices structurally). `load_item_bank` reads `stem=d.get("stem")`.
  2. `src/mentar/engine/itemgen.py` — new module-level helper:
     `def compose_mc_problem(stem: str, choices: Sequence[str]) -> str` returning
     `f"{stem} " + "  ".join(f"{L}) {c}" ...) + ". Answer with the letter."` (exact format
     the generators use today — copy it, don't invent). In `ItemGenerator._make`: when the
     generator returned choices, treat the 3rd tuple element as the STEM — set
     `problem=compose_mc_problem(stem, choices)`, `stem=stem` on the Item; non-choice
     generators are unchanged (stem=None).
  3. `src/mentar/engine/science_items.py` `_mc_which_is` — return the stem WITHOUT the
     inline options (delete its local composition; it becomes
     `(answer_type, checker, stem, letter, options)`). Keep the fact-table logic identical.
  4. `src/mentar/engine/au_items.py` `_mc` — same change: drop the inline composition,
     return the stem; delete the now-unused `opts_text` line.
  5. `src/mentar/dialogue/controller.py` — new read-only property `current_question_stem`:
     `getattr(self._ctx.current_item, "stem", None)` when state in `_QUESTION_AWAIT`, else
     None (mirror `current_choices`' shape/docstring style). `question_display` composition
     is UNCHANGED (CLI/transcript keep the full inline text + letter hint — they have no
     radios).
  6. `src/mentar/web/app.py` `_turn_context` — when `choices` AND
     `ctrl.current_question_stem`: `question = ctrl.current_question_stem` (stem only, no
     format hint). Otherwise unchanged.
- **Files:** the five above + `tests/engine/test_au_items.py`,
  `tests/engine/test_science_items.py`, `tests/web/test_app_smoke.py`,
  `tests/dialogue/test_controller.py`.
- **Accept (hand-write the tests — gemma's self-written tests are only trusted for pure
  helpers):**
  - mc items carry `stem` (no "A)" inside it) AND `problem` still contains "A)" and
    "Answer with the letter" (CLI/transcript unchanged) — assert both in the au/science
    generator tests.
  - web: for the science subject, the `.question-text` div contains the stem but NOT "A)"
    and NOT "(answer with a letter"; the 4 radios still render; `/parent`'s transcript
    still shows the full inline options text.
  - controller: `current_question_stem` returns the stem for an mc item and None for an
    int item.
  - Full suite + ruff green.

## R2.2 — TTS: pause/resume instead of restart-from-the-top  `[G]` ✅ DONE 2026-07-11 (commit d85788e) — needs maintainer's hands-on audio check

- **Why (maintainer finding):** clicking 🔊 while it's reading restarts the whole sentence;
  there's no pause. Wanted: click → pause icon; click again → pause; click again → resume
  from where it stopped.
- **Design:** a three-state button driven by the Web Speech API's `pause()`/`resume()`:
  `idle` (🔊 "Read the question aloud") → click → `speaking` (⏸ "Pause") → click →
  `paused` (▶️ "Resume") → click → `speaking`. Natural end (or error) → back to `idle`.
  State lives module-level in the script (the button element is REPLACED by every htmx
  swap, so never store state on the element).
- **Spec — rewrite `src/mentar/web/static/tts.js` (owned, no deps, ~60 lines):**
  1. Keep the feature-detect (hide `.tts-btn` when `speechSynthesis` is unavailable) and
     the document-level click delegation (survives htmx swaps with no rebinding).
  2. Module state: `let state = "idle";` Click on `.tts-btn`:
     - `idle` → assemble text from `.question-text` textContent + each `.choice-option`
       textContent (joined ". "), `speechSynthesis.cancel()` first (clear any stale queue),
       create the utterance (rate 0.9), set `utterance.onend` AND `utterance.onerror` to a
       `reset(btn)` that restores 🔊/aria-label and `state="idle"`, then `speak()`;
       `state="speaking"`, button shows ⏸ with `aria-label="Pause"`.
     - `speaking` → `speechSynthesis.pause()`; `state="paused"`; button ▶️
       `aria-label="Resume reading"`.
     - `paused` → `speechSynthesis.resume()`; `state="speaking"`; button ⏸.
  3. New-question safety: `document.body.addEventListener("htmx:afterSwap", ...)` →
     `speechSynthesis.cancel(); state="idle";` — WITHOUT this, the previous question's
     audio keeps playing over the new question (the swap replaces the button, which comes
     back as 🔊/idle by construction, so only the module state + audio need resetting).
  4. Comment the known platform ceiling: `speechSynthesis.pause()` is unreliable on some
     mobile browsers (may behave as stop) — acceptable for the desktop/tablet pilot;
     no workaround attempted.
- **Files:** `src/mentar/web/static/tts.js` only (plus, if the icon needs it, a one-line
  CSS tweak in `style.css`).
- **Accept:** JS isn't covered by pytest — gate = ruff/pytest untouched-green plus this
  **manual checklist for the maintainer's next hands-on look** (record the outcome in
  UI_REQUIREMENTS.md §9): (a) click 🔊 → reads stem + options once (no duplication — needs
  R2.1 first), icon becomes ⏸; (b) click ⏸ mid-sentence → audio stops, icon ▶️; (c) click
  ▶️ → resumes from where it stopped (NOT from the top); (d) letting it finish → icon back
  to 🔊; (e) submitting an answer mid-read → audio stops, new question's button is 🔊.

## R2.3 — answer-mode registry: one configurable place mapping answer types → input widgets  `[G]` ✅ DONE 2026-07-11 (commit e043dc4)

- **Why (maintainer ask):** "better to have config for different modes for answering
  things." Today the widget choice is hardcoded as an if/elif chain in `_turn.html`
  (choices → radios; `fraction` → num/den boxes; else text) and the server-side
  answer-composition rule (`answer_num`/`answer_den` → `"n/d"`) is inlined in `/answer`.
  Adding a new answering mode (mixed numbers `1 1/2`, a future decimal widget, a typed
  letter fallback…) currently means touching template AND route in lockstep. One registry
  = one place to add/adjust a mode.
- **Design:** a single owned registry module — code-level config, NOT a YAML file (there's
  no per-deployment reason to vary widgets at runtime; a dict in one module is the
  configuration surface, reviewable and testable). Each answer mode owns BOTH halves of
  the contract: how the input renders, and how the posted form composes back into the
  single answer string the verifier already accepts. The verifier grammar itself is
  UNTOUCHED — modes only shape input/display.
- **Spec:**
  1. New `src/mentar/web/answer_modes.py`:
     ```python
     @dataclass(frozen=True)
     class AnswerMode:
         widget: str                 # template branch key: "radio" | "fraction" | "number" | "text"
         show_format_hint: bool      # whether question_display's "(answer like …)" hint is shown on the web
         compose: Callable[[Mapping], str]   # request.form -> the single answer string for ctrl.step()

     def _compose_default(form): return form.get("answer", "").strip()
     def _compose_fraction(form):
         answer = _compose_default(form)
         if answer: return answer
         num, den = form.get("answer_num", "").strip(), form.get("answer_den", "").strip()
         return f"{num}/{den}" if num and den else ""

     ANSWER_MODES: dict[str, AnswerMode] = {
         "mc4":      AnswerMode("radio",    show_format_hint=False, compose=_compose_default),
         "fraction": AnswerMode("fraction", show_format_hint=True,  compose=_compose_fraction),
         "int":      AnswerMode("number",   show_format_hint=True,  compose=_compose_default),
         "free_text": AnswerMode("text",    show_format_hint=True,  compose=_compose_default),
     }
     DEFAULT_MODE = ANSWER_MODES["free_text"]
     def mode_for(answer_type): return ANSWER_MODES.get(answer_type or "", DEFAULT_MODE)
     ```
     ("number" = the plain text input but `type="number" inputmode="numeric"` — a nicer
     mobile keyboard for int answers; behaviour otherwise identical.)
  2. `src/mentar/web/app.py` — `/answer` replaces its inline fraction-compose block with
     `answer_text = mode_for(ctrl.current_answer_type).compose(request.form)`;
     `_turn_context` adds `"mode": mode_for(ctrl.current_answer_type)` and uses
     `mode.show_format_hint` to decide stem-vs-full-display for mc4 (folds into R2.1's
     branch — after R2.1, "show the stem" = `not mode.show_format_hint and choices`).
  3. `src/mentar/web/templates/_turn.html` — switch on `mode.widget` instead of the
     current `choices`/`answer_type == "fraction"` conditions (radio branch still guards
     on `choices` being present — an mc4 item without structured choices falls back to the
     text input, same as today).
  4. Adding a future mode (e.g. mixed number) = one `AnswerMode` entry + one template
     branch + its compose function — document this in the module docstring as the
     extension recipe.
- **Files:** `src/mentar/web/answer_modes.py` (new), `src/mentar/web/app.py`,
  `src/mentar/web/templates/_turn.html`, `tests/web/test_app_smoke.py` (+ a small pure
  test file `tests/web/test_answer_modes.py`).
- **Accept (hand-write tests):** pure-registry tests — `mode_for("mc4").widget == "radio"`,
  unknown/None answer_type falls back to text, `_compose_fraction` composes "3/4" and
  prefers a direct `answer` field when both present; existing web tests (radios render,
  fraction composes server-side, letter answers score) still pass unchanged through the
  registry path; int questions now render `type="number"`; full suite + ruff green.

## R2.4 — concept-map node labels truncate mid-word ("Equivalent fra")  `[G]` ✅ DONE 2026-07-11 (commit 83b9b1c)

- **Why (maintainer finding, /progress):** node labels on the concept-graph SVG are
  hard-cut at 14 characters with no ellipsis (`progress.html:15` —
  `{{ n.label | truncate(14, True, "") }}`), so the longer AU labels render as
  "Place value to" and "Equivalent fra". SVG `<text>` does not wrap on its own.
- **Design:** word-wrap the label into multiple lines in `_compute_graph_layout()`
  (pure Python, same testable-layout pattern as the rest of that function) and render one
  `<tspan>` per line. Never cut mid-word; the full label stays available as the hover
  `<title>` tooltip (already rendered).
- **Spec:**
  1. `src/mentar/web/app.py` — new module-level pure helper
     `_wrap_label(label: str, max_chars: int = 16, max_lines: int = 3) -> list[str]`:
     greedy word-wrap (split on spaces; a word longer than max_chars gets its own line,
     kept WHOLE — never sliced); if words remain after max_lines, drop them and append
     "…" to the last line. In `_compute_graph_layout`, each node dict gains
     `"label_lines": _wrap_label(node_label)` (keep `"label"` unchanged — the tooltip
     uses it). Bump the per-level height constant from 22 to 26 (`"height":
     max(n_levels * 26, 26)`) so up-to-3-line labels don't collide with the next row's
     circles.
  2. `src/mentar/web/templates/progress.html` — replace the single truncated `<text>`
     with:
     ```html
     <text x="{{ n.x }}" y="{{ n.y + 8 }}" text-anchor="middle" class="graph-node-label">
       {% for line in n.label_lines %}<tspan x="{{ n.x }}" {% if not loop.first %}dy="4"{% endif %}>{{ line }}</tspan>{% endfor %}
     </text>
     ```
     (first line sits at the existing y+8; subsequent lines step down 4 units — the label
     font is 3.1px in a 100-unit viewBox, so 4 units ≈ 1.3 line-height.)
- **Files:** `src/mentar/web/app.py`, `src/mentar/web/templates/progress.html`,
  `tests/web/test_progress.py`.
- **Accept (hand-write tests):** `_wrap_label("Equivalent fractions")` ==
  `["Equivalent", "fractions"]` (no mid-word cut); `_wrap_label` of a long AU label
  ("Division facts from the times tables") stays ≤3 lines with "…" only when words were
  dropped; a short label stays one line; live `/progress` for `au_year4_maths` contains
  the complete word "fractions" inside a `<tspan>` and does NOT contain the string
  "Equivalent fra<" (the old cut); node `"label"` (tooltip) still carries the full text;
  full suite + ruff green.

**R2 batch ✅ ALL FOUR DONE 2026-07-11** (R2.1 e264652, R2.3 e043dc4, R2.2 d85788e,
R2.4 83b9b1c). R2.2's pause/resume behaviour still needs the maintainer's hands-on audio
check (not verifiable in-sandbox). **R3 (Year > Subject IA) remains plan-only** below —
was explicitly scoped "plan but don't execute"; needs a fresh go-ahead before building.

---

# R3 — Year > Subject information architecture (maintainer ask, 2026-07-10) ✅ ALL DONE 2026-07-11 (R3.1 90f1fc1, R3.2 10f3fd9)

Maintainer direction: the picker and the progress page should read **Year → Subject →
parts of the subject** (concept nodes), and the year/subject catalog should be *derived*,
not hand-registered. Design decision (recorded here so gemma doesn't relitigate it): the
catalog is derived **server-side at startup by scanning template front matter** — the
template files are the source of truth (`country`/`year_level`/`subject` are already in
every front matter), it works with JS disabled, and it keeps the offline/no-SPA posture
(U-80/U-81). No client-side fetch "script"; the front end renders a grouped structure the
server already computed. Generators are code, so templates reference their item source BY
NAME (`item_source:` front-matter key → a named registry in engine code) — adding a new
year/template becomes: drop a `.md` file in, reference an existing generator set (or add
one to the registry).

**Also fixes a real defect:** `/progress`'s star-card list currently pulls ALL of a
learner's `skill_state` rows regardless of subject — with the AU templates added, pilot
fractions/science and AU Year 3/4 nodes mix into one undifferentiated list.

**Execute in order R3.1 → R3.2** (R3.2 renders what R3.1 discovers). Both `[G]`.

## R3.1 — template catalog auto-discovery + named item-source registry  `[G]`

- **Spec:**
  1. `src/mentar/engine/curriculum.py` — new `load_template_meta(path) -> dict` returning
     `{"template_id", "country", "year_level", "subject", "label", "icon",
     "description", "item_source"}` from the front matter (reuse the existing
     split-on-`\n---\n` + `yaml.safe_load` pattern of `load_template_subject`; missing
     keys → None). New optional front-matter keys `label:`, `icon:`, `description:`,
     `item_source:` — add them to all 5 existing templates (values = exactly what the
     `SUBJECTS` dict hardcodes today; `item_source` names: `pilot_fractions`,
     `arithmetic`, `science`, `au_year3`, `au_year4`).
  2. New `src/mentar/engine/item_sources.py` — `ITEM_SOURCE_REGISTRY: dict[str, dict]`
     mapping those names → `{"generators": <registry dict>, "itembank": <Path or None>}`
     (pilot_fractions carries the bank path; the module docstring documents "adding a new
     template" = drop the .md in + reference a registered name).
  3. `src/mentar/web/app.py` — `SUBJECTS` is BUILT by scanning
     `curriculum/templates/**/*.md` (skip `_template.md`/underscore-prefixed non-pilot
     scaffolding; keep the `_pilot/` dir included) via `load_template_meta` +
     `ITEM_SOURCE_REGISTRY[meta["item_source"]]`. Subject key = `template_id` with
     dashes→underscores (KEEP the current keys stable for existing session cookies:
     verify the 5 derived keys equal today's literals — if any differs, add an explicit
     `subject_key:` front-matter override to that template rather than breaking
     sessions). A template naming an unregistered `item_source` → startup `RuntimeError`
     naming template + name (same fail-loud pattern as A16 validation, which stays).
  4. Group metadata for R3.2: `SUBJECT_GROUPS: list[(group_label, [subject_keys])]`
     computed from the scan — group by `year_level` (sorted: real years ascending, then
     `"pilot"` last as "Try-out topics"); group label = `f"{year_level} ({country})"`
     when country is set, else the year_level/pilot label.
- **Files:** `engine/curriculum.py`, `engine/item_sources.py` (new), `web/app.py`, all 5
  templates' front matter, `tests/engine/` (new `test_template_catalog.py`),
  `tests/web/test_app_smoke.py`.
- **Accept (hand-write tests):** the scan discovers all 5 templates with the same keys /
  labels / generators the hardcoded dict has today (assert equality against a literal
  snapshot); unregistered `item_source` fails loudly at startup naming the template; all
  existing web tests pass unchanged (keys stable); full suite + ruff green.

## R3.2 — picker + progress grouped Year → Subject → parts  `[G]`

- **Spec:**
  1. `subjects.html` — render `SUBJECT_GROUPS` as year sections (an `<h3>` per group,
     e.g. "Year 3 (Australia)", "Year 4 (Australia)", "Try-out topics"), each containing its subject
     cards (card contents unchanged).
  2. `/progress` — three levels on one page: (a) a year/subject switcher at the top
     (simple links `?subject=<key>`, current one highlighted; grouped by the same
     `SUBJECT_GROUPS`; default = the session's active subject); (b) the concept-graph map
     for the SELECTED subject (already per-subject today); (c) the star-card list
     **filtered to the selected subject's node ids only** (`skill_id in
     _SUBJECT_CURRICULA[selected]`) — fixes the all-subjects mixing defect. Per-subject
     mastered/total counts shown next to each switcher link (reuse
     `_subjects_progress()`).
  3. No new JS: plain links + server render (htmx not needed here; a full reload on a
     progress-page subject switch is fine).
- **Files:** `web/app.py` (`/progress` route), `web/templates/subjects.html`,
  `web/templates/progress.html`, `tests/web/test_progress.py`.
- **Accept (hand-write tests):** picker HTML contains the year group headings with the AU
  subjects under their years and pilot topics under the try-out group; `/progress?subject=
  au_year3_maths` shows only au3_* skill cards (a learner with fractions AND au3 history
  sees NO fractions rows there — build both histories in the test); the graph renders the
  selected subject's node count; the switcher shows per-subject mastered counts; default
  (no query param) = active session subject; full suite + ruff green.

---

# R4 — bug: homepage lands on a quiz, not the Year > Subject picker  `[G]` ✅ DONE 2026-07-11
**Reported 2026-07-11 (maintainer, live testing). Investigated + root-caused, NOT YET FIXED —
maintainer said "note it, don't do anything" this round.**

- **Root cause:** `session["subject"]` lives in the long-lived browser cookie with no expiry.
  `index()` (`GET /`) skips the picker whenever `session.get("subject")` is any valid key —
  so once a subject has EVER been chosen (a past dev test, a prior day's session, or simply
  after a server restart that wiped the in-memory `_controllers`/`_turn_logs` dicts while the
  cookie survived), every future visit to `/` silently resumes straight into a fresh quiz
  question instead of showing "choose year and subject." Confirmed: `_get_or_create_controller`
  happily creates a brand-new controller instance when `learner_uuid not in _controllers`
  (reusing the durable DB learner row via A6, so mastery is fine) — nothing in that path
  distinguishes "genuinely resuming an in-progress browser tab" from "a stale cookie value with
  no live session behind it."
- **Why the obvious fix (always show the picker on `/`) is NOT safe as a one-liner:** `/answer`'s
  non-htmx (JS-disabled) fallback path does `redirect(url_for("index"))` after EVERY answer
  submission to redisplay the next question — `/` currently does double duty as both "the
  homepage" and "the mid-quiz redisplay target." Blindly making `/` always show the picker would
  break the JS-disabled answer loop (every submitted answer would bounce back to the picker
  instead of the next question).
- **Correct fix — separate the two roles into two routes:**
  1. New `GET /learn` — everything `index()` currently does AFTER the "subject chosen" check
     (get-or-create controller, escalation-freeze check, first-turn step, render
     `learner.html`) moves here unchanged.
  2. `index()` (`GET /`) — becomes ONLY the picker render (still creates `learner_uuid` if
     missing, for `_subjects_progress()`), with NO subject/controller logic at all. Always the
     picker, unconditionally.
  3. `/choose` POST — redirect target becomes `url_for("learn")` instead of `url_for("index")`.
  4. `/answer`'s non-htmx advancing-case redirect → `url_for("learn")` (not `index`) — keeps the
     JS-disabled answer loop working exactly as today, just pointed at the renamed route.
  5. `/parent/ack`'s post-resume redirect → `url_for("learn")` (resuming a frozen session should
     land back on the quiz, not the picker).
  6. Template links: `done.html`'s "Start again" and `progress.html`/`parent.html`'s "Back to
     lesson" currently point at `/` — repoint to `/learn` (going back to the ACTUAL lesson, not
     the topic picker). `_base.html`'s brand-logo link and `parent.html`'s header brand link stay
     pointed at `/` deliberately — clicking the Mentar logo taking you to "choose what to learn"
     is normal, expected home-link behaviour, not the bug.
  7. `/frozen`'s own fallback redirect (`ctrl is None or not frozen → redirect(index)`) can stay
     pointed at `/` — an edge case (bad/missing state), picker is a safe universal fallback there.
- **Files:** `web/app.py` (new `/learn` route, `index()` simplified, 4 redirect-target updates),
  `web/templates/done.html`, `web/templates/progress.html`, `web/templates/parent.html`.
  `tests/web/test_app_smoke.py`, `tests/web/test_progress.py` (any test currently asserting quiz
  content via `GET /` needs to move to `GET /learn`).
- **Accept (hand-write tests):** the actual regression test — `GET /` with `session["subject"]`
  ALREADY set to a valid key (simulating the stale-cookie/restart scenario) still renders the
  picker, never a question; `GET /learn` with a subject chosen renders the quiz (existing
  behaviour, just relocated); `/choose` POST → 302 to `/learn`; a full no-JS answer loop
  (`POST /answer` with no `HX-Request` header) still redirects through `/learn`, never bounces to
  the picker mid-quiz; `done.html`/`progress.html`/`parent.html` "back to lesson" links resolve
  to `/learn`; **clicking the brand icon (`_base.html`'s `<a href="/" class="brand">`) from ANY
  screen, including mid-quiz, lands on the picker — this needs no separate change (the brand
  link already points at `/`, which R4 makes picker-only), just an explicit test proving it**
  (maintainer follow-up, 2026-07-11: "clicking mentar icon on top may need to take us to the
  home page" — confirmed this is the same bug, not a second one); full suite + ruff green.

---

# R5 — Settings page: voice picker + relocate the theme toggle  `[G]` ✅ DONE 2026-07-11 — needs maintainer hands-on audio check (a)-(d) below
**Maintainer ask, 2026-07-11.** New `/settings` page. Two decisions clarified via
AskUserQuestion: (1) voice picker = the raw `speechSynthesis.getVoices()` list, not a
simplified/grouped one; (2) Settings also becomes the new home for the existing dark/light
toggle (moved OUT of the header, not duplicated). A third ask ("download new curriculum or
subjects") was clarified as **already satisfied by R3.1's auto-discovery** — dropping a new
template file into `curriculum/templates/` already makes it appear automatically, no download
mechanism needed; NOT in scope here (a real network-fetch feature would be a genuine departure
from the app's offline-only design — flagged, not built, not asked for after clarification).

- **Design:**
  - `GET /settings` — plain server-rendered page (no htmx; a full reload on save is fine, same
    posture as the R3.2 progress switcher). Reachable via a ⚙️ link in `_base.html`'s shared
    header (replaces the standalone `.theme-toggle` button there — the toggle itself moves
    into this page, not duplicated) + a "⚙️ Settings" link added to `learner.html`'s and
    `progress.html`'s existing footer-nav rows. Deliberately NOT added to `frozen.html` (U-60
    zero-chrome invariant, unchanged) or `parent.html`'s minimal header (stays as-is, matching
    its existing "more serious tone" design call from the R1 build).
  - Voice list is inherently CLIENT-SIDE ONLY (`speechSynthesis.getVoices()` can't be queried
    server-side) — the page renders an empty `<select id="voice-select">` server-side; new
    owned `static/settings.js` populates it in JS. Handle the async voice-list-population
    quirk some browsers have: call `getVoices()` immediately AND re-populate on the
    `speechSynthesis.onvoiceschanged` event (covers both eager and lazy browsers).
  - Persistence: localStorage, same pattern as `theme.js` — a new key (e.g.
    `mentar-tts-voice`) storing the chosen voice's `voiceURI` (spec-guaranteed unique per
    browser, more robust than `.name`). No server round-trip; this is a pure client
    preference, same shape as the theme choice.
  - `static/tts.js`'s speak logic (in the `STATE_IDLE` branch, where the utterance is built)
    reads the stored `voiceURI`, looks it up via
    `speechSynthesis.getVoices().find(v => v.voiceURI === stored)`, and sets
    `utterance.voice = match` when found. **Graceful degradation, not an error:** if the
    stored voice isn't available on this device/browser (e.g. settings synced from a
    different machine), silently fall back to the browser's default voice — same
    never-break posture as the rest of tts.js.
  - Nice-to-have, small: a "🔊 Test this voice" button on the settings page itself, using the
    CURRENTLY-SELECTED-IN-THE-DROPDOWN voice (not yet saved) to speak a short fixed sample
    sentence — lets a parent preview before committing. Same `SpeechSynthesisUtterance`
    mechanics as `tts.js`, just triggered from `settings.js` instead.
  - Theme toggle: the existing `.theme-toggle` button markup + `theme.js`'s wiring logic move
    from `_base.html`'s header into `settings.html`'s content — `theme.js` itself needs
    little to no change (it already queries `.theme-toggle` wherever it lives in the DOM, and
    the top-level `data-theme` application is unconditional, not gated on the button
    existing).
- **Files:** `web/app.py` (new `/settings` route — no controller/session logic, purely
  static), `web/templates/settings.html` (new), `web/templates/_base.html` (header: swap
  `.theme-toggle` for the `/settings` link), `web/templates/learner.html` +
  `web/templates/progress.html` (footer-nav: add the Settings link),
  `web/static/settings.js` (new), `web/static/tts.js` (read the stored voice),
  `web/static/style.css` (small: a `.settings-link` style, reusing `.theme-toggle`'s look).
- **Accept:** `GET /settings` returns 200 and contains a `<select id="voice-select">` +
  the relocated theme-toggle button; `_base.html`'s header no longer contains
  `.theme-toggle` (moved, not duplicated) on any page using the default header block;
  `frozen.html`/`parent.html` still show no settings link (unchanged invariant/design);
  pytest covers the server-rendered parts (route 200, expected markup present, footer
  links present on learner/progress). JS behaviour (voice enumeration, selection,
  persistence, fallback-when-voice-missing, the test-voice button) isn't pytest-testable —
  syntax-check via `node --check` plus a **manual hands-on checklist for the maintainer**
  (same ceiling as R2.2): (a) open Settings, confirm a non-empty voice list appears; (b)
  pick a non-default voice, click "Test this voice", confirm it plays in that voice; (c)
  save, return to a quiz, click 🔊 — confirm it now reads in the chosen voice; (d) the
  dark/light toggle still works exactly as before, now from Settings instead of the header.

---

# R6 — bugs: concept-graph bottom row clipped + inconsistent skill display names
**Reported 2026-07-11 (maintainer, live testing on AU Year 3). Both root-caused, NEITHER
FIXED — maintainer said "note it for now" for both; #2 explicitly wants a ground-up pass,
not a quick patch.**

## R6.1 — concept-graph bottom row is clipped off  `[G]` ✅ DONE 2026-07-11 (commit ba48ae2) — (small, isolated, tight enough to
spec now even though #2 needs more design first)

- **Root cause, confirmed by direct reproduction against the real AU Year 3 template:**
  `_compute_graph_layout()`'s y-coordinate formula and its returned SVG viewBox height use
  TWO DIFFERENT, uncoupled scales. `row_height = 100 / n_levels` positions nodes on a fixed
  **0–100** scale (matching the x-axis), but the function separately returns
  `"height": max(n_levels * 26, 26)` for the viewBox — a completely different scale, never
  reconciled. R2.4 changed the per-level height constant from 22 to 26 (to fit wrapped
  labels) but never updated the y-position formula to match. Reproduced directly: for AU
  Year 3 (3 levels), viewBox height = 78, but the bottom row's nodes sit at y=83.3 (circle
  radius extends to ~87.3, wrapped labels extend further still) — outside the visible
  viewBox, hence clipped. Any curriculum with ≥3 levels hits this; the pilot's 8-node
  fractions graph (also ≥3 levels) likely has the same bug, just less noticeable if no one
  scrolled to check.
- **Fix direction:** compute `row_height` as a fraction of the ACTUAL height value, not a
  hardcoded 100 — i.e. `height = max(n_levels * 26, 26)` first, THEN
  `row_height = height / n_levels`, and use `height` (not `100`) as the y-axis reference
  throughout. x stays on 0–100 (unaffected, still correct). Also worth adding a small
  bottom margin/padding to `height` beyond the last row's radius+label extent, so labels on
  the LAST row never sit flush against the viewBox edge either.
- **Files:** `web/app.py` (`_compute_graph_layout`), `tests/web/test_progress.py`.
- **Accept:** for every existing template (fractions/arithmetic/science/au_year3/au_year4),
  the bottom-most node's y + circle radius + full wrapped-label extent stays ≤ the returned
  `height`; a direct regression test reproducing this exact AU Year 3 case (previously
  y=83.3 > height=78) now passes; full suite + ruff green.

## R6.2 — skill display names: four inconsistent strategies for the same data, needs a
ground-up unification, NOT a quick patch (per maintainer explicitly) ✅ DONE 2026-07-11 —
resolved via `docs/design/MULTI_COUNTRY.md` §5 (the "ground up" design pass this needed),
built same wave

- **The reported symptom** ("Au3 Place Value ??? ... need a better way to identify this")
  is a visible symptom of a real structural gap: **skill_id (the machine-safe, namespaced
  identifier) and its human display name are conflated everywhere except one place.**
  Confirmed by grep — FOUR different rendering strategies currently coexist for the exact
  same underlying skill_id:
  1. `progress.html`'s concept-graph SVG — **the only correct one**: joins back to
     `curriculum[node_id]["concept"]`, the template-authored label (e.g. "Place value to
     999", no machine prefix, properly cased).
  2. `progress.html`'s star-card list + `learner.html`'s per-skill mastery bar — naive
     `skill_id | replace("_"," ") | title`, which is WHERE "Au3 Place Value" comes from:
     the `au3_` namespace prefix (added in R3.1 specifically so skill_state rows can't
     collide across curricula) leaks straight into the display, and gets wrongly
     capitalized as if it were a word.
  3. `parent.html`'s mastery table + answers table — **no transform at all**, shows the
     raw `skill_id` verbatim (e.g. literally "au3_place_value") to a parent — arguably the
     worst of the four.
  4. `done.html`'s session recap — same naive `replace + title` as #2.
  Root data already exists and is already clean: `engine/curriculum.py`'s `load_curriculum`
  reads each node's YAML `label:` field and stores it — but under the dict key `"concept"`,
  a naming mismatch with the source field worth fixing at the same time ("structure and IDs
  needs to be defined clearly" — the maintainer's own words apply to this internal
  inconsistency too, not just the rendered output).
- **Why this needs a proper pass, not a patch (per maintainer):** simply swapping the 3
  wrong sites to also do `curriculum[skill_id]["concept"]` would fix today's symptom, but
  doesn't address the underlying issue: THREE different templates each independently
  deciding how to turn an id into a name is exactly the kind of ad-hoc-per-template display
  logic this whole UI rebuild has been steadily replacing with structural, single-source
  answers (same principle as R1's TurnResult.message/.question split and R2.1's mc4
  stem/choices separation — display data should be computed ONCE, correctly, and every
  template just renders it, never re-derives it).
- **Design questions a future pass should answer before speccing:** (a) rename
  `curriculum[id]["concept"]` → something clearer (`"label"` or `"display_name"`, matching
  the YAML source field name) — is this internal-only or does it also need a schema/
  migration note in `docs/PHASE0.md`'s W3.1 template schema? (b) where should the
  id→display-name lookup live — a single helper function all 4 templates' routes call
  before rendering, or should routes attach a `display_name` field directly onto every
  skill/answer dict they pass to templates (so templates never do id-logic at all)? (c)
  does this same unification need to also cover node ids shown elsewhere not grepped here
  (e.g. any future audit surfaces, CLI output)? (d) is there a broader "how do we name
  things" convention worth writing down once (a short design note) so future curriculum
  authors and future template additions don't reintroduce the same drift?
- **Not spec'd as a tactical `[G]` task** — deliberately, per the maintainer's own framing.
  R6.1 (the graph clipping) can be executed independently and immediately since it's small
  and fully isolated; R6.2 needs the above design questions answered first.

---

# R7 — evergreen Try-out practice sampler + Settings LLM status check  `[G]` ✅ DONE 2026-07-11

**Maintainer ask, 2026-07-11.** Two unrelated asks bundled into one build wave: (1) a
permanent, country-agnostic "practice makes perfect" sampler under the picker's Try-out
group ("times tables up to 12... practically like a demo for this product"); (2) the
Settings page should show whether the local LLM is actually reachable ("it's guess work to
see if it's running or not via the interface"), discovered while root-causing a reported
voice-picker bug.

## R7.1 — practice sampler pack

- **New directory `curriculum/templates/practice/`** (not `_pilot/` — maintainer's call,
  "makes more sense for now and long term"; not `_practice/` either — the leading
  underscore is reserved for `_pilot`'s specific no-prefix exemption, any other directory
  already auto-prefixes via `derive_subject_key()`, so a plain `practice/` name gives the
  cleanest auto-derived key: `practice_maths`/`practice_english`).
- **Maths practice** (`curriculum/templates/practice/maths.md`, 3 flat nodes, `int`
  answers): times tables 1–12, skip counting/number patterns, doubles & halves.
- **English practice** (`curriculum/templates/practice/english.md`, 4 flat nodes, `mc4`
  answers): synonyms & antonyms, rhyming words, odd one out, plural forms.
- **New `engine/practice_items.py`**: generator functions + `MATHS_PRACTICE_GENERATORS`/
  `ENGLISH_PRACTICE_GENERATORS` registries, wired into `engine/item_sources.py` as
  `maths_practice`/`english_practice`. The 4 English generators reuse one relocated shared
  helper (`itemgen.mc_which_is`, moved from `science_items.py` where it was private-named
  `_mc_which_is` — same disjoint-fact-table-with-distractors shape science already used)
  rather than four bespoke generators.
- **Node ids are manually prefixed `practice_`** (e.g. `practice_times_tables`) — skill_id
  is NOT auto-namespaced by directory the way the subject_key is; this matches the AU
  templates' own `au3_`/`au4_` convention and avoids ever colliding with a future
  country's node id. Guarded by a new collision test across every shipped template.
- **No licensing work needed** — 100% Mentar-authored generic facts (times tables, common
  vocabulary), unlike country-curriculum content.
- **Content-quality review** (Sonnet-led, not gemma): all 5 curated fact tables
  (synonyms/antonyms/rhymes/odd-one-out/plurals) hand-verified pairwise-disjoint (no word
  appears under two different labels, which would make a distractor accidentally correct)
  — enforced going forward by `test_english_fact_tables_are_pairwise_disjoint`.
- **Accept:** both subjects appear under "Try-out topics" in the picker (grouping is by
  `year_level: pilot`, not by directory name); every generator self-validates against the
  deterministic verifier across 200+ seeds; no skill_id collides with any other shipped
  template; full suite + ruff green.

## R7.2 — Settings: local LLM connectivity check

- **New `GET /settings/llm-status`** route: a SHORT 5-second-timeout `models.list()` call
  against `LLM_BASE_URL`/`LLM_CRED` — deliberately a separate, much shorter timeout than
  the app's own 120s generation call, so a genuinely unreachable backend can't hang the
  settings page. Returns `{ok, model, base_url, latency_ms, error}` as JSON.
- **`settings.js`** auto-checks on page load + a "🔄 Check again" button; renders
  "🟢 Connected (model, Nms)" or "🔴 Not reachable at <url> (<error>)".
- **Voice-picker bug, root-caused while building this:** `settings.js`'s test-voice button
  and `tts.js`'s real read-aloud logic both set `utterance.voice` but never
  `utterance.lang` — a well-documented Web Speech API gotcha where several browsers
  silently fall back to the default voice when `.lang` doesn't match the assigned
  `.voice`. Fixed in both files (2 lines each). Also added a brief "Saved ✓" flash on the
  voice `<select>`'s change event — not an actual Save button (the auto-save-on-change was
  already correct), just visible confirmation that a no-button choice actually persisted.
- **Accept:** endpoint tested with a mocked reachable + unreachable backend (no real
  network in tests); JS syntax-checked with `node --check`; the `.lang` fix and "Saved ✓"
  flash are JS-only and not pytest-testable — same ceiling as R2.2/R5's voice features,
  flagged for a maintainer hands-on check alongside the existing R5 audio checklist.

---

# R8 — content-download MVP + India (general Class 3 maths) pack  `[G]` ✅ DONE 2026-07-12 — ⚠️ delivery model SUPERSEDED by R10 (see below): shipped packs are now in-repo toggles, not downloads; the fetch machinery here is kept dormant for future remote packs only

**Maintainer ask, 2026-07-11.** In-app curriculum management from Settings: see what's
installed, download what isn't, delete what you no longer want — the in-app counterpart to
today's developer-only "drop a `.md` file in `curriculum/templates/`" mechanism. Confirmed
via AskUserQuestion: git-pull-based fetch (repo is currently private; the design targets the
repo's future PUBLIC url shape so nothing needs rework at launch); mechanism + India content
built together; delete/uninstall built now, preserve-mastery-by-default only (the harder
"fully erase" escape hatch explicitly deferred, see below).

## R8.0 — licence gate: NCERT (India) flagged NO-DERIVATIVES, scope changed to a generic pack

Attempted the same live-verification discipline as ACARA's clearance; `epathshala.nic.in`
was unreachable both from the sandbox and by the maintainer. Two independently-converging
web searches surfaced identical language: *"No person is permitted to adapt, translate,
alter, summarize, or make any derivation of NCERT E-content... without the specific,
written permission of NCERT."* Treated as confirmed per this project's own no-shortcut
rule (`docs/CONTENT_LICENSES.md` §2b, v0.4) — materially stricter than ACARA's CC BY 4.0,
and the restriction is NOT scoped to commercial use ("No person"), so an individual family's
personal use doesn't change the analysis; Mentar shipping the template is a distributed
feature, not a one-off personal act, either way.

**Decision: no `IN_NCERT`/`IN_CBSE` pack this wave.** Instead, `IN_GENERIC` — universally-
taught Class 3 maths topics (place value/addition/subtraction, times tables, basic
fractions), 100% Mentar-authored via **existing, already-shipped generic generators**
(zero new generator logic): `itemgen.py`'s `_gen_addition`/`_gen_subtraction`/
`_gen_unit_fractions` + `practice_items.py`'s `_gen_times_tables`, re-registered under new
`in_generic_*` node ids in a new small `engine/in_generic_items.py`. No NCERT/CBSE branding,
codes, or claimed curriculum alignment anywhere — label reads "Maths — Class 3 🇮🇳
(general)", description says plainly this is general content, not an official mapping.
Re-verify `epathshala.nic.in`'s licence directly before ever attempting a real
`IN_NCERT`/`IN_CBSE` pack.

## R8.1 — manifest + fetch mechanism

- **Two physically separate directories, not just a manifest-level distinction:**
  `curriculum/templates/` is what `web/app.py`'s auto-discovery scans (`glob("**/*.md")`)
  — anything here ships with every checkout and needs no download (AU, `practice/`).
  Downloadable packs live SOURCE-side in a sibling directory the scanner never touches,
  **`curriculum/downloadable_packs/<DIR>/`** — present in the git tree (so the raw-URL
  fetch below can find real content) but invisible to the picker until explicitly
  installed, which COPIES the files into `curriculum/templates/<DIR>/`. (Putting a
  downloadable pack directly under `templates/` would defeat the whole feature — every
  fresh `git clone` would auto-discover it immediately, no download needed.)
- **`curriculum/packs.json`** (new, lives in the repo, auto-discovered like everything
  else): one entry per downloadable pack — `{id, dir, label, description, licence,
  files: [{name, sha256}]}`, `files` naming paths under `downloadable_packs/<dir>/`.
  `IN_GENERIC` is the first (and only) entry this wave.
- **Fetch is HTTPS against ONE pinned, hardcoded base URL**
  (`https://raw.githubusercontent.com/avps82/mentar/main/`) — never a user-supplied URL,
  never configurable from the UI. This is git-pull-shaped (same trust boundary you already
  have via `origin`) but expressed as plain HTTPS raw-file fetches so it needs no local git
  binary/credentials wrangling from Flask, and works unchanged the moment the repo goes
  public (nothing to rework at launch — this was the point of designing against the
  *future* public shape now).
- **Security, same posture as R7.2's short-timeout discipline:** short per-file timeout;
  every downloaded file's sha256 verified against the manifest BEFORE it's written to disk
  (mismatch = reject, nothing written); content is markdown/YAML template data, parsed by
  the EXISTING `yaml.safe_load` path — never executed as code; explicit user-initiated
  action only (a button click), never automatic/background, matching the app's otherwise
  fully-offline (U-80) design — this is the one deliberate, narrowly-scoped exception.
- **New routes:** `GET /settings/curriculum-packs` (fetches `packs.json`, diffs against
  what's locally present under `curriculum/templates/`, returns available vs. installed);
  `POST /settings/curriculum-packs/<pack_id>/install` (fetch + verify + write); `POST
  /settings/curriculum-packs/<pack_id>/uninstall` (remove the pack's directory).
- **Known MVP limitation, flagged not silently absorbed:** `SUBJECTS`/`_SUBJECT_CURRICULA`
  are built ONCE at `web/app.py` import time (R3.1's auto-discovery scans at startup, not
  per-request) — a freshly-downloaded pack won't appear in the picker, and an uninstalled
  one won't disappear, until Mentar is restarted. The UI says this explicitly after
  install/uninstall ("Restart Mentar to start this new topic") rather than implying it's
  immediate. Making discovery fully dynamic (re-scan per request) is a real but separate
  change — not needed for this MVP and not built here.
- **Uninstall semantics:** deletes the pack's `curriculum/templates/<DIR>/` (so it stops
  being discovered) but the child's `skill_state` DB rows for that pack's node ids are
  UNTOUCHED (they're a separate table, keyed by skill_id, never touched by a file delete —
  this is the free, automatic default, not code that needs writing). **Deferred, not built
  this wave:** a separate, harder-to-reach "also erase this child's mastery history for
  this pack" action — flagged in the design doc §4 as a distinct escape hatch; scope-cut
  for MVP since preserve-by-default (the safety-relevant default) is what actually matters
  here, and a destructive erase action deserves its own careful confirm-flow design later.
- **Settings UI:** a new "Curricula" section — installed packs listed with an "Uninstall"
  button; available (not-yet-installed) packs listed with their licence + a "Download"
  button; both actions show the restart note above.

## R8.2 — IN_GENERIC Class 3 maths content

- `curriculum/templates/IN_GENERIC/class3_maths.md` — 4 flat nodes (no prereqs):
  `in_generic_addition`, `in_generic_subtraction`, `in_generic_times_tables`,
  `in_generic_unit_fractions`. `country: IN`, `curriculum_standard: null` (deliberately —
  no claimed board alignment).
- `engine/in_generic_items.py` (new, ~15 lines): imports the 4 existing generator
  functions named above from `itemgen.py`/`practice_items.py`, re-registers them under the
  `in_generic_*` node ids in one `IN_GENERIC_MATHS_GENERATORS` dict — no new generator
  logic written, matching this pack's "borrow proven, non-controversial content" posture.
- `engine/item_sources.py`: new `"in_generic_maths"` registry entry.
- Auto-derived subject key (via existing `derive_subject_key()`, zero code change):
  `in_generic_class3_maths`.

## Accept (both R8.1 and R8.2)

- Manifest/fetch tested with a mocked HTTP layer (no real network in tests, same pattern
  as R7.2's LLM-status mocking) — covers: available-vs-installed diffing, checksum
  verification (both match and MISMATCH-rejects-the-write), install writes files,
  uninstall removes the directory, mastery rows survive an uninstall.
- `IN_GENERIC`'s 4 generators self-validate against the deterministic verifier (reused
  functions, but re-verify under the new node ids/registry entry regardless).
- Template passes `validate_or_raise`; no skill_id collision with any other shipped
  template (existing cross-template guard test extends automatically).
- Full suite + ruff green. JS/network-fetch UI pieces flagged for a maintainer hands-on
  check (can't exercise a real download against the still-private repo from here) —
  same ceiling as R5/R7.2's other unverifiable-in-sandbox features.

---

# R9 — first-run setup gate + live backend switch (no restart)  `[G]` ✅ DONE 2026-07-13

**Maintainer ask, 2026-07-13.** Two related asks that turned into one piece of work
using the same config-writing/reload machinery: (1) let Settings switch between a
local model and a remote API backend, not just show status; (2) a fresh install
should route to a setup page FIRST, before the picker, rather than let a family
reach a broken app with no model configured. Confirmed: gate on config MISSING **or**
unreachable (not missing-only); build/test the web-side gate now, the CLI installer's
own API-backend support later, separately.

**The `mentar setup` CLI already writes `config/inference.yaml`** for local models
(auto-selected from a roster) — this wave adds the web-side counterpart, not a
replacement.

## Design

- **`GET/POST /setup`** — a plain page with two forms: "Local model" (base URL,
  model to load) and "Remote API" (base URL, model, optional API key). Reuses
  `write_inference_config()` (already used by `mentar setup`) to write the config —
  no new file-writing logic invented.
- **API key never inlined in the yaml.** If provided, it's written to a gitignored
  `.env` next to the config (`_upsert_dotenv_value`, a small write-side counterpart
  to `backend.py`'s existing `_load_dotenv`), and the yaml gets `${MENTAR_VLLM_API_KEY}`
  — the SAME env-var-reference convention already used everywhere else in this
  codebase. A blank key writes `"no-key"` (matches `_resolve_http`'s own default),
  not "keep whatever was there before" — simplest correct behavior for a form that
  never round-trips a previously-saved secret back to the browser.
- **Gate:** `@app.before_request` redirects every route except `/setup` itself to
  `/setup` when `_setup_is_complete()` is false — false when
  `config/inference.yaml` doesn't exist, OR it exists but the backend fails the
  SAME short-timeout reachability probe `/settings/llm-status` already used
  (`_probe_llm_backend`, extracted so the two can never disagree about "working").
  An in-process llamacpp backend has no HTTP endpoint to probe — its mere presence
  counts as configured. Cached 30s so the common (healthy backend) case doesn't add
  a live network probe to every single page request.
- **Reload, no restart, either from `/setup` or a future Settings toggle:**
  `_reload_inference_config()` re-reads the config and resets every derived cache
  (`_INFERENCE_CFG`, `_GROUNDING_CFG`, `_LLM_STATUS_ENDPOINT`, `_llm_call_cached`).
  This works with zero restart because `_llm_call` (the function every
  `SessionController` holds a reference to, wrapped in its own `_make_safe_llm`) is
  a stable indirection — it reads `_INFERENCE_CFG`/`_llm_call_cached` fresh via
  `global` on every call, never a snapshot captured at controller-construction time.
  An ALREADY-RUNNING session picks up a backend change on its very next turn.
  Proven directly in tests (`test_llm_call_reflects_new_backend_immediately_no_restart`),
  not just asserted.
- **Real bug caught by writing the reload test, not by inspection:** the first
  version of `_reload_inference_config()` called `load_inference_config()` with no
  path argument, which resolves its OWN independently-computed default location —
  happens to match `_INFERENCE_CONFIG_PATH` in production (both compute the same
  `<repo>/config/inference.yaml`), so it looked correct, but silently ignored
  whatever path `_setup_is_complete()`/`write_inference_config()` were actually
  using. Fixed to load explicitly from `_INFERENCE_CONFIG_PATH`.
- **Test-suite impact:** every existing web test now needs the gate bypassed
  (`_SETUP_GATE_BYPASS`, a module flag every test file's `_client()` helper sets) —
  otherwise all ~500 existing web tests would redirect to `/setup` the moment the
  gate is added, since test runs have no real, reachable backend. One test
  (`test_learner_id_survives_server_restart`) does its OWN mid-test
  `importlib.reload()` to simulate a real restart — that resets the bypass flag
  too, needed re-setting there specifically.

## Accept

- New `tests/web/test_setup_gate.py` (11 tests, gate deliberately NOT bypassed):
  redirects on missing config, redirects on unreachable-but-present config, allows
  through when reachable, allows an in-process backend through without probing,
  `/setup` itself is never gated, a successful save writes the right yaml + reloads
  live, an API key never appears in the yaml (only in `.env`), a blank key writes
  `no-key`, an unreachable save shows an error and does NOT redirect (config is
  still written so the parent doesn't have to re-type everything once they fix
  connectivity), missing required fields are rejected before anything is written.
- Full suite (553 tests) + ruff green.

## R9.1 — CLI counterpart + ongoing-switch discoverability (2026-07-13 follow-up)

- **`mentar setup --runtime vllm --base-url ... --model ... [--api-key ...]`** — the
  CLI now supports remote-API setup too, not just local models. No roster/download
  involved (`_setup_remote_api`, a separate branch in `_setup()` before the
  roster-selection logic even runs). Reuses the exact same `write_inference_config()`
  the local path already used, plus a NEWLY SHARED `upsert_dotenv_value()` (relocated
  from `web/app.py`'s private copy into `inference/backend.py` and exported publicly
  — one place that touches a credential file, not two independently-maintained
  copies). `--dry-run` writes NOTHING to disk, including the `.env` — a real bug
  caught while testing this manually: the first version wrote the `.env` file even
  on a dry run, because the API-key write happened before the dry-run check instead
  of after. Fixed; verified with a smoke test that checks the file genuinely isn't
  created.
- **Settings now links to `/setup`.** `/setup`'s own routes were already exempt from
  the gate (reachable any time, not just when something's broken) — but nothing
  linked to it once a family was past first-run, so there was no way to find your
  way back to switch backends without knowing the URL. Added a "⚙️ Change AI model"
  link in Settings' Local AI model section.
- **Accept:** new `tests/cli/test_setup_cmd.py` (5 tests: missing required args,
  dry-run writes nothing, successful write puts the key in `.env` not the yaml, a
  blank key defaults to `no-key`, an unreachable backend still writes the config but
  returns exit code 1) + 2 new `tests/inference/test_backend.py` tests for the
  relocated `upsert_dotenv_value` + 1 new web test proving the Settings link exists
  and `/setup` is genuinely reachable on a voluntary visit. **561 tests pass, ruff
  clean.**

---

# R10 — curriculum packs: in-repo on/off toggles (supersedes R8's download model for shipped packs)  `[G]` ✅ DONE 2026-07-16

**Maintainer critique, 2026-07-13→16.** R8 delivered curriculum packs as an HTTPS
*download*, but the maintainer pointed out that for content **already shipped in the
repo** a download is over-built — "it should be part of the repo where they activate
it or deactivate it." Correct: R8's `IN_GENERIC` pack physically sat in the same
checkout, two folders from where the download copied it. R10 reframes shipped packs
as **local on/off toggles**; R8's fetch machinery is kept dormant for a genuine
future need (content NOT in the repo — community packs, an oversized library).

**Three decisions ratified via AskUserQuestion (2026-07-13):** keep R8's fetch code
dormant (don't delete); toggles apply on the next restart (not live — matches
scan-once-at-startup discovery); *everything* toggleable including the pilot/practice
base (max parental control).

## What changed

- **`IN_GENERIC` moved** `curriculum/downloadable_packs/IN_GENERIC/` →
  `curriculum/templates/IN_GENERIC/`, so it's auto-discovered like AU/practice and
  becomes a toggle. `downloadable_packs/` is removed; `packs.json` ships **empty**
  (a documented dormant manifest reserved for genuine remote packs).
- **Per-install state:** a gitignored `curriculum/pack_state.json`
  (`{"disabled": [subject_key, ...]}`), env-overridable via `MENTAR_PACK_STATE`
  (like `MENTAR_DB_PATH`). Startup discovery skips disabled keys; a corrupt file
  defaults to all-enabled (never breaks startup).
  > **SUPERSEDED 2026-08-14** (maintainer: "default setting is all toggles are
  > disabled for all subjects and grades for each country. Only toggle enabled is
  > the general ones — thereby, user doesn't need to switch off any unwanted
  > ones"). The file is now an ALLOW-list, `{"enabled": [subject_key, ...]}`, and
  > the default with no file is the country-less General packs only. A pack is on
  > iff listed, so a country pack shipped by a later release also defaults to off
  > instead of appearing uninvited. A legacy `{"disabled": [...]}` file is still
  > honoured as written (an existing install keeps its packs) and is rewritten in
  > the new shape on the next toggle. A corrupt file now falls back to the
  > General-only default, not all-enabled.
- **New routes:** `GET /settings/curricula` (every in-repo pack + on/off state,
  including disabled ones so they can be re-enabled) and
  `POST /settings/curricula/<key>/<enable|disable>`. New Settings "Curricula" toggle
  UI; the dormant R8 download list renders nothing when `packs.json` is empty.
- **Turning a curriculum off preserves the child's mastery** (`skill_state` untouched
  — disable only writes the state file), same preserve-by-default posture as R8's
  uninstall. Re-enabling brings progress back.
- **"Everything toggleable" edge:** a family *can* disable every pack. That's made a
  recoverable state, not a dead end — the picker shows "No curricula are turned on →
  go to Settings," and Settings (+ the toggle list) stays reachable to re-enable.

## Accept

- New `tests/web/test_curriculum_toggle.py` (8): list shows all packs enabled by
  default; disable writes state + listing reflects it; enable removes from disabled;
  a disabled pack is genuinely absent from `SUBJECTS` after a restart; unknown-key
  and bad-action rejected; disabling preserves `skill_state`; all-disabled shows the
  friendly picker message with Settings still reachable; a corrupt state file
  defaults to all-enabled. R8's 8 download tests reworked to run against a
  **synthetic** manifest (dormant machinery, no real download-gated pack). Env-var
  isolation added to every web `_client()` so a toggle test can't leak
  `MENTAR_PACK_STATE` into another file. **568 tests pass, ruff clean.**
- **Open, still the maintainer's call (`[[project_r8_download_vs_toggle_question]]`):**
  none — R10 *is* the resolution of that question. The dormant R8 fetch code stays
  only for a real future "content not in this repo" need.

---

# R11 — Micro-learning: interleaving + spaced review + micro-sessions  `[G]` ✅ DONE 2026-07-18

**Maintainer ask, 2026-07-18:** "see if micro-learning can be applied … concepts switched
together." The three pillars of micro-learning map onto three one-point gaps — no curriculum
or template changes, purely a delivery-policy change over content that already exists.

## What changed

- **Interleaving:** `NODE_SELECT` used to pick `sorted(fringe)[0]` — the child drilled ONE
  concept until mastered (blocked practice). New pure policy `engine/fringe.select_next`
  (gemma-drafted, `[G]`): prefers a ready concept ≠ the one just practised; every
  `rng.choice` draws from a `sorted(...)` list so A19 seed-replay still holds.
- **Spaced review:** mastered nodes used to leave the fringe forever, which made the shipped
  forgetting machinery (`STALE_MASTERY_DAYS`, `ProbeClass.FORGETTING_SUSPECT`, probe demote)
  **unreachable**. Every `REVIEW_EVERY_N=4`-th completed item, `select_next` injects a
  mastered-but-stale node for review; `_do_bkt_update` now refreshes the in-session
  staleness clock so a just-reviewed node isn't re-picked all session. A still-mastered
  review node makes `probe_due` fire → probe classifies with `mastery_is_stale=True` →
  forgetting path live, by design, zero new BKT/probe code.
- **Micro-sessions:** new `SessionController(max_items=…)` (default `None` = uncapped);
  `BRANCH_DECISION` ends the session warmly ("That's a great session — see you next time!")
  after that many completed items, checked before the probe rule. Web passes
  `MENTAR_SESSION_ITEMS` (default **10**, `0` disables).

## Accept

- New `tests/engine/test_select_next.py` (7, gemma-drafted): interleave switches away from
  current; sticks when it's the only fringe node; review fires exactly on multiples of
  `REVIEW_EVERY_N` (not at 0/off-cycle); fringe-empty→stale-review fallback; all-done→None;
  same-seed determinism.
- New `tests/dialogue/test_micro_learning.py` (7, hand-written — FSM wiring): alternation
  over two roots; stale-mastered injection at item 4 (and NOT when fresh); BKT stamps the
  staleness clock; `max_items` ends warmly at `SESSION_END_COMPLETE`; no cap by default;
  same-seed node-sequence replay.
- `tests/dialogue/test_probe_help_pressed.py` made node-agnostic (it assumed the old
  alphabetical first-pick; with interleaving the first pick among equal roots is rng-based).
- `SESSION_FSM.md` §3: NODE_SELECT policy note + new `BRANCH_DECISION → SESSION_END_COMPLETE`
  (`max_items_reached`) edge — kept honest by the T3.7 conformance test.

---

# R12 — Settings rework + Explain fixes  `[G]`+hand ✅ DONE 2026-07-18

Source: the 2026-07-18 maintainer feedback row (PHASE0_STATUS backlog). Five parts:

- **R12.1 (confirmed bug):** explanations couldn't be read aloud — 🔊 existed only on the
  question block. `_turn.html` feedback block gained its own tts-btn + `.msg-text` wrapper
  (NOT `feedback-*` — tests split fragments on `<div class="feedback`); `tts.js` reads the
  CLICKED block, tracks `activeBtn`/`activeUtterance` (handler-detach before cancel() so the
  old utterance's async onend can't repaint the new button idle mid-speech). gemma drafted;
  review caught the repaint race + a brittle nextElementSibling.
- **R12.2:** Curricula text buttons → real switch widgets (native checkbox + ~10 CSS lines,
  `.switch`); server-rejected/failed toggles revert the checkbox (never show unapplied state).
- **R12.3:** Settings grouped+reordered with native `<details open>` (tabs were optional):
  Curricula (grouped BY COUNTRY — payload already had `country`; absorbs R14/R15's ~40 packs)
  → AI model → Read-aloud voice → Appearance.
- **R12.4:** all 5 `help_*.md` gained a variety line over new `{{previous_explanation}}`
  (threaded from `ctx.last_explanation`, reset on fresh PRESENT); `help_visual.md` now
  instructs concrete emoji-diagrams (🟩🟩⬜⬜). Prompt hashes recomputed (frontmatter+README).
- **R12.5:** "Explain more": new `HELP_ELABORATE` state (shared `_do_help_explain(elaborate=True)`
  handler — same A14 verified-arithmetic + fallback guards), `help_elaborate.md` unpacks the
  SAME explanation one level deeper; entered from HELP_RECHECK_AWAIT on "more"/💡 button
  (`can_elaborate` property drives the web button); capped ELABORATE_CAP=2 per Help chain.
  SESSION_FSM.md §3 rows added (T3.7-enforced).

**Accept:** new `tests/dialogue/test_elaborate.py` (6) + feedback-tts web test; **589 tests
pass, ruff clean, 3× dialogue/web rerun stable.** A18 honoured: T1.5 adversarial re-run
2026-07-18 — 19/0/1 (review item human-checked benign), 0 hard-fails; recorded in
EVAL_RESULTS.md §3.2. gemma drift caught in review: it silently rewrote two unrelated
comments in settings.js (wrongly) — full-file replacement rejected, targeted section applied.

---

# R-MC — Multi-country ratification: AU→AU_ACARA rename + derive_subject_key rework ✅ DONE 2026-07-19

Wave 2 of the 2026-07-18 release-backlog plan (R12 was wave 1) — done BEFORE R14/R15 author
~40 new templates, so the rename happens once, now, while zero external users exist.

- **`docs/design/MULTI_COUNTRY.md` ratified** (maintainer, 2026-07-19). §2's
  `country_authority` naming convention built; §2b's year-subfolder + `LATEST` pointer
  mechanism stays explicitly UNBUILT (nothing to point at until a second publication year
  exists).
- **`git mv curriculum/templates/AU curriculum/templates/AU_ACARA`.** Audited the 4
  lowercase `au/in/uk/us` dirs found under `curriculum/templates/` — confirmed empty AND
  untracked by git (`git ls-files` returned nothing; no history either) — removed as stray
  local cruft, not a migration.
- **`engine/curriculum.py::derive_subject_key`** reworked: resolves the AUTHORITY directory
  (the one directly under `templates/`) via a new `_authority_dir_name()` helper that walks
  up past any future `<AUTHORITY>/<year>/` subfolder, instead of assuming the immediate
  parent. Produces the IDENTICAL key as before for every shipped template today (no
  subfolders exist yet) — the rework is pure future-proofing for the deferred §2b mechanism.
- **Blast-radius check done properly, not assumed:** traced every subject-key consumer
  (`SUBJECTS` dict — rebuilt from disk each start; `_DISABLED_PACKS`/`pack_state.json` —
  persisted; `session["subject"]` cookie; `_learner_subject` — in-memory) vs. every
  `country="AU"`/`"AU"` DB-column reference (unrelated — ISO country code, not the directory
  name, untouched). Confirmed `skill_state` mastery is keyed by NODE id (`au3_*`), never by
  subject_key — genuinely unaffected. One real one-time impact, documented not migrated (2
  templates, zero external users): a `pack_state.json` disabled-entry for the old key
  silently stops matching post-rename (pack re-enables); a stale session cookie already
  degrades gracefully to the picker (pre-existing code).
- **`docs/CONTENT_LICENSES.md`**: §2b's ACARA row path updated; new §2c licence-onboarding
  checklist (MULTI_COUNTRY §3, verbatim) added — run before any R14/R15 template is authored.
- Updated the templates the rename actually touched: `tests/engine/test_template_catalog.py`
  (`_EXPECTED` + new authority-past-a-year-subfolder test), `tests/web/test_curriculum_toggle.py`,
  `tests/web/test_progress.py` (10 key-string refs), `engine/au_items.py` docstring. Historical
  dated changelog/spec entries referencing the old `AU/` path (PHASE0_STATUS.md, UI_REQUIREMENTS.md,
  REMAINDER_PLAN.md's own R2/R3 sections) deliberately left as-is — they're a record of what was
  true then, not live paths.

**Accept:** **590 tests pass, ruff clean.**

---

# R-RES — Session resume across a server-process restart  `[O]` ✅ DONE 2026-07-19

**Why:** documented, known, never-built gap — `docs/SESSION_FSM.md` §4 invariant 3 literally
said *"Not automated — no `session_resume` code path exists yet."* Reproducing the "Explain
more" bug live surfaced the real trigger: while the server process keeps running, navigating
away and back already resumes perfectly (`_controllers` holds the live `SessionController`
in memory). Mastery already survives a restart too (A6). What's actually lost on a
server-process restart (dev-server restart, crash, redeploy) is the in-memory controller
itself — a fresh one starts a new session_id, a fresh `items_completed` counter, and
re-derives NODE_SELECT from scratch, landing on *a* sensible node but not necessarily the one
the child was just on.

**Scope decision (AskUserQuestion, 2026-07-19): same topic, fresh question.** Re-enter the
exact node the child was on, but present a NEW item for it rather than the literal on-screen
question — avoids `Item` serialization, RNG mid-replay, and template-drift edge cases, while
fixing what's actually felt (wrong topic + a reset counter). **Hard safety constraint,
non-negotiable:** a session frozen when the process stopped resumes FROZEN, unconditionally —
no code path may silently unfreeze on restart.

## What changed

- **Schema (v3→v4):** `session` gained `checkpoint_state TEXT` (JSON:
  `current_node_id`/`frozen`/`items_completed`/`items_since_probe`), written best-effort every
  turn. New `LearnerStore.update_session_checkpoint()` / `.get_open_session()` (most recent
  `ended_at IS NULL` row). `create_session`'s INSERT became `INSERT OR IGNORE` — a resumed
  session reuses its ORIGINAL id so `response_log`/`transcript`/`help_event`/`probe_event` keep
  accumulating under one row.
  - **Bug found + fixed in the same pass:** `schema.sql` hardcodes its OWN
    `PRAGMA user_version`, independent of `store.py`'s `_EXPECTED_VERSION` — bumping only the
    latter left a fresh DB one version behind, colliding with the migration on next open
    ("duplicate column name"). Both must move together now (documented inline in schema.sql).
- **Controller:** new `resume_checkpoint: dict | None` ctor param. `_do_session_start`'s
  outcome, inlined (not a helper — T3.7's AST-based conformance test only sees literal
  `ctx.state = FSMState.X` assignments inside `_do_` handler bodies): no checkpoint →
  `NODE_SELECT` (unchanged); `frozen: True` → `ESCALATION_FREEZE`, unconditionally; a valid
  unmastered checkpointed node → seeds `current_node_id`/counters, `PATTERN_SELECT` directly
  (skips `NODE_SELECT`'s own `select_next` — which would otherwise prefer switching AWAY from
  `current` per R11's interleave policy, defeating "same topic"); a stale/missing/now-mastered
  node → safe degrade to `NODE_SELECT`. New `_write_checkpoint()` called from both `step()` and
  `parent_acknowledge()`.
- **Web wiring:** `_get_or_create_controller` looks up `store.get_open_session()` before
  constructing a new controller; reuses its session_id + checkpoint ONLY when the checkpointed
  node belongs to the CURRENT subject's curriculum (a learner's open session could be for a
  different, still-abandoned subject — reusing that id here would wrongly mix two subjects'
  rows under one session; this also matches PRE-EXISTING behaviour where switching subjects
  same-process already discards/bypasses a frozen controller — escalation freeze has always
  been per-subject, not global).
- **`docs/SESSION_FSM.md`:** two new backtick-quoted transition rows (T3.7-enforced) +
  mermaid diagram lines; §4 invariant 3 updated to record what shipped vs. what was
  deliberately scoped down (same-topic-fresh-question, not exact mid-question replay).

## Accept

New `tests/dialogue/test_session_resume.py` (8): no-checkpoint unchanged; frozen resumes
frozen + stays absorbing; frozen ignores node validity (unconditional); valid node resumes
same topic with seeded counters; mastered-since / missing node both degrade safely to
`NODE_SELECT`; `step()` writes a checkpoint every turn; the checkpoint reflects `frozen: True`
after a real escalation trigger. New `tests/web/test_app_smoke.py` tests (2, same
`importlib.reload` restart-simulation pattern as A6): a restarted process resumes the SAME
node + reuses the SAME session_id (no duplicate session row); a frozen session redirects
straight back to `/frozen` after "restart", never a fresh unfrozen question.
`tests/db/test_datamodel.py`'s migration suite extended to v3→v4 (schema_version 3→4
throughout, `test_v1_to_current_migration_adds_new_columns` now also exercises
`checkpoint_state`, `test_no_migration_path_raises` retargeted to the next genuinely
unregistered gap). **603 tests pass, ruff clean, 3× dialogue/web/db rerun stable.**

**Explicitly skipped (per the scope decision):** exact mid-question resume (literal on-screen
question + live Help/probe sub-state) — bigger, riskier, not chosen; scoping the open-session
lookup by a new subject DB column — the curriculum-membership check does the same job simpler;
resuming an older stale session if a MORE RECENT one for a different subject was also left
open — narrow edge case, not worth a multi-row scan for a single-family pilot.

---

# R13 — Verifier grammar extension: `decimal` answer type  ✅ DONE 2026-07-19

Gates Y5+ curriculum content for R14/R15: decimal-flavoured maths (currency, measurement,
division-with-remainder-as-decimal) needed a verifier grammar the pilot never had —
`eval/verify_numeric.py` safe-rejects any decimal-shaped output for `int`/`fraction`, and that
rejection is correct and load-bearing ([[decision_verifier_decimal_safe_reject]]). Built as a
pure extension: new functions, two new one-line dispatch branches, **zero edits** to the
existing int/fraction code paths — proven by running `tests/eval/test_verify_numeric.py` +
`tests/engine/test_verifier.py` byte-identical (confirmed via `git diff --stat`, both empty).

## What shipped

- **`eval/verify_numeric.py`:** new `answer_type="decimal"` / `checker="decimal_exact"`.
  `normalise_decimal()` gates through a **strict pre-parse regex**
  (`-?\d+(\.\d+)?$`, `fullmatch`) BEFORE ever calling `Decimal(...)` — Python's `Decimal()`
  constructor otherwise silently accepts `NaN`/`Infinity`/exponent notation (`5E2`), none of
  which should ever compare "equal" to a ground truth for a kids' arithmetic answer; the regex,
  not `Decimal`'s own leniency, is the real safety boundary. `_extract_decimal()` mirrors
  `_extract_numeric`'s priority/ambiguity shape (`<answer>` tag → decimal-dotted token →
  bare-int fallback, "or"-connective ambiguity → SAFE_REJECT). `_check_decimal_exact()`
  mirrors `_check_fraction_equiv`'s stricter SAFE_REJECT-on-bad-candidate posture (not
  `_check_int_exact`'s laxer FAIL posture) — matches the file's own "err on safe-reject"
  philosophy. `Decimal("0.50") == Decimal("0.5")` gives trailing-zero AND int/decimal
  equivalence for free (`2` == `2.0`), no special-casing needed.
- **`web/answer_modes.py` + `_turn.html`:** new `"decimal"` widget —
  `inputmode="decimal" step="any"`, deliberately NOT the existing `"number"` widget's
  `inputmode="numeric"` (which suppresses the decimal-point key on some mobile keyboards).
- **Already correctly plumbed, verified not touched:** `bkt.py`'s `_NUMERIC_TYPES` already had
  `"decimal"`; `controller.py`'s `_answer_format_hint` already had a `"decimal"` entry;
  `validate_template.py` has no answer_type/checker allow-list to extend.

## Gemma routing (corrected mid-plan — [[feedback_local_generate_sonnet_verify]])

First draft of this plan declared the whole file "not gemma-routed" purely because it's
safety-critical — maintainer corrected that as an over-broad exclusion: safety-critical gates
who DECIDES and VERIFIES, not who types, once the judgment itself is pinned. Split actually
used: the safety decisions (strict-regex-before-`Decimal`, SAFE_REJECT-vs-FAIL parity with
`fraction_equiv`) and the two dispatch-chokepoint insertions were authored directly; the four
new additive functions and the full test battery were gemma-drafted from an exact spec, then
reviewed. **Two real issues caught in review:** the ambiguity check used a bare `"or" in
text.lower()` substring test (would misfire on "before"/"corridor") instead of the file's own
`\bor\b` word-boundary convention — fixed; `_check_decimal_exact` called the private
`_extract_decimal` directly instead of the public `extract_answer()` dispatcher every sibling
checker uses — fixed, and this also surfaced a genuine spec gap (ambiguous-candidate had
collapsed into `EXTRACT_FAIL` instead of `SAFE_REJECT`, contradicting the plan's own promised
test case) — closed to match `_check_fraction_equiv`'s precedent. The test file also had one
bizarre gemma artifact (`normalise_diamond_none := ... is None`, functionally correct by
operator precedence but clearly a mistake) — cleaned up during review, not left in.

## Accept

New `tests/eval/test_verify_numeric_decimal.py` (28: 15 `normalise_decimal` unit tests incl.
NaN/Infinity/exponent/comma rejection, 11 `check()` integration tests, 2 explicit
regression-intent markers for the untouched int/fraction paths). Manually verified: a real
`check("decimal", "decimal_exact", ...)` round-trip PASS/FAIL, and `_turn.html` rendered
directly via Jinja with `widget="decimal"` produces the `inputmode="decimal" step="any"`
input. **631 tests pass, ruff clean, 3× eval/web rerun stable.**

**Explicitly skipped:** tolerance-based comparison (exact match only — no decimal-answer
template exists yet to prove tolerance is needed); locale-aware decimal separators (rejected
outright); extending `explain_check.py`'s arithmetic-claim verification to decimal claims
(separate, unrequested scope).

---

# R14a — AU_ACARA breadth: Year 2/5/6, Maths + English  ✅ DONE 2026-07-19  (India deferred to R14b)

Maintainer asked to split R14 (originally AU Y2/5/6 + IN Y2/4/5) and do AU first. R13 (decimal
verifier) shipped the same day specifically to unblock this — Year 5/6 maths needs decimal
answers (place value, add/sub/mult/div) the pilot's int/fraction-only grammar couldn't honestly
support before. 6 new templates, 21 new generator functions, 2 registry entries per file.

## What shipped

- **Maths:** `AU_ACARA/year2_maths.md` (5 nodes: place value, add/sub within 100, times
  tables 2/5/10, halves/quarters), `year5_maths.md` (5 nodes: decimal place value, add/sub
  decimals, fraction×whole, percentage-of-quantity, negative numbers — the pilot's FIRST use
  of R13's decimal type in real content), `year6_maths.md` (5 nodes: order of operations,
  mult/div decimals, rectangle area/perimeter, fraction-to-decimal). All in
  `engine/au_items.py`'s new `AU_YEAR2/5/6_GENERATORS` dicts.
- **English:** `AU_ACARA/year2_english.md`/`year5_english.md`/`year6_english.md` (4 nodes
  each — word classes, synonyms/antonyms, plurals/rhyming/compound-words/figurative-language),
  ALL built on the ALREADY-PROVEN `mc_which_is` helper (R7) over new, hand-verified
  pairwise-disjoint curated tables — zero new generator shapes needed, only new content, in a
  new `engine/au_english_items.py`.
- `engine/item_sources.py`: 6 new registry rows (`au_year2/5/6`, `au_english_year2/5/6`).

## Correctness discipline (this is where the real risk lives, not the YAML)

- **Every one of the 21 new generators self-validated 300–3000 draws through the REAL
  verifier** (not just "does it run") — 0 failures. Caught and fixed a real bug myself before
  it ever reached a test: `Decimal(N) / 10` silently drops the trailing zero on an exact
  division (`Decimal(40) / 10 == Decimal('4')`, not `'4.0'`) — cosmetically wrong next to a
  genuinely-one-decimal-place sibling value in the same question (e.g. "What is 4 + 2.1?").
  New `_one_dp(tenths: int) -> Decimal` helper (string-constructed, not divided) fixes every
  call site; verified with 3000 more samples that the display bug is gone.
- Every English curated table hand-verified pairwise-disjoint by me before it shipped (R7's
  own discipline) — confirmed programmatically too (`test_au_english_items.py` asserts 4
  distinct MC choices on every one of 3600 draws across the 12 tables).
- **Two gemma structural failures caught in review, not shipped:** the Year 5 maths draft
  dropped `grounding: {}` + every inline ACARA-code comment and mis-scoped a comment inside
  the frontmatter block; the **Year 6 maths draft put the entire `concepts:` list OUTSIDE the
  YAML frontmatter, after a second stray `---`** — would not have parsed as a valid curriculum
  template at all. Both rebuilt directly by hand using the Year 2 template's proven-correct
  structure as the reference, rather than re-prompting a second time.
- Manually drove full FSM round-trips (not just unit tests) for a decimal node (Year 5
  `au5_add_sub_decimals`: presented "What is 2.9 + 7.9?", submitted the generator's own
  ground truth, scored correct, advanced) and an English node (Year 6 preposition
  classification) — both real, live, end-to-end.

## Accept

New `tests/engine/test_au_english_items.py` (3 self-validate tests, 12 nodes × 200 draws each
via `ItemGenerator`); `tests/engine/test_au_items.py` gained 3 more self-validate tests (Y2/5/6
maths); `tests/engine/test_template_catalog.py`'s `_EXPECTED` dict gained 6 rows. All 6 new
templates pass `validate_or_raise` (DAG/schema check). Auto-discovery (R3.1) means zero picker
code changes — confirmed the 6 new subject keys appear in `SUBJECTS` after a fresh app import.
**637 tests pass, ruff clean, 3× engine/web rerun stable (190 passed each run).**

**Explicitly deferred (this is R14a of R14, not the whole thing):** India (R14b, Class 2/4/5,
`IN_GENERIC`) — separate wave, separate plan, once picked up. Ratio/rate content (Y6) — no
ratio-string checker in the verifier grammar, dropped rather than force-fit. Punctuation/
spelling-with-full-sentences (Y6 English) — would need a new hand-curated sentence-bank shape,
not the proven word-table mechanism everything else this wave used.

---

# R15 (partial) — AU Year 7-8 maths, shipped fast for a same-day demo  2026-07-19

Maintainer was time-pressured (kids arriving for a demo same day) and asked for R15 scoped to
AU only, "at least Year 7 or 8." Deliberately shipped Y7+Y8 solidly rather than stretch to Y9
and risk something untested for a live audience — same pattern as R14a (self-validate every
generator through the real verifier, gemma drafts generators from an exact spec, templates
hand-written directly after R14a's Year 6 near-miss taught that gemma has real structural risk
assembling YAML frontmatter).

**Shipped:** `year7_maths.md` (integers add/sub, order-of-operations-with-negatives,
unlike-denominator fraction addition via `fractions.Fraction`, one-step equations — the
pilot's first "solve for x" content, still a plain int answer — multiplying decimals) and
`year8_maths.md` (two-step equations, squares, negative-number multiplication, percentage
change, dividing decimals). 10 new generators in `engine/au_items.py`
(`AU_YEAR7_GENERATORS`/`AU_YEAR8_GENERATORS`), 2 new `item_sources.py` rows.

**Verification, compressed for time but not skipped on correctness:** every one of the 10
generators self-validated 500 draws through the real deterministic verifier (0 failures);
eyeballed a sample of each for display sense (negative numbers, multi-decimal-place results
render correctly, no repeat of R14a's `Decimal(N)/10` trailing-zero bug since `_one_dp()` was
reused throughout); drove one live FSM round-trip per year (present → answer with the
generator's own ground truth → scored correct → advanced) through the real
`SessionController`. Skipped the usual 3× flake-rerun given time pressure — justified because
the self-validate draw count (500/generator) is a stronger correctness signal than rerun count
for this kind of pure-function content, and nothing here touches session/RNG-replay logic
(R11's actual flakiness source).

**Explicitly deferred, not forgotten:** English Y7/8, Year 9 (only "at least Y7/8" was
promised), India (R14b), the maintainer-checkpoint structure the original R15 plan called for
between phases (skipped under time pressure — worth reinstating once the demo pressure is
off). `docs/PHASE0_STATUS.md`/memory updated; a fuller retrospective write-up can follow once
today's demo is done.

**Accept:** 639 tests pass, ruff clean.

---

# Remainder Build Plan — v2

Most of v1 shipped; **G0 is essentially validated** (model pick, safety, retrieval, E2E,
licence, decisions all done). This is the refreshed list of what's left, with **tight specs for
the parts local `gemma4:12b` can code** (generate → Opus/Sonnet verify; per-task gate =
`pytest` green + `ruff` clean; one branch+PR per task).

## Done since v1 (for context — don't redo)
W1.3 pick (`gemma2:9b`) · W4.2 AGPL-3.0 · W5.6 + W2.2 decisions ratified · W7.4 reader verified on
real ZIMs (Vikidia + Simple-WP) · eval: quality + **safety pipeline 20/20** + **retrieval 9/9** +
E2E clean · local red-team (pii + policy) · DB logging + parent-oversight + escalation-resume ·
go-public docs. `main` green.

---

## A. Codeable now — Gemma-able `[G]`, tight specs

### A1 — W5.6 session-start assent line + loss-of-assent note  `[G]`
- **Why:** W5.6 ratified *continuous-assent*; the session-start "you can stop anytime" line is the
  one unbuilt piece. (Parent-end-as-loss-of-assent is already captured by
  `session.ended_reason='ended_by_parent'`.)
- **Spec:** add a module constant `ASSENT_LINE = "Remember — you can stop anytime, just say 'stop'."`
  in `controller.py`. Include it **once** in the first child-facing turn (prepend in
  `_do_session_start`'s hand-off to the first PRESENT, or accumulate it onto the first `step(None)`
  output). Add a one-line comment tying `_END_REASON['ended_by_parent']` to W5.6 loss-of-assent
  (no new mechanism). Don't repeat the line on later turns.
- **Files:** `src/mentar/dialogue/controller.py`; new assertion in `tests/dialogue/`.
- **Accept:** first `step(None)` output contains the assent phrase; it does **not** reappear on
  subsequent turns; full suite + ruff green.

### A2 — NIAH reusable run config  `[G]`
- **Why:** the NIAH run worked but its run config was ad-hoc in `/tmp`; make it reproducible.
- **Spec:** add `eval/niah/run.example.yaml` using the verified schema (`run_name`, `model` =
  filename stem, `task: {type: uuid}`, `haystack: {type: text, text: "..."}`, `sweep:
  {context_lengths, depth_percents}`, `store`). Keep model configs gitignored. README already
  documents the `OPENAI_BASE_URL` gotcha.
- **Files:** `eval/niah/run.example.yaml`.
- **Accept:** `niah run eval/niah/run.example.yaml --model-dir eval/niah/models --dry-run` validates
  on a Node ≥20.20 host.

---

## A3–A19 — Repo-review wave (2026-07-03)

Source: **[REVIEW_2026-07-03.md](_legacy/REVIEW_2026-07-03.md)** (full detail + rationale per task;
section refs below). Same per-task gate: pytest green + ruff clean, one branch+PR per task.
Ordered by the review's priority table.

### A3 — escalation_log schema v2 + single write path  `[O]` *(safety-critical path — Opus-led, not Gemma)*
- **Why:** audit rows are missing `severity`, `session_id`, turn index (SAFETY §3.3/§3.5 claim
  all three) and `session_outcome` records `'frozen'` even for logged-only jailbreaks. REVIEW §1.2.
- **Spec:** schema migration to `user_version=2` (add `severity TEXT`, `session_id TEXT`,
  `turn_index INTEGER`; migration hook already exists in `store._apply_schema_if_needed`);
  extend `LearnerStore.write_escalation(...)`+adapter+controller call to pass severity, session,
  turn, and outcome (`'logged_only'` for LOW jailbreak, `'frozen'` otherwise); delete
  `escalation.handle_trigger()` (uncalled, drifted duplicate) or reduce it to a docstring example.
- **Files:** `src/mentar/db/schema.sql`, `db/store.py`, `web/app.py` adapter,
  `dialogue/controller.py`, `safety/escalation.py`, `tests/db/`, `tests/safety/`.
- **Accept:** v1→v2 migration test passes; jailbreak row asserts `logged_only`+severity;
  frozen row carries session_id+turn_index.

### A4 — SAFETY.md truth-sync + session-start AI-transparency line  `[G]` (docs) + `[G]` (one-liner)
- **Why:** SAFETY.md overstates shipped controls (§1.5.2 strip step; §4.6/SECURITY.md retention
  "is applied"); §5.5 start-of-session disclosure unbuilt. REVIEW §1.1/1.3/1.5.
- **Spec:** (1) rewrite §1.5.2(2) to the actual control (marker data-wrapping, no strip) with a
  changelog note; (2) reword §4.6 + SECURITY.md retention to "planned — pilot retains all data;
  deletion = delete the .db file" pending the C-row decision; (3) extend the first-turn preamble
  in `controller.step()` to `ASSENT_LINE` + "I'm Mentar, a computer learning helper — not a
  person." + test (mirrors `tests/dialogue/test_assent.py`).
- **Accept:** no present-tense claim in SAFETY/SECURITY lacking an implementation; first
  `step(None)` contains both lines exactly once.

### A5 — per-node, child-initiated `help_pressed` for probe classification  `[G]`
- **Why:** stale-across-nodes + auto-help pollution corrupts the false-confidence metric.
  REVIEW §2.2.
- **Spec:** add `ctx.help_by_node: dict[str, bool]` set ONLY on child-initiated help
  (`_is_help_request` paths, not the auto-help branch in `_do_bkt_update`); pass
  `help_pressed=ctx.help_by_node.get(ctx.current_node_id, False)` in `_do_probe_classify`.
- **Files:** `dialogue/controller.py`, `tests/dialogue/test_controller.py`.
- **Accept:** regression tests: help on node A ≠ help on node B's probe; auto-help alone
  still classifies `false_confidence` when the table says so.

### A6 — durable learner id in the web app  `[G]`
- **Why:** every `mentar serve` restart creates a new learner row → mastery/history reset.
  REVIEW §2.3.
- **Spec:** in `_get_or_create_controller`, look up `learner_profile` by the deterministic
  name `pilot-<uuid8>` before `create_learner` (add `LearnerStore.get_learner_by_name`);
  reuse the existing id.
- **Files:** `web/app.py`, `db/store.py`, `tests/web/`, `tests/db/`.
- **Accept:** test simulating restart (fresh module state, same cookie) reuses the learner id
  and sees prior skill_state.

### A7 — subject-parameterised system prompt  `[G]`
- **Why:** system prompt scope-locks to fractions; arithmetic/science calls conflict.
  REVIEW §2.1.
- **Spec:** add `{{subject}}` + `{{scope_line}}` slots to `prompts/system_prompt.md`
  (bump version hash + README registry); `_render_system_prompt` fills from the active
  curriculum template's `subject:`/`year_level`; web `SUBJECTS` passes them through.
- **Files:** `prompts/system_prompt.md`, `prompts/README.md`, `dialogue/controller.py`,
  `web/app.py`, `tests/test_prompt_registry.py`.
- **Accept:** T4.6 hash check green; science session's system text contains "science", not
  "fractions".

### A8 — frozen page for the child + confirm-word on parent ack  `[O]` *(safety-critical path)*
- **Why:** escalation currently redirects the child to `/parent` (verbatim trigger text +
  un-gated resume button). REVIEW §1.4.
- **Spec:** new `/frozen` view showing ONLY the two fixed handoff messages; `/answer` +
  `/` redirect there while `state == ESCALATION_FREEZE`; `/parent` no longer auto-navigated
  (typed URL only); `/parent/ack` requires a typed confirmation word (e.g. "RESUME") in the
  form. PIN gate stays Phase 1 — this is the honor-system-compatible minimum.
- **Files:** `web/app.py`, `web/templates/` (+`frozen.html`), `tests/web/`.
- **Accept:** escalated child view contains handoff text and NO trigger text/ack control;
  ack without the confirm word is a no-op.

### A9 — loud-fail on uncovered nodes + extraction-loop cap  `[G]`
- **Why:** silent mis-scoring fallback (`expected_answer` = a *question*) + infinite
  SAFE_REJECT/EXTRACT_FAIL re-ask loop. REVIEW §2.4/2.5.
- **Spec:** (1) at controller/web startup, if any curriculum node lacks item-source coverage
  AND a real `expected_answer`, raise a config error naming the node; (2) in `_do_score`,
  after 3 consecutive unreadable answers on the same question, route into the Help loop
  unscored (reuse the auto-help entry).
- **Files:** `dialogue/controller.py`, `web/app.py`, tests.
- **Accept:** uncovered-node fixture fails loudly at startup; 3× gibberish lands in
  HELP_MODALITY_SELECT, nothing logged as scored.

### A10 — retention: reword now, design decision logged  `[G]` (docs part)
- **Why:** REVIEW §1.3 — retention claims vs. immutability triggers are mutually exclusive
  as designed. Docs part is A4(2); the *mechanism* needs a maintainer call → see C row.

### A11 — SESSION_FSM conformance test (T3.7) or doc re-sync  `[O]` verify-led
- **Why:** promised drift-detector never built; doc already drifted. REVIEW §3.1.
- **Spec (preferred):** build `tests/dialogue/test_session_fsm.py` parsing the doc's §2
  transition table vs. `FSMState`/`_tick` reachability; THEN update SESSION_FSM.md (with
  changelog rows) for the legitimate new transitions (auto-help, probe→help, LOW-severity
  continue, probe demote) and remove or wire the dead `PARENT_ACK_WAIT`.
- **Accept:** test fails on either missing-documented or undocumented-reachable transition;
  suite green after the doc update.

### A12 — CI: pytest+ruff gate + secret scan  `[G]`
- **Why:** the gate is convention-only; the secret hook is opt-in. REVIEW §3.2.
- **Spec:** `.github/workflows/ci.yml` — matrix py3.11/3.12/3.13:
  `pip install -e ".[dev,web]"` → `python -m pytest tests/ -q` → `ruff check .`; plus a
  gitleaks (or `detect-secrets`) job. No eval/LLM jobs (eval is run-only, off-CI).
- **Accept:** green run on a PR; a planted fake `sk-…` string in a PR fails the scan job.

### A13 — output-side safety gate (`safety/output_guard.py`)  `[O]` *(safety-critical path — Opus-led)*
- **Why:** SAFETY L2's discard-and-log + scope/age checks have no implementation; LLM output
  reaches the child with only credential redaction + trailing-question strip. REVIEW §1.6.
- **Spec:** new pure module `safety/output_guard.py` — `screen_output(text, subject_scope) ->
  (text | None, incident | None)`: v0 = deterministic blocklist for the §2.1 hard-block
  categories + a scope heuristic; on match, DISCARD (return None), write an incident row
  (reuse escalation_log with a distinct class, or a new `output_incident` table — decide in
  A3's schema v2), controller serves a neutral redirect instead. Wire as a second stage inside
  `_make_safe_llm` (same chokepoint pattern as the credential guard). Blocklist swappable
  wholesale (Bucket E lands here later).
- **Files:** `src/mentar/safety/output_guard.py`, `dialogue/controller.py`,
  (`db/schema.sql` if new table), `tests/safety/`, `tests/dialogue/`.
- **Accept:** a stubbed LLM returning blocked content never reaches `TurnResult.text`; an
  incident row exists; clean output passes byte-identical; suite + ruff green. SAFETY §2.1/§2.2
  reworded (or made true) in the same PR — no present-tense overclaim left.

### A14 — verify numeric steps in Help explanations before serving  `[O]` *(safety-critical path)*
- **Why:** SAFETY §6.2 Level 2 (verify re-explanations, discard+regenerate on failure) is
  unimplemented — the verifier only ever checks child answers. REVIEW §1.7.
- **Spec:** in `_do_help_explain`, extract arithmetic claims (`a <op> b = c`, fraction forms
  included) from the explanation via a small parser; check each with `verify_numeric`; on any
  FAIL, regenerate (bounded by the existing modality/retry budget — no new loop); if still
  failing, serve `_fallback_hint` (grounding passage / worked example — already deterministic).
  SAFE_REJECT/EXTRACT_FAIL on a claim = not checkable → pass through (don't block prose).
- **Files:** `dialogue/controller.py` (+ helper in `eval/verify_numeric.py` or a thin
  `engine/explain_check.py`), `tests/dialogue/`.
- **Accept:** stubbed LLM emitting "3/4 + 1/4 = 2/4" never reaches the child; correct worked
  example passes unchanged; fallback path covered; suite + ruff green.

### A15 — escalation-log fallback sink (never silently dropped)  `[O]` *(safety-critical path)*
- **Why:** `write_escalation` failures are swallowed → verbatim disclosure lost, violating
  SAFETY §3.1. REVIEW §8.1.
- **Spec:** on DB-write failure in the controller's escalation branch, append
  `{iso_ts, trigger_class, severity, verbatim_text}` (one JSON line) to an append-only
  `escalation_fallback.log` next to the DB file; parent view shows a "durable logging degraded"
  banner when that file is non-empty. Freeze behaviour unchanged.
- **Files:** `dialogue/controller.py`, `web/app.py`/`templates/parent.html`, tests
  (fake store raising on write_escalation).
- **Accept:** DB-failure test still freezes AND the fallback line exists verbatim; happy path
  writes no fallback file.

### A16 — validate curriculum templates at startup  `[G]`
- **Why:** cyclic/bad template → empty fringe → false "you've mastered everything!" to the
  child. REVIEW §8.2.
- **Spec:** `web/app.py` startup + `run-session` call `validate_template.validate()` per loaded
  template; any error → exit non-zero naming template + error (config error, not a 500).
- **Files:** `web/app.py`, `cli/__main__.py`, tests with a deliberately cyclic fixture template.
- **Accept:** cyclic fixture refuses to serve with a clear message; valid templates unaffected.

### A17 — de-tangle layering: curriculum loader + store adapter out of `web/`  `[G]`
- **Why:** CLI imports `mentar.web.app` (Flask required for headless use; module-level side
  effects on import). REVIEW §8.3.
- **Spec:** move `_load_curriculum` → `engine/curriculum.py` (public `load_curriculum(path)`),
  `_DbStoreAdapter` → `db/adapter.py`; web + CLI import from there; `web/app.py` keeps only
  web wiring. No behaviour change.
- **Accept:** `python3 -c "import mentar.cli.__main__"` succeeds without Flask installed;
  suite + ruff green.

### A18 — prompt-change ⇒ safety-eval re-run rule  `[G]` (docs + CI hook)
- **Why:** the 20/20 pipeline-safety claim silently ages across prompt re-hashes. REVIEW §8.4.
- **Spec:** (1) rule added to AGENTS.md gate + CONTRIBUTING: any `prompts/*.md` body-hash change
  ⇒ re-run T1.5 adversarial through the pipeline before merge, record run date in
  EVAL_RESULTS.md next to the claim; (2) once A12 lands, a CI step that flags PRs touching
  `prompts/` with a required-checklist comment.
- **Accept:** rule present in both docs; CI flag fires on a prompts-touching PR.

### A19 — small hygiene batch: age_mode assertion + lockfile + seeded RNG  `[G]`
- **Why:** REVIEW §8.6/§8.7 — `age_mode` stored but never read; floating deps; unreplayable
  sessions.
- **Spec:** (1) controller/web startup asserts `age_mode == "parent_mediated"` (pilot scope;
  clear error otherwise); (2) add a `constraints.txt` (or uv lock) pinned from a green env,
  referenced in CI; (3) `SessionController` takes an optional `rng_seed` (default: random,
  logged at session start + stored on the session row if A3's migration is in).
- **Accept:** independent-mode profile refuses with a clear message; CI installs pinned;
  same-seed session replays identically in a test.

---

## B. Codeable but verify-led  `[O]` + `[G]`

### B1 — Pilot grounding-anchor QA + re-point — ✅ **DONE 2026-07-05 (re-pointed to Khan Academy)**
- **What actually happened:** confirmed empirically (not by filename inspection) that all 8
  nodes resolved to `""` against the real `/mnt/zim` — no Vikidia/Simple-WP ZIM exists there
  (only stackexchange/wikipedia/khanacademy/gutenberg/ifixit/mdwiki). Maintainer chose:
  **re-point to Khan Academy** (`khanacademy_en_all_2023-03.zim`, already mounted — and
  arguably better-suited math content than a general encyclopaedia anyway).
- **Real content problem found + solved:** KA lesson-page HTML is a video-embed shell with
  only a one-line description (would have repeated the exact "thin passage" problem this task
  exists to fix) — the substantive content is the video's English subtitle (`.vtt`) transcript.
  Searched the real ZIM (`libzim.search.Searcher`) for all 8 concepts, verified each candidate's
  transcript by actually fetching and reading it (not guessed): all 8 are genuinely distinct,
  on-topic, substantive (1081–4023 chars) — this also directly resolves the REVIEW §2.6
  distinctness addendum (was: 7/8 nodes anchored the identical Vikidia article).
- **Built:** `grounding/reader.py` gained `get_by_path()` (direct ZIM-internal-path lookup —
  KA has no recoverable external URL) and `get_video_narration()` (finds the English `<track>`,
  strips WebVTT markup to plain narration text). `grounding/resolve.py` gained a small
  per-source extractor registry (`_SOURCE_EXTRACTORS`) — generic wiki-article path by default,
  `khanacademy` overrides with the video-narration path; not a general plugin system, just a
  registry for the "critical few" sources whose content shape genuinely differs. `source_map.py`
  exempts `khanacademy` from the URL-host scope guard (its anchor is a ZIM-internal path, like
  `parent_upload`/`builtin`). `curriculum/templates/_pilot/fractions.md`'s 8 nodes re-pointed to
  verified KA anchors. `config/inference.example.yaml` documents the new source shape.
- **Verified end-to-end** (not just unit-level): `load_curriculum` → `resolve_grounding` → all 8
  nodes return substantive, distinct passages against the real ZIM; a real `SessionController`
  Help turn correctly threads a KA transcript into the system prompt's `GROUNDING_BEGIN/END`
  wrapper. `validate-template` still passes.
- **Tests:** `tests/fixtures/build_fixture_zim.py` gained a KA-shaped synthetic entry (video
  HTML shell + `.vtt`, mirroring the real ZIM's shape) for fast CI-safe regression coverage of
  the new extraction code, independent of the multi-GB real ZIM.

### B2 — doc-drift sweep (mechanical)  `[G]`
- **Why:** REVIEW §4 table — 9 factual mismatches (ARCHITECTURE.md missing `grounding/`+`web/`
  modules + wrong CLI list + phantom `pytest.ini`; README stale Status/tree/test-count;
  AGENTS.md missing `mentar eval`; EVAL_RESULTS pre-pick framing; SAFETY.md Appendix C `_legacy`
  paths; pyproject 3.13 classifier). Overlaps DOC_AUDIT §C — action both in one pass.
- **Files:** `docs/ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `docs/EVAL_RESULTS.md`,
  `docs/SAFETY.md` (App. C only), `pyproject.toml`, `docs/DOC_AUDIT.md` (mark actioned).
- **Accept:** every row of REVIEW §4 either fixed or explicitly waived inline; ruff/pytest green.
- **✅ DONE 2026-07-05, merged (PR #72)**: all 9 REVIEW §4 rows + all 11
  DOC_AUDIT §F rows actioned — see `docs/DOC_AUDIT.md` §F for the per-row status. Also picked up
  `docs/SPEC.md` (Cowork bridge TODO resolved, eval-host connection details supplied,
  Appendix B delivery note) and `docs/llm-compatibility.md`'s stale "pick pending" line while
  in the neighbourhood.

---

## C. Maintainer-only (NOT codeable — flagged so they're not lost)
- ~~Paste the full **AGPL-3.0 text** into `LICENSE`~~ — **done 2026-08-12 (159bb25)**: canonical
  661-line text fetched and installed verbatim; LICENSING.md + CLA.md shipped alongside.
- ~~**Rotate** the eval-host token~~ — **done (maintainer confirmed 2026-08-12)**; the key in
  `.claude/settings.local.json` is the post-rotation one (auth verified same day).
- **Safeguarding professional review** — handoff wording + child-facing emergency signposting
  (gates rollout beyond the supervised single-family pilot).
- ~~Place Vikidia + Simple-WP on a writable runtime `zim_dir`~~ — **superseded 2026-07-05 (B1):
  pilot re-pointed to Khan Academy** (already mounted, read-only is fine). Optional future
  enhancement only, not a blocker: if Vikidia/Simple-WP are ever placed on a writable `zim_dir`,
  those sources still work unmodified (`_extract_generic_article` handles them).
- **Sign `PILOT_CONSENT`** before session 1.
- **Explicit-harm + iterative-jailbreak red-team** — needs promptfoo Cloud or an uncensored+capable
  generator (the aligned-Claude refusal is structural; the local 7B was too weak). Decision + setup.
- ~~Retention mechanism decision~~ — **ratified 2026-07-04 (option ii: pilot retains
  everything, deletion = delete the `.db` file), docs reworded 2026-07-05 as task A4.** Compliance
  wording (COPPA 2025 / GDPR-K) against public docs still a separate future check — the
  documents no longer overclaim, but a formal compliance-language pass hasn't been done.
- ~~BKT rising-mastery-on-wrong call~~ — **ratified 2026-07-04 (Option B), built 2026-07-05 as
  task A20, merged** (PR #66). No longer a pending C-row.
- Run the **pilot** (P1–P5).

## Execution
Route `[G]` tasks through the `gemma` skill (spec → gemma codes → Opus/Sonnet verifies); needs
`MENTAR_VLLM_*` in the session. Backlog (post-pilot): private/public MCP, AU/ACARA template, W6.5
manipulatives, W7.5/7.6, LLM-guided onboarding — see the `PHASE0_STATUS.md` backlog section.
