# Documentation Audit — 2026-06-26

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
