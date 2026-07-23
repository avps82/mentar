---
type: Mentar Status Doc
title: Documentation Audit
description: Staleness register — what's done, what's left, which docs have drifted from the code. Findings + fix log across multiple audit passes.
tags: [audit, docs, staleness]
timestamp: "2026-07-23T00:00:00Z"
---

# Documentation Audit — 2026-06-26 (addendum 2026-07-03 below)

A snapshot of **what's done, what's left, and which docs have gone stale.**

> **Findings only — not actioned.** Per maintainer instruction this is a register, not a fix.
> Canonical task state stays in [`PHASE0_STATUS.md`](PHASE0_STATUS.md) (ledger) +
> [`REMAINDER_PLAN.md`](REMAINDER_PLAN.md) (plan); this file points at them and lists drift,
> deliberately **not** duplicating their content.

## A. Done — recent + this session
- **Built earlier:** engine (BKT/fringe/probe/itembank/itemgen), dialogue FSM controller, safety
  escalation, inference backend, grounding reader (W7.1–3), web app, CLI, DB store + schema.
- **This session (PRs #4–#9):** DB logging wired + `classify_probe` crash fix (**merged, #4**);
  parent-oversight DB reads + escalation-ack persistence + handoff-wording harness (#5);
  escalation-freeze resume/end (#8); promptfoo red-team scaffold (#6); go-public docs incl.
  `LICENSE_AUDIT.md` (#7); status-ledger sync (#9). **363 tests, ruff clean.** Detail in the
  `PHASE0_STATUS.md` 2026-06-26 changelog entry.

## B. Remaining — maintainer-gated (not locally doable)
- **W1.2 → W1.3** — candidate eval-host run + model pick (needs `MENTAR_VLLM_*` creds + the host).
- **W4.2** — LICENSE ratification. Audit points to **AGPL-3.0** (GPL `libzim` is a core dep).
- **W5.6** — distress/runway thresholds (decision).
- **W2.2** — emergency-services signposting decision **+** professional handoff-wording review.
- **W7.4** — real Vikidia/Simple-WP ZIM download + reader path verification (needs NAS/ZIMs).
- **Post-pilot 🔭:** W5.4 COPPA recheck, W5.5 effort estimates, W6.5 manipulatives, W7.5/7.6,
  private/public MCP tasks.
- **Local backlog: exhausted** — the only open local items are the unmerged PRs #5–#9 themselves.

## C. Stale-document findings (NOTE — do not action yet)
1. **`PHASE0_STATUS.md` frontmatter `last-updated: 2026-06-14`** — months behind; bump on next edit.
2. **`PHASE0_STATUS.md` → "Next batch (immediately actionable)"** — **STALE**: lists the grounding
   reader, dialogue controller, and web app as "doable next", but all are built. Superseded by
   `REMAINDER_PLAN.md`. Replace or delete the section.
3. **`PHASE0_STATUS.md` → "Tests written but not yet runnable as a suite"** — **STALE**: claims the
   sandbox has no `pip`/`pytest`; the suite runs (363 tests). Remove/replace.
4. **`PHASE0_STATUS.md` W3.3 / W3.4 "Remaining (Sonnet): caller wiring"** notes — **STALE**: the
   FSM caller wiring is done.
5. **`PHASE0_STATUS.md` W2.2 note** ("handoff wording validation … remain required") — partly
   addressed: a wording **harness** exists (PR #5); the **professional** review is still open.
   Reword to distinguish the two.
6. **Line-count drift** in `PHASE0_STATUS.md` (e.g. "SAFETY.md 692 lines" → now 715;
   "escalation.py 220 lines"). Cosmetic.
7. **`pyproject.toml` `license = { text = "TBD" }`** — blocks public release; resolve with W4.2.
8. **`docs/EVAL_RESULTS.md` (231 ln) + `docs/llm-compatibility.md` (57 ln)** — **VERIFY**: the
   W1.2 eval-host run hasn't happened, so confirm neither presents un-run/placeholder numbers as
   real results. `README.md` links both.
9. **`docs/MODEL.md`** — confirm it reads as a *plan/roster* (W1.3 pick not yet made), not a
   settled selection.
10. **`docs/SPEC.md` v0.3 (2026-06-11)** — verify it reflects later decisions (W5.x, W7 grounding,
    media/interactivity); it may lag.
11. **`README.md` doc links** — re-check once PRs #5–#9 merge (SECURITY.md + the disclaimer banner
    arrive via #7; AGENTS/CONTRIBUTING via #7).

## D. Suggested fix order (when actioned)
1. Refresh `PHASE0_STATUS.md` (drop the stale "Next batch" + "Tests not runnable" sections; bump
   the frontmatter date; clear the done "Remaining" wiring notes) — highest signal-to-effort.
2. Verify/refresh `EVAL_RESULTS.md` + `llm-compatibility.md` so they don't imply results that
   haven't been produced.
3. Resolve `pyproject` license alongside the W4.2 decision.

---

# Addendum — 2026-07-03 (independent repo review)

New stale/drifted docs found by the 2026-07-03 review (detail: `REVIEW_2026-07-03.md` §4, §1,
§8; mechanical fixes batched as REMAINDER_PLAN **B2**; safety-doc truth-sync = **A4**). This
section supersedes §B/§C above where they conflict.

## E. This file itself is stale (§B above)
§B lists W1.3, W4.2 (licence), W5.6 and W7.4-verification as "remaining" — all were **done
2026-06-27** per PHASE0_STATUS. §C items 1–4 remain valid but partially actioned (frontmatter
dates bumped 2026-07-03; stale sections still present). §C7 is resolved (`license =
"AGPL-3.0-only"` is in pyproject; the LICENSE *text* paste is still open — REMAINDER_PLAN C).

## F. New stale-doc register (2026-07-03) — ✅ all rows actioned 2026-07-05 (B2, PR pending)
| Doc | Staleness | Fix task | Status |
|---|---|---|---|
| `docs/SAFETY.md` | **Overstates shipped controls** (§1.5.2 strip step; §4.6 retention "applied"; §5.5 start-of-session disclosure; §3.5 "records severity"; §3.3 session-id/turn in escalation log) — worst-in-class because a safeguarding reviewer audits against it | A4, A3, A13, A14 | ✅ fixed (A3/A4/A13/A14) |
| `SECURITY.md` | Retention "is applied" — unimplemented | A4 | ✅ fixed (A4) |
| `docs/SESSION_FSM.md` | Claims a conformance test that doesn't exist; transition table missing auto-help, probe→help, LOW-severity continue, probe demote; `PARENT_ACK_WAIT` dead in code | A11 | ✅ fixed (A11) |
| `docs/ARCHITECTURE.md` | Module map missing `grounding/` + `web/`; phantom `pytest.ini`; CLI list missing `setup`/`run-session`; §2 claim "all output passes through the safety layer" false until A13 | B2 (+A13) | ✅ fixed (module map + CLI list updated; §2 claim now true post-A13) |
| `README.md` | Status section calls E2E loop + model eval "next milestones" (both done, pick made 2026-06-27); tree omits `grounding/`+`web/`; "150+ tests" (398) | B2 | ✅ fixed (Status reworded, tree updated, test count -> 450+) |
| `docs/EVAL_RESULTS.md` | last-updated 2026-06-16, still "front-runner" framing (pick made 2026-06-27); pipeline-safety 20/20 claim now predates several prompt re-hashes — needs run-date stamping | B2, A18 | ✅ fixed (frontmatter reworded; A18's re-run recorded in docs/MODEL.md) |
| `AGENTS.md` | Commands list omits `mentar eval` (RULES invariant added 2026-07-03) | B2 | ✅ fixed |
| `docs/SPEC.md` | §24 #14 (Cowork filesystem bridge "not running") — resolved, this review ran over it; §22 "connection details to be supplied" — supplied 2026-06-15; Appendix B delivery note stale | B2 (rows only) | ✅ fixed (all 3 rows) |
| `docs/PHASE0_STATUS.md` | "Test suite: 363 tests" section vs 398 in its own changelog; the §C1–C4 stale sections from June are still present | B2 | ✅ fixed (test count -> 455; §C1–C4 items already resolved in an earlier pass, confirmed still true) |
| `pyproject.toml` | Classifiers stop at 3.12 while RUNNING.md recommends 3.13 for libzim | B2 | ✅ fixed (3.13 classifier added) |
| `compliance/README.md` + `docs/llm-compatibility.md` | Not re-verified this pass — inherit §C8 "verify" status | (verify in B2) | ✅ verified — `compliance/README.md` not stale; `llm-compatibility.md`'s "pick pending" line updated to the actual 2026-06-27 pick |

**Not stale (checked):** `docs/MODEL.md` (post-pick, 2026-06-27), `docs/RUNNING.md` (2026-06-27),
`docs/CONTENT_LICENSES.md`, `docs/LICENSE_AUDIT.md`, `docs/PILOT_CONSENT.md`, `CONTRIBUTING.md`,
`docs/TESTS.md` (flat paths are a *documented* pre-src-layout convention — ARCHITECTURE §7),
`docs/TESTING_NOTES.md` (raw by design), `docs/design/*` (point-in-time records).

---

# Addendum — 2026-07-22 (post-R15/R-RES/graphify audit pass)

Full codebase audit using graphify (code graph), OKF frontmatter sweep, and grep. 717 tests passing at time of audit.

## G. Fixes applied 2026-07-22

| Doc | Staleness | Fix |
|-----|-----------|-----|
| `docs/ARCHITECTURE.md` | Module map last updated 2026-06-13; missing ~18 engine/safety/web/grounding sub-modules added after that date; pyBKT described as "wiring" in hot path (wrong — offline only); generate() signature outdated; HARDWARE.md filename wrong; import examples referenced non-existent classes | Module map expanded to cover all current modules; pyBKT wording corrected to "offline only (W3.3)"; inference abstraction section rewritten to match actual `backend.py` API; filename corrected to `hardware-requirements.md`; import examples fixed. Version bumped v0.1→v0.3, `last-updated` bumped to 2026-07-22. |
| `docs/SESSION_FSM.md` | S6/H5 state descriptions said "via pyBKT" (wrong — `engine/bkt.py`); status still "Draft — Pilot Pending" despite pilot being active | S6/H5 corrected to "Mentar's own deterministic BKT recurrence (`engine/bkt.py`)". Status changed to "Active — Pilot in progress". Version v0.2→v0.3, `last-updated` bumped. |
| `docs/TESTS.md` | T3.3 pre-condition said "PRE: pyBKT installed"; GOAL/CONTEXT described pyBKT API exploration; all superseded by the 2026-06-14 W3.3 decision | T3.3 rewritten to describe the actual implementation (`engine/bkt.py` deterministic recurrence, no pyBKT dependency). |
| `docs/SPEC.md` | §19.2 listed `pyBKT` as the BKT library with no offline-only caveat; glossary entry same; `HARDWARE.md` filename wrong | Both pyBKT references updated to distinguish hot-path (bkt.py) from offline-fit (pyBKT). Filename corrected. |
| `docs/LICENSE_AUDIT.md` | `pyBKT` listed as scope="core" (incorrect — not a runtime dependency) | Scope corrected to "offline eval only". |
| `docs/PHASE0_STATUS.md` | `last-updated: 2026-07-11` while changelog has entries through 2026-07-22 | Bumped to 2026-07-22. |
| `docs/MODEL.md` | `last-updated: 2026-06-27` while roster has entries added 2026-07-22 | Bumped to 2026-07-22. |
| `docs/REMAINDER_PLAN.md` | `updated: 2026-07-05`, header "status as of 2026-07-10" | Both bumped to 2026-07-22. |
| `README.md` | Test count said "450+" (actual 717) | Updated to "717+". |
| `docs/SPEC.md` | Status "Design Phase — Pilot Pending" despite pilot being active; Last Updated: "12 June 2026" | Status updated to "Pilot in progress (single-family supervised pilot)"; date bumped to 2026-07-22. |
| `docs/SAFETY.md` | Status "Draft — Pilot Pending"; `last-updated: 2026-07-10`; version v0.1 | Status updated to reflect pilot in progress + W2.2 gate still open; date bumped; version v0.1→v0.2. |

## J. Second-pass fixes (from multi-agent workflow scan, same date)

| Doc | Issue | Fix |
|-----|-------|-----|
| `docs/SESSION_FSM.md` | HELP_ELABORATE state in diagram+§3 but not §2 state table; unreachable BRANCH_DECISION→SESSION_END_BY_LEARNER Mermaid edge; probe trigger help-rate clause not implemented; counter table listed `probes_this_session`/`help_rate_window`/`modalities_used` with wrong field names; LINK_BACK sticking_point+parent-alert claimed as implemented (they aren't); LOW severity safety_trigger path undocumented; PROBE_CLASSIFY retry implied for all classes (only SLIP_SUSPECT); v0.3 changelog entry missing | All 8 corrected. Counter table fields aligned to `_SessionCtx` names; unimplemented design placeholders noted. LOW severity path added to pre-empts table. v0.3 changelog entry added. |
| `docs/MODEL.md` | `gemma4:12b` row said "eval queued" (evaluation was done — profile in §6); hardware-limited TODO note (full-GPU run had already resolved it); `qwen2.5:3b`/`qwen2.5:0.5b` in roster (ranks 7/8) but absent from candidate table | `gemma4:12b` row updated to reference actual eval results; TODO note updated to ✅ resolved; two missing models added to candidate table. |
| `docs/RUNNING.md` | `--runtime` flag listed `ollama\|llama_app\|gguf` (missing `auto` and `vllm`); `phi3.5` (not in roster) instead of `phi4-mini` | Fixed both. |
| `docs/PHASE0_STATUS.md` | "No CI" known-defect not marked ✅ RESOLVED (CI shipped as A12); Science visual templates row claimed "no science curriculum ships AT ALL" (wrong — `science.md`+`science_items.py` exist); R12 follow-up item (2) "Explain more unreproduced" not marked fixed | All 3 corrected. |
| `docs/design/UI_REQUIREMENTS.md` | Status "U-2a still pending" when §9 body documents U-2a as completed | Status updated to reflect completion; date bumped. |
| `docs/design/W3.3_bkt.md` | last-updated: 2026-06-14 contradicted by git history (last commit 2026-07-05) | Date corrected to 2026-07-05. |
| `docs/design/W7_grounding_reader.md` | last-updated: 2026-06-15 contradicted by git; status "Sonnet builds B1-B5" (B1+B2 are done) | Date corrected; status updated. |

## H. Confirmed not stale (2026-07-22)

- `docs/SAFETY.md` — W2.2 open items (handoff wording + emergency signposting) correctly marked as known gaps with a rollout guard; no overclaims (this row added after the status-only bump above).
- `docs/design/W2.2_escalation.md`, `docs/design/W6.3_pilot_interface.md` — point-in-time design records, not living docs.
- `REMAINDER_PLAN.md` R2–R15 + R-RES + R-MC task entries — all accurately reflect shipped/open states.
- `curriculum/visual_scaffolds/` — frontmatter timestamps consistent with build dates.
- `prompts/README.md` — hashes match current prompt files.

## I. Open / not fixed (design decisions, out of scope for a doc-only pass)

- `docs/PHASE0.md` W2.2 professional-review gate — still open by design; noted in SECURITY.md + README.md (correct).
- `docs/TESTS.md` T3.4 (false-confidence classifier) — the test spec references a W3.4 decision table that exists; test implementation path `tests/engine/test_probe_classify.py` needs verification on next test-suite audit.
- `docs/SPEC.md` §24 overall — verified not to overclaim; open §24 items are tagged "Open" or "Pilot path live". No false "done" claims found.
- `docs/SESSION_FSM.md` — LINK_BACK `sticking_point` flag + parent-alert row: design placeholder, not implemented. Documenting the gap is the right call; building it is a separate task.
- `docs/SESSION_FSM.md` — `probe_frequency_cap` (W2.4) and help-rate probe clause (W5.3): not implemented. Noted in doc but not built; needs a design decision before implementation.
- `compliance/` — `docs/research/compliance/australia.md` is referenced in `compliance/README.md` but the file does not exist. Low-risk gap (compliance/ is supplementary); log for next audit.
- `docs/PHASE0_STATUS.md` line counts (W2.1/W2.2/W3.6/W6.1/W6.2/W7) in ✅-done rows are point-in-time delivery snapshots — files have grown since delivery. Not corrected (historical record, not overclaims).

## K. OKF spec-compliance correction (2026-07-23)

**§H's earlier claim above ("curriculum/visual_scaffolds/ — frontmatter timestamps consistent")
was true but incomplete** — it checked concept-file timestamps only, never verified the actual
[OKF v0.1 spec text](https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md)
against `index.md` files. When asked to properly verify OKF compatibility, fetching the real spec
found: **§6 requires `index.md` to carry NO frontmatter at all** (not just "no `type:` field," which
is what an earlier pass in this repo had assumed). Every `index.md` in `curriculum/templates/` (5)
and `curriculum/visual_scaffolds/` (4) had frontmatter — a real, repo-wide violation that predates
this session and was never caught because verification was pattern-matched against existing files
rather than the spec itself.

**Fixed 2026-07-23:**
- Stripped frontmatter from all 9 pre-existing `index.md` files (descriptions folded into body prose).
- Converted `docs/` into a full OKF bundle per maintainer request: `docs/README.md` → `docs/index.md`
  (README isn't a reserved name, so it wasn't fulfilling the manifest role correctly); added
  `docs/design/index.md` and `docs/research/compliance/index.md`; `docs/research/compliance/README.md`
  → `overview.md` (converted to a proper concept file with `type: Mentar Compliance Research`).
- Added `type:` (the one required OKF field) to all 18 `docs/` concept files, all 22
  `docs/design/` files, and all 5 `docs/research/compliance/` files — 7 of these had zero frontmatter
  and needed a full block added (description/tags/timestamp derived from existing content).
- **Regression caught by the test suite**: `tests/engine/test_template_catalog.py::test_no_skill_id_collides_across_any_shipped_template`
  globbed `**/*.md` without excluding `index.md`/`log.md` (unlike its sibling test in the same file,
  and unlike `web/app.py`'s discovery code, both of which already exclude them correctly). This was
  a latent bug masked by index.md's stray frontmatter (parsed as an empty-`concepts:` dict by
  accident); stripping the frontmatter correctly exposed it as an `AttributeError`. Fixed by adding
  the same exclusion. All 717 tests green after the fix; `ruff check .` shows only 2 pre-existing,
  unrelated errors (not touched this session).
- Added an "OKF documentation bundles" section to `AGENTS.md` (after Project layout) so future doc
  creation/edits in `docs/`, `curriculum/templates/`, `curriculum/visual_scaffolds/` reference the
  spec's two hard rules directly, instead of re-deriving them by inference each time.

**Lesson, stated plainly:** "I confirmed X is spec-compliant" is only true if the spec was actually
read. Pattern-matching against sibling files that may themselves be non-compliant produces false
confidence — this is exactly what happened in the 2026-07-22 pass above.
