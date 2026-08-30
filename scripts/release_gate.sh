#!/usr/bin/env bash
# Mentar release gate — everything CI would check, run locally, in one command.
#
#   ./scripts/release_gate.sh
#
# Why this is a SCRIPT and not the pre-push hook (2026-08-24):
#
#   `git push` opens the SSH connection to the remote FIRST (it needs the remote
#   refs to feed the hook on stdin), THEN runs pre-push, THEN transfers over that
#   same already-open connection. A hook that takes 21 minutes leaves the
#   connection idle for 21 minutes, and GitHub closes it long before that -- so
#   the hook PASSES and the push then dies with SIGPIPE and no error message.
#   Measured three times: a fast push always succeeds, a full-suite pre-push hook
#   never completes the transfer. A slow pre-push hook is not slow, it is broken.
#
# So: this script does the heavy work and stamps the commit it verified.
# pre-push stays fast and just checks the stamp matches what is being pushed.
set -uo pipefail
cd "$(dirname "$0")/.."

# The stamp records a SHA, but the gate tests the WORKING TREE. With
# uncommitted changes those are different things, and the stamp would certify a
# commit nobody tested -- exactly the "we know it can fail" case this is meant
# to prevent (caught 2026-08-25, the first time the two diverged in practice).
# So: commit first, then gate, then push.
if [ -n "$(git status --porcelain)" ]; then
  echo "GATE REFUSED: the working tree is dirty." >&2
  echo "" >&2
  echo "  The stamp records a commit SHA, but the gate tests what is on disk." >&2
  echo "  With uncommitted changes it would certify a commit that was never run." >&2
  echo "" >&2
  echo "      git add -A && git commit && ./scripts/release_gate.sh && git push" >&2
  exit 1
fi
# Checking cleanliness only HERE is not enough: a ~24 min run leaves a wide
# window to edit or commit, and the stamp written at the end would then certify
# a tree that was never the one tested. Remember what we actually ran against.
head_at_start=$(git rev-parse HEAD)
tree_at_start=$(git status --porcelain)

PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
RUFF=".venv/bin/ruff";  [ -x "$RUFF" ] || RUFF="ruff"
# A failed gate must not leave a PASSING stamp behind. Without this the stamp
# from an earlier green run survives, and if HEAD has not moved since, pre-push
# would accept a tree the gate just rejected (spotted 2026-08-25, first time the
# gate failed for real).
fail() { rm -f .gate-passed; echo ""; echo "GATE FAILED: $1" >&2; exit 1; }

echo "== 1/6 ruff"
command -v "$RUFF" >/dev/null 2>&1 || [ -x "$RUFF" ] || fail "ruff not installed"
"$RUFF" check . || fail "ruff is not clean"

echo "== 2/6 doc paths"
"$PY" src/mentar/tools/check_doc_paths.py || fail "a doc references a path not in the repo"

echo "== 3/6 test suite (~22 min)"
set +e
# --durations: the suite takes ~22 min on this 2-core box and recorded no
# per-test timings, so "why so long" could only be guessed at. Costs nothing.
out=$("$PY" -m pytest tests/ -q -rs --durations=15 2>&1); rc=$?
set -e
# tail -45, not -25: the durations block is ~17 lines and would otherwise push
# the -rs skip reasons out of view.
printf '%s\n' "$out" | tail -45
[ "$rc" -eq 0 ] || fail "tests are failing"

echo "== 4/6 browser checks actually ran"
# CI installs chromium and runs these; _skip_unless_browser() skips the whole
# file without it, so a green suite can mean "verified nothing about rendering".
if printf '%s' "$out" | grep -qE 'SKIPPED.*test_browser_ui|test_browser_ui.*[Ss]kipped'; then
  fail "the browser checks SKIPPED (chromium missing) -- CI runs them, so this would go red"
fi

echo "== 5/6 packaging imports (frozen-binary safety)"
# The single-file builds failed on all three platforms for days behind a green
# gate and green CI: nothing here touched the packaging path, so a module-level
# `import inflect` (it reads Python source while importing, which a PyInstaller
# bundle has none of) went unnoticed. These tests import the app under that
# exact condition. They do NOT build a binary -- only scripts/build_binary.py
# proves a bundle runs -- but they are the part that costs seconds, so the
# cheap half of the check can never rot again.
"$PY" -m pytest tests/test_frozen_imports.py -q >/dev/null \
  || fail "the app cannot be imported in a frozen binary (see tests/test_frozen_imports.py)"

echo "== 6/6 gitleaks (full history)"
if command -v gitleaks >/dev/null 2>&1 && gitleaks --help 2>&1 | grep -qE '^[[:space:]]+git[[:space:]]'; then
  gitleaks git . --no-banner --redact -v || fail "gitleaks found something"
else
  echo "   NOTE: gitleaks missing or older than CI's v8.30.1 -- not gated locally" >&2
fi

# Re-verify before stamping. If HEAD moved or the tree was touched during the
# run, some tests ran against code that is no longer here and the stamp would be
# a lie that pre-push then trusts. Refuse rather than certify a mixed tree.
sha=$(git rev-parse HEAD)
if [ "$sha" != "$head_at_start" ]; then
  fail "HEAD moved during the run ($head_at_start -> $sha) — re-run the gate"
fi
if [ "$(git status --porcelain)" != "$tree_at_start" ]; then
  fail "the working tree changed during the run — re-run the gate"
fi
echo "$sha" > .gate-passed
echo ""
echo "GATE PASSED for $sha  (stamped .gate-passed — pre-push will accept this commit)"
