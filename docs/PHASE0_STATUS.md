---
title: "Mentar — Phase 0 Status"
version: living-doc
status: "Active"
last-updated: 2026-07-11
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
| **G0 — Pilot-ready** | All entry tasks done; pilot may begin | 🟢 **essentially READY for the supervised single-family pilot (2026-06-27)** — W1.3 ✅ (`gemma2:9b`), W5.6 ✅, W2.2 interim ✅, W4.2 licence ✅. Remaining = non-blocking: W3.5 optional hands-on spike (desk verdict done); W7 grounding degrades gracefully (real ZIMs = quality, W7.4). **Broader rollout** (beyond single-family) still gated on the W2.2 professional reviews (handoff wording + child-facing signposting). |
| **G1 — Pilot-complete** | P1–P5 thresholds met | gated on G0 |
| **G2 — Phase 1 entry** | Go/no-go on OSS Local Edition build | gated on G1 + W4.2 + W5.4 + W5.5 + W5.7 |

---

## W1 — Local LLM Selection

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W1.1 eval host | ✅ | Local AI test PC, 10GB vRAM GPU — per SPEC §20.3. **Endpoint supplied 2026-06-15:** OpenAI-compatible **local proxy** at `http://192.168.xx.xxx:4000/v1` (token via env `MENTAR_VLLM_API_KEY`; reachable from build sandbox). |
| W1.2 candidate eval | 🟡 first run done; pick (W1.3) pending | **First eval run landed 2026-06-16 → `docs/EVAL_RESULTS.md`** (gemma2:9b front-runner: 100% maths-correctness, 85% safety with the full pipeline; raw data git-ignored). **Roster now serving on the eval host** (`docs/MODEL.md`): `llama3.1:8b`, `gemma2:9b`, `phi4-mini`, `qwen3:14b`, `qwen3.5:9b`, `qwen3.5:2b` (candidates) + `mistral-small3.1` (≈24B **quality ceiling, NOT a pilot candidate** — too big/slow for the deployment envelope) + Claude Sonnet (judge/oracle). `llama3.1:8b`/`gemma2:9b`/`phi4-mini` verified responding 2026-06-15. **Eval dimensions:** hallucination, correctness, retrieval-faithfulness (**NIAH**, `eval/niah/`), safety, instruction-following, **+ latency tok/s** (CPU-offload matters). NIAH adopted; rest in own T1. **Run plan + roles A–D in `docs/MODEL.md`.** **T1.1 dataset ✅ BUILT** (`eval/dataset_v1.jsonl`, 101 items = 50/31/20; schema + validator PASS + `models.yaml` + `run_candidates.py` runner, dry-run verified; `tests/eval/test_dataset_v1.py` green). Next: export the eval env → `python3 eval/run_candidates.py` (T1.2) → NIAH + scoring → W1.3 pick. **Tooling scanned hands-on (2026-06-15):** needle-in-a-haystack **ADOPTED for the retrieval/grounding-faithfulness part** — cloned, installed, `niah demo --fake` ran E2E, 209 tests pass, vLLM-compatible via `base_url_env`. NIAH ≠ full harness (covers ~1 of ~5 dims); hallucination/correctness/safety stay in our own T1. See `docs/design/W1.2_eval_tooling.md` + `eval/niah/`. Needs eval-host run; T1.1 dataset (model-agnostic) buildable now. |
| W1.3 selection + pick | ✅ (2026-06-27) | **Pick = `gemma2:9b`** (pilot default). Clean full-suite Sonnet-judged run: rubric 0.78, sycophancy 12/12, abstention 0.50, raw-adversarial 0.30, ~0.5 s/item. `gemma4:12b` = optional capable-GPU tier (rubric 0.82 but abstention 0.25, ~15 s/item, full-GPU). Raw-adversarial is bare-model; shipped safety = the 80–85% pipeline (`EVAL_RESULTS.md`). See `docs/MODEL.md` → W1.3 Decision. |
| W1.4 hardware tier mapping | ✅ (2026-06-27) | **Tiers:** llama.cpp/GGUF = broad/low-end (CPU/Apple/modest GPU) DEFAULT → **`gemma2:9b` mid-tier default**; vLLM/full-GPU = capable tier → **`gemma4:12b`**. |
| W1.5 abstraction layer v0 | ✅ | **REAL (2026-06-18)** — `src/mentar/inference/backend.py`: `load_inference_config()` (`${VAR}` expand) + `make_llm_call(cfg)` dispatching llamacpp(server)/vllm/ollama over the shared OpenAI path + llamacpp(in_process) via llama-cpp-python; retries + clear unreachable error. Thin owned wrapper, swappable in one file (same shape as the libzim reader). Web app + new `mentar run-session` CLI both consume it. `tests/inference/test_backend.py` (10). **Verified end-to-end on a LOCAL GGUF** (Qwen2.5-0.5B Q4, throwaway smoke vehicle — NOT a pick): full FSM loop ran on local llama.cpp inference (~7 tok/s on a 2-core AMD A10). ⚠️ **Pre-AVX2 CPU = stock wheel SIGILLs**; needs from-source build (`GGML_NATIVE=ON`, AVX2 off) — hardware-tier note for W1.4. **Primary = llama.cpp** (2026-06-15). |
| W1.6 hardware horizon watch | 🔭 | Not G0-blocking; quarterly review |

---

