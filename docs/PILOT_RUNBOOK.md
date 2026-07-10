---
title: "Mentar — Pilot Runbook"
version: v0.1
status: "Draft — checklist not yet run against a real session"
last-updated: 2026-07-10
scope: "Operational runbook for the supervised single-family Phase-0 pilot ONLY. Not a general deployment guide (see RUNNING.md for that)."
sources: "PHASE0.md §26.7 (P1–P5 verbatim, thin overlay); REMAINDER_PLAN.md §C (maintainer-only checklist); PILOT_CONSENT.md; SAFETY.md; docs/RUNNING.md"
---

# Pilot Runbook

Thin overlay, same convention as `PHASE0_STATUS.md`: task IDs and criteria are never
duplicated from `PHASE0.md` — only status and pointers live here. Two parts: a
**pre-session-1 checklist** (hard gates before the first real session) and a **per-session
procedure** (what to do each time the pilot runs).

---

## 1. Pre-session-1 checklist

Every row here is a hard gate — **do not run session 1 until all are checked**, per
`REMAINDER_PLAN.md` §C (the maintainer-only rows that no amount of local build work can
close).

| # | Gate | Status as of 2026-07-10 | Source |
|---|------|--------------------------|--------|
| 1 | **`PILOT_CONSENT` signed** by the parent before session 1 | ⏳ not yet — do this last, right before session 1 | [`docs/PILOT_CONSENT.md`](PILOT_CONSENT.md) |
| 2 | **AGPL-3.0 full text pasted into `LICENSE`** | ⏳ open (gnu.org unreachable from the build sandbox — needs a human fetch) | `REMAINDER_PLAN.md` §C |
| 3 | **Eval-host token rotated** | ⏳ open — maintainer action, not codeable | `REMAINDER_PLAN.md` §C |
| 4 | **Safeguarding professional review** — handoff wording + child-facing emergency signposting | ⏳ open. Automated harness exists (`safety/handoff_check.py`), but the human review this pilot's SAFETY.md scope depends on has not happened. **This is the highest-stakes unclosed gate** — it's what keeps the pilot scoped to "supervised single-family," not broader rollout. | `SAFETY.md` §3.1/§5.2 (Bucket D); `docs/design/W2.2_signposting_decision_prep.md` |
| 5 | **Explicit-harm + iterative-jailbreak red-team decision** | ⏳ open — needs promptfoo Cloud or an uncensored+capable generator (local 7B models were too weak; aligned-Claude refuses to play the adversarial role). Decision + setup, not yet run. | `REMAINDER_PLAN.md` §C |
| 6 | **ZIM grounding source reachable** | ✅ done — pilot re-pointed to Khan Academy (B1, 2026-07-05), `khanacademy_en_all_2023-03.zim`, already mounted read-only. Verify before session 1 that the *same host* still has it mounted: `ls $MENTAR_ZIM_DIR/khanacademy_en_all_*.zim` (or wherever `config/inference.yaml`'s `grounding.zim_dir` points). | `docs/CONTENT_LICENSES.md` §1; `config/inference.example.yaml` |
| 7 | **Backend self-verify passes** | Run before every session, not just once — see §2 below. | `scripts/check_backend.py` |
| 8 | **Retention policy understood by the parent** | ✅ docs are accurate (ratified 2026-07-04: pilot retains everything; deletion = delete the `.db` file — no purge mechanism exists or is promised). Make sure this is communicated when consent is signed (#1), not assumed. | `SAFETY.md` §4.6; `SECURITY.md` |
| 9 | **`mentar backup` understood** | ✅ tooling exists (`./mentar backup`) — decide a backup cadence for the pilot (e.g. after each session) before session 1, not during it. | `AGENTS.md` Commands |

**Compliance wording (COPPA 2025 / GDPR-K) against public docs** is a known separate open
item — the docs no longer *overclaim*, but a formal compliance-language pass hasn't been
done. Not a hard gate for a supervised single-family pilot (no public rollout), but flagged
here so it isn't lost — see `REMAINDER_PLAN.md` §C.

---

## 2. Per-session procedure

**Before every session (not just the first):**
1. `./scripts/check_backend.py` (or let `mentar setup`/`mentar serve` do it — both self-verify
   the backend responds before declaring ready).
2. Confirm the parent is present and available for the session's duration (parent-mediated
   mode — SPEC §6.2 — is the only supported mode; the app itself asserts this at startup and
   refuses otherwise).
3. `./mentar serve` (or `./mentar run-session` for a terminal-only session, per
   `docs/RUNNING.md`).

**During the session:**
- The child sees the assent line ("you can stop anytime, just say 'stop'") and the AI-
  transparency line ("I'm Mentar, a computer learning helper — not a person") once, at the
  start — this is automatic, nothing to trigger manually.
- If an escalation fires, the child's screen shows only the two fixed handoff messages
  (`/frozen`) — the parent resumes via `/parent` (typed URL only) + the `RESUME` confirm word.
  This is also automatic; the runbook's job here is just: **know that `/parent` is the
  resume path**, don't go looking for a resume button on the child's screen.

**After the session:**
1. `./mentar backup` — checkpoint + copy + verify the DB. Keep the backup; don't rely on the
   live `.db` file alone.
2. Review the session via `/parent` (safety alerts first, then summary/mastery/answers, then
   the collapsed full transcript) — this is also where P1–P5 evidence gets recorded (§3).
3. Note anything qualitatively off (frustration spirals, a re-explanation that felt wrong,
   an escalation that shouldn't have fired) even if no threshold was crossed — P3's "parent
   reviews 100% of generated re-explanation variants" is a real per-session task, not just a
   pass/fail gate.

---

## 3. P1–P5 — what to record, and where

IDs and full criteria are defined in `PHASE0.md` §26.7 — not duplicated here. This table is
only "what evidence to capture, using what's already in the app," so a maintainer running
the pilot doesn't have to re-derive it each session.

| ID | What to record | Where to find it |
|----|-----------------|-------------------|
| **P1** Adaptive traversal | Which nodes were visited, in what order, across the pilot's sessions (≥6 of 8 fractions nodes via fringe selection, no manual sequencing — there's no manual-sequencing control in the UI to begin with, so this is really "did the child reach ≥6 nodes") | `/progress` concept-graph map (mastered/learning/not-started per node) + `/parent`'s per-skill mastery table, checked cumulatively across sessions |
| **P2** Help loop closure | Every Help press → a different-modality re-explanation → a mandatory transfer re-check → a BKT update with the hinted-win discount | `/parent`'s Answers table (🆘 marks help-assisted answers) + the full transcript (collapsed `<details>`) for the modality-variety detail |
| **P3** Guardrail stress | 100% of generated (non-bank) re-explanation variants reviewed by the parent; 0 uncaught wrong explanations | Full transcript in `/parent`, reviewed manually each session (this is the one P-task without an automatic pass/fail counter in the UI — it's a human review requirement) |
| **P4** Proactive probing | Probe count, class distribution (per W3.4), baseline false-confidence rate | `escalation_log`/`response_log` via the DB directly (no dedicated UI view yet — `sqlite3 mentar_pilot.db "SELECT * FROM response_log WHERE ..."` or a future `/parent` addition) |
| **P5** Safety layer live test | ≥3 scripted (adult-injected) test inputs trigger correctly, zero unlogged triggers | `/parent`'s Safety alerts table (verbatim trigger text, acknowledged status) cross-checked against the scripted list the maintainer typed in |

**G1 pass thresholds** (≥90% Help-loop completion, 0 uncaught wrong explanations, ≥1
detected `false_confidence` event, 100% scripted escalation triggers handled, no
qualitative frustration spiral) are defined in `PHASE0.md` §26.7 verbatim — read them there
before judging pass/fail, don't rely on a paraphrase.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-10 | v0.1 — first draft (D5, post-release-wave gap sweep). Checklist not yet run against a real session; P1–P5 recording guidance not yet validated end-to-end. |
