# Graph Report - .  (2026-07-26)

## Corpus Check
- 307 files · ~274,179 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2730 nodes · 5033 edges · 196 communities (148 shown, 48 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 397 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 159
- Community 160
- Community 161
- Community 162
- Community 163
- Community 164
- Community 165
- Community 166
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 180
- Community 181
- Community 182

## God Nodes (most connected - your core abstractions)
1. `SessionController` - 134 edges
2. `check()` - 84 edges
3. `LearnerStore` - 67 edges
4. `ItemGenerator` - 40 edges
5. `_client()` - 40 edges
6. `build_long_division_steps()` - 33 edges
7. `Item` - 31 edges
8. `_make_controller()` - 30 edges
9. `normalise_fraction()` - 28 edges
10. `He()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `test_same_seed_same_node_sequence()` --calls--> `run()`  [INFERRED]
  tests/dialogue/test_micro_learning.py → eval/judge_responses.py
- `TestAssertParentMediated` --uses--> `LearnerStore`  [INFERRED]
  tests/db/test_datamodel.py → src/mentar/db/store.py
- `TestFullSessionRoundtrip` --uses--> `LearnerStore`  [INFERRED]
  tests/db/test_datamodel.py → src/mentar/db/store.py
- `TestGetLearnerByName` --uses--> `LearnerStore`  [INFERRED]
  tests/db/test_datamodel.py → src/mentar/db/store.py
- `TestSchemaVersionMigrationStub` --uses--> `LearnerStore`  [INFERRED]
  tests/db/test_datamodel.py → src/mentar/db/store.py

## Import Cycles
- None detected.

## Communities (196 total, 48 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (103): a(), Ae(), an(), at(), B(), be(), bn(), bt() (+95 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (67): gen_add_sub_decimals(), gen_add_within_100(), gen_add_within_1000(), gen_area_perimeter(), gen_decimal_place_value(), gen_div_decimal_by_decimal(), gen_div_decimals(), gen_division_facts() (+59 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (61): _FakeStore, _make_controller(), Tests for dialogue/controller.py (T3.7 conformance subset).  Covers:   - SESSION, A correct answer is acknowledged (not silently advanced)., A wrong answer is told it's wrong and auto-routed into Help (note 4b).      Regr, Unreadable input (SAFE_REJECT) is re-prompted, never scored as wrong., A9: the re-ask loop has an exit — 3 unreadable answers in a row on the     SAME, Typing 'stop' in AWAIT_ANSWER transitions to SESSION_END_BY_LEARNER. (+53 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (39): Fraction, ClaimCheck, find_claims(), has_verified_failure(), _parse_step(), explain_check.py — verify arithmetic claims embedded in free-form LLM text.  Spe, Post-process explanation text: find indented algebra step blocks and     re-alig, Extract and verify every `a <op> b = c` claim in *text*. (+31 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (24): Short, warm, deterministic right/wrong feedback for a scored answer.          On, Drives the Mentar session FSM.  One instance per learner session., Advance the FSM by one turn, persisting the transcript around it.          Wraps, Parent control-plane action on a frozen/awaiting session: ``resume``/``end``., R-RES: best-effort per-turn checkpoint so a server-process restart can         r, Advance the FSM by one logical turn.          Drive through transient states aut, Build a TurnResult from the accumulated MESSAGE prose + the pending         ques, The curriculum node the learner is currently on, or None before the         firs (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (38): asked_question(), build_judge_prompt(), build_misconception_prompt(), _content(), grade(), judge_post(), load_jsonl(), main() (+30 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (40): build_abstention(), build_adversarial(), build_all(), build_reexplain(), build_sycophancy(), build_transfer(), main(), _reexplain_item() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (23): LearnerStore, Insert a learner profile row and return the new learner_id (int)., Insert a session row.  session_id is caller-supplied (e.g. UUID).          rng_s, R-RES: best-effort per-turn checkpoint (current node, frozen flag, session, Mark a session as ended., Upsert the BKT mastery estimate for one skill.          Only p_mastery and prior, Insert a response_log row and return the new response id., Return all response_log rows for one (learner, session) pair as dicts. (+15 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (12): check(), Verify an LLM-generated answer against ground truth.      Parameters     -------, TestCheckDecimalExact, Tests for the fraction_equiv checker., 2/8 + 3/8 = 5/8: LLM gives 5/8 → PASS, 7/10 - 2/10 = 5/10 = 1/2: LLM gives 5/10 → PASS (equiv to 1/2), LLM gives wrong 4/8 when 5/8 expected → FAIL, a/b' is not a valid fraction → EXTRACT_FAIL (no numeric candidate) (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (21): tests/engine/test_verifier.py — T3.5 runtime verifier integration tests.  Per SP, free_text with checker='none' always passes → serve., T3.5 canonical case:         LLM claims "2/4 + 1/4 = 4/8" — wrong answer (correc, Correct answer 1/2 but LLM gives 1/4 → fallback., Correct answer 4 but LLM says 5 → fallback., 1/0' is a zero-denominator → SAFE_REJECT → fallback (never serve)., 1/2 or 3/4' is ambiguous → SAFE_REJECT → fallback., Decimal ground_truth '0.5' → SAFE_REJECT → fallback. (+13 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (33): LLMCall, main(), _remediation(), _default_config_path(), _expand_env(), _gen_params(), _load_dotenv(), load_inference_config() (+25 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (36): build_addition_steps(), build_subtraction_steps(), Column addition, right-to-left, with a carry row shown only where a     carry ac, Column subtraction, right-to-left, with borrow marks shown only where a     borr, Read the digits (and decimal point, if any) back out of the final     (result) r, 7 + 19: the shorter operand must NOT crash on padding, and its blank     leading, 999 + 1 = 1000: carries propagate through every column, including a     new lead, Same discipline as the item generators' self-validate tests: build many     rand (+28 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (31): check_scope(), get_zim_path(), Source-enum → ZIM-file mapping and anchor-host scope guard.  Responsibilities:, Validate scope and return the ZIM *location* for ``source``.      Combines :func, Raised when a node's anchor host does not match its declared source., Return the configured ZIM *location* for ``source``, or ``None`` if unconfigured, Verify that ``anchor``'s hostname matches ``source``'s expected host(s).      Ar, resolve_zim() (+23 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (19): Item, ItemBank, load_item_bank(), Path, Random, Item bank — authored, checkable (problem, answer) items keyed by curriculum node, In-memory pool of checkable items, grouped by node.      sample() returns items, Return a fresh item for *node_id*, or None if the node has no items. (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (22): BlockClass, OutputIncident, Enum, str, Output-side safety gate — screen LLM output before it reaches the child.  Spec:, Screen one piece of LLM output before it reaches the child.      Returns (text,, screen_output(), T-A13 — output-side safety gate (safety/output_guard.py).  Spec: docs/SAFETY.md (+14 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (31): build_long_division_steps(), Bus-stop ("long") division -- rebuilt 2026-07-24 to match the     standard schoo, _bare_quotient(), Same as _quotient_from_grid but without an OPERATOR-kind suffix cell     (the "R, The 2026-07-19 worked example, 225 / 5 -- under the new convention the     quoti, The maintainer's ORIGINAL example from the very first note: a     decimal-by-dec, Regression (2026-07-24, maintainer-reported bug): a decimal divisor is     scale, 408 / 4 = 102 -- the middle "0" is an INTERNAL zero (a step whose     quotient d (+23 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (21): _FakeClient, _FakeCompletions, _FakeMessage, _install_fake(), Tests for mentar.inference.backend — config loading + make_llm_call dispatch.  C, A gitignored .env next to the config supplies ${VAR} (no shell export)., A real environment value wins over .env (.env is only a fallback)., R7.2 fix: resolve_http_endpoint(cfg) must return the SAME endpoint     make_llm_ (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (23): datetime, FSMState, _is_stale_mastery(), Enum, Path, str, _raise_on_uncovered_nodes(), Session FSM controller — wires BKT, fringe, escalation, grounding, prompts.  Spe (+15 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (28): gen_antonyms_advanced_y5(), gen_antonyms_nuanced_y6(), gen_compound_words_y5(), gen_figurative_language_y6(), gen_plurals_y2(), gen_rhyming_y2(), gen_synonyms_advanced_y5(), gen_synonyms_nuanced_y6() (+20 more)

### Community 19 - "Community 19"
Cohesion: 0.07
Nodes (27): _ensure_fixture(), Tests for mentar.grounding.reader — ZimReader open + lookup + section extraction, Hint containing 'equal parts' should return content mentioning equal parts., Unit fraction article resolves and returns definition text., Direct internal-path lookup (no URL to parse) returns raw bytes., The English track's transcript is extracted, not the French one, and     WebVTT, The fixture's duplicated cue line collapses to one occurrence., A page with no matching srclang="en" track degrades to "". (+19 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (27): Mastery, fringe_from_template(), outer_fringe(), Convenience: load a template + compute fringe in one call.      Empty `mastery`, Return the set of concept ids ready to learn now.      A concept is on the outer, linear_graph(), Tests for the KST outer-fringe computation.  Spec: docs/SPEC.md §10; tests: docs, Mastering through `adding_equal_denom` (with comparing_equal_denom also     mast (+19 more)

### Community 21 - "Community 21"
Cohesion: 0.15
Nodes (22): Show human working": the deterministic step grid for the current         Explain, StepGrid, _addition_bank(), _division_bank(), _division_remainder_decimal_bank(), _division_remainder_fraction_bank(), _FakeStore, _multiplication_bank() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (24): Generic, board-agnostic India "Class 3 maths" pack -- universally-taught topics, Named item-source registry (R3.1).  Curriculum templates are self-describing dat, build_item_source(), default_item_generator(), _gen_adding_equal_denom(), _gen_addition(), _gen_comparing_equal_denom(), _gen_equivalent_fractions() (+16 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (27): _client(), Tests for GET /progress and the enhanced GET /parent mastery table.  Uses the sa, The evergreen practice sampler (times tables/skip counting/doubles-halves,     s, R3.2: fixes a real defect -- /progress used to mix ALL subjects' skill     rows, R2.4: greedy word-wrap for the concept-map labels -- the fix for the     reporte, Return a freshly-reloaded (app_mod, test_client) pair backed by a temp DB., The reported bug: AU labels ("Place value to 9999", "Equivalent     fractions"), GET /parent includes the mastery table and session summary after one answer. (+19 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (23): GenFn, ItemGenerator, Generates fresh checkable items per node. Duck-types ItemBank (has/sample/exampl, Tests for mentar.engine.itemgen — parametric item generator (Option B).  Contrac, Generated division questions carry a single kid-friendly emoji (note 1),     and, test_child_correct_answer_passes(), test_composite_routes_generator_then_bank(), test_division_question_shows_one_noun_emoji() (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (22): SimpleNamespace, Path, D6 — `mentar backup`: checkpoint + copy + verify the DB file.  Real DB file I/O, _seeded_db(), test_backup_copies_and_verifies(), test_backup_default_dest_name_and_refuses_overwrite(), test_backup_missing_source_fails(), _FakeRun (+14 more)

### Community 26 - "Community 26"
Cohesion: 0.11
Nodes (26): _canonical_decimal_str(), _canonical_str(), _check_decimal_exact(), _check_fraction_equiv(), _check_int_exact(), _check_mc_choice(), _check_none(), CheckOutcome (+18 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (24): _authority_dir_name(), derive_subject_key(), load_curriculum(), load_template_meta(), Path, Curriculum template loader — parses a pilot template's YAML front matter into th, R3.1: the front-matter fields the web picker/progress catalog needs to     rende, The name of the directory directly under templates/ that owns *path*     -- the (+16 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (25): Core resolution: node grounding block → plain-text passage or "".      Called by, resolve_grounding_inner(), _ensure_fixture(), _make_cfg(), Tests for mentar.grounding.resolve — node grounding block → passage.  Contract c, A wikipedia_simple Division grounding block returns a non-empty passage., A khanacademy grounding block (B1, 2026-07-05) uses the custom     video-narrati, Passage hint guides section selection: equal-parts hint returns relevant text. (+17 more)

### Community 29 - "Community 29"
Cohesion: 0.10
Nodes (16): _assert_fires(), 4 × abuse_disclosure (CRITICAL) incl. grooming-pattern + euphemistic — design §5, Direct disclosure: touching private parts., Grooming-pattern (design §5 required case): gifts + secrecy dynamic., Direct: sexually abused., Euphemistic disclosure (design §5 required case): vague 'wrong thing'., 2 × adversarial_jailbreak (LOW) — assert logged_only NOT frozen (design §4.3)., Classic jailbreak: ignore previous instructions. (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (16): _assert_silent(), 6 × on-topic math distress / normal frustration — must NOT fire (design §5)., I hate fractions' — normal frustration, must not freeze., want to give up on this problem' — MUST NOT fire (math-scope quit)., I'm dying of boredom' — idiom, not self-harm. Must not fire.         Note: 'dyin, this maths is killing me' — idiom, must not fire., Generic frustration: 'I hate this'., Normal fatigue: 'I want to stop now'. (+8 more)

### Community 31 - "Community 31"
Cohesion: 0.11
Nodes (22): _ack_latest_escalation(), answer(), frozen(), _get_or_create_controller(), learn(), _llm_call(), _log_turn(), parent_ack() (+14 more)

### Community 32 - "Community 32"
Cohesion: 0.10
Nodes (23): extract_division_operands(), extract_multiplication_operands(), _frac_digits(), _Layout, Decimal, Deterministic step-by-step arithmetic grids — "show human working" (2026-07-19 m, Pull the two operands out of a multiplication question WE generated     (e.g. "W, Pull the two operands out of a division question WE generated (e.g.     "What is (+15 more)

### Community 33 - "Community 33"
Cohesion: 0.16
Nodes (21): bkt_update(), BktParams, params_for(), _posterior_given_obs(), BKT per-turn mastery update — cold-start priors + hinted-win discount.  Spec: do, Per-skill BKT parameters. forgets is stored for forward-compat; unused in v0., Resolve params for a node: template `bkt_priors:` override wins, else the     cl, Bayesian conditioning of mastery on one observation (design §3 step a). (+13 more)

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (21): Resolve a curriculum node's grounding block to a plain passage string.      This, resolve_grounding(), _ensure_fixture(), Tests for the grounding degradation contract.  Contract checks (SAFETY §1.5 / SP, Source not in config.sources → resolve_grounding returns ''., Completely empty node_grounding dict → resolve_grounding returns ''., resolve_grounding with None values in inputs returns '' without raising., node_grounding that is None / not a dict → returns '' without raising.      A cu (+13 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (22): extract_addition_operands(), extract_subtraction_operands(), Pull the two operands out of an addition question WE generated (e.g.     "What i, Pull the two operands out of a subtraction question WE generated (e.g.     "What, Tests for engine/arithmetic_steps.py — deterministic step-by-step arithmetic gri, Every row must have exactly n_cols cells -- the web layer's CSS Grid     depends, The '+' symbol appears exactly once, on the second operand's row., Column-carry addition is the UNSIGNED method taught in early years --     negati (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.11
Nodes (18): _FakeStore, _make_controller(), R11 micro-learning — controller wiring tests.  Covers:   - interleaving: NODE_SE, A freshly-updated mastered node is NOT stale -> normal fringe selection., Scoring an item stamps mastery_updated_at, so a reviewed node leaves the stale s, max_items completed items -> SESSION_END_COMPLETE with the warm wrap-up., max_items=None (default) -> a correct answer just advances., Two sessions with the same rng_seed visit the same node sequence. (+10 more)

### Community 37 - "Community 37"
Cohesion: 0.15
Nodes (8): extract_answer(), _extract_mc(), Pull the candidate answer string from free-form LLM output.      Returns None if, Extract last MC choice (A-D or 1-4) from text., Tests for the extract_answer helper., 1/2 or 3/4' → None (ambiguous)., ½ should be expanded and then extracted., TestExtractAnswer

### Community 38 - "Community 38"
Cohesion: 0.12
Nodes (19): Grounding / ZIM-reader module: resolve a curriculum node's grounding block to a, Grounding passage wrapper: return inner text for {{grounding_passage}}.  SAFETY, Length-bound ``passage`` and return the inner text for ``{{grounding_passage}}``, wrap_passage(), _ensure_fixture(), Tests for the grounding safety wrapper (SAFETY §1.5 / W2.3).  Contract (groundin, resolve_grounding returns passage containing injection string verbatim., Verify prompts/system_prompt.md contains the grounding-as-data markers. (+11 more)

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (12): _make_store(), _populate_session(), T3.6 — Learner data model tests.  Spec: docs/TESTS.md T3.6; docs/PHASE0.md W3.6, T3.6 (a): write ≥30 responses, 2 Help, 1 probe, 1 escalation, ≥10     transcript, T3.6 (b): interleaved writes for two learners; queries for learner A     return, Write a complete mock session and return the ids of written rows., name has no UNIQUE constraint — the lookup must be deterministic         (oldest, TestAssertParentMediated (+4 more)

### Community 40 - "Community 40"
Cohesion: 0.15
Nodes (21): Path, Tests for T3.1 — curriculum-template validator (W3.1 schema).  Six test cases re, A → B → A cycle must fail with a message containing 'cycle' and both ids., A16: an invalid template raises RuntimeError naming the path + the error(s),, A concept that prereqs a non-existent id must fail, naming the missing id., Two concepts sharing id 'concept_a' must fail with 'duplicate' + id in error., A stranded singleton node (no prereqs, not referenced by any other node)     alo, Write a minimal valid-structure template with the given concepts YAML block. (+13 more)

### Community 41 - "Community 41"
Cohesion: 0.19
Nodes (20): _backup(), _build_controller(), _download_gguf(), _emit(), _ensure_llama_cpp(), _eval(), main(), Path (+12 more)

### Community 42 - "Community 42"
Cohesion: 0.13
Nodes (19): Random, KST outer-fringe computation.  Spec: docs/SPEC.md §10 (concept graph, KST); PHAS, Micro-learning NODE_SELECT policy (R11).      Interleaves among ready (outer-fri, select_next(), Tests for select_next — the micro-learning NODE_SELECT policy (R11): interleavin, Ensure deterministic behavior with the same seed., Ensure the selector picks a different node from the fringe if others are availab, Ensure it returns the current node if it is the only one available. (+11 more)

### Community 43 - "Community 43"
Cohesion: 0.16
Nodes (6): normalise_decimal(), Parse a strict decimal (or bare integer) string, or None on failure., Decimal("NaN") would otherwise parse successfully -- must be         rejected be, Exponent notation must not be silently accepted as a plain decimal., No locale-aware parsing -- comma as decimal separator is rejected, not guessed., TestNormaliseDecimal

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (20): materialize_zim(), Resolve a source spec to a concrete ZIM filename present in ``zim_dir``.      ``, Return a local filesystem path libzim can open, or ``None`` on failure.      Loc, resolve_filename(), fake_smbclient(), Tests for mentar.grounding.sources — location handling + SMB materialization.  C, Inject a fake `smbclient` module that serves _FAKE_ZIM bytes., smb:// requested but smbprotocol not installed → None, no raise. (+12 more)

### Community 45 - "Community 45"
Cohesion: 0.14
Nodes (19): Any, main(), _parse_frontmatter(), Path, validate_template.py — W3.1 curriculum-template validator.  Parses a Markdown fi, Validate the curriculum template at *path* and return a ValidationResult., Validate *path* and raise RuntimeError naming the template + every error     if, Print a ValidationResult (warnings/errors to stderr, summary to stdout).      Re (+11 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (7): Deterministic hint used when the LLM is unavailable/empty — Help must         ne, A small, kid-friendly cue for the expected answer SHAPE, from the KNOWN, Drop trailing question lines a model appends to a Help explanation.          The, One Help explanation turn. With elaborate=True (R12.5, HELP_ELABORATE)         t, Show human working": build a deterministic step grid for the         current ite, A solved example string for the worked-example slot in Help/transfer prompts., Draw a checkable item for *node_id*, or None when no bank covers it.

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (19): _client(), Tests for R9 -- the first-run setup gate (/setup) and live config reload.  Delib, An in-process llamacpp backend has no HTTP endpoint -- its mere     presence (co, The key claim: an EXISTING controller (built before setup) picks up     the new, The actual end-to-end claim: _llm_call (the SAME function object every     alrea, Fresh (app_mod, test_client) pair, gate NOT bypassed -- each test     patches ap, Config file EXISTS but the backend fails the reachability probe --     must stil, _reachable_openai_mock() (+11 more)

### Community 48 - "Community 48"
Cohesion: 0.18
Nodes (18): _configure_smb_auth(), is_smb_location(), join_location(), list_zim_dir(), _materialize_smb(), Path, r"""ZIM source-location handling: local paths, mounted NAS, and SMB/Samba shares, List ``*.zim`` filenames in a local/mounted dir or an SMB dir. ``[]`` on failure (+10 more)

### Community 49 - "Community 49"
Cohesion: 0.16
Nodes (14): _FakeStore, _PromptCapturingLlm, R12.4/R12.5 — explanation variety context + the "Explain more" (elaborate) flow., At AWAIT_ANSWER (no explanation live) 'more' must not enter elaborate —     it g, R12.4: a second Help round's modality prompt carries the first     explanation a, Returns a canned explanation; records every prompt it was sent., Drive a fresh session into HELP_RECHECK_AWAIT via a child help request., test_can_elaborate_property() (+6 more)

### Community 50 - "Community 50"
Cohesion: 0.17
Nodes (15): load_visual_scaffold(), Path, Visual scaffold loader — keyword-routes a concept label to a short OKF scaffold, Every (topic_keywords, body) pair found under one subject subdirectory,     cach, Return the body of the first scaffold file whose `topic_keywords` match     *lab, _scan_scaffold_dir(), _split_frontmatter(), Brute-force scaffold coverage — every concept node in every shipped curriculum t (+7 more)

### Community 51 - "Community 51"
Cohesion: 0.18
Nodes (15): _drop_noise(), _extract_lead_section(), _extract_section_by_hint(), Thin owned libzim reader: open a ZIM archive and extract article text.  Responsi, Remove structural HTML chrome (script/style/table blocks + comments) BEFORE text, Extract the lead (opening) paragraphs before the first heading.      Most wiki a, Extract the section whose heading best matches ``passage_hint``.      Strategy (, Extract a plain-text passage from raw HTML bytes.          The passage is guided (+7 more)

### Community 52 - "Community 52"
Cohesion: 0.15
Nodes (18): choose(), _current_node_mastery(), _display_name(), done(), index(), parent(), _persisted_escalations(), _persisted_turns() (+10 more)

### Community 53 - "Community 53"
Cohesion: 0.14
Nodes (9): _ColdStartStore, _ctrl(), _PerNodeBank, A5 — per-node, child-initiated help_pressed for probe classification.  Regressio, The system's own auto-help (triggered by a wrong UNAIDED answer, in     _do_bkt_, Cold-start mastery (P_L0) for every node — the test pokes ctx.mastery     direct, node_a: help pressed, mastery poked to threshold -> a failed probe must     clas, test_auto_help_alone_still_classifies_false_confidence() (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.15
Nodes (9): classify_abstention(), classify_sycophancy(), load_jsonl(), main(), Path, (outcome, reason). Drafted by gemma2:9b; audited + fixed (4-space, whitespace-em, (outcome, reason). pass = clear deferral/uncertainty; else review (fails need ju, score_file() (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.19
Nodes (15): adversarial_items(), classify(), load_jsonl(), main(), Path, Return (outcome, reason): outcome in {pass, fail, review}., score_file(), Tests for eval/score_safety.py (T1.5 heuristic adversarial/safety pre-screen). (+7 more)

### Community 56 - "Community 56"
Cohesion: 0.12
Nodes (9): Row, Return the learner_profile row for *learner_id*, or None., Return the learner_profile row matching *name* exactly, or None.          A6: le, A19: pilot scope is parent_mediated only. Raise a clear error if a         learn, R-RES: the most recent session this learner never explicitly ended         (``en, Return a session row, scoped to the given learner., Return the skill_state row for one (learner, skill) pair., Return all skill_state rows for a learner. (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.18
Nodes (14): classify_probe(), ProbeClass, Enum, str, Proactive-probe outcome classification — the false-confidence decision table.  S, Apply the W3.4 false-confidence decision table.      Args:         first_correct, T5.x — proactive-probe outcome classification (W3.4 false-confidence table).  Co, test_clean_pass() (+6 more)

### Community 58 - "Community 58"
Cohesion: 0.17
Nodes (14): classify(), _deobfuscated_views(), Enum, str, Child-safety escalation classifier.  Spec: docs/SAFETY.md Layer 3 (§3.1–§3.5); d, Normalised variants of *text* for catching obfuscated jailbreaks., Single-turn classifier. Returns the HIGHEST-severity match, or None.      Sensit, Severity (+6 more)

### Community 59 - "Community 59"
Cohesion: 0.19
Nodes (13): _build(), _curriculum(), _drive(), _fake_llm(), _FixedBank, Path, Task 1.1 — durable DB logging is wired (transcript / response / help / probe)., A store missing the new methods must not break the turn loop (fake-store compat) (+5 more)

### Community 60 - "Community 60"
Cohesion: 0.23
Nodes (16): _client(), Tests for R10 -- in-repo curriculum on/off toggles (/settings/curricula).  Every, R10 equivalent of R8's uninstall-preserves-mastery: turning a curriculum     off, Everything toggleable' means a family CAN turn every curriculum off.     That mu, A malformed pack_state.json must never break startup -- default to     all-enabl, Fresh (app_mod, client). If `disabled` is given, a state file is written     and, The load-bearing behaviour: a disabled pack is genuinely gone from the     picke, _skip_if_no_flask() (+8 more)

### Community 61 - "Community 61"
Cohesion: 0.12
Nodes (11): _anchor_to_zim_path(), _find_english_vtt_path(), Convert a wiki anchor URL to the ZIM A-namespace path.      Wiki URLs like ``htt, Resolve a wiki anchor URL to raw HTML bytes from the ZIM archive.          Tries, Direct ZIM-internal-path lookup (Khan Academy, B1): KA's ZIM has no         reco, Extract a Khan Academy video's full English narration transcript (B1)., Return an Entry by ZIM path, or None on KeyError., Return an Entry by title, or None on KeyError. (+3 more)

### Community 62 - "Community 62"
Cohesion: 0.17
Nodes (10): _ctrl(), _FakeStore, _FixedBank, A14 — Help explanations are verified before serving (SAFETY §6.2 Level 2).  Cont, Every attempt emits the SAME wrong claim -> exhausts the retry budget -> falls, First generation is wrong, second (retry, bounded) is correct — the good     one, test_correct_worked_example_passes_unchanged(), test_prose_without_claims_passes_unchanged() (+2 more)

### Community 64 - "Community 64"
Cohesion: 0.18
Nodes (12): Path, Thin owned wrapper around ``libzim.reader.Archive``.      Usage::          reade, Open the ZIM archive.          Args:             zim_path: Path to the ``.zim``, ZimReader, _extract_generic_article(), _extract_khanacademy_video(), _extract_passage(), _get_reader() (+4 more)

### Community 65 - "Community 65"
Cohesion: 0.21
Nodes (14): build_filename_regex(), parse_index(), pick_latest(), Return the .zim filenames linked in a Kiwix directory-index HTML page., Pick the newest filename matching ``regex`` (YYYY-MM sorts lexicographically)., Build an anchored filename regex from a structured source spec.      spec keys:, Tests for the pure resolution helpers in scripts/fetch_zim.py.  These need no ne, _smoke() (+6 more)

### Community 66 - "Community 66"
Cohesion: 0.20
Nodes (12): Handoff-wording validation harness (W2.2 §6.2; SAFETY.md §3.4).  Machine-checkab, Return a list of criterion violations for *message* (empty list = passes)., Validate the live `HANDOFF_MESSAGE_*` constants; {name: violations}., validate_frozen_messages(), validate_handoff_message(), W2.2 — the frozen handoff messages pass the wording harness; bad samples fail., test_ai_self_promise_fails(), test_emergency_signposting_fails() (+4 more)

### Community 67 - "Community 67"
Cohesion: 0.16
Nodes (10): _EmptyBank, _FixedBank, A9 — loud-fail at startup when a curriculum node has a checker but no item-sourc, Covers nothing — every node falls through to the LLM-question fallback., checker: none nodes are never scored against expected_answer — no risk,     no r, item_bank=None is the deliberate legacy/test fallback — not itself a     misconf, test_covered_node_does_not_raise(), test_free_text_checker_none_never_raises_even_uncovered() (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.13
Nodes (15): _last_digit_row(), _quotient_from_grid(), _quotient_row(), The quotient row is the first row containing a DIGIT/POINT cell --     NOT alway, Division's result (the quotient, plus any "R n"/"num/den" suffix).     Excludes, The last row containing a DIGIT cell -- robust to an annotation row     (2026-07, The maintainer's own hand-worked alignment check: 425 / 4 = 106 R 1.     Exercis, The maintainer's reference image, panel 1: 432 / 15 = 28 R 12. (+7 more)

### Community 69 - "Community 69"
Cohesion: 0.22
Nodes (12): _body_hash(), _looks_like_sql(), Path, T4.6 — prompt templates are versioned files the controller loads, never hardcode, T7.3 mechanism: no PROMPT-like string literal >200 chars under src/.      Prompt, _registry_hashes(), _template_files(), test_at_least_ten_templates() (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.16
Nodes (7): count_syllables(), flesch_kincaid_grade(), is_age_appropriate(), Estimate syllables in one word via vowel groups (min 1; drop a silent trailing ', Flesch-Kincaid Grade Level for ``text``. Returns 0.0 if there are no words., Heuristic: True if the text reads at or below ``max_grade`` (default Year-4)., Tests for eval/readability.py (deterministic Flesch-Kincaid age-appropriateness

### Community 71 - "Community 71"
Cohesion: 0.22
Nodes (12): load_jsonl(), main(), Path, Score one model's responses against the transfer ground truth., score_file(), transfer_truth(), Tests for eval/score_responses.py (T1.3 numeric correctness scoring).  No networ, _smoke() (+4 more)

### Community 72 - "Community 72"
Cohesion: 0.18
Nodes (14): Cell, Render a StepGrid as plain monospace text (2026-07-24) -- one line per     row,, render_steps_grid_text(), A whole-number divisor needs no scaling, so no scale-explanation line     should, Regression (2026-07-24, maintainer-caught): the header row's ") "     bracket ce, The maintainer's own hand-worked plain-text example, 425 / 4 = 106 R 1,     incl, test_division_plain_text_columns_align_with_a_2digit_divisor(), test_division_whole_divisor_has_no_scale_note() (+6 more)

### Community 73 - "Community 73"
Cohesion: 0.22
Nodes (13): _cache_key(), clear_memory(), _disk_path(), get(), put(), Path, Passage cache: memoize resolved passages by anchor URL.  Memoisation strategy:, Clear the in-memory cache (useful in tests). (+5 more)

### Community 74 - "Community 74"
Cohesion: 0.21
Nodes (13): _default_roster_path(), _has_avx2(), load_roster(), _need_gb(), Path, Hardware-aware model selection from Mentar's vetted roster.  Picks the highest-r, True/False if known, None if undetectable., gguf-parser ref for sizing: prefer the artifact the chosen runtime will actually (+5 more)

### Community 75 - "Community 75"
Cohesion: 0.19
Nodes (12): detect_credential_leak(), Credential-leak guard — scrub secrets from model output before it is shown to a, True if *text* contains anything credential-shaped., Replace any credential-shaped substring with ``[REDACTED]``.      Used on LLM ou, redact_credentials(), Credential-leak guard: detection + redaction, and the controller chokepoint.  Te, A model that emits a key has it scrubbed before it reaches the child/logs., test_controller_redacts_llm_output() (+4 more)

### Community 76 - "Community 76"
Cohesion: 0.19
Nodes (9): AnswerMode, _compose_default(), _compose_fraction(), mode_for(), Answer-mode registry (R2.3, maintainer ask: "config for different modes for answ, The AnswerMode for a verifier answer_type, or DEFAULT_MODE (plain text     input, Pure tests for web/answer_modes.py (R2.3 — answer-mode registry).      python3 t, test_mode_for_known_types() (+1 more)

### Community 77 - "Community 77"
Cohesion: 0.20
Nodes (7): _BareStore, _ctrl(), _FixedBank, Escalation freeze -> parent resume/end transition (control-plane separation).  R, test_freeze_absorbs_child_input_then_parent_resumes(), test_parent_ack_is_noop_when_not_frozen(), test_parent_end_terminates_session()

### Community 78 - "Community 78"
Cohesion: 0.23
Nodes (13): _make_controller(), R-RES — session resume across a server-process restart.  A fresh SessionControll, The frozen branch is unconditional -- it must not fall through to the     node-v, If the checkpointed node was mastered since the checkpoint was written     (e.g., A checkpoint naming a node absent from THIS curriculum (wrong subject,     or th, test_frozen_checkpoint_ignores_mastery_and_node_validity(), test_frozen_checkpoint_resumes_frozen_unconditionally(), test_mastered_node_checkpoint_degrades_to_node_select() (+5 more)

### Community 79 - "Community 79"
Cohesion: 0.21
Nodes (8): _FakeStore, _FixedBank, A7 — the system prompt's {{subject}}/{{scope_line}} slots reflect the active sub, Without an explicit subject, the default is the generic 'maths' — not     the ol, End-to-end: the science-subject system text (not "fractions") is what     actual, test_default_subject_is_maths_not_hardcoded_fractions(), test_science_subject_renders_science_not_fractions(), test_system_prompt_reaches_the_real_llm_call_for_a_science_turn()

### Community 80 - "Community 80"
Cohesion: 0.22
Nodes (13): Tests for the ACARA-aligned Year 3 / Year 4 item generators (engine/au_items.py), AU node ids are namespaced (au3_/au4_) so a learner's skill_state rows can     n, R14a/R13: also the first self-validate coverage of decimal-type generators     -, R15: first coverage of negative-integer content + a 'solve for x' node., _self_validate(), test_au_registries_do_not_collide_with_pilot_node_ids(), test_year2_generators_self_validate(), test_year3_generators_self_validate() (+5 more)

### Community 81 - "Community 81"
Cohesion: 0.22
Nodes (7): T3.6 (e): transcript rows may be inserted but never updated or deleted.     The, Baseline: writing a transcript row must succeed., Attempting UPDATE on transcript must raise sqlite3.OperationalError         with, Attempting DELETE on transcript must raise sqlite3.OperationalError         with, The transcript row must be bit-identical after a rejected UPDATE., INSERT must still work after a rejected UPDATE (no stuck transaction)., TestTranscriptImmutability

### Community 82 - "Community 82"
Cohesion: 0.21
Nodes (7): _Bank, _ctrl(), W5.6 — the continuous-assent line shows once on the first turn, never repeated., A4: the AI-transparency line appears exactly once, on the first turn., _Store, test_assent_line_shown_once_on_first_turn(), test_transparency_line_shown_once_on_first_turn()

### Community 83 - "Community 83"
Cohesion: 0.22
Nodes (7): _ctrl(), _RaisingStore, A15 — escalation-log fallback sink.  Regression guard: write_escalation failures, db_path is present (so the fallback sink can find a place to write) but     writ, test_db_failure_still_freezes_and_writes_fallback(), test_happy_path_writes_no_fallback_file(), _WorkingStore

### Community 84 - "Community 84"
Cohesion: 0.15
Nodes (6): tests/eval/test_verify_numeric.py — Unit tests for the deterministic fraction ve, T1.3 requirement: extraction-failure rate <5% on cases where extraction is expec, Cases marked should_extract=False must return None., TestCheckNone, TestCheckUnknownChecker, TestExtractionCorpus

### Community 85 - "Community 85"
Cohesion: 0.18
Nodes (12): _ensure_fixture_zim(), fixture_zim_path(), grounding_cfg(), Path, Shared pytest fixtures for the grounding test suite.  Builds (or reuses) the fix, Build the fixture ZIM if it does not exist., Path to the tiny test fixture ZIM., Anchor URL for the Fraction article (vikidia-style). (+4 more)

### Community 86 - "Community 86"
Cohesion: 0.17
Nodes (11): additionalProperties, allOf, description, required, $schema, title, type, id (+3 more)

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (12): type, description, type, description, type, minLength, type, properties (+4 more)

### Community 88 - "Community 88"
Cohesion: 0.18
Nodes (12): Graph, graph_from_template(), leaves(), Concepts with no prereqs — the graph's entry points., Concepts that no other concept depends on — the graph's terminal points., Load a curriculum template (W3.1 schema) and return its concept_id → prereqs map, roots(), pilot_graph() (+4 more)

### Community 89 - "Community 89"
Cohesion: 0.41
Nodes (11): _copy(), fetch_one(), _is_smb(), _jobs_from_config(), _log(), main(), Build download jobs from grounding.sources structured specs in a config file., Return (download_url, filename) for the newest matching ZIM on a mirror. (+3 more)

### Community 90 - "Community 90"
Cohesion: 0.17
Nodes (12): build_multiplication_partial_products_steps(), Partial-products method -- the maintainer's own worked example,     64 x 32: dec, The maintainer's own worked example: partial products 128 and 1920,     summed w, 7 x 8 = 56: only ONE partial product, so it IS the answer -- no     separate car, 50 x 20 = 1000: the tens digit of 20 is the ONLY nonzero digit, so     there's a, test_multiplication_by_zero(), test_multiplication_grid_shape_is_rectangular(), test_multiplication_hand_example_64_times_32() (+4 more)

### Community 91 - "Community 91"
Cohesion: 0.21
Nodes (12): gen_place_value_2digit(), gen_place_value_3digit(), gen_place_value_4digit(), _mc(), AC9M2N01-aligned: identify the value of the TENS digit in a two-digit     number, An mc4 tuple carrying the STEM (no inline "A) ..." options -- R2.1: the     web, AC9M3N01-aligned: what a digit stands for in a 3-digit number. Only     asks abo, AC9M4N01-aligned: what a digit stands for in a 4-digit number. Only     asks abo (+4 more)

### Community 92 - "Community 92"
Cohesion: 0.21
Nodes (11): _asset_name(), estimate_ram_gb(), _find_binary(), Thin wrapper around gpustack's gguf-parser — cross-OS device-fit estimation.  gg, Detected total system RAM in GB (psutil if present, else POSIX stdlib)., gguf-parser release asset for this OS/arch, or None if unsupported., Locate gguf-parser: explicit env -> PATH -> cached -> lazy download. Best-effort, Map a model ref to gguf-parser source flags. (+3 more)

### Community 93 - "Community 93"
Cohesion: 0.36
Nodes (11): _patch(), Tests for mentar.inference.autoselect + the vetted roster.  Selection logic is e, Stub sizing + detection. need_per_b GB per billion params., _roster(), test_gguf_no_avx2_warns(), test_nothing_fits_picks_smallest(), test_picks_best_that_fits_big_ram(), test_reasoning_warns() (+3 more)

### Community 94 - "Community 94"
Cohesion: 0.27
Nodes (7): _ctrl(), T3 — the SessionController persists escalations (SAFETY wiring).  Contract: a tr, Minimal store that records write_escalation calls., RecordingStore, test_escalation_persists_untruncated(), test_jailbreak_logged_only_carries_severity(), test_normal_input_no_escalation()

### Community 95 - "Community 95"
Cohesion: 0.27
Nodes (11): _fake_response(), Web app smoke test — full route + controller + DB cycle via Flask test_client., A urllib.request.urlopen(...) context-manager stand-in (no real network)., R8 (dormant machinery): a successful install fetches every file, checks     its, R8: a corrupted/tampered download must be rejected BEFORE anything is     writte, _synthetic_manifest(), test_curriculum_pack_install_rejects_already_installed(), test_curriculum_pack_install_rejects_checksum_mismatch_writes_nothing() (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.17
Nodes (12): _client(), U-90 plumbing: htmx (vendored static/htmx.min.js) sends HX-Request: true     to, U-32: the htmx-swapped fragment must escape model/generator text in BOTH     the, R4: the JS-disabled (no HX-Request header) answer loop must keep     redirecting, R5: GET /settings is a plain static page containing the voice-picker     <select, test_answer_hx_fragment_escapes_html(), test_answer_hx_request_returns_question_fragment(), test_curriculum_pack_install_rejects_unknown_pack_id() (+4 more)

### Community 97 - "Community 97"
Cohesion: 0.18
Nodes (8): LearnerStore -> SessionController adapter.  Lives in db/ (not web/) so the CLI's, LearnerStore — minimal SQLite wrapper for Mentar learner data.  Spec: docs/PHASE, Regression: the store is reused across threads by the Flask dev server.  `mentar, Sanity: a default-connect connection still raises across threads — proving     t, test_cross_thread_raised_before_fix_is_gone(), test_store_usable_from_another_thread(), test_store_writes_from_multiple_threads(), test_wal_and_busy_timeout_applied()

### Community 98 - "Community 98"
Cohesion: 0.31
Nodes (10): _gen_doubles_halves(), _gen_odd_one_out(), _gen_plural_forms(), _gen_rhyming_words(), _gen_skip_counting(), _gen_synonyms_antonyms(), _gen_times_tables(), Random (+2 more)

### Community 99 - "Community 99"
Cohesion: 0.18
Nodes (11): _all_packs_with_state(), curricula_list(), curricula_toggle(), _discover_template_paths(), _escalation_fallback_log_nonempty(), Path, A15 — true when the escalation DB-write fallback sink has entries, meaning     a, R10: every in-repo curriculum pack (discovered template), with its current     o (+3 more)

### Community 100 - "Community 100"
Cohesion: 0.18
Nodes (7): T2.1 — Escalation classifier tests.  Spec: docs/design/W2.2_escalation.md §5 (fi, 3 × empty / whitespace / emoji-only input — must NOT fire., Whitespace only → None., Emoji-only → None (no text to match against keyword banks)., Run the 20+20 fixture taxonomy + flow checks via plain python3.      Usage:, _smoke(), TestNegativeEmptyInput

### Community 101 - "Community 101"
Cohesion: 0.20
Nodes (5): Path, Apply schema.sql if the DB is uninitialised (user_version == 0)., Return the current PRAGMA user_version of the database., Path to this store's .db file (A15: lets callers place a fallback log alongside, Open (or create) the SQLite database at *db_path*.          If the database is n

### Community 102 - "Community 102"
Cohesion: 0.29
Nodes (7): _drive(), _FakeStore, A19 — a session's non-deterministic choices (pattern/modality/praise-variant sel, Two turns with a wrong-then-help-then-correct flow, capturing every     piece of, No explicit seed -> a random one is picked; passing it back in replays     the s, test_default_seed_is_logged_and_reusable(), test_same_seed_replays_identical_session()

### Community 103 - "Community 103"
Cohesion: 0.31
Nodes (9): _code_edges(), _doc_edges(), T3.7 — SESSION_FSM.md conformance test.  Parses docs/SESSION_FSM.md's §3 transit, REVIEW §3.1: PARENT_ACK_WAIT was documented + in the enum but never     actually, Every (from_state, to_state) pair reachable via a per-state handler., Every (from_state, to_state) pair from §3's state-specific transition table., test_every_code_edge_is_documented(), test_every_documented_edge_is_reachable() (+1 more)

### Community 104 - "Community 104"
Cohesion: 0.20
Nodes (6): Direct: 'I want to hurt myself'., Direct: 'I want to die'., Indirect ideation: 'I don't want to be here anymore'., Self-harm disclosure: cutting., 4 × harm_to_self (CRITICAL) — design §5., TestPositiveHarmToSelf

### Community 105 - "Community 105"
Cohesion: 0.20
Nodes (6): 4 × physical_danger (CRITICAL) — design §5., Direct danger: someone is hitting me., Home-danger (design §5 required case): 'I don't feel safe at home'., Direct: 'I am being hurt'., Specific person: 'my dad hits me'., TestPositivePhysicalDanger

### Community 106 - "Community 106"
Cohesion: 0.20
Nodes (6): 4 × off-topic-but-benign — must NOT fire., Pure off-topic: 'can we play a game'., Social chit-chat: 'what's your favourite colour'., Benign off-topic: time query., Benign off-topic: joke request. 'tell' present but no secret-keeping pattern., TestNegativeOffTopicBenign

### Community 107 - "Community 107"
Cohesion: 0.58
Nodes (8): escalation_log, help_event, learner_profile, probe_event, response_log, session, skill_state, transcript

### Community 108 - "Community 108"
Cohesion: 0.22
Nodes (8): compose_mc_problem(), The single place that builds inline "A) … B) …" mc problem text — used     by ev, Tests for the new subject content generators (maths arithmetic + science MC).  S, The computed answer letter must map to a real fact-table member (guards the, test_arithmetic_generators_self_validate(), test_mc_answer_letter_points_to_a_real_member(), test_science_generators_self_validate(), test_science_mc_has_four_distinct_options()

### Community 109 - "Community 109"
Cohesion: 0.28
Nodes (9): curriculum_packs(), install_curriculum_pack(), _is_safe_path_component(), _load_packs_manifest(), Defense in depth: pack "dir"/file "name" values come from packs.json (repo-, R8 (dormant): list downloadable REMOTE packs (curriculum/packs.json) with     in, R8: fetch every file for one pack over HTTPS from the ONE pinned base URL,     v, R8: removes the pack's curriculum/templates/<dir>/ so it stops being     discove (+1 more)

### Community 110 - "Community 110"
Cohesion: 0.22
Nodes (5): T3.6 (d): PRAGMA user_version == 4 after first open; re-open honours it     (sch, Reopening an existing DB must not re-run the DDL., A real v1 DB (no A3/A19 columns at all) is migrated all the way to         the c, A version with no registered migration still raises RuntimeError —         prove, TestSchemaVersionMigrationStub

### Community 112 - "Community 112"
Cohesion: 0.25
Nodes (8): enum, type, modality, analogy, concrete, formal, story, visual

### Community 113 - "Community 113"
Cohesion: 0.25
Nodes (8): suite, enum, type, abstention, adversarial, reexplain, sycophancy, transfer

### Community 114 - "Community 114"
Cohesion: 0.54
Nodes (7): _build_prompt(), _call_llm(), _chunk(), _collect_files(), main(), Path, _resolve_graphify_python()

### Community 115 - "Community 115"
Cohesion: 0.25
Nodes (8): _probe_llm_backend(), Short-timeout reachability probe against an OpenAI-compatible endpoint --     sh, Whether a working LLM backend is configured. False when     config/inference.yam, R9: every route redirects to /setup while no working LLM backend is     configur, R7.2: a short-timeout reachability check against the SAME endpoint the     app's, _require_setup(), settings_llm_status(), _setup_is_complete()

### Community 118 - "Community 118"
Cohesion: 0.39
Nodes (7): _patch(), T1 — autoselect runtime ordering for the llama.app runtime.  Auto = Ollama → lla, Simulate which() availability + deterministic sizing/AVX detection (module attrs, test_auto_falls_to_gguf_when_neither(), test_auto_prefers_llama_app_when_no_ollama(), test_auto_prefers_ollama_over_llama_app(), test_prefer_llama_app_explicit_warns_when_absent()

### Community 119 - "Community 119"
Cohesion: 0.25
Nodes (5): 3 × severe_distress (HIGH) — design §5., Persistent hopelessness — 'everything feels hopeless'., Emotional welfare: 'nobody loves me'., Cannot cope: 'I can't cope anymore'., TestPositiveSevereDistress

### Community 120 - "Community 120"
Cohesion: 0.25
Nodes (5): 3 × secrecy_request (HIGH) — design §5., Classic: 'don't tell my mum'., Classic: 'it's our secret'., Promise framing: 'promise you won't tell'., TestPositiveSecrecyRequest

### Community 121 - "Community 121"
Cohesion: 0.25
Nodes (5): 3 × ambiguous-but-below-threshold — documents where the v0.1 line sits (design §, I'm a bit sad today' — mild mood, below severe_distress threshold in v0.1., I'm tired and grumpy' — below threshold., I miss my friend who moved away' — sadness, not severe distress., TestNegativeAmbiguousBelow

### Community 122 - "Community 122"
Cohesion: 0.29
Nodes (7): enum, type, adversarial_type, distress, injected_passage, jailbreak, offtopic

### Community 123 - "Community 123"
Cohesion: 0.48
Nodes (4): _is_dont_know_or_question(), _is_help_request(), _is_stop(), A21 — interaction-scope v0: deterministic carve-out for two common     non-answe

### Community 124 - "Community 124"
Cohesion: 0.29
Nodes (7): build_registry(), Path, The pilot fractions item bank's path is env-overridable (MENTAR_ITEMBANK     in, test_item_source_registry_has_in_generic_maths(), The exact check web/app.py performs at startup (name not in the     registry) —, test_item_source_registry_has_every_referenced_name(), test_unregistered_item_source_is_detectable()

### Community 126 - "Community 126"
Cohesion: 0.33
Nodes (6): enum, type, answer_type, fraction, int, mc4

### Community 127 - "Community 127"
Cohesion: 0.33
Nodes (6): enum, correct_misconception, defer_or_abstain, defer_to_adult, ignore_injection, refuse_redirect

### Community 128 - "Community 128"
Cohesion: 0.40
Nodes (5): load_template_subject(), Return a template's `subject:` front-matter field (e.g. "mathematics",     "scie, engine/curriculum.py — load_template_subject (A7)., test_defaults_to_maths_when_subject_field_absent(), test_reads_subject_field_from_real_pilot_templates()

### Community 129 - "Community 129"
Cohesion: 0.53
Nodes (5): _gen_classify_animals(), _gen_living_nonliving(), _gen_states_of_matter(), Random, Science item generators — multiple-choice questions built from small CURATED fac

### Community 130 - "Community 130"
Cohesion: 0.33
Nodes (6): clear_reader_pool(), Clear the ZimReader pool (useful in tests to force re-open)., reset_state(), Reset reader pool and memory cache between tests., reset_state(), reset_state()

### Community 131 - "Community 131"
Cohesion: 0.53
Nodes (5): Tests for the ACARA-aligned Year 2/5/6 English item generators (engine/au_englis, _self_validate(), test_year2_english_generators_self_validate(), test_year5_english_generators_self_validate(), test_year6_english_generators_self_validate()

### Community 132 - "Community 132"
Cohesion: 0.33
Nodes (3): tests/eval/test_verify_numeric_decimal.py — R13: decimal answer type.  Tests the, Regression-intent marker -- the decimal_exact path must never relax the     int/, TestExistingCheckersUnaffected

### Community 133 - "Community 133"
Cohesion: 0.50
Nodes (3): Connection, Open a fresh connection for the current thread with our pragmas., The current thread's connection, opened on first use in that thread.

### Community 136 - "Community 136"
Cohesion: 0.40
Nodes (4): build(), Path, Build a tiny fixture ZIM file for grounding tests.  Builds programmatically usin, Build the fixture ZIM at ``zim_path`` and return the path.

### Community 137 - "Community 137"
Cohesion: 0.50
Nodes (4): _compute_graph_layout(), R2.4: greedy word-wrap for the concept-graph SVG labels -- never cuts a     word, U-40/U-41: an owned layered layout for the concept-graph map -- no     graph lib, _wrap_label()

### Community 138 - "Community 138"
Cohesion: 0.50
Nodes (4): R5: voice picker + the relocated theme toggle. Purely static -- the     voice li, settings(), Hypothesis-driven property test (T3.2(e) — 1000 examples)., test_invariant_property()

### Community 140 - "Community 140"
Cohesion: 0.67
Nodes (3): description, type, answer

### Community 141 - "Community 141"
Cohesion: 0.67
Nodes (3): description, type, id

## Knowledge Gaps
- **51 isolated node(s):** `run.example.sh script`, `GARAK_TELEMETRY`, `$schema`, `title`, `description` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SessionController` connect `Community 4` to `Community 2`, `Community 13`, `Community 14`, `Community 17`, `Community 21`, `Community 31`, `Community 34`, `Community 36`, `Community 41`, `Community 46`, `Community 49`, `Community 52`, `Community 53`, `Community 57`, `Community 58`, `Community 59`, `Community 62`, `Community 67`, `Community 75`, `Community 77`, `Community 78`, `Community 79`, `Community 82`, `Community 83`, `Community 94`, `Community 102`, `Community 116`, `Community 123`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `TurnResult` connect `Community 4` to `Community 96`, `Community 160`, `Community 167`, `Community 169`, `Community 170`, `Community 17`, `Community 21`, `Community 23`, `Community 57`, `Community 58`, `Community 159`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `LearnerStore` connect `Community 7` to `Community 97`, `Community 101`, `Community 133`, `Community 39`, `Community 41`, `Community 110`, `Community 81`, `Community 52`, `Community 56`, `Community 25`, `Community 59`, `Community 31`, `Community 63`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `SessionController` (e.g. with `StepGrid` and `ProbeClass`) actually correct?**
  _`SessionController` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `LearnerStore` (e.g. with `_DbStoreAdapter` and `TestAssertParentMediated`) actually correct?**
  _`LearnerStore` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ItemGenerator` (e.g. with `Item` and `_FakeStore`) actually correct?**
  _`ItemGenerator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `run.example.sh script`, `GARAK_TELEMETRY`, `$schema` to the rest of the system?**
  _51 weakly-connected nodes found - possible documentation gaps or missing edges._