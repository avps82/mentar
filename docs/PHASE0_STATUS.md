---
title: "Mentar — Phase 0 Status"
version: living-doc
status: "Active"
last-updated: 2026-06-14
---

# Phase 0 — Status

Single-page status tracker for the W1–W6 entry tasks and the P1–P5 pilot-execution tasks
defined in [PHASE0.md](PHASE0.md). Updated as work lands; the W/P task IDs match PHASE0.md
exactly, so this doc is a thin overlay — never duplicate text from PHASE0.md, only status.

**Legend:** ✅ done · ⏳ pending · 🔭 watch (not G0-blocking) · 🚫 blocked

---

## Gate snapshot

| Gate | Meaning | Status |
|------|---------|--------|
| **G0 — Pilot-ready** | All entry tasks done; pilot may begin | 🚫 blocked on: **W1.2–W1.3** (eval-host run — needs gaming PC) · W5.6 (needs Pradeep's distress/runway thresholds) · W3.5 (desk verdict done; optional hands-on spike) |
| **G1 — Pilot-complete** | P1–P5 thresholds met | gated on G0 |
| **G2 — Phase 1 entry** | Go/no-go on OSS Local Edition build | gated on G1 + W4.2 + W5.4 + W5.5 + W5.7 |

---

## W1 — Local LLM Selection

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W1.1 eval host | ✅ | Gaming PC, vLLM, 10GB vRAM — per SPEC §20.3 |
| W1.2 candidate eval | ⏳ | T1 suite scaffolded inline; needs eval host run |
| W1.3 selection + pick | ⏳ | Produces `docs/MODEL.md` |
| W1.4 hardware tier mapping | ⏳ | Backend-dependent; needs W1.3 |
| W1.5 abstraction layer v0 | ✅ | DECIDED (pluggable backends, SPEC §20.1); code stub at `src/mentar/inference/` |
| W1.6 hardware horizon watch | 🔭 | Not G0-blocking; quarterly review |

---

## W2 — Safety Spec

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W2.1 SAFETY.md v0.1 | ✅ | `docs/SAFETY.md` (692 lines, 6-layer) |
| W2.2 Bucket D interim escalation | ✅ | `src/mentar/safety/escalation.py` (classify + handle_trigger; 220 lines) + `tests/safety/test_escalation.py` (20+20 fixtures, flow tests; 390 lines). All 20 positives fire with correct class; all 20 negatives silent; jailbreak=logged_only; escalation_log row written with untruncated verbatim text. Rollout guard intact: emergency signposting + handoff wording validation both remain required before any rollout beyond single-family pilot. Bucket D supersedes trigger list post-pilot. |
| W2.3 RAG/injection threat model | ✅ | SAFETY.md L1 §1.5 |
| W2.4 probe Art. 5 justification | ✅ | SAFETY.md L2 §2.7 |
| W2.5 pilot consent note | ✅ | `docs/PILOT_CONSENT.md` — signable template (local-only data, parent present, escalation-route-to-parent limitation called out, right to stop). **Must be signed before session 1.** |
| W2.6 parent-mediated mechanism | ✅ | DECIDED (honor + PIN phased); recorded in SPEC §6.2 + SAFETY.md L5 |

---

## W3 — Pedagogy Engine

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W3.1 template→graph schema | ✅ | `curriculum/_template.md` + validator at `src/mentar/tools/validate_template.py` |
| W3.2 pilot concept graph | ✅ | `curriculum/templates/_pilot/fractions.md` (8 nodes, DAG verified) |
| W3.3 BKT cold-start + hinted-win | ✅ | `src/mentar/engine/bkt.py` (deterministic recurrence) + `docs/design/W3.3_bkt.md`. Hinted-win = elevated-guess class; cold-start priors hand-set by node class; pyBKT scoped OUT of hot path → offline fit only. 7 invariants verified numerically. SPEC §11 updated. **Remaining (Sonnet):** formal `tests/engine/test_bkt.py` (T3.3) + caller wiring in FSM `bkt_update`. |
| W3.4 false-confidence classifier | ✅ | `src/mentar/engine/probe_classify.py` (decision table, 7 cases smoke-verified) + SPEC §14.4 (definition + table). Forgetting checked before false_confidence; false_confidence only when both-fail ∧ mastery≥threshold ∧ no-Help. Remaining (Sonnet): formal T5.x tests + caller wiring of stale-mastery window from `skill_state.updated_at`. |
| W3.5 Open TutorAI build-vs-adopt | 🟡 | **Verdict: REFERENCE-ONLY** (don't fork) — `docs/design/W3.5_build_vs_adopt.md` + SPEC §19.2. Desk assessment (no sandbox web); §5 lists a hands-on spike to confirm. Unblocked W6.3. |
| W3.6 learner data model | ✅ | `src/mentar/db/schema.sql` (202 lines) + `store.py`; triggers verified |

**Bonus** (W3-adjacent, ahead of schedule):

| Test | Status | Artifact |
|------|--------|----------|
| T3.1 validator | ✅ | Smoke + 5 negative cases pass |
| T3.2 fringe selection | ✅ | `src/mentar/engine/fringe.py` — all 5 T3.2 cases verified |
| T1.3 / T3.5 verifier | ✅ | `src/mentar/eval/verify_numeric.py` — decimal SAFE_REJECT bug found + fixed |
| T3.6 SQLite | ✅ | Schema loads, triggers enforce immutability, FKs work |

---

## W4 — Licensing & Naming

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W4.1 pilot content licence audit | ✅ | `docs/CONTENT_LICENSES.md` — Vikidia (CC BY-SA 3.0) + Simple English Wikipedia (CC BY-SA 4.0) CLEARED for local pilot w/ attribution+share-alike notes; Khan CC BY-NC-SA logged as Phase-3 hosted-tier conflict (SPEC §24 #18). |
| W4.1b name "Mentar" check | ✅ | Clear on GitHub/npm/PyPI; **namespace reservation still pending — Pradeep** |
| W4.2 OSS licence + trademark | ⏳ | G2 blocker, not G0 |

---

## W5 — Spec Hygiene & Decisions

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W5.1 UX moat decide-or-rewrite | ✅ | Option B taken — UX deferred to Phase 1 |
| W5.2 23/24 SAFETY.md cross-ref | ✅ | SPEC §23 anchors "safety layer active" to SAFETY.md v0.1 (W2.1) + W2.2 escalation; §24 row #6 updated to "pilot path live; Bucket D open". Contradiction resolved. |
| W5.3 pilot defaults from placeholders | ✅ | SPEC §21 TBDs promoted to **pilot default (v0)**: pattern mix 40/30/30, Help retry cap 3, mastery threshold 0.85 (matches `engine/fringe.py`), + new Probe-cadence row (every 5 items OR mastery≥0.85 ∧ Help-rate<1/10). All revisable post-pilot. |
| W5.4 COPPA post-April-2026 check | ⏳ | G2 blocker, not G0 — verify |
| W5.5 phase effort estimates | ⏳ | After G0 tasks scoped |
| W5.6 kill criteria + scope-cut order | 🟡 | **Drafted in SPEC §25.1–25.2** (criteria a–e + ordered cut list + never-cut bar). ⏳ Needs Pradeep: (c) distress threshold (default proposed) + (e) optional personal time/€ runway line. Otherwise complete. |
| W5.7 data flywheel posture | ⏳ | G2 decision (24 #16) |

---

## W6 — Core Design Artifacts

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W6.1 session state machine | ✅ | `docs/SESSION_FSM.md` (188 lines, Mermaid + transition tables) |
| W6.2 prompt template registry | ✅ | `prompts/` — 10 versioned templates (3 patterns + 5 Help modalities + transfer-gen + system prompt) + `PROMPTS.md` registry. Hashing convention documented; **T4.6-equivalent check PASSES** (10/10 body hashes match registry + headers). Remaining (Sonnet): formal `tests/test_prompt_registry.py` (T4.6) + controller load-wiring. |
| W6.3 pilot interface decision | ✅ | **Decided: minimal local web app** (Flask/FastAPI localhost, 4 views). `docs/design/W6.3_pilot_interface.md` + SPEC §23. Fork ruled out by W3.5; TUI rejected. |
| W6.4 repo architecture sketch | ✅ | `docs/ARCHITECTURE.md` (149 lines, src-layout) |

---

## Repo scaffolding (cross-W)

| Artifact | Status |
|----------|--------|
| `pyproject.toml`, `.gitignore`, `pytest.ini` | ✅ |
| `src/mentar/` package skeleton (engine, dialogue, safety, inference, eval, tools, cli, db) | ✅ stubs in place |
| `tests/` mirroring `src/`, smoke test passes (modulo pytest install) | ✅ |
| `prompts/`, `reports/`, `eval/` top-level dirs | ✅ empty, ready |
| TESTS.md path-translation note (src-layout vs flat) | ✅ |

---

## Tests written but not yet runnable as a suite

The sandbox has no `pip` / `pytest`. PyYAML was vendored under `.vendor/` for runtime checks
of the validator/fringe; full pytest runs need `pip install -e ".[dev]"` from a real shell.

| Test file | Lines | Inline smoke check |
|-----------|-------|--------------------|
| `tests/tools/test_validate_template.py` | 283 | 5 negative cases + pilot template ✅ pass |
| `tests/eval/test_verify_numeric.py` | 265 | 10 hand-picked cases ✅ pass (after decimal bug fix) |
| `tests/engine/test_verifier.py` | 193 | not run; depends on T3.5 integration |
| `tests/db/test_datamodel.py` | 391 | schema load + trigger E2E ✅ pass |
| `tests/engine/test_fringe.py` | 200 | 5 T3.2 cases ✅ pass |
| `tests/safety/test_escalation.py` | 689 | 20+20 T2.1 fixtures + flow ✅ pass (re-verified) |

**Verified inline but no formal test file yet** (pending Sonnet): `src/mentar/engine/bkt.py`
(7 invariants verified numerically, T3.3) and `src/mentar/engine/probe_classify.py`
(7 decision-table cases verified, T5.x).

---

## Next batch (immediately actionable)

**Needs Pradeep (G0):**
- **W5.6** — confirm the (c) distress threshold + optional (e) personal time/€ runway line in SPEC §25.1 (defaults proposed; just say yes or give numbers).
- **W1.2 → W1.3** model eval/selection — needs the gaming-PC eval host run; not doable in sandbox.
- **W4.1b** — reserve `mentar` namespace (npm + PyPI placeholder publish).

**Doable autonomously next (Sonnet grunt):**
1. **T1.1 eval dataset** — 50 + 30 + 20 prompts; needed before the eval-host run.
2. **Dialogue controller** — wire the W6.2 prompts + FSM + engine modules into the turn loop (the dialogue framework T4/T5 assume).
3. **Pilot web app** (W6.3 build) — Flask/FastAPI + the 4 views.

**Test/wiring follow-ups (not G0-blocking, Sonnet):** formal `tests/engine/test_bkt.py`
(T3.3), `tests/engine/test_probe_classify.py` (T5.x), `tests/test_prompt_registry.py` (T4.6);
FSM caller wiring for `bkt.py`, `escalation.py` (handle_trigger), `probe_classify.py`
(stale-mastery window from `skill_state.updated_at`); full `pytest` once `pip install -e ".[dev]"`.

**Test/wiring follow-ups (not G0-blocking, Sonnet):** formal `tests/engine/test_bkt.py`
(T3.3) and `tests/engine/test_probe_classify.py` (T5.x); FSM caller wiring for `bkt.py`,
`escalation.py` (handle_trigger), and `probe_classify.py` (stale-mastery window from
`skill_state.updated_at`); full `pytest` run once `pip install -e ".[dev]"` is available.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-13 | Initial. Reflects work landed in the 13 Jun build session. |
| 2026-06-14 | W2.2 design frozen — `docs/design/W2.2_escalation.md` (Opus). Pins escalation module contract + 2 interim safety decisions (emergency signposting, handoff wording) w/ rollout guard; SAFETY.md §3.5 updated. Unblocks Sonnet impl of `escalation.py` + T2.1. |
| 2026-06-14 | W3.3 ✅ (Opus) — `src/mentar/engine/bkt.py` + `docs/design/W3.3_bkt.md`. Deterministic BKT recurrence, hinted-win = elevated-guess class, hand-set cold-start priors; pyBKT scoped to offline fit only. 7 invariants verified numerically; SPEC §11 corrected. Unblocks W3.4. Remaining: T3.3 test file + FSM caller wiring (Sonnet). |
| 2026-06-14 | W2.2 ✅ (Sonnet) — `src/mentar/safety/escalation.py` + `tests/safety/test_escalation.py` + schema.sql comment (logged_only). All 20+20 T2.1 fixtures verified via inline smoke check. Trigger→freeze→alert path demonstrated with real in-memory SQLite. Two rollout guards (emergency signposting + handoff wording validation) remain load-bearing. |
| 2026-06-14 | W5.2 ✅ (Opus) — resolved §23/§24 safety contradiction. SPEC §23 anchors "safety layer active" to SAFETY.md v0.1 + W2.2; §24 row #6 updated to reflect the live pilot escalation path (Bucket D open for post-pilot refinement). |
| 2026-06-14 | W5.3 ✅ (Opus) — SPEC §21 placeholders promoted to pilot default (v0): pattern mix 40/30/30, Help retry cap 3, mastery threshold 0.85, + Probe-cadence row. |
| 2026-06-14 | W3.4 ✅ (Opus) — `src/mentar/engine/probe_classify.py` + SPEC §14.4 false-confidence decision table; 7 cases smoke-verified. |
| 2026-06-14 | W4.1 ✅ (Opus) — `docs/CONTENT_LICENSES.md`; pilot sources (CC BY-SA) cleared, Khan NC conflict logged (§24 #18). |
| 2026-06-14 | W2.5 ✅ (Opus) — `docs/PILOT_CONSENT.md` signable consent template; required before session 1. |
| 2026-06-14 (overnight) | W6.2 ✅ (Opus, after cloud routine failed on private-repo access) — 10 versioned templates in `prompts/` + `PROMPTS.md` registry; hashing convention documented; T4.6-equivalent check passes 10/10. |
| 2026-06-14 (overnight) | W3.5 🟡 (Opus) — verdict REFERENCE-ONLY (desk assessment); `docs/design/W3.5_build_vs_adopt.md` + SPEC §19.2. |
| 2026-06-14 (overnight) | W6.3 ✅ (Opus) — pilot interface = minimal local web app (4 views); `docs/design/W6.3_pilot_interface.md` + SPEC §23. |
| 2026-06-14 (overnight) | W5.6 🟡 (Opus) — kill criteria + scope-cut order drafted in SPEC §25.1–25.2; awaits Pradeep's distress/runway thresholds. |
| 2026-06-14 (overnight) | Docs hygiene — rewrote stale `README.md` to match real src-layout; created `compliance/README.md` (coverage-status map per SPEC §17.5). |
