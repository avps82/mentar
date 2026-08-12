# Contributing to Mentar

Thanks for helping! Mentar is a **children's** product, so safety comes before features. Please
read [`SECURITY.md`](SECURITY.md) and [`docs/SAFETY.md`](docs/SAFETY.md) before touching anything
in `src/mentar/safety/` or the escalation path.

The tool-neutral project guide is [`AGENTS.md`](AGENTS.md) — start there for layout, commands, and
the protected-path rules. This file is the contributor workflow.

## Dev setup
```bash
git clone <repo> && cd mentar
pip install -e ".[dev,web]"
```

## The gate (required before every PR)
```bash
python -m pytest tests/ -q     # all tests green
ruff check .                   # lint clean
```
A change isn't done until both pass. New behaviour needs a test; each test file also carries an
inline `python3 tests/.../test_x.py` smoke runner (project convention).

## src-layout note
Code is at `src/mentar/<module>/`, **not** flat at repo root. If you hit an import error running a
test directly, the root `conftest.py` puts `src/` (and `.vendor/`) on `sys.path`; see
[`docs/TESTS.md`](docs/TESTS.md).

## Evaluation
Model/prompt evaluation lives in `eval/` (dataset, runner, judge, scorers). Run-only tools
(promptfoo, MathTutorBench) are invoked via their own runtimes and are **never vendored** or added
to `pyproject.toml`. Live model runs need the eval-host endpoint via env (`MENTAR_VLLM_BASE_URL` /
`MENTAR_VLLM_API_KEY`) — never commit those.

**Touching `prompts/*.md`?** A body-hash change invalidates the last recorded safety-eval claim
(`docs/EVAL_RESULTS.md`'s T1.5 adversarial run) — it was run against the old prompt text. Re-run
T1.5 through the pipeline against your new prompt and record the run date + result in
`docs/EVAL_RESULTS.md` before merging (see `AGENTS.md`). CI flags prompts-touching PRs as a
reminder; it doesn't run the eval itself.

## Commits & PRs
- Small, focused PRs off `main`; describe the change and how it was verified.
- Commit-message trailer: `Co-Authored-By: …` is fine; **do not add a `Claude-Session:` URL
  trailer** (public-repo hygiene).
- **Never commit secrets** (endpoints, tokens) or third-party grounding content. A pre-commit hook
  guards secret filenames/inline secrets — activate it via `core.hooksPath` (see `config/README.md`).
- Don't weaken a protected path (see `AGENTS.md` → RULES) without explicit maintainer sign-off.

## Licensing of contributions (CLA)

Mentar is AGPL-3.0-only and **dual-licensed**: the maintainer also offers commercial licences,
which requires the project's copyright to stay consolidated. Before a first external
contribution is merged you'll be asked to agree to a Contributor License Agreement granting
the maintainer the right to relicense your contribution. The full, honest reasoning — including
what you give up and what the AGPL guarantees you regardless — is in
[`LICENSING.md`](LICENSING.md). If that trade isn't acceptable to you, say so before investing
work; it's a fair position and better discussed up front.

## Where work is tracked
`docs/PHASE0_STATUS.md` is the canonical task ledger; `docs/REMAINDER_PLAN.md` holds the
prioritised remaining work.
