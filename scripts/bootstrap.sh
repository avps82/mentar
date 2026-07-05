#!/usr/bin/env bash
# Create/refresh the project venv and install mentar into it.
# ponytail: venv is the wrap; `source .venv/bin/activate` per shell is unavoidable
# (a script can't mutate its parent shell's env).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,web]"

echo
echo "Done. Run ./mentar serve (no activation needed — it uses .venv directly)."
echo "For pytest/ruff: .venv/bin/python -m pytest, .venv/bin/ruff check ."
