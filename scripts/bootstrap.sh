#!/usr/bin/env bash
# Create/refresh the project venv and install mentar into it.
# ponytail: venv is the wrap; `source .venv/bin/activate` per shell is unavoidable
# (a script can't mutate its parent shell's env).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,web]"

# Activate the secret-scan pre-commit hook (scripts/git-hooks/pre-commit) --
# previously documented in CONTRIBUTING.md but never auto-wired, so a fresh
# clone had NO secret guard until a contributor manually ran this themselves
# (2026-07-25 finding: exists, was inert by default).
git config core.hooksPath scripts/git-hooks

echo
echo "Done. Run ./mentar serve (no activation needed — it uses .venv directly)."
echo "For pytest/ruff: .venv/bin/python -m pytest, .venv/bin/ruff check ."
echo "Secret-scan pre-commit hook activated (core.hooksPath=scripts/git-hooks)."
