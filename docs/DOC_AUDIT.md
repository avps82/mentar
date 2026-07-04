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
