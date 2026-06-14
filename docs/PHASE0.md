# 26 — Phase 0 Entry Plan & Task List
*Source: plan review session, 2026-06-10 | Last updated: 2026-06-12. Status: ACTIVE. Supersedes the implicit sequencing in 25 Phase 0.*

> **Purpose.** 23 defines the pilot's pedagogical scope; this section defines what must be TRUE before the pilot starts (Gate G0), what runs during it (Gate G1), and what each task's exit criterion is. Three sequencing inversions from the review are corrected here: (1) local-LLM selection moves AHEAD of the pilot; (2) a minimal SAFETY.md + Bucket D escalation flow moves AHEAD of any session with a real child; (3) the UX-moat claim (4) gets an explicit decide-or-rewrite task.

> **Decisions resolved 2026-06-11 (this update):**
> - ✅ **W1.1** Eval host = gaming PC (10GB vRAM, vLLM). → 20.3
> - ✅ **W1.5** Model layer = **pluggable backends** (local Ollama default; own vLLM / Gemini / Claude opt-in, parent owns key). → 20.1
> - ✅ **W2.6** Parent-mediated mechanism = Phase 0 honor system + transcript log; Phase 1 PIN gate. → 6.2
> - ✅ **W4.1b** Name "Mentar" clear on GitHub/npm/PyPI — keep it. ⏳ namespace reservation pending (Pradeep).
> - ✅ **W5.1** UX moat → Option B: dropped from Phase 0 moat, deferred to Phase 1. → 4.1
> - 🔭 **W1.6** Hardware + backend-integration watch added (NVIDIA *consumer* RTX Spark / AMD Strix Halo / Apple MLX) — forward-looking, not G0-blocking; deliverable = per-backend integration-effort matrix. → 20.4
> - ⏳ Still open (G0): W1.2–W1.3 (model eval/pick), W2.1–W2.5 (safety spec), W3.1–W3.6 (pedagogy foundations), W4.1 (content licence audit), W5.2–W5.3 (spec hygiene).
>
> **Added 2026-06-12 (reconciliation pass):**
> - ➕ **W6 workstream** (26.6A) — core design artifacts: session state machine (W6.1, owns 24 #7), versioned prompt set (W6.2), pilot interface decision (W6.3), repo sketch (W6.4). W6.1–W6.3 G0-blocking. Tests: T3.7, T4.6.
> - ➕ **W5.6** kill criteria + scope-cut order (G0, small).
> - ➕ **W5.7** data-flywheel posture decision (G2) — resolves new 24 #16 (local-first vs learn-from-usage tension in 10 + 15).
> - 🔧 Spec 11 hinted-win overclaim corrected in-place; spec 24 rows #2–4/7/13 refreshed; 24 #16–17 added.

---

## 26.1 Gate Structure

| Gate | Name | Meaning | Blocking tasks |
|------|------|---------|----------------|
| **G0** | Pilot-ready | All entry tasks done; pilot may begin | W1.1–W1.3, W2.1–W2.4, W3.1–W3.4, W4.1, W5.1–W5.3, W5.6, **W6.1–W6.3** |
| **G1** | Pilot-complete | Pilot success criteria (26.7) evaluated against thresholds | P1–P5 |
| **G2** | Phase-1 entry | Go/no-go on OSS Local Edition build | G1 pass + W4.2, W5.4, **W5.7** |

Task ID convention: `W{workstream}.{n}` = entry task; `P{n}` = pilot-execution task. Each task lists: **Dep** (dependencies), **Exit** (binary completion criterion), **Ref** (spec section it modifies/feeds).

---

## 26.2 Workstream W1 — Local LLM Selection (was TODO #2–4, 20; now G0-blocking)

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W1.1 | ✅ **DONE (2026-06-11).** Eval environment = **Pradeep's gaming PC, 10GB vRAM, serving via vLLM** (already configured + running, reachable). CT 114 cannot run eval. 10GB sufficient for ≤14B candidates. Box/connection details supplied at eval time. *(Rejected: cloud burst, Mac — local GPU already on hand.)* | — | ✅ Eval host live; vLLM serving | 20.3 |
| W1.2 | **Candidate shortlist + eval harness.** Shortlist 3–5 OSS models ≤14B (instruct-tuned; candidates to confirm at eval time, e.g. current Llama/Qwen/Phi/Gemma small variants). Build a fixed eval set: ≥50 fraction re-explanation prompts (one per 13.2 modality per pilot node) + ≥30 transfer-question generation prompts + ≥20 adversarial/jailbreak prompts (child-voice). Score: factual correctness (deterministic check where numeric), age-appropriateness, instruction adherence, refusal correctness. | W1.1 ✅ | Scored comparison table exists; ≥1 model meets thresholds in W1.3 | 20 #1 |
| W1.3 | **Selection thresholds + pick.** Minimum bar (initial, revisable): ≥95% numeric correctness on deterministic-checkable items; 0 hard safety failures on adversarial set; subjective age-appropriateness pass ≥90%. Pick primary model + 1 fallback. | W1.2 | `MODEL.md` records: chosen model, quantisation, thresholds met, fallback | 20 |
| W1.4 | **Hardware tier mapping** (was TODO #3). *Backend-dependent (per 20.1 decision):* for the **local Ollama** default, measure chosen model's RAM/CPU/GPU floor at usable latency (<10s per re-explanation suggested) and publish min-spec table (8GB/16GB/GPU tiers ↔ model/quant). For own-vLLM-cluster or cloud-API backends, hardware = parent's responsibility (cloud = internet + key only). | W1.3 | Min-spec table in `MODEL.md` for local backend; pilot hardware confirmed against it | 20 #2 |
| W1.5 | **Model abstraction layer v0 — PLUGGABLE BACKENDS** (was TODO #4; expanded 2026-06-11). Thin interface: `generate(prompt, grounding_passages, constraints) → text`, backend-agnostic. Backends: **local Ollama/llama.cpp (default)**, parent's own vLLM cluster, Gemini API (opt-in, parent owns key), Claude API (opt-in, parent owns key). Swappability = config + env var only, no code change. Cloud opt-in ⇒ parent is operator/controller for that data flow (17.2, 20.1). | W1.3 | ≥2 backends (local default + 1 other) run behind the same interface in a smoke test; backend switch is config-only | 20.1, 20 #3 |
| W1.6 | 🔭 **Hardware-horizon + backend-integration WATCH (forward-looking; NOT G0-blocking — re-verify quarterly).** Two linked questions: *what local hardware will parents have*, and *how much code does each backend actually need*. **Hardware snapshot (2026-06, [⚠️ Verify — fast-moving]):** **NVIDIA RTX Spark** = the *consumer* box (GB10-derived, 20-core Arm + Blackwell ≈ RTX 5070, 128GB unified, 1 PFLOP, ~120B local, ~1M ctx); **Windows-on-Arm**; Surface Laptop Ultra + Asus/Dell/Lenovo/HP/MSI; **ships ~Q3/fall 2026, no pricing.** (DGX Spark/Station = dev tier, already out, ~$4–5k — reference only, NOT the consumer target.) **AMD Strix Halo / Ryzen AI Max+ 395** (128GB unified, $1.5–3.3k, runs 70B, x86) → Ryzen AI Halo box ~Jun 2026 → Gorgon 2026 → Medusa Halo 2027. **Apple** = open *in principle* but **integration cost unknown** — system on-device model is Swift-only; Python route = MLX (`mlx-lm`) / OpenAI-compatible MLX server, NOT Apple's system model directly. **Deliverable = per-backend integration-effort matrix**, classifying each as: *drop-in* (OpenAI-compatible HTTP, no Mentar code) / *shim* (thin adapter in the W1.5 layer) / *native-code-needed* (e.g. Swift glue for Apple system model). Must also verify: (a) does the Python stack (Ollama/llama.cpp/vLLM) run **natively on Windows-on-Arm** for RTX Spark, or only via x86 (Prism) emulation, and at what latency; (b) how open Apple actually is for a non-Swift caller. **Action:** maintain `docs/HARDWARE.md`; fold confirmed tiers into W1.4 min-spec; no purchase decision for pilot. | — | `docs/HARDWARE.md` exists with: 3-vendor consumer-hardware snapshot + **per-backend integration-effort matrix** + Win-on-Arm + Apple-openness verify lines + re-verify date | 20.4, 20 #2, 20.1 |

*Note: W1.4–W1.5 are G0-desirable but only W1.1–W1.3 are G0-blocking; pilot can run on the eval host if min-spec work lags.*

---

## 26.3 Workstream W2 — Minimal Safety Spec (G0-blocking if pilot learner is a real child)

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W2.1 | **SAFETY.md v0.1 draft.** Write the 6-layer skeleton (16.0) with Layers 1, 2, 4, 5, 6 populated from existing 15–16 content. Mark Layer 3 sections as v0.1-interim pending Bucket D. | — | `docs/SAFETY.md` exists; every 16.1–16.3 requirement maps to a layer section | 16.0, TODO (Appendix B) |
| W2.2 | **Bucket D minimum-viable escalation flow.** Full Bucket D research can continue post-pilot, but pilot needs an interim rule set: (a) distress/disclosure keyword+classifier trigger list; (b) on trigger → freeze tutoring, show fixed child-appropriate handoff message, alert supervising parent (pilot = parent physically present, so alert = on-screen flag + log entry); (c) NEVER continue the session past a trigger without parent acknowledgment; (d) all triggers logged verbatim for review. | W2.1 | Interim escalation rules written into SAFETY.md Layer 3; trigger→freeze→alert path demonstrated in a scripted test | 16.3, Bucket D |
| W2.3 | **RAG/content injection threat model** (new — review finding). Add to SAFETY.md Layer 1: prompt-injection via Kiwix passages and parent-uploaded question banks; child-initiated jailbreak attempts. Mitigations v0: instruction/data separation in prompts (grounding passages wrapped as quoted data, never as instructions); strip/flag imperative-to-AI text in retrieved passages; adversarial child-voice prompts included in W1.2 eval set. | W2.1 | Threat-model subsection exists; W1.2 adversarial set includes ≥5 injected-passage cases | 16 L1, 15 |
| W2.4 | **Proactive-probe Art. 5 justification note.** One-paragraph SAFETY.md entry: why non-skippable probes are pedagogical necessity, not engagement/dark-pattern mechanics (bounded frequency, no streaks/rewards, parent-visible, parent can cap frequency). Add probe-frequency cap to 21 parent config. | W2.1 | Justification paragraph in SAFETY.md; `probe_frequency_cap` row added to 21 | 14.2, 16.2, 21 |
| W2.5 | **Pilot consent & ethics note** (if pilot learner is a real child). Written parental consent; parent physically present (under-13 ⇒ parent-mediated, 6.2); session transcripts retained locally and reviewable; right to stop at any time. | W2.1 | Signed consent note on file before first child session | 6.2 |
| W2.6 | ✅ **DECIDED (2026-06-11).** Parent-mediated mode mechanism: **Phase 0 = honor system + full transcript logging + parent review** (parent physically present at pilot). **Phase 1 = add parent PIN gate** to start/resume session; same PIN gates escalation ack. Bones-first rationale: lighter mechanism during build, harden when scaling to non-technical parents. *(Rejected (c) periodic re-auth — too much friction.)* | — | ✅ Recorded in 6.2; to mirror into SAFETY.md Layer 5 (W2.1) | 6.2 |

---

## 26.4 Workstream W3 — Pedagogy Engine Foundations (G0-blocking)

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W3.1 | **Template→graph schema v0** (new — review finding). Define the contract between 9 Markdown templates and 10 graph nodes. Suggested: YAML frontmatter block per template listing `concepts: [{id, label, prereqs: [ids]}]`; body Markdown remains human guidance. Validation script: DAG check (no cycles), orphan check, id uniqueness. This is the OSS contribution format — keep it diff-reviewable. | — | Schema doc written; pilot fractions template authored in it; validator passes | 9, 10 |
| W3.2 | **Pilot concept graph authored.** 8–10 fraction nodes per 23 sample graph, in W3.1 format, with per-node: 1 vetted grounding passage reference (Kiwix/Vikidia anchor), ≥2 authored transfer-question seeds, deterministic-check spec (answer type + verifier). | W3.1 | All nodes pass validator; every node has grounding + ≥2 transfer seeds + verifier | 10, 23 |
| W3.3 | **BKT cold-start policy** (new — review finding). pyBKT cannot fit `learns/forgets/guess/slip` from one learner's first sessions. Policy v0: hand-set priors per node class (suggest: guess 0.2 for 4-option MC / 0.05 for free-numeric; slip 0.1; learns 0.2; forgets 0 for within-session); document when fitted parameters supersede priors (not before N≥~100 scored responses per skill — i.e., post-pilot). **Correct the 11 overclaim:** standard BKT has no native hint handling — implement hinted-win discount as a separate observation class or KT-IDEM-style multi-guess extension; verify against current pyBKT API. [⚠️ Verify pyBKT capability] | — | Priors table written; hinted-win mechanism chosen + unit-tested against pyBKT; 11 wording corrected | 11 |
| W3.4 | **False-confidence operational definition** (new — review finding). Disambiguate probe failure: classify as `false_confidence` only when (BKT mastery ≥ threshold) AND (no Help pressed on that concept) AND (probe failed) AND (immediate retry on a second transfer variant also failed — rules out slip). Single-failure = `slip_suspect`; decayed-mastery window = `forgetting_suspect`. Log all three classes distinctly. | W3.3 | Definition + decision table in spec; classifier logic stubbed | 14, 23 |
| W3.5 | **Build-vs-adopt assessment: Open TutorAI** (timeboxed 1 day). Spike: can its modular learner/parent interface skeleton be forked for the dialogue framework, or is it reference-only (like OATutor)? Output: adopt / fork / reference-only verdict + rationale. | — | One-page verdict recorded in 19 | 19.2 |
| W3.6 | **Learner data model v0.** Local-only store (suggest SQLite, single file): learner profile, per-skill BKT state, response log (timestamped, scored, hinted flag), Help events, probe events + class (W3.4), escalation log (W2.2), session transcripts. Define export/backup (file copy) and multi-learner namespacing now — cheap now, painful later. | W3.3, W3.4 | Schema DDL written; smoke test writes/reads a full mock session | new |

---

## 26.5 Workstream W4 — Licensing & Naming (G0: W4.1 only)

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W4.1 | **Content licence audit — pilot sources only.** Verify licences of pilot grounding sources (Vikidia, Simple English Wikipedia: CC BY-SA — compatible with local use). Flag Khan Academy CC BY-NC-SA as **hosted-tier conflict** (NC clause vs paid tier) — record as Phase-3 blocker, don't resolve now. [⚠️ Verify per source] | — | Licence table for pilot sources; Khan NC conflict logged in 24 | 18, 24 |
| W4.1b | ✅ **Name check DONE (2026-06-11).** "Mentar" CLEAR on GitHub / npm / PyPI (only a dormant org stub + 2017 fork; no conflict). Alts rejected: Curio (npm taken), Gradus (npm graveyard), Paideia (active org + brand overload), Tutela/Hearth (weak). **Decision: keep Mentar.** ⏳ **PENDING SUBTASK (Pradeep to run):** reserve namespace — publish placeholder `mentar` v0.0.0 to npm (`npm publish`) + PyPI (`twine upload`) to claim the name before any public repo. ~5 min. | — | Name decision logged (1); ⏳ npm + PyPI namespace reserved | 1 |
| W4.2 | **Mentar OSS licence + name clearance** (was TODO #13). *Name clearance now done (W4.1b).* Remaining: choose project licence — permissive (Apache-2.0, maximises adoption) vs copyleft (AGPL, protects hosted-tier moat); decide deliberately. Basic trademark search ("Mentar", edtech classes). G2-blocking, not G0. | — | Licence chosen + recorded; trademark search logged | 1, TODO #13 |

---

## 26.6 Workstream W5 — Spec Hygiene & Decisions (G0-blocking, all small)

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W5.1 | ✅ **DECIDED (2026-06-11) — Option B.** 4 rewritten: Phase 0/1 differentiator bar = **safety + pedagogy + local-first**; UX removed from the moat claim and **deferred to Phase 1 as an iteration surface** (bones first, skin later). No UX workstream in Phase 0. | — | ✅ 4.1 edited | 4 |
| W5.2 | **Fix 23/24 contradiction.** 23 says "run with safety layer active"; 24 says the safety spec is pending. Resolve by pointing 23 at SAFETY.md v0.1 (W2.1) as the pilot's definition of "active". | W2.1 | 23 references SAFETY.md v0.1 explicitly | 23, 24 |
| W5.3 | **Confirm placeholders as pilot defaults.** Promote 21 placeholders to pilot-config (revisable post-pilot): pattern mix 40/30/30, Help retry cap N=3, mastery threshold 0.85, probe after every 5 items OR when (mastery ≥0.85 ∧ Help-rate < 1 per 10 items) — whichever first. | — | 21 "TBD" rows replaced with "pilot default (v0)" values | 21, 13, 14 |
| W5.4 | **COPPA date check** (G2). Spec cites full compliance 22 Apr 2026 — now past; confirm amendments landed as described before Phase-1 US rollout framing. [⚠️ Verify] | — | 17.3 updated with post-April-2026 status | 17.3 |
| W5.5 | **Rough phase effort estimates.** Solo project; attach order-of-magnitude durations to Phases 0–3 in 25 (even ±50% bands) so scope survivability is visible. | G0 tasks scoped | 25 rows carry duration bands | 25 |
| W5.6 | **Kill criteria + scope-cut order** (new — review 2026-06-12). Pre-commit 3–5 "if X then Y" lines, e.g.: (a) no model passes T1.6 gates → raise size ceiling once; if still 0 → pause project, revisit local-first bar; (b) EU AI Act verification (24 #1) concludes high-risk applies even to the OSS local edition → halt EU framing, US/parental-consent-first only, reassess at Phase 3; (c) pilot learner disengages or shows distress past defined threshold → stop sessions, redesign before resuming; (d) Phase 0 actuals exceed W5.5 estimate by >2× → invoke scope-cut order. **Scope-cut order (drop first → last):** W1.6 watch · W3.5 spike · multi-learner namespacing polish · vetted variant bank (serve live-generation + review only) · probe classifier granularity (keep binary) · NEVER cut: safety layer, transfer re-check, deterministic verifier. | — | Kill-criteria list + ordered cut list recorded in 25; referenced by G1/G2 review | 25, 26.7 |
| W5.7 | **Data-flywheel posture decision** (new — review 2026-06-12; G2, not G0). Resolve 24 #16: DAKS graph inference + shared variant bank need multi-learner data the local edition never collects. Options: (a) declare them hosted-tier-only (cleanest; keeps OSS edition data-light); (b) opt-in anonymized contribution path (community value, but reopens 17 compliance posture — needs its own consent/minimisation design); (c) per-household only (no shared flywheel). Decide before Phase-1 messaging promises "improves from usage". | — | Decision row in 24 #16 updated; 10 + 15 caveats resolved to the chosen posture | 24 #16, 10, 15, 17 |

---

## 26.6A Workstream W6 — Core Design Artifacts (new 2026-06-12; G0-blocking except W6.4)

> **Why this workstream exists:** the test plan (TESTS.md) repeatedly tests a "pipeline", "controller", and "session" that no design document defines. These four artifacts are the missing 20% between plan and build.

| ID | Task | Dep | Exit criterion | Ref |
|----|------|-----|----------------|-----|
| W6.1 | **Session state machine spec.** Define the end-to-end turn loop as explicit states + transitions: `session_start → node_select (fringe) → pattern_select → present → answer → score (verifier) → bkt_update → branch{advance, probe (T5.1 rule), help_loop (13.1), escalation_freeze (W2.2)} → session_end`. Include: pending-re-check persistence across close/reopen (T4.3), escalation freeze as an absorbing state until parent_ack, probe non-skippability, completion-criteria evaluation. Owns 24 #7. Format: one Mermaid/state table doc — `docs/SESSION_FSM.md`. | W3.1 (graph loads), W2.2 (escalation states) | `docs/SESSION_FSM.md` exists; every T4/T5 test maps to a named state/transition; T3.7 conformance test passes | 24 #7, 13, 14, T3.7 |
| W6.2 | **Prompt template set v0 — versioned files.** One template file per: interaction pattern (×3, 12), Help modality (×5, 13.2), transfer-question generation, system prompt (with safety framing + grounding-as-data wrapper per W2.3). Stored under `prompts/` with a version hash; the dialogue controller loads them — never hardcoded strings. T7.3 regression triggers on any change to these files. | W2.3 (injection framing) | `prompts/` dir exists with ≥10 template files + `PROMPTS.md` registry (file, purpose, version hash); T4.6 loads-and-versions test passes | 12, 13.2, T7.3, T4.6 |
| W6.3 | **Pilot interface decision.** Decide the surface the child sees: (a) terminal/TUI (fastest, weakest for a child), (b) minimal local web app — suggest Flask/FastAPI + 4 plain HTML views: learner question screen, Help pop-up, probe interrupt, parent log view (recommended), (c) fork an existing skeleton (only if W3.5 verdict = fork). Decision only — building it is Phase 0 build work, not this task. | W3.5 verdict | Decision + 4-view list recorded here and in 23 pilot parameters | 23, W3.5 |
| W6.4 | **Repo architecture sketch** (G0-desirable, not blocking). Half-page `ARCHITECTURE.md`: module layout (`engine/` KST+BKT, `dialogue/` controller+prompts, `safety/`, `eval/`, `tools/`, `db/`, `curriculum/`, `docs/`, `tests/`, `reports/` gitignored), entry point (CLI `mentar serve` + library), storage (SQLite per W3.6), web layer per W6.3. Prevents week-1 code becoming the de facto architecture. | W6.3 | `ARCHITECTURE.md` exists; module list matches TESTS.md artifact paths | 19, 22, TESTS.md 0 |

---

## 26.7 Pilot Execution Tasks & Success Criteria (Gate G1)

**Pilot parameters (fill at G0):** learner = ___ (age, consent per W2.5) · sessions = suggest ≥8 sessions × ~20 min over 2–3 weeks · hardware = ___ (per W1.4) · model = per W1.3.

| ID | Task | Measures |
|----|------|----------|
| P1 | **Adaptive traversal** — learner moves through ≥6 of 8–10 nodes via fringe selection only (no manual sequencing) | Coverage %, fringe-selection log |
| P2 | **Help loop closure** — every Help press → different-modality re-explanation → mandatory transfer re-check → BKT update with hinted-win discount | Loop-completion rate, retry-cap hits, link-back events |
| P3 | **Pedagogical guardrail stress** — log every served re-explanation; parent/builder reviews 100% of generated (non-vetted-bank) variants post-session | Wrong-explanation rate (target: 0 uncaught; any uncaught = incident per 16) |
| P4 | **Proactive probing** — probes fire per W5.3 rule; outcomes classified per W3.4 | Probe count, class distribution, baseline false-confidence rate |
| P5 | **Safety layer live test** — W2.2 escalation path triggers correctly on ≥3 scripted (adult-injected) test inputs; zero unlogged triggers | Trigger/freeze/alert/log all fire |

**G1 pass thresholds (initial, revisable):**
- ≥90% Help-loop completion (P2); 0 skipped re-checks
- 0 uncaught wrong explanations in reviewed transcripts (P3); caught-and-flagged acceptable
- ≥1 detected `false_confidence` event OR documented evidence the probe mechanism functions on synthetic injection (P4 — a single learner may genuinely produce none)
- 100% scripted escalation triggers handled (P5)
- Learner-experience check: session transcripts show no frustration spiral (>3 consecutive failed retries without link-back) — qualitative parent judgment

**G1 outputs:** pilot report (metrics above + transcript review notes) → feeds W5.5 re-estimate and G2 go/no-go.

---

## 26.8 Dependency Snapshot (critical path)

```
W1.1 → W1.2 → W1.3 ─┬→ W1.4 → W1.5
                     │
W2.1 → {W2.2, W2.3, W2.4} ; W2.5, W2.6 independent
                     │
W3.1 → W3.2 ; W3.3 → W3.4 → W3.6 ; W3.5 independent
                     │
W4.1, W5.1–W5.3, W5.6 independent ; W3.1+W2.2 → W6.1 ; W2.3 → W6.2 ; W3.5 → W6.3 → W6.4
                     ▼
                  ── G0 ── → P1–P5 → G1 → {W4.2, W5.4, W5.5, W5.7} → G2 (Phase 1 go/no-go)
```
Critical path: **W1.1→W1.3** (model selection) and **W2.1→W2.2** (interim escalation) — everything else parallelises around them.

---

## 26.9 Changes This Section Imposes on Existing Sections

| Section | Change | Status |
|---------|--------|--------|
| 4 | UX moat: decide-or-rewrite (W5.1) | ✅ done 2026-06-11 |
| 10, 15 | Flywheel caveats added (multi-learner data dependency → 24 #16, W5.7) | ✅ done 2026-06-12 |
| 11 | Correct "BKT handles hinted-win natively" overclaim (W3.3) | ✅ wording corrected 2026-06-12; mechanism verification still in W3.3/T3.3 |
| 17.3 | COPPA post-April-2026 status (W5.4) | ⏳ pending |
| 20 | TODOs #2–4 re-homed as W1.1–W1.5 with exit criteria | ✅ done; 20.1–20.4 added |
| 21 | Placeholders → pilot defaults; add probe_frequency_cap (W2.4, W5.3) | ⏳ pending |
| 23 | Reference SAFETY.md v0.1; add pilot parameters + G1 thresholds (26.7); record W6.3 interface choice | ⏳ pending (W5.2, W6.3) |
| 24 | Rows #2–4/7/13 refreshed (re-homed/resolved markers); #16 flywheel + #17 design artifacts added; Khan NC conflict row still pending (W4.1) | ✅ partial 2026-06-12 |
| 25 | Phase 0 = this section; duration bands (W5.5); kill criteria + scope-cut order (W5.6) | ⏳ pending |
