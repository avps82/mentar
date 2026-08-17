# AGENTS.md

Tool-neutral guidance for any AI coding agent (or human) working in this repo. Tool-specific files
(e.g. `CLAUDE.md`) point here; keep project guidance in **this** file.

## What Mentar is
An OSS-first, **local-first AI tutor for children** that supplements school. Python `src`-layout;
a deterministic FSM dialogue engine + BKT mastery + a safety layer + ZIM grounding. Spec authority
lives in `docs/` — **`docs/PHASE0_STATUS.md` is the canonical task ledger**, and
`docs/REMAINDER_PLAN.md` tracks remaining work.

## Setup
```bash
./scripts/bootstrap.sh          # creates .venv, installs dev+web extra into it
```
Modern Python installs (Homebrew, Debian/Ubuntu system Python) refuse global `pip install`
(PEP 668 `externally-managed-environment`) — the venv is required, not optional.

Base principle: everything runs from `.venv`, always. Use the repo-root `./mentar` wrapper —
it execs `.venv/bin/mentar` directly, so you never need `source .venv/bin/activate` just to run
the CLI (a subprocess can't activate a venv for its parent shell, so this sidesteps that instead
of fighting it):
```bash
./mentar serve                   # same for setup / run-session / eval / validate-template
```
`source .venv/bin/activate` is still needed for non-`mentar` tools in the same shell (`pytest`,
`ruff`) — or prefix those too: `.venv/bin/python -m pytest`, `.venv/bin/ruff check .`.

If you manage your own venv/tooling, the raw install is `pip install -e ".[dev,web]"`. CI installs
`.[dev,web,grounding]` pinned against `constraints.txt` (A19) — regenerate it after a deliberate
dependency bump (see the comment at the top of that file).

## Commands
```bash
.venv/bin/python -m pytest tests/ -q   # full test suite
.venv/bin/ruff check .                 # lint (must be clean)
./mentar setup                         # hardware-aware model pick + download
./mentar run-session                   # headless tutoring session
./mentar serve                         # localhost web app
./mentar validate-template <path>      # curriculum template validator
./mentar eval                          # T1 eval harness over eval/dataset_v1.jsonl
./mentar backup                        # checkpoint + copy the DB, then verify the copy
```

## Project layout
- Code: `src/mentar/<module>/` (**src-layout, not flat**). Modules: `engine`, `dialogue`,
  `safety`, `inference`, `eval`, `grounding`, `db`, `tools`, `cli`, `web`.
- Tests mirror src under `tests/`; each test file also carries an inline `python3`-runnable smoke
  runner. The root `conftest.py` puts `src/` (and `.vendor/`) on `sys.path`; see `docs/TESTS.md`.
