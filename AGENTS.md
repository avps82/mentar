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
pip install -e ".[dev,web]"     # dev tools + the Flask web extra
```
CI installs `.[dev,web,grounding]` pinned against `constraints.txt` (A19) — regenerate it after
a deliberate dependency bump (see the comment at the top of that file).

## Commands
```bash
python -m pytest tests/ -q       # full test suite
ruff check .                     # lint (must be clean)
mentar setup                     # hardware-aware model pick + download
mentar run-session               # headless tutoring session
mentar serve                     # localhost web app
mentar validate-template <path>  # curriculum template validator
```

## Project layout
- Code: `src/mentar/<module>/` (**src-layout, not flat**). Modules: `engine`, `dialogue`,
  `safety`, `inference`, `eval`, `grounding`, `db`, `tools`, `cli`, `web`.
- Tests mirror src under `tests/`; each test file also carries an inline `python3`-runnable smoke
  runner. The root `conftest.py` puts `src/` (and `.vendor/`) on `sys.path`; see `docs/TESTS.md`.
- `eval/` = model/prompt evaluation (run-only tools like promptfoo/MathTutorBench live here, never
  vendored). `prompts/` = **tutor product** prompt templates (not agent prompts — don't conflate).

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
- **Secrets:** never commit endpoints/tokens (a pre-commit hook guards this). Commit messages use a
  `Co-Authored-By` trailer but **no `Claude-Session` URL trailer**.

Safety first: read `SECURITY.md` + `docs/SAFETY.md` before touching anything in `safety/` or the
escalation path.
