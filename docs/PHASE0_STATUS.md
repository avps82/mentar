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
| **G0 — Pilot-ready** | All entry tasks done; pilot may begin | 🚫 blocked on: **W1.2–W1.3** (eval-host run — needs gaming PC) · W5.6 (needs Pradeep's distress/runway thresholds) · W3.5 (desk verdict done; optional hands-on spike). **W7 grounding** = G0-relevant but degrades gracefully (no ZIM → empty passage), so **not** a hard blocker — pilot quality improves once W7.1–W7.4 land. |
| **G1 — Pilot-complete** | P1–P5 thresholds met | gated on G0 |
| **G2 — Phase 1 entry** | Go/no-go on OSS Local Edition build | gated on G1 + W4.2 + W5.4 + W5.5 + W5.7 |

---

## W1 — Local LLM Selection

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W1.1 eval host | ✅ | Gaming PC, 10GB vRAM — per SPEC §20.3. **Endpoint supplied 2026-06-15:** OpenAI-compatible **LiteLLM proxy** at `http://192.168.1.191:4000/v1` (token via env `MENTAR_VLLM_API_KEY`; reachable from build sandbox). |
| W1.2 candidate eval | ⏳ (roster live, run pending) | **Roster now serving on the eval host** (`docs/MODEL.md`): `llama3.1:8b`, `gemma2:9b`, `phi4-mini`, `qwen3:14b`, `qwen3.5:9b`, `qwen3.5:2b` (candidates) + `mistral-small3.1` (≈24B **quality ceiling, NOT a pilot candidate** — too big/slow for the deployment envelope) + Claude Sonnet (judge/oracle). `llama3.1:8b`/`gemma2:9b`/`phi4-mini` verified responding 2026-06-15. **Eval dimensions:** hallucination, correctness, retrieval-faithfulness (**NIAH**, `eval/niah/`), safety, instruction-following, **+ latency tok/s** (CPU-offload matters). NIAH adopted; rest in own T1. **Run plan + roles A–D in `docs/MODEL.md`.** **T1.1 dataset ✅ BUILT** (`eval/dataset_v1.jsonl`, 101 items = 50/31/20; schema + validator PASS + `models.yaml` + `run_candidates.py` runner, dry-run verified; `tests/eval/test_dataset_v1.py` green). Next: export the eval env → `python3 eval/run_candidates.py` (T1.2) → NIAH + scoring → W1.3 pick. **Tooling scanned hands-on (2026-06-15):** needle-in-a-haystack **ADOPTED for the retrieval/grounding-faithfulness part** — cloned, installed, `niah demo --fake` ran E2E, 209 tests pass, vLLM-compatible via `base_url_env`. NIAH ≠ full harness (covers ~1 of ~5 dims); hallucination/correctness/safety stay in our own T1. See `docs/design/W1.2_eval_tooling.md` + `eval/niah/`. Needs eval-host run; T1.1 dataset (model-agnostic) buildable now. |
| W1.3 selection + pick | ⏳ | Produces `docs/MODEL.md` |
| W1.4 hardware tier mapping | ⏳ | Backend-dependent; needs W1.3. **Tiers (2026-06-15):** llama.cpp/GGUF = broad/low-end (CPU/Apple/modest GPU) DEFAULT; vLLM = capable-GPU tier. |
| W1.5 abstraction layer v0 | ✅ | Pluggable backends (SPEC §20.1), stub at `src/mentar/inference/`; **primary = llama.cpp** (2026-06-15). llama.cpp + vLLM share the OpenAI-compatible provider path. `config/inference.example.yaml` adds llamacpp (server + in_process). |
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
| W3.3 BKT cold-start + hinted-win | ✅ | `src/mentar/engine/bkt.py` (deterministic recurrence) + `docs/design/W3.3_bkt.md`. Hinted-win = elevated-guess class; cold-start priors hand-set by node class; pyBKT scoped OUT of hot path → offline fit only. 7 invariants verified numerically. SPEC §11 updated. `tests/engine/test_bkt.py` (T3.3) landed ✅. **Remaining (Sonnet):** caller wiring in FSM `bkt_update`. |
| W3.4 false-confidence classifier | ✅ | `src/mentar/engine/probe_classify.py` (decision table, 7 cases smoke-verified) + SPEC §14.4 (definition + table). Forgetting checked before false_confidence; false_confidence only when both-fail ∧ mastery≥threshold ∧ no-Help. `tests/engine/test_probe_classify.py` landed ✅. Remaining (Sonnet): caller wiring of stale-mastery window from `skill_state.updated_at`. |
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
| W5.6 kill criteria + scope-cut order | 🟡 | **SPEC §25.1–25.2** (criteria a–e + cut list + never-cut bar). (c) **DEFERRED to Bucket D** (Pradeep 2026-06-15) — no auto-stop until a distress-signal mechanism exists; must not halt on normal frustration; present-parent judgment governs interim. ⏳ Still optional: (e) personal time/€ runway line. |
| W5.7 data flywheel posture | ✅ | **DECIDED (Pradeep, 2026-06-15): (c) per-child / per-household** — no shared flywheel in the OSS local edition; aggregate features = hosted-tier-only if ever. SPEC §24 #16 updated; §10/§15 caveats resolved. |

---

## W7 — Grounding / Retrieval

New workstream (2026-06-15). **G0-relevant but not a hard blocker** — grounding is core to
SPEC §15, but the reader degrades gracefully (returns `""`) without ZIMs, so a degraded pilot can
still run. Build-vs-adopt settled; **pilot scope = anchor-resolution only** (no LLM/BM25/embeddings).
Frozen build contract: `docs/design/W7_grounding_reader.md`. **Opus froze the design; Sonnet builds
B1–B5.**

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W7.1 reader | ✅ | `src/mentar/grounding/reader.py` (Sonnet build + Opus review, 2026-06-15). Thin owned `libzim` reader; anchor URL → entry → verbatim text. Tries `A/<slug>` AND bare `<slug>` (modern libzim 3.x ZIMs drop the A/ namespace) + title fallback; follows redirects. libzim import deferred (module imports without libzim). |
| W7.2 resolve + scope/safety | ✅ | `resolve.py` + `source_map.py` (host scope guard rejects cross-source roam, e.g. `evilvikidia.org`) + `wrapper.py` (length-bound only, never strips passage — SAFETY §1.5). Public `resolve_grounding(node_grounding, cfg) -> str`. |
| W7.3 config + degradation | ✅ | `grounding:` block in `config/inference.example.yaml` + `cache.py`. Degradation hardened: non-dict/None input type-guarded + all exceptions absorbed → `""`, never raises (Opus review). |
| W7.4 ZIM acquisition + NAS/Samba | 🟡 | Tooling ✅: `scripts/fetch_zim.py` (multi-mirror Kiwix → **local / mounted-NAS / `smb://`** dest; **auto-resolves newest `YYYY-MM`**; `--config` drives downloads from `grounding.sources`) + read-side `grounding/sources.py` (same three location forms; `smb://` copied once to `zim_cache_dir`; optional `[nas]` extra = `smbprotocol`). **Config now declares sources structurally** — `{project, lang, selection, flavour, pin?}` per `<project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim`; the reader **auto-picks the latest** matching file in `zim_dir` (pin overrides; plain string = exact filename, back-compat). + config `smb:`/`zim_cache_dir` block + `.gitignore *.zim` + programmatic fixture ZIM. **Pending (manual/Pradeep, no save in current env):** point `zim_dir` at the NAS (mount or `smb://`), download the real Vikidia + Simple-Wikipedia ZIMs, and verify the reader's path convention against a real modern ZIM (contract verification step 2). **Future:** Kiwix OPDS catalog auto-discovery (global mirrors, any-OS dest). |
| W7.5 open retrieval | 🔭 | **DEFERRED (Phase 2)** — title-prediction → ZIM lookup (Hermit idea, clean-room) + BM25 fallback; embeddings only if measured. Not in the pilot. |
| W7.6 vetted ZIM media serving | 🔭 | **POST-PILOT scoped (2026-06-15).** Serve static ZIM media (images→audio/video) to the web app via libzim; gated on child-safety vetting/whitelist + a media field in the curriculum schema. Distinct from W6.5. `docs/design/media_and_interactivity.md`. |

**Tests:** `tests/grounding/` — 7 files, **57 tests, all pass** (`pytest tests/grounding/`, libzim available in sandbox; SMB mocked via `sys.modules`, no live server needed). Each file carries an inline `python3` smoke runner + pytest fns (project convention). **Remaining (Sonnet wiring):** dialogue controller calls `resolve_grounding` into the `{{grounding_passage}}` slot.

---

## W6 — Core Design Artifacts

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W6.1 session state machine | ✅ | `docs/SESSION_FSM.md` (188 lines, Mermaid + transition tables) |
| W6.2 prompt template registry | ✅ | `prompts/` — 10 versioned templates (3 patterns + 5 Help modalities + transfer-gen + system prompt) + `PROMPTS.md` registry. Hashing convention documented; **T4.6-equivalent check PASSES** (10/10 body hashes match registry + headers). `tests/test_prompt_registry.py` (T4.6 + T7.3 literal scan) landed ✅. Remaining (Sonnet): controller load-wiring. |
| W6.3 pilot interface decision | ✅ | **Decided: minimal local web app** (Flask/FastAPI localhost, 4 views). `docs/design/W6.3_pilot_interface.md` + SPEC §23. Fork ruled out by W3.5; TUI rejected. |
| W6.4 repo architecture sketch | ✅ | `docs/ARCHITECTURE.md` (149 lines, src-layout) |
| W6.5 interactive manipulatives | 🔭 | **POST-PILOT scoped (2026-06-15).** Mentar-OWNED interactive widgets (draggable fraction bar, splittable pie), parameterized per concept, rendered in the web app — NOT from ZIM (avoids unvetted ZIM-JS in a child webview). Needs a curriculum-schema widget field + a small owned widget lib. `docs/design/media_and_interactivity.md`. |

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
| `tests/engine/test_bkt.py` | — | 7 T3.3 invariants ✅ pass |
| `tests/engine/test_probe_classify.py` | — | 7 decision-table cases ✅ pass |
| `tests/test_prompt_registry.py` | — | 6 T4.6/T7.3 checks ✅ pass (incl. src literal scan) |

All test files carry an inline `python3`-runnable smoke runner **and** pytest-style
functions; full `pytest` run still pending `pip install -e ".[dev]"`.

---

## Next batch (immediately actionable)

**Needs Pradeep (G0):**
- **W5.6** — confirm the (c) distress threshold + optional (e) personal time/€ runway line in SPEC §25.1 (defaults proposed; just say yes or give numbers).
- **W1.2 → W1.3** model eval/selection — needs the gaming-PC eval host run; not doable in sandbox.
- **W4.1b** — reserve `mentar` namespace (npm + PyPI placeholder publish).

**Doable autonomously next (Sonnet grunt):**
1. **W7 grounding reader (B1–B5)** — build `src/mentar/grounding/` per the frozen contract `docs/design/W7_grounding_reader.md`: thin `libzim` reader + resolve/scope/safety wrapper + config + degradation + `tests/grounding/`. Sandbox has pip/net → spike `libzim` hands-on against a fixture ZIM.
2. **T1.1 eval dataset** — 50 + 30 + 20 prompts; needed before the eval-host run.
3. **Dialogue controller** — wire the W6.2 prompts + FSM + engine modules into the turn loop (the dialogue framework T4/T5 assume); includes calling `resolve_grounding` into the `{{grounding_passage}}` slot.
4. **Pilot web app** (W6.3 build) — Flask/FastAPI + the 4 views.

**Wiring follow-ups (not G0-blocking, Sonnet):** FSM caller wiring for `bkt.py`,
`escalation.py` (handle_trigger), `probe_classify.py` (stale-mastery window from
`skill_state.updated_at`), and the controller loading `prompts/` templates; full `pytest`
once `pip install -e ".[dev]"`. (Test files for bkt/probe/registry now landed ✅.)

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
| 2026-06-14 (overnight) | Test files landed (Opus) — `tests/engine/test_bkt.py` (T3.3, 7), `tests/engine/test_probe_classify.py` (7), `tests/test_prompt_registry.py` (T4.6+T7.3, 6). All pass via inline smoke; pytest-compatible. |
| 2026-06-15 | Secret safeguard added — `.gitignore` secret rules + `config/inference.example.yaml` + `config/README.md` + `scripts/git-hooks/pre-commit` (blocks secret filenames + inline secrets; activate via `core.hooksPath`). Tested: blocks, clean commits pass. |
| 2026-06-15 | Decisions (Pradeep) — **W5.7 = (c) per-child** (§24 #16); EU AI Act high-risk clarified **not local/G0-blocking** (§24 #1, §17.2); W5.6 (c) revised to safeguarding-informed assent-based threshold w/ external guides. |
| 2026-06-15 | Decisions (Pradeep, mobile) — W5.6 (c) **deferred to Bucket D** (no auto-stop mechanism yet; don't halt on normal frustration); W1.2 model shortlist set (Qwen2.5-7B / Llama-3.1-8B / Gemma-2-9B / Phi-4-mini + more), eval focus = hallucination + retrieval accuracy via needle-in-a-haystack; cloud GitHub access to be granted (enables cloud routines). |
| 2026-06-15 | W1.2 eval-tooling scan (Opus, hands-on) — NIAH cloned/installed/run (`demo --fake` E2E, 209 tests pass, vLLM-compatible). Verdict: **adopt for retrieval-faithfulness only**, not a full harness. `docs/design/W1.2_eval_tooling.md` + `eval/niah/` (vLLM config). |
| 2026-06-15 | Directives (Pradeep) — **llama.cpp = primary local backend** (lightweight, broadest HW support; SPEC §20.1/§21, config, inference stub). **Hermit-AI** scanned hands-on as ZIM-grounding reference (AGPL → clean-room ideas only): borrow title-prediction-over-ZIM + libzim + staged retrieval; implies a new grounding/retrieval W-task. `docs/design/grounding_zim_reference_hermit.md`. |
| 2026-06-15 | Grounding reader decision — verified ZIM-MCP option = **OpenZIM MCP** (`cameronrye/openzim-mcp`, **MIT**, libzim, maintained). **Decision: BUILD a thin owned `libzim` reader** (reuse OpenZIM MCP's MIT code as reference; **skip the MCP server** — wrong shape for our controlled FSM + safety-critical path). Depend on `libzim` only. MCP-server-as-runtime = a Phase-2/agentic option, not the pilot. |
| 2026-06-15 | **W7 — Grounding/Retrieval workstream opened** (Opus design freeze; Pradeep approved scope). New `26.6B` in PHASE0.md (W7.1–W7.5) + this W7 status section. Frozen build contract `docs/design/W7_grounding_reader.md`. **Pilot scope = anchor-resolution only** (pilot nodes carry explicit `anchor:` URLs → no LLM title-prediction/BM25/embeddings; those = W7.5 deferred). G0-relevant but degrades gracefully (`resolve_grounding` → `""` on missing ZIM), so not a hard G0 blocker. SPEC §15 cross-references the new `src/mentar/grounding/` producer. |
| 2026-06-16 | **T1.1 eval dataset BUILT** (Opus, after the overnight build was rate-limited). `eval/dataset_v1.jsonl` = 101 items (50 reexplain across 8 nodes × 5 modalities + 31 transfer with checkable answers + 20 adversarial: 5 each jailbreak/offtopic/distress/injected_passage). + `eval/schema.json`, `eval/build_dataset.py` (authored source), `eval/validate_dataset.py` (PASS → `reports/T1.1/result.json`), `eval/models.yaml` (roster), `eval/run_candidates.py` (T1.2 runner; stdlib; env-driven; dry-run verified; 6 tests in `tests/eval/test_dataset_v1.py` incl. transfer answers verifying PASS via verify_numeric). **W1.2 is now runnable** — export the eval env and run the runner. Stale `OVERNIGHT_STATUS.md` removed. |
| 2026-06-15 | **W1.1 endpoint live + W1.2 roster complete** (Pradeep stood up the eval host; Opus recorded). OpenAI-compatible **LiteLLM proxy** at `http://192.168.1.191:4000/v1` now serves the full cross-family candidate set — `llama3.1:8b`, `gemma2:9b`, `phi4-mini`, `qwen3:14b`, `qwen3.5:9b`, `qwen3.5:2b` + `mistral-small3.1` (ceiling, not candidate) + Sonnet (judge). Three verified responding. New `docs/MODEL.md` = canonical roster + roles A–D + size→tier map + eval dimensions (incl. latency) + run plan. Config `vllm:` block points at the proxy (token via env, never committed). **Ready to run** once T1.1 dataset is built. |
| 2026-06-15 | **W7.4 structured sources + auto-latest** (Opus; Pradeep flagged the gap). ZIM filenames follow `<project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim`. Config `grounding.sources` now declares those parts (`{project, lang, selection, flavour, pin?}`) instead of a fixed filename; the **reader auto-picks the newest matching file in `zim_dir`** (latest YYYY-MM wins; `pin` = date or exact file override; plain string still accepted = exact filename). Shared helpers `build_filename_regex`/`pick_latest`/`list_zim_dir`/`resolve_filename` in `grounding/sources.py`, reused by `scripts/fetch_zim.py` (+`--config` mode). `source_map.get_zim_path` resolves via spec. +7 tests (real-world names: `wikipedia_en_astronomy_maxi`, `wikipedia_ace_all_nopic`) → 57 pass; E2E auto-latest verified against the fixture ZIM. |
| 2026-06-15 | **Media/interactivity decision + 2 W-tasks scoped** (Opus; Pradeep asked). `docs/design/media_and_interactivity.md`: grounding stays **text-only** (correct — text LLM, pilot needs no media); media/interactivity is a **presentation-layer** concern → **W6.5** (Mentar-OWNED interactive manipulatives, not ZIM-JS — safety + pedagogy) + **W7.6** (vetted ZIM static-media serving, gated on child-safety whitelist). Both post-pilot, not G0. Flagged: **Khan Academy = CC BY-NC-SA** (NC) — fine local/personal, not for a commercial/hosted edition (already SPEC §24 #18 / CONTENT_LICENSES.md); PhET = CC BY (better if interactive ZIM content ever adopted). Also added general `scripts/fetch_zim.py` (auto-resolve latest ZIM by project+pattern from Kiwix mirror index; local/NAS/SMB dest) for future ad-hoc downloads (Khan, PhET, …). |
| 2026-06-15 | **W7.4 NAS/Samba support** (Opus) — ZIM sources now read/download from **local / mounted-NAS / `smb://`** locations. New `src/mentar/grounding/sources.py` (`materialize_zim`: local/mounted pass-through, `smb://` copied once to `zim_cache_dir` via `smbclient`); fetch script rewritten `scripts/fetch_zim.py` (multi-mirror Kiwix incl. `lbo.download.kiwix.org` → local/NAS/SMB dest). `source_map`/`resolve` route through materialization (cache-hit skips SMB copy). Optional `[nas]` extra (`smbprotocol>=1.12`); mounted shares need nothing. Config `smb:`/`zim_cache_dir` block. +`test_sources.py` (8 tests, SMB mocked) → 46 tests pass. Future goal recorded: Kiwix OPDS catalog auto-discovery. smbclient API confirmed via Context7. |
| 2026-06-15 | **W7.1–W7.4 BUILT** (Sonnet grunt build + Opus review/hardening). `src/mentar/grounding/` (reader/resolve/source_map/wrapper/cache + public `resolve_grounding`) + `tests/grounding/` (38 tests, all pass) + `grounding:` config block + `libzim>=3.10` pin + Kiwix fetch script + programmatic fixture ZIM. Opus review caught + fixed: (1) non-dict/None input could escape the except handler → type-guarded; (2) reader only tried `A/<slug>` → now also tries bare `<slug>` for modern libzim 3.x ZIMs. **W7.4 real-ZIM download + path-convention verification still pending (manual).** Controller wiring of `resolve_grounding` into `{{grounding_passage}}` = thin Sonnet follow-up. |
