---
title: "Mentar — Remainder Build Plan v2 (post-G0-validation)"
version: living-doc
status: "Active"
updated: 2026-07-05
---

# Release Wave — pilot-ready main (status as of 2026-07-10)

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
  `P(L') = P(L|obs) + (1−P(L|obs))·learns` only when the observation is NOT a bare-wrong
  (unaided incorrect) attempt; a wrong unaided answer only runs the conditioning step (posterior
  drops via slip/guess), no `learns` term added. Hinted-win / correct / probe observations still
  get the `learns` credit as before. Add a literature reference in
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

## R2.1 — MCQ shows its options THREE times; web should show stem + radios only  `[G]`

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

## R2.2 — TTS: pause/resume instead of restart-from-the-top  `[G]`

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

Source: **[REVIEW_2026-07-03.md](../REVIEW_2026-07-03.md)** (full detail + rationale per task;
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
- Paste the full **AGPL-3.0 text** into `LICENSE` (gnu.org unreachable from the sandbox).
- **Rotate** the eval-host token.
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
