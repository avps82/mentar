---
title: "Mentar — Remainder Build Plan v2 (post-G0-validation)"
version: living-doc
status: "Active"
updated: 2026-07-03
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

### B1 — Pilot grounding-anchor QA + re-point
- **Why:** verification found Simple-WP "Fraction" is a **thin disambiguation (75c)**; several nodes
  (`comparing_equal_denom`, `adding_equal_denom`, `subtracting_equal_denom`) point at
  `wikipedia_simple` "Fraction" → poor grounding. Vikidia's Fraction is substantive (216c).
- **Spec:** for each of the 8 pilot nodes, run `ZimReader`/`resolve_grounding` against its anchor
  (zim_dir holding Vikidia + Simple-WP), capture extracted length; **re-point any anchor whose
  extract is thin/disambiguation (< ~150c) to the best available source** (prefer Vikidia for
  fractions). Update the node `grounding: {source, anchor}` blocks.
- **Files:** `curriculum/templates/_pilot/fractions.md`.
- **Accept:** every node's anchor extracts substantive verbatim (no disambiguation stubs);
  `validate-template` still passes.
- **Owner:** Opus produces the per-node extraction report (needs the ZIMs on a readable `zim_dir`);
  Gemma/mechanical applies the anchor edits.
- **Addendum (repo review 2026-07-03, REVIEW §2.6):** the report must also check **distinctness**,
  not just length — 7 of 8 nodes anchor the same Vikidia `Fraction` article; log which section each
  `passage_hint` actually resolved to (`get_section` heading match vs. lead fallback). Where hints
  don't hit a heading, author per-node passage text in the template or split anchors across
  articles. Accept: no two nodes ground to an identical passage unless explicitly waived.

### B2 — doc-drift sweep (mechanical)  `[G]`
- **Why:** REVIEW §4 table — 9 factual mismatches (ARCHITECTURE.md missing `grounding/`+`web/`
  modules + wrong CLI list + phantom `pytest.ini`; README stale Status/tree/test-count;
  AGENTS.md missing `mentar eval`; EVAL_RESULTS pre-pick framing; SAFETY.md Appendix C `_legacy`
  paths; pyproject 3.13 classifier). Overlaps DOC_AUDIT §C — action both in one pass.
- **Files:** `docs/ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `docs/EVAL_RESULTS.md`,
  `docs/SAFETY.md` (App. C only), `pyproject.toml`, `docs/DOC_AUDIT.md` (mark actioned).
- **Accept:** every row of REVIEW §4 either fixed or explicitly waived inline; ruff/pytest green.

---

## C. Maintainer-only (NOT codeable — flagged so they're not lost)
- Paste the full **AGPL-3.0 text** into `LICENSE` (gnu.org unreachable from the sandbox).
- **Rotate** the eval-host token.
- **Safeguarding professional review** — handoff wording + child-facing emergency signposting
  (gates rollout beyond the supervised single-family pilot).
- Place **Vikidia + Simple-WP** on a *writable* runtime `zim_dir` (the `/mnt/zim` mount is read-only).
- **Sign `PILOT_CONSENT`** before session 1.
- **Explicit-harm + iterative-jailbreak red-team** — needs promptfoo Cloud or an uncensored+capable
  generator (the aligned-Claude refusal is structural; the local 7B was too weak). Decision + setup.
- **Retention mechanism decision (repo review 2026-07-03, REVIEW §1.3)** — the documented 90-day
  rolling purge and the transcript immutability triggers are mutually exclusive as designed.
  Ratify one: (i) purge path designed alongside immutability (time-boxed trigger exception,
  schema v2+), or (ii) pilot retains everything + deletion = delete the .db file (docs reworded
  by A4). Compliance-weighted — verify wording against COPPA 2025 / GDPR-K before public docs.
- **BKT rising-mastery-on-wrong call** (Known-defects 2026-06-29) — review concurs with
  **Option B** (gate `learns` on non-wrong observations): the probe-demote patch already deviates
  from classic BKT, and the parent-facing % matters more than model purity. Needs your ratify.
- Run the **pilot** (P1–P5).

## Execution
Route `[G]` tasks through the `gemma` skill (spec → gemma codes → Opus/Sonnet verifies); needs
`MENTAR_VLLM_*` in the session. Backlog (post-pilot): private/public MCP, AU/ACARA template, W6.5
manipulatives, W7.5/7.6, LLM-guided onboarding — see the `PHASE0_STATUS.md` backlog section.