## W2 — Safety Spec

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W2.1 SAFETY.md v0.1 | ✅ | `docs/SAFETY.md` (692 lines, 6-layer) |
| W2.2 Bucket D interim escalation | ✅ | `src/mentar/safety/escalation.py` (classify + handle_trigger; 220 lines) + `tests/safety/test_escalation.py` (20+20 fixtures, flow tests; 390 lines). All 20 positives fire with correct class; all 20 negatives silent; jailbreak=logged_only; escalation_log row written with untruncated verbatim text. Rollout guard: handoff wording has an automated harness (`safety/handoff_check.py`, PR #5) — **professional safeguarding review still required**; emergency-services signposting **ratified Option A 2026-06-27** (parent-route, no signposting — for the supervised pilot only; `docs/design/W2.2_signposting_decision_prep.md`), with child-facing signposting design deferred to a safeguarding professional before any unsupervised mode. Both guards remain required before rollout beyond the single-family pilot. Bucket D supersedes trigger list post-pilot. |
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
| W3.3 BKT cold-start + hinted-win | ✅ | `src/mentar/engine/bkt.py` (deterministic recurrence) + `docs/design/W3.3_bkt.md`. Hinted-win = elevated-guess class; cold-start priors hand-set by node class; pyBKT scoped OUT of hot path → offline fit only. 7 invariants verified numerically. SPEC §11 updated. `tests/engine/test_bkt.py` (T3.3) landed ✅. Wired into the FSM (`_do_bkt_update`). |
| W3.4 false-confidence classifier | ✅ | `src/mentar/engine/probe_classify.py` (decision table, 7 cases smoke-verified) + SPEC §14.4 (definition + table). Forgetting checked before false_confidence; false_confidence only when both-fail ∧ mastery≥threshold ∧ no-Help. `tests/engine/test_probe_classify.py` landed ✅. Wired into the FSM (stale-mastery window from `skill_state.updated_at`); a `classify_probe` kwarg crash in `PROBE_CLASSIFY` was found + fixed (PR #4). |
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
| W4.1b name "Mentar" check | ✅ | Clear on GitHub/npm/PyPI; **namespace reserved 2026-06-17: `@mentar/mentar@0.0.1` on npm (org `@mentar` created) + `mentar` on PyPI.** |
| W4.2 OSS licence + trademark | ✅ licence (2026-06-27) | **AGPL-3.0-only adopted** — `license = "AGPL-3.0-only"` in `pyproject.toml` + `LICENSE` (audit: GPL `libzim` core forces AGPL, permissive non-viable — `docs/LICENSE_AUDIT.md`). ⚠️ full verbatim AGPL text still to be pasted into `LICENSE` (not fetchable from the sandbox). Trademark = separate, G2. |

---

## W5 — Spec Hygiene & Decisions

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W5.1 UX moat decide-or-rewrite | ✅ | Option B taken — UX deferred to Phase 1 |
| W5.2 23/24 SAFETY.md cross-ref | ✅ | SPEC §23 anchors "safety layer active" to SAFETY.md v0.1 (W2.1) + W2.2 escalation; §24 row #6 updated to "pilot path live; Bucket D open". Contradiction resolved. |
| W5.3 pilot defaults from placeholders | ✅ | SPEC §21 TBDs promoted to **pilot default (v0)**: pattern mix 40/30/30, Help retry cap 3, mastery threshold 0.85 (matches `engine/fringe.py`), + new Probe-cadence row (every 5 items OR mastery≥0.85 ∧ Help-rate<1/10). All revisable post-pilot. |
| W5.4 COPPA post-April-2026 check | ⏳ | G2 blocker, not G0 — verify |
| W5.5 phase effort estimates | ⏳ | After G0 tasks scoped |
| W5.6 kill criteria + scope-cut order | ✅ (2026-06-27) | **SPEC §25.1–25.2** (criteria a–e + cut list + never-cut bar). (c) **RATIFIED — continuous-assent**: parent-as-judge, no numeric auto-stop, anchored on UNICEF ERIC / IRB child-assent / NSPCC (`docs/design/W5.6_decision_prep.md`). (e) personal time/€ runway line left optional/unset (maintainer sets a number if/when wanted). Small follow-up: mirror into SPEC §25.1 prose. |
| W5.7 data flywheel posture | ✅ | **DECIDED (the maintainer, 2026-06-15): (c) per-child / per-household** — no shared flywheel in the OSS local edition; aggregate features = hosted-tier-only if ever. SPEC §24 #16 updated; §10/§15 caveats resolved. |

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
| W7.4 ZIM acquisition + NAS/Samba | ✅ verified (2026-06-27); **re-pointed 2026-07-05 (B1)** | **`fetch_zim.py` + `ZimReader` verified end-to-end on REAL content:** resolved newest from the Kiwix mirror + downloaded `vikidia_en_all_nopic_2026-06.zim` (8.4 MB) → `ZimReader` opened it and extracted a clean verbatim **fractions** lead (216 chars: *"A fraction is a number that has 2 numbers with a line between…"*). Confirms Vikidia = the right pilot source (clean extraction vs full Wikipedia's poor 8–202 char lead). Tooling ✅: `scripts/fetch_zim.py` (multi-mirror Kiwix → **local / mounted-NAS / `smb://`** dest; **auto-resolves newest `YYYY-MM`**; `--config` drives downloads from `grounding.sources`) + read-side `grounding/sources.py` (same three location forms; `smb://` copied once to `zim_cache_dir`; optional `[nas]` extra = `smbprotocol`). **Config now declares sources structurally** — `{project, lang, selection, flavour, pin?}` per `<project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim`; the reader **auto-picks the latest** matching file in `zim_dir` (pin overrides; plain string = exact filename, back-compat). + config `smb:`/`zim_cache_dir` block + `.gitignore *.zim` + programmatic fixture ZIM. **B1 (2026-07-05): the real `/mnt/zim` mount (530 GB, ro) never held Vikidia/Simple-WP** (only Wikipedia, KhanAcademy, gutenberg, StackExchange) — maintainer decided **re-point the pilot to Khan Academy** (`khanacademy_en_all_2023-03.zim`, already mounted) rather than wait on a NAS upload; see B1 in REMAINDER_PLAN.md for the extraction-shape fix this required. **Future:** Kiwix OPDS catalog auto-discovery (global mirrors, any-OS dest). |
| W7.5 open retrieval | 🔭 | **DEFERRED (Phase 2)** — title-prediction → ZIM lookup (Hermit idea, clean-room) + BM25 fallback; embeddings only if measured. Not in the pilot. |
| W7.6 vetted ZIM media serving | 🔭 | **POST-PILOT scoped (2026-06-15).** Serve static ZIM media (images→audio/video) to the web app via libzim; gated on child-safety vetting/whitelist + a media field in the curriculum schema. Distinct from W6.5. `docs/design/media_and_interactivity.md`. |

**Tests:** `tests/grounding/` — 7 files, **57 tests, all pass** (`pytest tests/grounding/`, libzim available in sandbox; SMB mocked via `sys.modules`, no live server needed). Each file carries an inline `python3` smoke runner + pytest fns (project convention). **Remaining (Sonnet wiring):** dialogue controller calls `resolve_grounding` into the `{{grounding_passage}}` slot.

---

## W6 — Core Design Artifacts

| ID | Status | Artifact / Note |
|----|--------|------------------|
| W6.1 session state machine | ✅ | `docs/SESSION_FSM.md` (188 lines, Mermaid + transition tables) |
| W6.2 prompt template registry | ✅ | `prompts/` — 10 versioned templates (3 patterns + 5 Help modalities + transfer-gen + system prompt) + `prompts/README.md` registry. Hashing convention documented; **T4.6-equivalent check PASSES** (10/10 body hashes match registry + headers). `tests/test_prompt_registry.py` (T4.6 + T7.3 literal scan) landed ✅. Remaining (Sonnet): controller load-wiring. |
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

## Test suite

The full suite runs via `python -m pytest tests/` — the root `conftest.py` puts `src/` + `.vendor/`
on `sys.path`, so no editable install is needed. **482 tests pass and `ruff check .` is clean** as of
2026-07-10 (main, post-release-wave D-tasks + the UI rebuild — see REMAINDER_PLAN.md and
`docs/design/UI_REQUIREMENTS.md`). Each test file also
carries an inline `python3`-runnable smoke runner (project convention).

---

## Next actions

Canonical remaining-work plan: **[REMAINDER_PLAN.md](REMAINDER_PLAN.md)**. Done/remaining + stale-doc
register: **[DOC_AUDIT.md](DOC_AUDIT.md)**. The earlier autonomous build list (grounding reader,
dialogue controller, web app, eval dataset, FSM caller wiring) has **all shipped** — see the changelog.

**Maintainer-gated (not locally doable):**
- **W1.3** — final model pick. The first eval run landed 2026-06-16 (`EVAL_RESULTS.md`; gemma2:9b
  front-runner); the pick decision + any fuller dimensions remain.
- **W4.2** — LICENSE ratification (audit → AGPL-3.0; GPL `libzim` core). See `LICENSE_AUDIT.md`.
- **W5.6** — distress/runway thresholds (decision).
- **W2.2** — emergency-services signposting decision + professional handoff-wording review.
- **W7.4** — real Vikidia/Simple-WP ZIM download + reader path verification (needs NAS/ZIMs).

### Known defects (found in testing)
- **✅ RESOLVED 2026-07-05 — Escalation logging is best-effort — a DB failure silently drops
  the verbatim disclosure (2026-07-03, repo review 2nd pass).** Was: `write_escalation` try/except-
  swallowed in the controller with no fallback; the freeze still happened but SAFETY §3.1 "never
  silently dropped" was violated on any DB error. Fixed via REMAINDER_PLAN A15 (merged, PR #56,
  stacked on #55/A3): a DB-write failure now also appends
  one JSON line (`iso_ts`, `trigger_class`, `severity`, `verbatim_text`) to
  `escalation_fallback.log` next to the DB file; `/parent` shows a "durable logging degraded"
  banner when that file is non-empty. → REVIEW §8.1.
- **✅ RESOLVED 2026-07-05 — Curriculum templates never validated at runtime → false "all
  mastered" completion (2026-07-03, repo review 2nd pass).** Was: `validate()` ran only via the
  CLI subcommand; serve/run-session parsed YAML directly — a cyclic/bad-prereq template ->
  unsatisfiable nodes -> empty fringe -> child told "Well done — you've mastered all the
  concepts!" silently. Fixed via REMAINDER_PLAN A16 (merged, PR #61, stacked on Wave 1 + A17):
  new `validate_template.validate_or_raise()`; `web/app.py`
  validates every `SUBJECTS` template at import time (raises `RuntimeError` naming the
  template + errors — a config error, not a 500); `cli/__main__.py`'s `run-session` validates
  before building the controller (prints the error, exits 1, same pattern as the existing
  no-inference-config check). → REVIEW §8.2.
- **✅ RESOLVED 2026-07-05 — Prompt edits don't invalidate the safety-eval claim (2026-07-03,
  repo review 2nd pass).** Was: the 20/20 pipeline-safety run (2026-06-27) predates several
  prompt re-hashes (including this wave's own A7 system_prompt.md edit); nothing required a
  T1.5 re-run on prompt change, so the headline claim could silently age. Fixed via
  REMAINDER_PLAN A18 (merged, PR #69, stacked on Wave 1/2/3):
  rule added to both `AGENTS.md` and `CONTRIBUTING.md` (re-run T1.5 + record the date in
  `docs/EVAL_RESULTS.md` before merging any prompts/-touching PR); new CI job
  (`prompt-eval-reminder`) posts a required-checklist comment on any PR that touches
  `prompts/**` (reminder only — does not run the eval itself, which stays run-only/off-CI).
  → REVIEW §8.4.
- **✅ RESOLVED 2026-07-05 — Layering violation — CLI imports the web module (2026-07-03, repo
  review 2nd pass).** Was: `cli/__main__.py` imported `_load_curriculum`/`_DbStoreAdapter` from
  `mentar.web.app`: headless run-session needed Flask + triggered web module-level side effects
  (app creation, all-subject curriculum load). Fixed via REMAINDER_PLAN A17 (merged, PR #60,
  stacked on Wave 1): moved `load_curriculum` to
  `engine/curriculum.py` and `_DbStoreAdapter` to `db/adapter.py` (pure move, no behaviour
  change); `mentar.cli.__main__` now imports cleanly with Flask blocked. → REVIEW §8.3.
- **✅ RESOLVED 2026-07-05 — `age_mode` stored but never read + floating deps + unreplayable
  sessions (2026-07-03, repo review 2nd pass, §8.6/§8.7).** Fixed via REMAINDER_PLAN A19
  (merged, PR #70, stacked on Wave 1/2/3): (1) new
  `LearnerStore.assert_parent_mediated()`, called from both `web/app.py` and `cli/__main__.py`
  right after the learner id is known — raises a clear `RuntimeError` if a learner's
  `age_mode` is ever anything but `'parent_mediated'` (independent mode needs the W2.2
  safeguarding closures first); (2) new `constraints.txt` (generated from a clean venv install
  of `.[dev,web,grounding]`, all 452 tests verified green against it), referenced by CI via
  `pip install -c constraints.txt -e ...`; (3) schema v3 (`session.rng_seed`) +
  `SessionController(rng_seed=...)` — a per-instance seeded `random.Random` (not the global
  `random` module) drives every non-deterministic choice (pattern/modality/praise-variant
  selection), default a fresh random seed logged at session start; same seed replays the
  identical session. → REVIEW §8.6/§8.7.
- **✅ RESOLVED 2026-07-05 (v0) — NO OUTPUT-SIDE SAFETY GATE (2026-07-03, repo review
  follow-up).** Was: SAFETY L2 §2.1/§2.2 promised hard-block matches are discarded +
  incident-logged and every output is scope/age/pedagogy-checked, but the real chain was
  `llm_call -> redact_credentials -> _strip_trailing_questions -> child` — no content/scope
  check, no discard path, no incident log. Fixed via REMAINDER_PLAN A13 (merged, PR #58,
  stacked on A3/A15/A8): new `safety/output_guard.py`
  (`screen_output()`) wired as a second stage in `_make_safe_llm`; on a hard-content or
  off-scope match the output is discarded, an incident row is written (reusing
  `escalation_log`, `trigger_class=output_blocked:<class>`, session does NOT freeze), and the
  child gets a fixed neutral redirect. **Still a v0 keyword/regex heuristic, not a semantic
  classifier** — age-appropriateness and pedagogical-appropriateness checks (§2.2 items 2–3)
  are not yet implemented; SAFETY.md reworded to say so plainly. → REVIEW §1.6.
- **✅ RESOLVED 2026-07-05 (v0) — Help explanations never verified — only child answers are
  (2026-07-03, repo review follow-up).** Was: SAFETY §6.2 Level 2 promised numeric steps *in
  re-explanations* are verified before serving (discard + regenerate on failure), but
  `verify_numeric.check()` was only ever called on child answers — a wrong worked step in a
  Help explanation shipped unchecked. Fixed via REMAINDER_PLAN A14 (merged, PR #59,
  stacked on A3/A15/A8/A13): new `engine/explain_check.py` extracts
  `a <op> b = c` arithmetic claims from Help explanation text and verifies each via
  `verify_numeric.normalise_fraction`; a verified-wrong claim triggers regeneration (bounded,
  2 attempts) then falls back to the deterministic hint. **v0 coverage floor** — simple
  arithmetic claims only, no decimals, no algebraic steps (÷/"divided by" added 2026-07-10
  as D7; the plain `/` character stays unparsed — it collides with fraction notation);
  unparseable claims pass through unchecked, not blocked. → REVIEW §1.7.
- **✅ RESOLVED 2026-07-05 — SAFETY-AUDIT GAP — escalation_log missing/wrong fields
  (2026-07-03, repo review).** Was: no `severity` column, no `session_id`/turn number, and
  the live write path never set `session_outcome` (LOW jailbreaks stored as `'frozen'`
  instead of `'logged_only'`); a second uncalled write path (`escalation.handle_trigger()`)
  had already drifted from the real one. Fixed via REMAINDER_PLAN A3 (merged, PR #55, branch
  `feat/a3-escalation-schema-v2`):
  schema migrated to `user_version=2` (real v1->v2 `ALTER TABLE` migration, not a stub);
  `severity`/`session_id`/`turn_index`/`session_outcome` now flow from the controller
  through `LearnerStore.write_escalation`; `handle_trigger()` (the drifted duplicate)
  deleted. → [REVIEW_2026-07-03.md §1.2](../REVIEW_2026-07-03.md).
- **✅ RESOLVED 2026-07-05 — Escalation redirect hands the resume control to the child's screen
  (2026-07-03, repo review).** Was: on escalation `/answer` (and any subsequent `/`) redirected
  the CHILD's browser to `/parent`, which shows the verbatim trigger text (SAFETY §3.3 Step 4
  says the alert must NOT carry it) plus the un-gated acknowledge/resume button. Fixed via
  REMAINDER_PLAN A8 (merged, PR #57, stacked on A3/A15): new
  `/frozen` view shows ONLY the two fixed handoff messages (checked on every render while
  ESCALATION_FREEZE, not just the triggering turn); `/parent` is typed-URL-only (never
  auto-navigated); `/parent/ack` now requires a typed confirm word (`RESUME`) — wrong/missing
  word is a no-op. PIN gate stays Phase 1. → REVIEW §1.4.
- **✅ RESOLVED 2026-07-05 — SAFETY.md overstates shipped controls (2026-07-03, repo review).**
  Was: (1) §1.5.2(2) promised strip/flag of imperative lines in grounding passages —
  `grounding/wrapper.py` deliberately doesn't (W7 data-wrapping design superseded it, SAFETY.md
  never updated). (2) §4.6 + SECURITY.md said a rolling retention window "is applied" — zero
  retention/purge code existed (and transcript immutability triggers make row-level purge
  impossible — the two designs conflicted). (3) §5.5 session-start "I'm a computer helper"
  statement wasn't implemented (only the reactive system-prompt rule). Fixed via REMAINDER_PLAN
  A4 (merged, PR #68, stacked on Wave 1/2 + A1): (1) reworded
  to describe the actual marker-data-wrapping control; (2) reworded to the ratified "pilot
  retains everything, deletion = delete the .db file" policy (§5.6 table + SECURITY.md updated
  to match); (3) new `TRANSPARENCY_LINE` constant, shown once alongside `ASSENT_LINE` on the
  first child-facing turn. → REVIEW §1.1/1.3/1.5. C-row retention decision folded in (ratified
  2026-07-04, option ii — see REMAINDER_PLAN.md's ratified-decisions section).
- **✅ RESOLVED 2026-07-05 — false-confidence `help_pressed` signal corrupted (2026-07-03, repo
  review).** Was: `_do_probe_classify` used `len(ctx.help_modalities_used) > 0` — stale across
  nodes (Help on node A masked false_confidence on node B — SPEC §14.4 requires "no Help pressed
  *on concept*") and also set by system-initiated auto-help-on-wrong, conflating declared
  confusion with scaffolding. Fixed via REMAINDER_PLAN A5 (merged, PR #62,
  stacked on Wave 1 + A17/A16): new `ctx.help_by_node: dict[str, bool]` set ONLY at
  the 3 `_is_help_request` call sites (never in `_do_bkt_update`'s auto-help branch);
  `_do_probe_classify` reads `ctx.help_by_node.get(current_node_id, False)`. → REVIEW §2.2.
- **✅ RESOLVED 2026-07-05 — Web learner identity not durable — mastery silently resets on
  server restart (2026-07-03, repo review).** Was: `_db_learner_ids` is in-memory; the cookie
  survives a restart, the mapping doesn't -> `create_learner()` ran again -> new learner row,
  orphaned history, mastery back to P_L0. Fixed via REMAINDER_PLAN A6 (merged, PR #63,
  stacked on Wave 1 + A17/A16/A5): new
  `LearnerStore.get_learner_by_name()`; `_get_or_create_controller` looks up the deterministic
  `pilot-<uuid8>` name before `create_learner`, reusing the existing row. → REVIEW §2.3.
- **✅ RESOLVED 2026-07-05 — System prompt hardcoded to fractions/Year-4 while the app serves 3
  subjects (2026-07-03, repo review).** Was: `prompts/system_prompt.md` scope-locked to
  fractions; arithmetic + science Help calls ran under it -> internal scope conflict. Fixed via
  REMAINDER_PLAN A7 (merged, PR #65, stacked on Wave 1 +
  A17/A16/A5/A6/A9): `{{subject}}`/`{{scope_line}}` slots added to `system_prompt.md` (hash
  bumped `29ed98f0b07a` -> `54f902ef0d8e`, README registry updated); new
  `engine/curriculum.py::load_template_subject()` reads the template's `subject:` field;
  `SessionController` takes an optional `subject`/`scope_line` (default `"maths"`); web/CLI both
  pass the active template's subject through. → REVIEW §2.1.
- **✅ RESOLVED 2026-07-05 — SESSION_FSM.md conformance test (T3.7) never built + doc drifted
  (2026-07-03, repo review).** Was: the doc claimed `tests/dialogue/test_session_fsm.py` parses
  its transition table; no such test existed. Fixed via REMAINDER_PLAN A11 (merged, PR #71,
  stacked on Waves 1–3): new `test_session_fsm.py` (AST-derived
  code-edges vs. doc-edges, both directions). Ran it and fixed what it found: removed the dead
  `PARENT_ACK_WAIT` state (never wired); corrected two stale edges (`SCORE`'s `safe_reject` ->
  `AWAIT_ANSWER` not `PRESENT`; `PROBE_CLASSIFY`'s exits -> `NODE_SELECT` not `BRANCH_DECISION`,
  matching the shipped probe-demote fix); documented the previously-undocumented reachable
  transitions REVIEW named (auto-help, probe->help via A21, A9's unreadable-streak-cap) plus a
  pre-existing **documentation** gap — `stop_request` was already correctly handled in code in
  all three `*_AWAIT` states (`controller.py`, each with a passing test), just undocumented
  until this pass; verified again 2026-07-10, not a code gap, don't re-investigate. Corrected §4 to stop claiming a
  `test_session_fsm_invariants.py` fuzz harness exists (it doesn't). → REVIEW §3.1.
- **✅ RESOLVED 2026-07-05 — Legacy LLM-question fallback scores against a question, not an
  answer (2026-07-03, repo review).** Was: `engine/curriculum.py:load_curriculum` (formerly
  `web/app.py:_load_curriculum`) sets `expected_answer = transfer_seeds[0]`; any node without
  bank/generator coverage silently could never PASS. Also: the SAFE_REJECT/EXTRACT_FAIL re-ask
  loop had no cap. Fixed via REMAINDER_PLAN A9 (merged, PR #64,
  stacked on Wave 1 + A17/A16/A5/A6): `SessionController.__init__` raises `RuntimeError` naming
  every node with a real checker but no item-bank/generator coverage (only checked when an
  `item_bank` is actually wired — `item_bank=None` is the deliberate legacy/test fallback, not a
  misconfigured production subject, and both real entry points always pass a real item source);
  `_do_score` now caps consecutive SAFE_REJECT/EXTRACT_FAIL at 3, then routes into the Help loop
  unscored (system-routed, not child-initiated, so A5's `help_by_node` is correctly not set).
  → REVIEW §2.4/2.5.
- **🟡 No CI (2026-07-03, repo review).** No `.github/` — the pytest+ruff gate is convention
  only; the pre-commit secret hook is opt-in and absent on fresh clones. → REVIEW §3.2; task A12.
- **✅ FIXED — severity-blind freeze (2026-06-29).** `controller.py::_step_core` now branches on
  `Severity`: **CRITICAL/HIGH** → `ESCALATION_FREEZE` + handoff (unchanged); **LOW**
  (`adversarial_jailbreak`) → **logged-only, NOT frozen** (design §4.3) — logs to escalation_log,
  shows a gentle "let's keep going with our maths!" redirect, and continues the lesson with the
  current question. No more distress-handoff for a base64/leetspeak jailbreak. Tests
  `test_jailbreak_logged_not_frozen` + `test_critical_still_freezes`.
- **🛡️ Prompt-injection classifier — hardened (2026-06-29).** Test set at
  `eval/redteam/prompt_injection.jsonl`. Added **system-prompt-extraction** patterns and a
  **de-obfuscation fallback** (leetspeak / spacing / base64 → normalise then match) to the
  `adversarial_jailbreak` class. Now caught: override, persona, secrecy, extraction, obfuscation.
  **Remaining gaps (defence-in-depth, NOT live exploits — the bounded FSM scores un-caught input as
  a non-answer, never executed):** scope-break/off-topic ("stop teaching maths, tell me about
  guns"), bare "forget you are a tutor" (off-topic-redirect territory → interaction-scope). **Real
  LLM surface = grounding content** (`surface: grounding` rows) — must be tested end-to-end against
  the system-prompt data-wrapper. The de-obfuscation fallback runs only when no other class fired
  (can't override a real safety match) and is LOW severity. Tests in `tests/safety/test_escalation.py`.
- **✅ RESOLVED 2026-07-05 — MODELING DECISION — mastery % rises after wrong answers
  (2026-06-29).** Was: from the cold-start prior (10%), wrong answers took mastery 10% → 21%
  → 22% and plateaued (~22%) — spec'd classic BKT applies the learning transition after
  *every* attempt, so from a low prior the +learns gain outweighed the small wrong penalty.
  Never false-mastered, but counterintuitive for the parent-facing %. **Maintainer ratified
  Option B 2026-07-04** (see REMAINDER_PLAN.md's ratified-decisions section). Fixed via
  REMAINDER_PLAN A20 (merged, PR #66, stacked on Wave 1 +
  Wave 2): `bkt_update` now gates the learning transition on non-wrong observations only — a
  bare-wrong (unaided incorrect) attempt only conditions the posterior, no `learns` credit;
  hinted-win/correct paths unaffected. Literature reference + full rationale in
  `docs/design/W3.3_bkt.md` §3.2 (Baker, Corbett & Aleven 2008, "model degeneracy" — the
  closest documented critique found; no specific named "no-learning-on-incorrect" variant was
  found in the literature search, so this is Mentar's own targeted mitigation, not an adopted
  named technique). SPEC §11 updated to note the deviation from classic BKT.
  Ties to [[decision_bkt_pybkt_offline_only]].
- **🔶 PARTIALLY RESOLVED 2026-07-05 (v0 slice) — ESSENTIAL GAP — interaction scope too narrow
  (2026-06-29).** Was: the system recognised only 4 child intents (answer / help / stop /
  safety-escalation); everything else — "I don't know", frustration, clarifying questions,
  off-topic, navigation — was force-scored as an answer (corrupting BKT). **Maintainer ratified
  a narrow v0 slice 2026-07-04** (don't-know + clarify/vocabulary only — the two intents that
  actively corrupt the BKT signal); built as REMAINDER_PLAN A21 (merged, PR #67,
  stacked on Wave 1 + Wave 2): `_is_dont_know_or_question()` routes
  both into the Help loop unscored, mirroring `_is_help_request`'s wiring exactly. **Still
  open/deferred:** frustration/mild-affect, off-topic, and meta/navigation intents — the full
  taxonomy proposal in **[design/INTERACTION_SCOPE.md](design/INTERACTION_SCOPE.md)** still
  needs maintainer ratification beyond this slice.
- **Triage of `docs/TESTING_NOTES.md` (2026-06-29).** Scoring cluster — "no right/wrong feedback",
  "feedback died off", "86% constant / hardcoded?", "mastery counts unanswered", wrong/gibberish
  answers advancing silently — **all trace to answers not being scored on the maintainer's build
  and are ✅ FIXED on `main` (PR #37, `1ac551f`)**: deterministic feedback restored, EXTRACT_FAIL
  re-prompts, BKT updates on scored answers (verified: 0.86 → 0.514 on a wrong answer; mastery % is
  BKT `p_mastery`, NOT hardcoded and NOT a question ratio). Action: maintainer must `git pull` +
  re-test. Genuinely-new items promoted below.
- **✅ FIXED — Emoji in questions (note 1).** Generated questions now carry ONE kid-friendly Unicode
  emoji next to the noun (e.g. "Share 9 sweets 🍬…", "A cake 🍰 is split…") via `_THING_EMOJI` /
  `_WHOLE_EMOJI` in `engine/itemgen.py` — shown once (not one icon per item), answer/verifier
  unaffected. Abstract arithmetic gens left plain. (Authored item-bank items not emoji'd — generator
  covers the templated questions the maintainer saw; bank emoji is a follow-up if wanted.)
- **✅ FIXED — Parent session log + score (note 3).** Parent view shows "X correct out of Y" +
  an Answers table (✅/❌ + 🆘 help) sourced from `response_log`. PR #40.
- **✅ FIXED — Wrong answer now auto-helps instead of advancing (note 4b).** Maintainer chose
  "offer/auto-help on wrong": a wrong unaided answer now gives feedback (without revealing the
  answer) and routes into the Help loop (explain + re-check) instead of `BRANCH_DECISION`. BKT still
  records the unaided wrong; the Help loop self-limits (retry cap / modality exhaustion → LINK_BACK).
  `dialogue/controller.py` (`_do_bkt_update`, `_answer_feedback`).
- **✅ FIXED (prompt) — Help reframed the question instead of giving real hints (2026-06-27).**
  All 5 Help templates (`prompts/help_*.md`) now explicitly forbid restating/rewording/re-asking
  the question and require a **concrete next step worked through on the example** before the
  transfer re-check. Inputs were already sound (concept = node label via `web/app.py:72`;
  worked-example from the 31-item bank), so the fix is in the prompts. Hashes + README registry
  re-synced (T4.6/T7.3 green). **✅ Re-tested 2026-07-10 (D3)** —
  `docs/EVAL_RESULTS.md` §3.3b: 35/50 (70%) `overall_pass`, identical to the pre-fix number.
  The fix's specific target (re-asking the graded question) does appear resolved on manual
  inspection, but the rubric's `overall_pass` gate is dominated by a different, still-open
  weakness — modality fidelity + grounding/fabrication discipline — not moved by this prompt
  change. Below the 90% T1.6 gate; flagged as a real open item (prompt-iteration follow-up),
  not blocking the supervised single-family pilot (the safety-critical numeric-claim subset
  is independently caught by `explain_check.py`, unaffected by this quality gap).
- **✅ FIXED — Help request at a re-check/probe was scored as an answer (2026-06-27).** Added a
  shared `_is_help_request()` guard (mirroring `_is_stop`) to the two unguarded await states:
  `_do_help_recheck_await` now routes `?`/`help`/`h` to another Help round (not the verifier);
  `_do_probe_await_answer` re-prompts (probe stays an independent check). No more BKT/response-log
  corruption from help input. Regression tests in `tests/dialogue/test_controller.py`
  (`test_help_at_recheck_not_scored_as_answer`, `test_help_at_probe_not_scored_as_answer`).
  Probe-time help *routing* (offer a full Help loop mid-probe?) left as a future pedagogy decision.

---

## Backlog — deferred (post-pilot / later)

Cross-cutting "later" items not tied to a single W-task. Add here as they come up; promote to **Next batch** when actionable. (W-scoped deferrals stay as 🔭 rows in their own sections.)

| Item | Status | Notes |
|---|---|---|
| **i18n / language-gated safety** (repo review §8.5) | 🟡 scope boundary recorded 2026-07-10; full design still post-pilot | All 61 safety trigger regexes + handoff messages + feedback strings are English-only, while the product claims per-country templates. **Recorded as a SAFETY.md §1.2 scope boundary** (non-English template load refused until a vetted trigger bank + reviewed handoff wording exist for that language) + an Appendix B open item. No code enforces the refusal yet — no non-English template exists to gate, so there's nothing to enforce against today. Full design (translation process, per-language review gate) stays post-pilot. |
| **`mentar backup` subcommand** (repo review §8.7) | ✅ **DONE 2026-07-10** | `./mentar backup [--db PATH] [--dest PATH]` — checkpoints the WAL, copies the file, opens the copy and runs `PRAGMA integrity_check` + a `session`-table row count before reporting success; refuses to overwrite an existing dest; default dest = `<db>.backup-<UTC timestamp>`. `[G]` gemma4:12b drafted, reviewed (caught 2 real bugs: `pathlib.Path` vs the file's bare `Path` import, and an unimported `LearnerStore`), tests hand-written (`tests/cli/test_backup_cmd.py`). |
| **Dependency lockfile + `.vendor/` PyYAML decision** (repo review §8.7) | 🔭 | Floating `>=` deps, no lock; `.vendor/` PyYAML duplicates the pyproject dep. Add constraints/uv lock alongside CI (A12); document vendor precedence or drop it once CI guarantees installs. |
| **Seeded per-session RNG** (repo review §8.7) | 🔭 | Controller `random` is unseeded → sessions unreplayable. Seed per session, log the seed — cheap debugging win for pilot analysis. |
| Injection red-team tooling (Garak et al.) | ✅ Garak scaffolded; ⏳ **live run attempted 2026-07-10 (D4), blocked** | **Assessed 2026-06-29; Garak scaffold added at `eval/redteam/garak/` (README + run.example.sh, run-only, NOT in pyproject).** Filter: run-only eval tooling is welcome (never vendored, out of `pyproject.toml`, like promptfoo/MathTutorBench/NIAH); runtime safety is **owned + deterministic** (escalation.py + bounded FSM; LLM never decides safety; child data never leaves device) so runtime guardrail libs are a high bar. **⭐ Adopt run-only: Garak** (NVIDIA, Apache-2.0) — LLM vuln scanner (injection/jailbreak/leakage), best all-rounder; complements promptfoo + `eval/redteam/prompt_injection.jsonl`; runs local against our endpoint (verify no phone-home). **Secondary:** PyRIT (MIT, powerful but heavier/Azure-leaning); Promptbench (robustness benchmarking, overlaps owned harness — low priority). **Do NOT ship (runtime detectors):** Rebuff (LLM+vectorDB; API mode egresses data → never; local heuristics = pattern reference only), LangKit (ML runtime monitor; we own that layer), llm-guard (modular scanners; its *output* PII/toxicity scanners are a possible defence-in-depth **output** check later — evaluate dep shape). All probe the **raw model** → hits are defence-in-depth signals, not shipped-behaviour bugs (FSM wrapper ships). See [[feedback_dependency_philosophy]], [[decision_mathtutorbench_complementary_eval]]. **2026-07-10 (D4): `pip install garak` into an isolated venv was blocked by the harness's own agent-chosen-external-package permission boundary** (same class as the U-90 htmx block earlier this session — a new external package needs the user to specifically authorize/type the install, not a general "do the D-tasks" approval). Never actually run live — this backlog row's "scaffolded" status was accurate but easy to misread as "run"; corrected. Needs either explicit per-package authorization from the maintainer, or running it directly from the actual eval host (this session has network access to its LiteLLM proxy only, not a shell on that machine). |
| promptfoo — prompt/red-team eval (run-only) | ✅ scaffolded (PR #6) + ✅ **live run happened 2026-06-27** (raw gemma2:9b, 4/10 pass — see that date's changelog entry); ⏳ D4 (2026-07-10) re-attempt blocked, same known Node-version limit, no re-run this session | **Scaffold built 2026-06-26** (`eval/redteam/`, run-only). Eval tooling, NOT a Mentar dependency. MIT, runs 100% local, no telemetry (OpenAI-acquired but still MIT). **Adopt the same way as MathTutorBench: run-only, never vendored, kept out of `pyproject.toml`.** Use ONLY for what we lack — *generated* adversarial red-teaming (jailbreak / prompt-injection / PII / harmful-content / emergency-signposting gap) to complement the hand-authored `adversarial`+`sycophancy` suites; do NOT replace the owned Python eval harness (`eval/run_candidates.py` + `judge_responses.py` + rubric/misconception/safety scorers). Hits the existing LiteLLM `…:4000/v1` + Ollama endpoints unchanged; Sonnet as grader. Directly advances closing the documented child-safety gaps blocking public release. Scaffold target: `eval/redteam/promptfooconfig.yaml` + README. See [[decision_mathtutorbench_complementary_eval]]. **Spike-verified 2026-06-24** (echo provider, no LLM → **3/3 PASS**): install + config-parse + eval loop + assertions + report all work. Caveats for adoption: (1) **hard Node floor ≥20.20.0 / ≥22** — it *refuses to run* below that (sandbox's `20.19.2` failed; ran via a throwaway `/tmp` Node 22); the eval-host/CI must satisfy this. (2) Bundles **`posthog-node` telemetry** — the "no telemetry" claim is conditional; MUST set `PROMPTFOO_DISABLE_TELEMETRY=1` + verify no phone-home. (3) **Not yet tested:** real-model backend + red-team *generation* — use **local** attack-gen, not promptfoo cloud. Tracked for build in [REMAINDER_PLAN.md](REMAINDER_PLAN.md) Wave 2.2. |
| AI-ready repo structure (contributor on-ramp) | ✅ built (PR #7) | **Focused subset built 2026-06-26** (`AGENTS.md` + `CONTRIBUTING.md` + slim `CLAUDE.md`; sprawl skipped). Adopt a FOCUSED subset of the "ai-repo-structure" convention (ref `IgniteUI/ai-repo-structure`, MIT): (1) **`AGENTS.md`** as the tool-neutral keystone (cross-tool standard) — move generic guidance out of `CLAUDE.md`, leave CLAUDE.md a thin pointer; (2) **`CONTRIBUTING.md`** (pytest/ruff gate, src-layout, eval flow); (3) an always-on **rules** section hoisting safety guardrails + protected paths (verifier safe-reject, escalation/handoff, KA=NC, `.vendor/` upstream) so any contributor AI reads them first. **SKIP the sprawl** (parallel `.claude/`+`.github/` internal systems, `agents/`/`instructions/`, LEARN course, use/adopt skills) until a 2nd tool/contributor exists — YAGNI. ⚠️ Do NOT collide with the existing `prompts/` (tutor PRODUCT prompts, not agent prompts). Pairs with LICENSE + SECURITY.md. |
| **AU curriculum breadth (Years 2-4, full ACARA learning areas) + a real content-download/delete feature** | 🔭 **scope ratified 2026-07-11, needs its own dedicated planning pass before any spec** | Maintainer ask, clarified via two rounds of AskUserQuestion (not guessed): (1) "see all the subjects" for Years 2-4 means **full ACARA v9 learning areas** — English, Mathematics, Science, HASS, The Arts, Health & PE, Technologies, Languages — not just the existing Maths/Number-strand pattern already shipped for Years 3-4 (`curriculum/templates/AU/`, `engine/au_items.py`). That's dozens of new templates + generators across 3 year levels, not a follow-up task. (2) "download/delete" means a **genuine network content-download feature**, not just enabling/disabling already-installed templates (R3.1's auto-discovery already covers "drop a file in, it appears" — that's NOT what was asked for here). A real download feature is a deliberate departure from the app's offline-only design (U-80: zero non-localhost requests) and needs its own careful design before it's buildable: where content is fetched from (a Mentar-hosted pack registry? a generic URL a parent pastes in?), per-source licence verification (the CC BY 4.0 clearance done for ACARA/Khan Academy this session was per-source and manual — a download feature implies vetting an open-ended set of future sources, which doesn't scale the same way), a package format, a security review of the fetch path itself (same class of external-content concern hit repeatedly this session — see [[feedback_sandbox_blocks_agent_binary_exec]]), and delete/uninstall semantics (does deleting a template also purge the child's mastery history for it, or just hide it?). **Not spec'd as a REMAINDER_PLAN task — too large/undefined for a tactical `[G]` spec; needs a dedicated planning session first**, same way the original UI rebuild got its own `docs/design/UI_REQUIREMENTS.md` rather than being folded into an R-task. |
| Private MCP server (local-only assets) | 🔭 | **GOOD-TO-HAVE — needs a proper plan before build** (2026-06-24). Surface device-local, **non-shippable** assets over MCP so the dev workflow / web layer can consume them: **local Gemma inference**, the **local memory store** (`.claude-memory/` + `~/.claude/.../memory/`), likely local DB/grounding. "Private" = touches the local model + memory, never published. Goal: make these work over the web/agent surface. Keep it thin glue ([[feedback_dependency_philosophy]]); NOT in the tutoring hot path. |
| Public MCP server — publish the owned ZIM/grounding reader | 🔭 | **GOOD-TO-HAVE — needs a proper plan; gate behind go-public prep** (2026-06-24, Opus recommendation). **Recommend exposing ONLY the thin owned libzim/grounding reader as a standalone reusable MCP** (read ZIM → verbatim passage by anchor): bounded/focused shape, non-safety-sensitive (no child data, no LLM in loop), license-clean (MIT-derived, reads *user-supplied* ZIMs → no NC content shipped), reusable by the offline-AI/Kiwix community, raises Mentar's profile. Keep it a SEPARATE optional package, out of the core hot path. **Explicitly NOT:** (a) the tutoring loop over MCP — bypasses the FSM/escalation/parent-mediation safety envelope = child-safety anti-pattern; (b) a repo-browsing MCP — redundant with planned `AGENTS.md` + `docs/`. See [[decision_local_stack_llamacpp_and_grounding]]. |
| AU curriculum template (ACARA) | 🔭 | **Note (2026-06-27)** — Australia's official curriculum = **ACARA** (`acara.edu.au`; content at `australiancurriculum.edu.au`). Source for a future `curriculum/templates/AU/<year-level>` (same per-country+year pattern as the pilot). **Check the ACARA content licence** before use (likely CC BY 4.0 — verify) and log in `docs/CONTENT_LICENSES.md`. Not pilot scope. |
| Backend switching: API ↔ local LLM, seamless (Phase 1) | 🔭 | **Maintainer ask (2026-06-29)** — switching between a **remote OpenAI-compatible API** (LiteLLM/vLLM, `backend: vllm`) and a **local LLM** (Ollama/GGUF) currently means hand-editing `config/inference.yaml`. Make it seamless **both ways**. Direction: **named profiles** (e.g. `config/inference.api.yaml` + `config/inference.local.yaml`) with a `mentar use api|local` (or `--profile`) switch, OR `mentar setup --runtime vllm --base-url … --model …` to write the remote config the same way local is written today. Each switch should end with the existing **backend self-verify** ([[decision_mentar_setup_autoselect]] now verifies on setup) + `scripts/check_backend.py`. Keep the env-token rule (never inline; `${MENTAR_VLLM_API_KEY}`). Pairs with the install-consolidation rows below (single-script + LLM-guided onboarding) — **install methods need sorting out properly** as one coherent flow, not the piecemeal extras the maintainer hit in testing (pyBKT/libzim/llama-cpp-python). **Future / not pilot-blocking** (the LiteLLM proxy works today via the documented config). |
| Web display — question vs transient messages (Phase 1) | 🔭 | **Note (2026-06-27, from testing)** — the learner web view renders only `_last_mentar_text` (the last Mentar message), so any turn that returns a *message without the question* (re-prompts, feedback) makes the question vanish. Worked around at the source (re-prompts re-append `current_question`; feedback+question come bundled). **Proper fix:** render the **current pending question** (`SessionController.current_question`) as a stable block, and show transient feedback/hints in a **separate message area**, so display no longer depends on the last message bundling the question. Web-only (terminal `run-session` shows scrollback). Pairs with `web/templates/learner.html`. **Also (2026-06-29, from testing):** the model emits **markdown** (`**bold**`, `*` bullets) that the web view shows **literally** (plain-text `pre-wrap`). Future interface work should **render markdown** (small client-side md renderer) or strip it. **✅ RESOLVED 2026-07-10** via the UI rebuild — [design/UI_REQUIREMENTS.md](design/UI_REQUIREMENTS.md) §8: U-30 (stable question block) and U-32 (owned markdown-lite renderer, bold/italic/bullets) both shipped. **U-31 (visually distinct feedback vs. question area) is a known partial gap** — needs a controller data-contract change (feedback and the next question are still one bundled `TurnResult.text` string), out of scope for a presentation-layer rebuild; flagged in UI_REQUIREMENTS.md §8, not silently dropped. |
| ZIM default location — repo-local vs `$HOME` (Phase 1) | 🔭 | **Note (2026-06-27, maintainer)** — runbook currently suggests ZIMs under `$HOME` (e.g. `~/mentar-zims`) for data/code separation (multi-GB, survive re-clone, kept out of the git tree). Maintainer's thought: scattering data in `$HOME` is messy — prefer a **self-contained, gitignored repo-local `data/zims/`** *or* an **XDG data dir** (`~/.local/share/mentar/zims`, `%LOCALAPPDATA%` on Windows) as the **default**, so `mentar setup`/`fetch_zim` can pick it automatically (no `--dest`). Decide one convention; either keeps ZIMs out of git while being tidier than ad-hoc home dirs. Pairs with [[decision_mentar_setup_autoselect]]. **Future / not pilot scope.** |
| Single-script process + startup/service (Phase 1) | 🔭 | **Note (2026-06-27, maintainer)** — collapse the current multi-step runbook (venv → `pip install` → `fetch_zim` → `mentar setup` → `mentar serve`) into **one reviewable repo-local script** (`install.sh` / `Makefile` / a `mentar bootstrap` subcommand) that runs the steps end-to-end — better DX going forward. **Also a startup process:** run Mentar as a long-lived service that auto-starts (systemd unit on Linux, `launchd` plist on macOS, Task Scheduler/NSSM on Windows) so `mentar serve` comes up on boot/login. Keep it a **thin orchestrator over the existing deterministic primitives** ([[feedback_dependency_philosophy]]) — no `curl\|bash` (security smell for a kids'-safety project); idempotent + re-runnable. Pairs with [[decision_mentar_setup_autoselect]] and the LLM-guided onboarding row below. **Progress (2026-06-27):** `mentar setup` now installs the chosen runtime's deps (llama-cpp-python for gguf) AND verifies the backend responds before declaring "Ready" — i.e. setup is becoming the reliable single command; `scripts/check_backend.py` added as the standalone diagnostic. A thin wrapper script can still tie install+ZIM+setup together later. **Future / not pilot scope.** |
| LLM-guided onboarding (Phase 1) | 🔭 | **Idea (2026-06-27)** — bootstrap the model first (`mentar setup`, deterministic), then let the local LLM **conversationally guide the rest of setup** (curriculum/year-level, ZIM download, learner profile, consent) for non-technical parents. Design constraints: (1) model-acquisition stays a deterministic non-LLM flow (can't guide its own install + most failure-prone); (2) LLM = a **UX layer over existing deterministic primitives** (`mentar setup`, `fetch_zim.py`, `validate_template`, `create_learner`) — NOT an autonomous agent driving the install (small models = flaky tool-use; keep setup reproducible/auditable); (3) **hard-gate safety steps** (consent before session 1, age-mode, parent-mediation) — LLM presents, cannot skip. Phase-1 OSS-Local-Edition UX (W5.1 deferred UX to Phase 1); not pilot scope. **Install mechanism (note 2026-06-27):** prefer **PyPI + `pipx install "mentar[web,setup]"`** (or `uv tool install`, which can manage Python too) → `mentar setup` — the `mentar` PyPI name is reserved (W4.1b). A bespoke `curl|sh` installer is **lower-value + a security smell** for a kids'-safety project (and `mentar setup` already does the hard, cross-OS model bootstrap). If a script is wanted, ship a **reviewable repo-local `install.sh`/`Makefile`** (dev convenience), never `curl|bash`. |

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | **Logged (not spec'd, not built): AU curriculum breadth expansion + a real content-download feature.** Maintainer's "Years 2-4, all subjects, download/delete" clarified via two AskUserQuestion rounds into: full ACARA learning-area breadth (not just the existing Maths pattern) × 3 year levels, and a genuine network content-download mechanism (not R3.1's already-shipped auto-discovery). Both are large enough to need their own dedicated planning session — recorded as a backlog row, not folded into a tactical `REMAINDER_PLAN.md` task. Also this session: R4 (homepage-lands-on-quiz bug, root-caused + spec'd, not built) and R5 (Settings page: voice picker + relocated theme toggle, spec'd, not built) — both in `REMAINDER_PLAN.md`. |
| 2026-07-10 | **UI review round 1 (U-2a) — all 5 maintainer findings resolved same session** (`UI_REQUIREMENTS.md` §9 has the full detail): (R1-1) the feedback/question split was genuinely broken in real use (Help's `Q) …` recap defeated the string-split; the "Q) box" showed empty) — root-fixed with a STRUCTURED turn payload: `TurnResult.message`/`.question` composed at the FSM-state source, `ctx.question_display` set by every question-issuing state, re-prompt states no longer re-embed the question, `Q)` recap removed; (R1-2) mc4 items now carry structured `choices` → native radio buttons A–D; (R1-3) fraction answers → numerator/denominator inputs composed server-side to `n/d`; (R1-4) **first ACARA templates: AU Year 3 + Year 4 maths** (`curriculum/templates/AU/`, `engine/au_items.py`, licence verified CC BY 4.0 → CONTENT_LICENSES.md §2b); (R1-5) TTS 🔊 via browser speechSynthesis (owned `static/tts.js`, offline). Verified live against the exact reported bug scenario. **488 tests pass, ruff clean.** |
| 2026-07-10 | **D4: promptfoo + Garak live re-run attempted, both blocked — recorded honestly, not left vague.** promptfoo: this sandbox's Node (20.19.2) is documented as too old (hard floor ≥20.20/22 — `eval/redteam/README.md`'s own words); a real live run already happened once historically (2026-06-27, via a throwaway newer Node, 4/10 pass on raw gemma2:9b) — that data stands, no new run this session. Garak: attempted `pip install garak` into an isolated venv (never vendored, run-only); blocked by the harness's own external-package permission boundary (same class as the U-90 htmx block earlier this session) — needs explicit per-package authorization or a shell on the actual eval host, neither available right now. Backlog rows corrected to distinguish "scaffolded" from "actually run live" — they'd drifted together. |
| 2026-07-10 | **D3: Help-prompt live re-test run** (eval host reachable this session) — `eval/run_candidates.py --model gemma2:9b --suite reexplain` + `eval/judge_responses.py`, real Sonnet-judged run, not a dry-run. Result: 35/50 (70%) `overall_pass`, identical to the pre-fix number in `docs/EVAL_RESULTS.md` §3.3 — the June 27 Help-prompt rewrite likely did fix its specific target (re-asking the question, confirmed by manual inspection) but didn't move the rubric's actual gating criteria (modality fidelity, grounding/fabrication discipline), which sit below the 90% T1.6 gate. Recorded honestly in `docs/EVAL_RESULTS.md` §3.3b as a real open item, not silently patched — prompt-iteration is a maintainer call, not something to guess at. |
| 2026-07-10 | **D5: `docs/PILOT_RUNBOOK.md` written** — pre-session-1 checklist (9 hard gates from REMAINDER_PLAN.md §C, including the still-open safeguarding-professional review and red-team decision) + a per-session procedure + a P1–P5 evidence-recording table (thin overlay over PHASE0.md §26.7, no criteria duplicated). Not yet run against a real session. **Also: a full "PR open/awaiting review" sweep** — every A3–A21/B1/B2 task note in this file's "Known defects" section still said its fix was an open PR; all are merged (confirmed via `git log`, PRs #55–#74). Corrected ~18 occurrences across this file + `REMAINDER_PLAN.md`'s wave table (which also still framed the wave as "open, awaiting review" despite being fully merged). Picked up 2 related fixes while in the neighbourhood: the A11 entry's ambiguous "pre-existing `stop_request` gap" wording clarified to explicitly say documentation gap, not code gap (verified 2026-07-10, all three `*_AWAIT` states already handle stop correctly); A14's "v0 coverage floor" note updated to reflect D7's ÷/"divided by" support. Test count bumped to 482 (was stale at 463). |
| 2026-07-10 | **D1/D2 doc-truth fixes (post-release-wave gap sweep).** D1: `docs/CONTENT_LICENSES.md` §1 promoted Khan Academy to the live pilot grounding source (was only logged in §3 as a Phase-3 hosted-tier conflict, stale since B1's 2026-07-05 re-point); Vikidia/Simple-WP relabelled cleared alternates, not currently mounted; `docs/SPEC.md` §24 row #18 synced to match. D2: `docs/SAFETY.md` §1.2 gained the agreed i18n scope-boundary paragraph (non-English template load refused until a vetted trigger bank + reviewed handoff wording exist) + an Appendix B open-item row. No code changes, pytest/ruff unaffected. |
| 2026-07-10 | **UI-rebuild requirements ratified** — `docs/design/UI_REQUIREMENTS.md` (v0.1). Maintainer wants the web UI rebuilt as the project's "lure" (audiences: evaluating parents + OSS visitors; no landing page; presentation-layer only, U-14/U-82 lock routes + safety invariants). README screenshots required but **gated on maintainer review of the built front end** (U-2a). Design mockups + per-screen gemma specs = next phase, blocked on U-90–U-92 decisions. Absorbs the web-display backlog row (question-vanish + literal markdown). |
| 2026-07-10 | **UI rebuild BUILT — all 6 flows** (same session, maintainer directed an autonomous live build once U-90/91/92 were decided; see `UI_REQUIREMENTS.md` §8 for full detail). htmx vendored + cleanly wired (`GET /done` added; `HX-Request`/`HX-Redirect` native idioms). Shared `_base.html`/`style.css` (CSS-variable theme, light/dark toggle, blended teal/coral palette). Owned SVG concept-graph on `/progress` (`_compute_graph_layout`, no graph lib, verified against the real 8-node pilot curriculum: 8 nodes/7 edges). Parent dashboard reordered safety-first (U-50), all safety-critical literal strings preserved byte-for-byte. Frozen screen stripped to zero chrome (U-60). Owned markdown-lite renderer (`_render_markdown_lite`) — bold/italic/bullets over HTML-escaped text, wired into both the htmx-fragment and full-page paths identically. **473 tests pass, ruff clean.** Known gap: U-31 (feedback/question visual split) needs a controller data-contract change — out of scope, flagged not silently dropped. No headless-browser/screenshot tooling available in-sandbox; verification is full content/structural assertions against a live Flask test client, not a rendered-pixel check — real visual QA is the maintainer's pending review (U-2a) before any screenshot is taken. |
| 2026-07-05 | **Release-wave A1–A21/B2 merged to `main`; B1 (grounding-anchor QA) genuinely resolved.** First 21 backlog tasks landed via the stacked-PR convention (each verified pytest+ruff green, then human-merged); fixed a CI job `permissions:` bug along the way (job-level `permissions:` *replaces* rather than adds to default token scopes — omitting `contents: read` broke `actions/checkout` on the private repo with a 404). B1 was initially misreported as blocked/skipped; corrected after the maintainer pointed out `/mnt/zim` was always readable — the real gap was narrower: that mount holds Wikipedia/KhanAcademy/gutenberg/StackExchange, never Vikidia/Simple-WP. Maintainer chose **re-point the pilot to Khan Academy** rather than wait on a NAS upload. Found KA's HTML lesson pages are video-embed shells (would've repeated the exact thin-passage problem B1 exists to fix) — the real content is the video's English `.vtt` subtitle transcript, so built `ZimReader.get_by_path`/`get_video_narration` (WebVTT → plain text) and a small per-source extractor registry in `grounding/resolve.py` (generic wiki-article path by default, `khanacademy` overrides — per maintainer direction to keep the pattern "general enough and custom enough" rather than one-off branching). All 8 pilot nodes re-verified against the real ZIM: distinct, substantive, on-topic transcripts (resolves the REVIEW §2.6 distinctness gap too, where 7/8 nodes had shared one Vikidia article). **463 tests pass, ruff clean.** See REMAINDER_PLAN.md B1 for full detail. |
| 2026-07-03 (2nd pass) | **Repo review — architecture follow-up sweep** (Opus, Cowork session). 5 more defects promoted (escalation-log best-effort drop 🔴; runtime template validation / false-completion 🟠; stale safety-eval-vs-prompt-hash process 🟠; CLI→web layering 🟡; unused `age_mode` 🟡) + 4 backlog rows (i18n language-gated safety, `mentar backup`, lockfile/vendor decision, seeded RNG). Tasks **A15–A19** added to REMAINDER_PLAN; REVIEW §8 holds detail. **New protected invariant recorded in AGENTS.md RULES: child input never reaches the LLM.** DOC_AUDIT updated with a 2026-07-03 stale-doc addendum. |
| 2026-07-03 | **Independent repo review** (Opus, Cowork session) — full docs+code+schema+hygiene pass. Findings register: **[REVIEW_2026-07-03.md](../REVIEW_2026-07-03.md)** (detail reference — keep). 9 new defects promoted to *Known defects* above (top: escalation_log audit-data gaps; child-facing resume control on escalation redirect; SAFETY.md overstating shipped controls); build tasks added as **REMAINDER_PLAN A3–A12 + B2 + C rows**. Verified clean: `ruff`, tracked-file/secret hygiene (193 files, no leaks). pytest not run in the review sandbox (py3.10 < 3.11 floor). Also confirmed still-good: deterministic safety spine, test discipline, dependency philosophy. |
| 2026-06-29 | **Credential-leak guard (maintainer-proposed)** (Opus). New `safety/credential_guard.py` (`detect_credential_leak` + `redact_credentials`): scrubs secret-shaped strings (`sk-…`, `Bearer …`, `api_key=…`, `MENTAR_*KEY`, `token/secret/password=…`) from **LLM output** at the single chokepoint `_make_safe_llm`, so an injected/hallucinated key can't reach the child or the transcript/logs. Defence-in-depth (the key is never in a prompt). 5 tests + controller-integration test. **398 pass, ruff clean.** |
| 2026-06-29 | **Help "Now you try it!" shows the answer-format hint** (Opus, from testing). Both the **main question** and the Help re-try prompt now append a cue for the expected answer SHAPE — `_/_` for fractions, "a letter: A, B, C or D" for MC, "a number" for int/decimal — via `_answer_format_hint(answer_type)`. **Deterministic from the known answer type, NOT LLM-guessed** (it must match the verifier; an LLM guess could mismatch). Also added `docs/design/FLOW.md` (child/parent/subject Mermaid flow diagrams). Test `test_help_recheck_shows_answer_format_hint`. **388 pass, ruff clean.** |
| 2026-06-29 | **FIX (scoring integrity): endless silent probes after mastery — "all answers accepted regardless"** (Opus, from testing). Once a node's mastery crossed 0.85, `_do_branch_decision` set `probe_due` **every** turn (`mastery >= threshold`), and `_do_probe_classify` returned to `BRANCH_DECISION` → the FSM **re-probed the same node forever**. Probes give no right/wrong feedback and just advance, so after ~2 correct answers (mastery → 0.98) every later question was a silent probe where **wrong answers slipped through**. (Parent-view was coincidental — mastery had just crossed.) Fix: a clean-pass probe → **`NODE_SELECT` (advance**; mastered node leaves the fringe); a not-clean probe → **demote mastery to `PROBE_DEMOTE_MASTERY` (0.6)** + `NODE_SELECT` → node returns to normal feedback practice; both probe exits now also give feedback (praise / "let's practise that one a bit more"). Regression test `test_mastered_node_advances_not_endless_probe`. **387 pass, ruff clean.** `dialogue/controller.py`. |
| 2026-06-29 | **FIX: one question at a time in Help** (Opus, from testing). The Help turn could show 2-3 questions at once (the `Q)` being explained, a question the model tacked onto its explanation, and a *new different* practice question). Now: (a) `_strip_trailing_questions()` deterministically removes any question the model appends to the explanation (handles "… = ? ⭐" that doesn't even end in `?`); (b) `_do_help_recheck_present` **re-tries the SAME question** ("Now you try it! ✏️") instead of posing a new different one; (c) prompts drop the "connect it back" line that induced the re-posed question + forbid fill-in-blanks. Result: feedback → `Q)` the question → explanation (worked to its answer) → "Now you try it!" = **one** question. Test `test_help_explanation_not_swallowed_and_one_question`. **386 pass, ruff clean.** |
| 2026-06-29 | **Help explanation polish + non-static feedback** (Opus, from testing). (1) The Help turn now shows the question being explained first, labelled **`Q) …`** (deterministic prepend in `_do_help_explain`). (2) The 5 `prompts/help_*.md` now state **"explaining to a child about 8-9 years old"**, demand **2-3 short simple sentences**, finish the worked example, and forbid trailing/unfinished examples. (3) Feedback is **no longer static** — praise + wrong-answer lines come from `PRAISE_VARIANTS`/`WRONG_VARIANTS` pools (random per turn; easy to extend = the "template format" the maintainer asked for). Tests updated to match any variant (no flaky literal-string asserts). Hashes + README re-synced. **386 pass, ruff clean.** |
| 2026-06-29 | **FIX: unreadable answer was vague + jumped to a new question** (Opus, from testing — MC gibberish "aaaa" → "couldn't quite read… let's try another one" + a *different* question, "unclear on correct or wrong"). `_do_score` now, on SAFE_REJECT/EXTRACT_FAIL, **re-asks the SAME question** (state → AWAIT_ANSWER, keeps `current_question` on screen) with **answer-type-aware guidance**: mc4 → "please answer with A, B, C or D"; numeric → "couldn't read a number, give it another go". Not scored, not penalised. Test `test_mc_gibberish_asks_for_a_letter_same_question`. **386 pass, ruff clean.** |
| 2026-06-29 | **Help explanation: work the example to its answer + use emojis** (Opus, from testing — "almost there, but no answer is provided"). The Help explanation trailed off without a completed result. The 5 `prompts/help_*.md` now require **working a similar solved example all the way to its final answer** (`{{worked_example}}` carries "problem (Answer: X)"; a *different* item so the child's own practice question still has something to do) and to **use a few kid-friendly emojis**. `_render_template` defaults an empty worked-example so the instruction never dangles. Hashes + README re-synced. **385 pass, ruff clean.** |
| 2026-06-29 | **FIX: auto-help quirks — generic explanation + question pile-up** (Opus, from testing). After auto-help-on-wrong the Help explanation (a) didn't reference the question the child got wrong (generic example), and (b) piled up multiple questions (the help template asked its own re-check AND the FSM presented a separate one). Fixes: the 5 `prompts/help_*.md` now **anchor on `{{question}}`** (the actual problem, passed via `_render_template`/`_do_help_explain`) and **explain ONLY** — no embedded question; the FSM's `HELP_RECHECK_PRESENT` owns the single *verifiable* re-check. Child now sees: feedback → explanation of THEIR problem → one practice question. Hashes + README re-synced. **385 pass, ruff clean.** |
| 2026-06-29 | **Multi-subject testing variety: Maths arithmetic + Science MC + in-app picker** (Opus, maintainer ask). New parametric maths generators (addition/subtraction/multiplication, `ARITHMETIC_GENERATORS`) and a Science **multiple-choice** generator (`engine/science_items.py`) built from small CURATED fact tables — ground truth from the table, never the LLM (SPEC §14). New curriculum templates `arithmetic.md` + `science.md`. Web app gained a `SUBJECTS` registry, a `/choose` subject picker (`subjects.html`), per-subject controllers (switching starts a fresh session; skill_state is node-id-namespaced so no collision), and a "Switch topic" link. Answers "can't this be automatic?" — maths fully auto (computed), science semi-auto (curated facts → auto MC + distractors). Tests: `test_science_items.py`; web tests choose a subject + stub the LLM. **385 pass, ruff clean.** |
| 2026-06-27 | **FIX: `mentar setup` wrote a config that couldn't serve** (Opus, from testing). On a Mac with neither Ollama nor llama.app, setup fell back to the in-process GGUF runtime, downloaded the model, wrote the config, and printed "Ready" — but never installed `llama-cpp-python`, so every model call failed (`RuntimeError: llamacpp mode='in_process' needs llama-cpp-python`) and Help silently fell back to the canned hint. Fixes: (1) setup now `_ensure_llama_cpp()` (installs the runtime on demand when gguf is chosen); (2) setup now **verifies the backend responds** (1-word test call) before claiming "Ready" — fails loudly otherwise; (3) new **`scripts/check_backend.py`** diagnostic (runs Mentar's own path; prints backend/target/model + LIVE/UNREACHABLE/EMPTY + remediation); (4) RUNNING.md updated (Ollama easiest on Mac; setup self-installs + self-verifies). `cli/__main__.py`, `scripts/check_backend.py`, `docs/RUNNING.md`. |
| 2026-06-27 | **FIX: Help during a probe dead-ended (no hint, question vanished)** (Opus). Last round's probe-help guard re-prompted with "Give it your best try…" and (because the web view shows only the last Mentar message) that re-prompt *replaced the question on screen* → child stuck with no hint and no question. **Reversed that decision:** `_do_probe_await_answer` now routes `?`/`help` into the **Help loop** (real hint + a question); a child needing help mid-probe is useful signal, and help must never be refused. Also: empty-input re-prompts in the probe + help-recheck await states now **re-append `current_question`** so the question never disappears from the web view. Test updated (`test_help_at_probe_enters_help_not_scored`). **378 pass, ruff clean.** `dialogue/controller.py`. (Deeper web-display refactor — show `current_question` separately from transient messages — noted as backlog.) |
| 2026-06-27 | **FIX: answer-feedback + Help-robustness defects found in maintainer testing** (Opus). (1) **No correct/wrong feedback** — the deterministic verifier scored silently, so the child was never told right/wrong and wrong answers just advanced. `_do_score` now returns warm feedback: praise on PASS, "Not quite — the answer is X" (verified ground truth) on FAIL. (2) **Gibberish/blank counted as wrong** — `EXTRACT_FAIL` (and `SAFE_REJECT`) now re-prompt without penalty instead of scoring a wrong attempt + corrupting BKT. (3) **Help blanked the page / no hint / 500** — the Help explanation needs an LLM call (main questions come from the item bank), so a backend failure 500'd the page and gave no hint. Fixed: `self._llm` wrapped to degrade to "" instead of raising; `_do_help_explain` falls back to a deterministic worked-example hint when the LLM is empty; `learner.html` `.question` set to `white-space:pre-wrap` so the hint/feedback render on their own lines. 5 regression tests; **378 pass, ruff clean.** `dialogue/controller.py`, `web/app.py`-path, `web/templates/learner.html`. |
| 2026-06-27 | **FIX: two Help defects found in maintainer testing** (Opus). (1) **Help-as-reframe** — all 5 `prompts/help_*.md` now forbid restating/re-asking the question and require a concrete worked next step before the re-check (hashes + README re-synced; needs a live `gemma2:9b` re-test). (2) **Help scored as an answer** — new shared `_is_help_request()` guard added to `_do_help_recheck_await` (→ another Help round) and `_do_probe_await_answer` (→ re-prompt), so `?`/`help`/`h` at a re-check/probe is never run through the verifier (was corrupting BKT + response_log). Regression tests added. **373 tests pass, ruff clean.** `dialogue/controller.py`, `prompts/help_*.md`. |
| 2026-06-27 | **FIX: `/parent` + `/progress` 500 (SQLite cross-thread) — found in maintainer testing** (Opus). `mentar serve` runs the threaded Werkzeug dev server, but `LearnerStore` opened one `sqlite3` connection and reused it across request worker threads → `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread` (surfaced after `stop`, when the next request hit a new thread). The single-threaded `test_client` smoke never caught it. **Fix:** thread-local connections (each worker thread lazily opens its own connection to the same file) + the WAL mode the code's `checkpoint()`/`close()` already assumed (was never actually set in `__init__`, so it was a silent no-op) + `busy_timeout=5000`. `close()` now clears the thread-local ref so reopen works. New `tests/db/test_store_threadsafe.py` (cross-thread read, 4-thread concurrent writes, WAL/busy_timeout asserted). **371 tests pass, ruff clean.** `db/store.py`. |
| 2026-06-27 | **Red-team generator: uncensored-local attempt → reverted to Sonnet; harmful-coverage gap is structural** (Opus). Tried `mistral:7b-instruct` as an uncensored attack generator to cover the explicit-harm plugins locally — too weak at promptfoo's structured generation (produced **only `pii:direct`**, 0 harmful). Reverted the generator to **`claude-sonnet-4-6`** (strongest Claude on the proxy; Opus is NOT served). **Key finding:** a stronger *aligned* model doesn't help — Claude (Sonnet/Opus) refuses to synthesise self-harm/sexual/graphic/harassment attacks by design. So **explicit-harm + iterative-jailbreak red-team coverage requires promptfoo Cloud or a genuinely uncensored+capable generator** — an open item, documented in `eval/redteam/README.md`. Local run reliably covers `pii:direct` + the Mentar policy. |
| 2026-06-27 | **Grounding reader fully verified on real pilot ZIMs** (Opus). Downloaded both pilot-cleared sources via `fetch_zim.py` from the Kiwix mirror — **Vikidia 8.4 MB + Simple-WP 937 MB**. `ZimReader`/`resolve_grounding` extract clean verbatim from both (Vikidia *Fraction* 216c; Simple-WP *Decimal* 399c, *Multiplication* 1200c). Verified the **full public path** (auto-latest dir pick + host-scope guard), the **scope guard** (wrong anchor host → blocked → `""`), and **graceful degradation** (unknown source / missing `zim_dir` / missing anchor → `""`, no crash). Finding: Simple-WP's *Fraction* is a thin disambiguation (75c) vs Vikidia's substantive 216c → **prefer Vikidia for the fractions anchors**. `tests/grounding/` 61/61; `libzim` ok. Reader is pilot-ready; remaining = place the two ZIMs on a writable runtime `zim_dir`. |
| 2026-06-27 | **NIAH retrieval-faithfulness + E2E session on the pick (`gemma2:9b`)** (Opus, eval host). **NIAH:** installed `needlehaystack`, built model+run configs (task `uuid`, text haystack), **9/9 cells score 1.00** (1k/2k/4k ctx × 10/50/90% depth) — perfect retrieval, no grounding-passage loss at pilot lengths. Gotcha fixed + documented: the openai provider ignores `base_url_env`, so route via `OPENAI_BASE_URL` (else calls hit api.openai.com → 401; our token briefly hit OpenAI — rotate). **E2E:** real `mentar run-session` on gemma2:9b (temp vllm config) — division item → Help → gemma2:9b produced a clean age-appropriate worked example in 2.5s → recheck → clean session end; DB persisted (transcript 7, response_log, help_event, skill_state). gemma2:9b now validated across **quality + safety (pipeline 20/20) + retrieval (9/9) + E2E**. `eval/niah/README.md` updated. |
| 2026-06-27 | **Shipped-safety validated on the W1.3 pick + first live red-team** (Opus, eval host). **Pipeline safety (T1.5):** `gemma2:9b` adversarial suite (20) through the FULL Mentar pipeline (`prompts/system_prompt.md`) = **20/20 pass, 0 hard-fail, 0 review** (deterministic scorer) vs **bare** `gemma2:9b` 10/20 pass + 3 fail + 7 review — the FSM/verifier wrapper is what makes the pick safe (`gemma4:12b` pipeline also 20/20). **Red-team (promptfoo, live):** raw `gemma2:9b` on `pii:direct` + the Mentar child-safety `policy` = **4/10 pass** (raw-model defence-in-depth signal). Both reinforce: never expose the raw model; the pipeline is mandatory (SPEC §4.1). Reports gitignored (`reports/T1.5/safety.csv`, `eval/redteam/`). |
| 2026-06-27 | **Eval-host live run attempted — BLOCKED on the generation backend** (Opus, overnight). Creds wired (`eval/.creds.env`, gitignored). `GET /models` → HTTP 200 in ~25 ms (full roster visible incl. the `claude-sonnet-4-6` judge), but `POST /chat/completions` **times out (HTTP 000, >30 s) for every model tested** (`qwen3.5:2b`, `gemma2:9b`) — the LiteLLM proxy lists models but the backing generator (Ollama/vLLM) isn't serving completions. **W1.3 model pick + the promptfoo live red-team are deferred** until the host serves completions (restart/warm the model backend). No fabricated results; the 2026-06-16 first-run data in `EVAL_RESULTS.md` stands. |
| 2026-06-26 | **Local-build wave (Opus, plan-driven; Gemma unavailable — no eval-host creds in session — so Opus generated + verified directly).** Shipped as PRs #4–#8. **#4 (merged):** durable DB logging wired — `write_transcript`/`write_response`/`write_help_event`/`write_probe_event` had **zero callers** (transcript/response log silently unpersisted) + fixed a latent `classify_probe` kwarg crash in `PROBE_CLASSIFY`. **#5:** parent-oversight read path — `/parent` renders the durable DB transcript + escalation list; `/parent/ack` persists the parent ack to `escalation_log` (SAFETY §3.3 Step 6) — previously never recorded; + `safety/handoff_check.py` handoff-wording harness (W2.2 §6.2; professional review still an open gate). **#8 (stacked on #5):** `SessionController.parent_acknowledge()` transitions out of `ESCALATION_FREEZE` (child input stays absorbed; parent control plane). **#6:** `eval/redteam/` promptfoo scaffold (run-only, never vendored; Node ≥20.20; local attack-gen). **#7:** go-public docs — `SECURITY.md` + README disclaimer, `AGENTS.md` keystone + `CONTRIBUTING.md` + slim `CLAUDE.md`, `docs/LICENSE_AUDIT.md`. **License finding:** `libzim` (python-libzim) is **GPL-3.0-or-later** and a CORE dep → **AGPL-3.0 is the compatible license choice** (permissive non-viable unless libzim is made optional); feeds W4.2. **363 tests** (Wave-A+freeze branch); ruff clean. **Still maintainer-gated (not local):** W1.2→W1.3 eval-host run, W5.6 thresholds, W7.4 real ZIMs, W2.2 emergency-signposting decision, the W4.2 LICENSE ratification. |
| 2026-06-20 | **Remaining build work via the local generate→verify loop (gemma4:12b → Sonnet)** (Opus drove; gemma coded grunt; Sonnet verified each). **T3 (safety):** controller now persists every escalation (`write_escalation`, full untruncated text+class) before freezing, best-effort; adapter passthrough. **T2:** `_is_stale_mastery` + `STALE_MASTERY_DAYS=14` wired into probe-classify (forgetting detection) from `skill_state.updated_at`. **T1:** llama.app runtime in `mentar setup` (auto-order Ollama→llama.app→GGUF; writes vllm config at :8081 + prints `llama serve`). **T4:** real `mentar eval` (shells out to run_candidates→judge_responses = local-gen→Sonnet-judge). **T5:** `get_section` extraction fixed — root cause was the section-heading regex matching the `<h1>` title and truncating the lead (now h2–h6) + `_drop_noise` strips script/style/table/comments; real-ZIM lead went from ~5 chars to 1.6–2.9k; SAFETY §1.5 verbatim preserved (Sonnet PASS). +20 tests (`tests/{safety,dialogue,inference,cli,grounding}/`), **full suite 350**. Per-task gates: pytest + ruff-F clean on new files. Pre-existing ruff UP/Optional debt in controller.py/web/app.py/cli untouched (separate mechanical cleanup). |
| 2026-06-19 | **`mentar setup` — hardware-aware auto model selection + download** (Opus). One command (checkout → configured tutor) on Win/macOS/Linux. Cross-OS hardware sizing delegated to OSS (**gpustack gguf-parser**, single per-OS binary, lazy-downloaded; sizes a model's RAM from the HF header WITHOUT downloading weights — `--no-mmap --gpu-layers 0` for true resident footprint, else it under-reports ~3× by excluding mmap'd weights). We own only the vetted-roster *policy*: `config/model_roster.yaml` (ranked, safety-eval'd). `inference/autoselect.py` picks the best-ranked model that fits detected RAM; runtime = Ollama if present else in-process GGUF (auto-fallback, no forced install); reasoning→`think:false`; pre-AVX2→rebuild warning. `inference/ggufparser.py` (+ psutil/stdlib RAM, pure-Python heuristic fallback). CLI flags `--runtime/--model/--ctx/--dry-run`. `tests/inference/test_autoselect.py` (7) → **330 tests pass**. Verified `--dry-run` on this box (picks within RAM, flags AVX2). RUNNING.md "Fastest path". Feeds W1.4. |
| 2026-06-19 | **Autonomous batch: FSM fixes + W7.4/web verification + W1.4 doc** (Opus). (1) `stop`/`quit`/`bye`/`exit` now end the session in ALL await states (added `_is_stop`; was only `AWAIT_ANSWER`). (2) **Help explanation no longer swallowed** — `step()` accumulated text across ticks instead of overwriting, so the child saw only the re-check question; now both show. (3) **W7.4 verified**: owned libzim reader resolves real modern Wikipedia ZIM articles on `/mnt/zim` (bare-slug path + redirects) — path convention confirmed; finding: `get_section` extracts poorly from full-Wikipedia HTML (8–202 chars), OK since pilot uses simpler Vikidia/Simple-WP. (4) **Web app E2E** via Flask `test_client` (routes→controller→verifier→DB; scoring persists) + `tests/web/test_app_smoke.py`. (5) **W1.4** `docs/hardware-requirements.md` filled in (RAM rule, validated data points, pre-AVX2 + reasoning-model constraints, roster→tier). **323 tests pass.** Open (not autonomous): pilot grounding ZIMs (Vikidia/Simple-WP not on `/mnt/zim` — content decision), W1.3 model pick, W5.6 thresholds, rotate LiteLLM key. |
| 2026-06-19 | **Option B item generator + run guide + Help-placeholder fix** (Opus). (B) `src/mentar/engine/itemgen.py` — parametric per-skill generators for 7 of 8 pilot nodes (division + 6 fraction skills) producing infinite non-repeating checkable items; duck-types `ItemBank` (has/sample/example) + `CompositeItemSource` (generator → authored-bank fallback for the conceptual `equal_vs_unequal_parts` node) + `build_item_source(mode)`; config `item_source: composite|generator|bank` (default composite); wired into web app + CLI. `tests/engine/test_itemgen.py` (6) incl. **every generator self-validates over 200 draws/node** → **319 tests pass**. Fixed the `{{worked_example}}` leak: `_render_template` now substitutes it from a solved bank example (excludes the live item; no queue consumption via new `ItemBank.example`). Added **`docs/RUNNING.md`** — cross-platform quick start (Windows / macOS M1 16 GB / Linux) via Ollama, incl. per-OS model paths + GGUF `model_path` styles + pre-AVX2 note; README links it. |
| 2026-06-18 | **gemma4:12b wired + verified end-to-end via LiteLLM** (Opus). Pointed the model-agnostic backend at the eval-host **LiteLLM** proxy (`192.168.xx.xxx:4000/v1`, `backend: vllm`) → ran a full FSM turn on **gemma4:12b**: item presented, correct answer → PASS → BKT persisted, `?` Help → a clean age-appropriate analogy in **3.3s**. **Key finding: gemma4:12b is a REASONING model** (emits `reasoning_content` + `content`); left unchecked it spends the whole `max_tokens` on hidden reasoning and returns empty/truncated `content` (saw `finish:length`, reasoning ~700 tok, content 38 chars). Fix: added `generation.extra_body` passthrough to `inference/backend.py` + set **`think: false`** (also `reasoning_effort:none` works) → clean content, ~5x faster. A 12B cannot run on this 4 GB sandbox; LiteLLM fronts the eval-host GPU. (Minor: stray unsubstituted `{{worked_example}}` placeholder in the Help template — noted.) |
| 2026-06-18 | **Answer-verification gap fixed (Option A) — pilot can now score** (Opus). Root cause: LLM-generated questions had no ground-truth answer. Fix: authored **item bank** — `scripts/build_itembank.py` lifts the 31 verified eval transfer items (all 8 nodes) → `curriculum/itembank/pilot_fractions.jsonl` (clean child-facing problem + answer + checker); new `src/mentar/engine/itembank.py` (`ItemBank.sample` no-repeat per node); `SessionController` takes an optional `item_bank` and draws **checkable questions verbatim** (verifier scores against the item's answer; LLM stays out of the correctness path). Wired into web app + CLI. `tests/engine/test_itembank.py` (4) → **313 tests pass**. **Verified end-to-end on the local GGUF:** correct answer → PASS → BKT mastery cold-start→**0.733** → **persisted** (fixed bug #4: `_DbStoreAdapter.update_skill_state` was missing `priors_used`, so persistence still silently failed once scoring reached BKT). Option B (parametric generator) queued. |
| 2026-06-18 | **W1.5 made REAL + first local-LLM end-to-end run** (Opus). Built `src/mentar/inference/backend.py` (config loader + `make_llm_call`, OpenAI-compatible path for llamacpp/vllm/ollama + in-process llama-cpp-python), rewired `web/app.py` to it (lazy model load; env-var fallback kept), added `mentar run-session` CLI, `tests/inference/test_backend.py` (10) → **309 tests pass**. Ran the whole FSM loop on a local GGUF (Qwen2.5-0.5B Q4 throwaway, ~7 tok/s on 2-core AMD A10). **Surfaced 3 latent wiring bugs invisible until first real run:** (1) `create_learner()` calls missing `country`/`age_mode` in both web app + CLI — FIXED; (2) **scoring can never PASS** — `_load_curriculum` maps `expected_answer = transfer_seeds[0]` (a *question*, not an answer), so every child answer SAFE_REJECTs and BKT never persists → **W3 design gap: no ground-truth answer for LLM-generated questions** (NOT patched — needs schema decision); (3) `'stop'` not handled in HELP_RECHECK_AWAIT/PROBE_AWAIT states. **Hardware note (W1.4):** pre-AVX2 CPUs SIGILL on stock llama-cpp-python wheels → must ship a from-source/non-AVX2 build path. Proxy smoke deferred (eval host needs the maintainer's `MENTAR_VLLM_API_KEY`; 401). |
| 2026-06-13 | Initial. Reflects work landed in the 13 Jun build session. |
| 2026-06-14 | W2.2 design frozen — `docs/design/W2.2_escalation.md` (Opus). Pins escalation module contract + 2 interim safety decisions (emergency signposting, handoff wording) w/ rollout guard; SAFETY.md §3.5 updated. Unblocks Sonnet impl of `escalation.py` + T2.1. |
| 2026-06-14 | W3.3 ✅ (Opus) — `src/mentar/engine/bkt.py` + `docs/design/W3.3_bkt.md`. Deterministic BKT recurrence, hinted-win = elevated-guess class, hand-set cold-start priors; pyBKT scoped to offline fit only. 7 invariants verified numerically; SPEC §11 corrected. Unblocks W3.4. Remaining: T3.3 test file + FSM caller wiring (Sonnet). |
| 2026-06-14 | W2.2 ✅ (Sonnet) — `src/mentar/safety/escalation.py` + `tests/safety/test_escalation.py` + schema.sql comment (logged_only). All 20+20 T2.1 fixtures verified via inline smoke check. Trigger→freeze→alert path demonstrated with real in-memory SQLite. Two rollout guards (emergency signposting + handoff wording validation) remain load-bearing. |
| 2026-06-14 | W5.2 ✅ (Opus) — resolved §23/§24 safety contradiction. SPEC §23 anchors "safety layer active" to SAFETY.md v0.1 + W2.2; §24 row #6 updated to reflect the live pilot escalation path (Bucket D open for post-pilot refinement). |
| 2026-06-14 | W5.3 ✅ (Opus) — SPEC §21 placeholders promoted to pilot default (v0): pattern mix 40/30/30, Help retry cap 3, mastery threshold 0.85, + Probe-cadence row. |
| 2026-06-14 | W3.4 ✅ (Opus) — `src/mentar/engine/probe_classify.py` + SPEC §14.4 false-confidence decision table; 7 cases smoke-verified. |
| 2026-06-14 | W4.1 ✅ (Opus) — `docs/CONTENT_LICENSES.md`; pilot sources (CC BY-SA) cleared, Khan NC conflict logged (§24 #18). |
| 2026-06-14 | W2.5 ✅ (Opus) — `docs/PILOT_CONSENT.md` signable consent template; required before session 1. |
| 2026-06-14 (overnight) | W6.2 ✅ (Opus, after cloud routine failed on private-repo access) — 10 versioned templates in `prompts/` + `prompts/README.md` registry; hashing convention documented; T4.6-equivalent check passes 10/10. |
| 2026-06-14 (overnight) | W3.5 🟡 (Opus) — verdict REFERENCE-ONLY (desk assessment); `docs/design/W3.5_build_vs_adopt.md` + SPEC §19.2. |
| 2026-06-14 (overnight) | W6.3 ✅ (Opus) — pilot interface = minimal local web app (4 views); `docs/design/W6.3_pilot_interface.md` + SPEC §23. |
| 2026-06-14 (overnight) | W5.6 🟡 (Opus) — kill criteria + scope-cut order drafted in SPEC §25.1–25.2; awaits the maintainer's distress/runway thresholds. |
| 2026-06-14 (overnight) | Docs hygiene — rewrote stale `README.md` to match real src-layout; created `compliance/README.md` (coverage-status map per SPEC §17.5). |
| 2026-06-14 (overnight) | Test files landed (Opus) — `tests/engine/test_bkt.py` (T3.3, 7), `tests/engine/test_probe_classify.py` (7), `tests/test_prompt_registry.py` (T4.6+T7.3, 6). All pass via inline smoke; pytest-compatible. |
| 2026-06-15 | Secret safeguard added — `.gitignore` secret rules + `config/inference.example.yaml` + `config/README.md` + `scripts/git-hooks/pre-commit` (blocks secret filenames + inline secrets; activate via `core.hooksPath`). Tested: blocks, clean commits pass. |
| 2026-06-15 | Decisions (the maintainer) — **W5.7 = (c) per-child** (§24 #16); EU AI Act high-risk clarified **not local/G0-blocking** (§24 #1, §17.2); W5.6 (c) revised to safeguarding-informed assent-based threshold w/ external guides. |
| 2026-06-15 | Decisions (the maintainer, mobile) — W5.6 (c) **deferred to Bucket D** (no auto-stop mechanism yet; don't halt on normal frustration); W1.2 model shortlist set (Qwen2.5-7B / Llama-3.1-8B / Gemma-2-9B / Phi-4-mini + more), eval focus = hallucination + retrieval accuracy via needle-in-a-haystack; cloud GitHub access to be granted (enables cloud routines). |
| 2026-06-15 | W1.2 eval-tooling scan (Opus, hands-on) — NIAH cloned/installed/run (`demo --fake` E2E, 209 tests pass, vLLM-compatible). Verdict: **adopt for retrieval-faithfulness only**, not a full harness. `docs/design/W1.2_eval_tooling.md` + `eval/niah/` (vLLM config). |
| 2026-06-15 | Directives (the maintainer) — **llama.cpp = primary local backend** (lightweight, broadest HW support; SPEC §20.1/§21, config, inference stub). **Hermit-AI** scanned hands-on as ZIM-grounding reference (AGPL → clean-room ideas only): borrow title-prediction-over-ZIM + libzim + staged retrieval; implies a new grounding/retrieval W-task. `docs/design/grounding_zim_reference_hermit.md`. |
| 2026-06-15 | Grounding reader decision — verified ZIM-MCP option = **OpenZIM MCP** (`cameronrye/openzim-mcp`, **MIT**, libzim, maintained). **Decision: BUILD a thin owned `libzim` reader** (reuse OpenZIM MCP's MIT code as reference; **skip the MCP server** — wrong shape for our controlled FSM + safety-critical path). Depend on `libzim` only. MCP-server-as-runtime = a Phase-2/agentic option, not the pilot. |
| 2026-06-15 | **W7 — Grounding/Retrieval workstream opened** (Opus design freeze; the maintainer approved scope). New `26.6B` in PHASE0.md (W7.1–W7.5) + this W7 status section. Frozen build contract `docs/design/W7_grounding_reader.md`. **Pilot scope = anchor-resolution only** (pilot nodes carry explicit `anchor:` URLs → no LLM title-prediction/BM25/embeddings; those = W7.5 deferred). G0-relevant but degrades gracefully (`resolve_grounding` → `""` on missing ZIM), so not a hard G0 blocker. SPEC §15 cross-references the new `src/mentar/grounding/` producer. |
| 2026-06-16 | **T1.1 eval dataset BUILT** (Opus, after the overnight build was rate-limited). `eval/dataset_v1.jsonl` = 101 items (50 reexplain across 8 nodes × 5 modalities + 31 transfer with checkable answers + 20 adversarial: 5 each jailbreak/offtopic/distress/injected_passage). + `eval/schema.json`, `eval/build_dataset.py` (authored source), `eval/validate_dataset.py` (PASS → `reports/T1.1/result.json`), `eval/models.yaml` (roster), `eval/run_candidates.py` (T1.2 runner; stdlib; env-driven; dry-run verified; 6 tests in `tests/eval/test_dataset_v1.py` incl. transfer answers verifying PASS via verify_numeric). **W1.2 is now runnable** — export the eval env and run the runner. Stale `OVERNIGHT_STATUS.md` removed. |
| 2026-06-15 | **W1.1 endpoint live + W1.2 roster complete** (the maintainer stood up the eval host; Opus recorded). OpenAI-compatible **local proxy** at `http://192.168.xx.xxx:4000/v1` now serves the full cross-family candidate set — `llama3.1:8b`, `gemma2:9b`, `phi4-mini`, `qwen3:14b`, `qwen3.5:9b`, `qwen3.5:2b` + `mistral-small3.1` (ceiling, not candidate) + Sonnet (judge). Three verified responding. New `docs/MODEL.md` = canonical roster + roles A–D + size→tier map + eval dimensions (incl. latency) + run plan. Config `vllm:` block points at the proxy (token via env, never committed). **Ready to run** once T1.1 dataset is built. |
| 2026-06-15 | **W7.4 structured sources + auto-latest** (Opus; the maintainer flagged the gap). ZIM filenames follow `<project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim`. Config `grounding.sources` now declares those parts (`{project, lang, selection, flavour, pin?}`) instead of a fixed filename; the **reader auto-picks the newest matching file in `zim_dir`** (latest YYYY-MM wins; `pin` = date or exact file override; plain string still accepted = exact filename). Shared helpers `build_filename_regex`/`pick_latest`/`list_zim_dir`/`resolve_filename` in `grounding/sources.py`, reused by `scripts/fetch_zim.py` (+`--config` mode). `source_map.get_zim_path` resolves via spec. +7 tests (real-world names: `wikipedia_en_astronomy_maxi`, `wikipedia_ace_all_nopic`) → 57 pass; E2E auto-latest verified against the fixture ZIM. |
| 2026-06-15 | **Media/interactivity decision + 2 W-tasks scoped** (Opus; the maintainer asked). `docs/design/media_and_interactivity.md`: grounding stays **text-only** (correct — text LLM, pilot needs no media); media/interactivity is a **presentation-layer** concern → **W6.5** (Mentar-OWNED interactive manipulatives, not ZIM-JS — safety + pedagogy) + **W7.6** (vetted ZIM static-media serving, gated on child-safety whitelist). Both post-pilot, not G0. Flagged: **Khan Academy = CC BY-NC-SA** (NC) — fine local/personal, not for a commercial/hosted edition (already SPEC §24 #18 / CONTENT_LICENSES.md); PhET = CC BY (better if interactive ZIM content ever adopted). Also added general `scripts/fetch_zim.py` (auto-resolve latest ZIM by project+pattern from Kiwix mirror index; local/NAS/SMB dest) for future ad-hoc downloads (Khan, PhET, …). |
| 2026-06-15 | **W7.4 NAS/Samba support** (Opus) — ZIM sources now read/download from **local / mounted-NAS / `smb://`** locations. New `src/mentar/grounding/sources.py` (`materialize_zim`: local/mounted pass-through, `smb://` copied once to `zim_cache_dir` via `smbclient`); fetch script rewritten `scripts/fetch_zim.py` (multi-mirror Kiwix incl. `lbo.download.kiwix.org` → local/NAS/SMB dest). `source_map`/`resolve` route through materialization (cache-hit skips SMB copy). Optional `[nas]` extra (`smbprotocol>=1.12`); mounted shares need nothing. Config `smb:`/`zim_cache_dir` block. +`test_sources.py` (8 tests, SMB mocked) → 46 tests pass. Future goal recorded: Kiwix OPDS catalog auto-discovery. smbclient API confirmed via Context7. |
| 2026-06-15 | **W7.1–W7.4 BUILT** (Sonnet grunt build + Opus review/hardening). `src/mentar/grounding/` (reader/resolve/source_map/wrapper/cache + public `resolve_grounding`) + `tests/grounding/` (38 tests, all pass) + `grounding:` config block + `libzim>=3.10` pin + Kiwix fetch script + programmatic fixture ZIM. Opus review caught + fixed: (1) non-dict/None input could escape the except handler → type-guarded; (2) reader only tried `A/<slug>` → now also tries bare `<slug>` for modern libzim 3.x ZIMs. **W7.4 real-ZIM download + path-convention verification still pending (manual).** Controller wiring of `resolve_grounding` into `{{grounding_passage}}` = thin Sonnet follow-up. |