- `eval/` = model/prompt evaluation (run-only tools like promptfoo/MathTutorBench live here, never
  vendored). `prompts/` = **tutor product** prompt templates (not agent prompts — don't conflate).

## OKF documentation bundles — creating/editing any `.md` under `docs/`, `curriculum/templates/`, or `curriculum/visual_scaffolds/`
These three trees are [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
(Open Knowledge Format) **v0.2** bundles — plain markdown + YAML frontmatter, readable by graphify
and other agents without bespoke parsing. Rules verified against the spec text itself (not
inferred from existing files — that inference was wrong once already, see `docs/DOC_AUDIT.md`
2026-07-23 addendum):

1. **`index.md` and `log.md` are reserved filenames — they carry NO frontmatter, with exactly one
   exception.** Just an `#` heading + body (a directory listing of links, per §6 of the spec).
   Never add `type:`, `title:`, `tags:`, etc. to one. Code already relies on this split —
   `_TEMPLATES_DIR` scans, `visual_scaffold.py`'s loader, and web app discovery all skip
   `index.md`/`log.md` explicitly; a test glob that forgets the exclusion will crash trying to
   YAML-parse a bare heading as a dict.
   **The exception (v0.2 §12):** a BUNDLE-ROOT `index.md` may declare `okf_version: "0.2"`, and
   that is "the only place frontmatter is permitted in an `index.md`". The three bundle roots
   (`docs/`, `curriculum/templates/`, `curriculum/visual_scaffolds/`) each carry exactly that one
   key and nothing else. Nested `index.md` files stay bare.
2. **Every other `.md` file in these trees is a concept document and MUST start with a frontmatter
   block whose first field is `type: <Concept Type Name>`** — the one truly required OKF field.
   `title`/`description`/`tags` are recommended; add them. Producer-specific extra keys
   (`version`, `owner`, …) are explicitly allowed by the spec and don't need to change.

3. **v0.2 renamed two v0.1 fields. Both old forms still parse, so existing files are valid:**
   - `timestamp:` → `generated: { by, at }` (§5.2). **`by` is REQUIRED inside `generated`** — an
     actor, `<producer>/<version>` for a tool (e.g. `claude/opus-5`), or `human:<id>`. The 265
     existing files keep bare `timestamp:` deliberately: the spec says a consumer "may fall back
     to legacy `timestamp` when `generated` is absent", and back-filling `by` for files written
     across many sessions would be inventing provenance. **New concept docs SHOULD carry
     `generated`** with a truthful actor.
   - body `# Citations` → `sources:` frontmatter (§5.1). This repo has no `# Citations` sections,
     so nothing to migrate; 18 files already use `sources:`.
   Also new and optional in v0.2: `verified`, `status`, `stale_after`, the `Attested Computation`
   concept type, and a `# Computation` body heading.

Before trusting any "is this OKF-compliant" claim (including a prior one in this repo's own
history), re-derive it from the spec text, not from what similar files already look like.

Two checks split that job, because they ask different questions:
- `tests/test_okf_conformance.py` — **offline**, every run. Does the repo match the version it
  *declares*? It never fetches, so no upstream edit can redden an unrelated commit.
- the `okf-spec-version` CI job — **network, weekly only**. Is the declared version still the
  *current* one? The bundles sat on v0.1 for two months after v0.2 shipped because nothing asked.
  It fails the weekly run on drift, and GitHub emails the owner when a scheduled workflow fails.
  To act on that failure: re-derive the diff from the spec text (above), then bump the three
  bundle-root `index.md` files **and** `DECLARED_VERSION` in the conformance test.

## The gate (every change)
`python -m pytest tests/ -q` **green** *and* `ruff check .` **clean** before a change is done.

## Prompt changes require a safety-eval re-run (A18)
Any change to a `prompts/*.md` file's body-hash (the versioned prompt templates — see
`prompts/README.md`) invalidates the last recorded pipeline-safety claim (the T1.5 adversarial
run in `docs/EVAL_RESULTS.md`), since the eval was run against the *old* prompt text. Before
merging a prompts/-touching PR:
1. Re-run the T1.5 adversarial suite through the pipeline against the new prompt.
2. Record the run date + result next to the existing claim in `docs/EVAL_RESULTS.md` (don't let
   the claim silently age against text it no longer describes).
CI flags PRs that touch `prompts/` with a required-checklist comment (see `.github/workflows/`)
as a reminder — it does not run the eval itself (eval is run-only/off-CI, per AGENTS.md's own
`eval/` convention above).

## Conventions
- DB/persistence writes from the controller are **best-effort** (`_safe_store`): a logging failure
  must never break a tutoring turn. Follow that pattern.
- Prefer well-maintained OSS libs for non-differentiating work; own only the thin glue + the
  safety-critical/differentiating logic. Judge a dependency by its *shape* (focused lib ✅ /
  wrong-shape framework-server ⚠️).

## RULES — protected paths (do not weaken without explicit sign-off)
- **Child input NEVER reaches the LLM.** The controller routes/scores child text
  deterministically only (verifier + FSM); no child-typed text is ever placed in an LLM prompt.
  This is why child-driven prompt injection is structurally dead here. Any change that relaxes
  it (e.g. the INTERACTION_SCOPE proposal) needs explicit safety review first.
  (Repo review 2026-07-03, REVIEW §8.8.)
- **`src/mentar/eval/verify_numeric.py`** — the decimal `SAFE_REJECT` is safety-critical. Don't
  regress it.
- **`src/mentar/safety/escalation.py`** — escalation/freeze + the fixed handoff wording. Changes
  need safety review.
- **DB transcript immutability** (schema triggers) — append-only; never add an update/delete path.
- **`.vendor/`** — vendored upstream (PyYAML). Don't edit; it ships its own LICENSE.
- **Content:** never commit third-party grounding content; Khan Academy is CC BY-NC-SA (NC). See
  `docs/LICENSE_AUDIT.md`.
- **UI work:** read `DESIGN.md` first — the token contract, contrast floors, the
  computed-vs-model-prose rendering split, and the guardrails that each shipped as
  a bug. Its token table is CI-checked against `style.css`, so it cannot go stale.
- **Secrets:** never commit endpoints/tokens (a pre-commit hook guards this). Commit messages use a
  `Co-Authored-By` trailer but **no `Claude-Session` URL trailer**.

Safety first: read `SECURITY.md` + `docs/SAFETY.md` before touching anything in `safety/` or the
escalation path.
