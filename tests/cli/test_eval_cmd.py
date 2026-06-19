"""T4 — `mentar eval` orchestration (_eval shells out: generate then judge).

Verifies the command wiring with subprocess mocked (no network): full run invokes
run_candidates then judge_responses; --dry-run skips the judge; --suite is passed through;
a non-zero generation exit short-circuits before judging.

Inline smoke runner:
    python3 tests/cli/test_eval_cmd.py
"""

from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import mentar.cli.__main__ as CLI  # noqa: E402

PATCH_TARGET = "mentar.cli.__main__.subprocess.run"


class _FakeRun:
    """Records each cmd list into `calls`; returns an object with the given returncode."""

    def __init__(self, calls: list, returncode: int = 0):
        self.calls = calls
        self.returncode = returncode

    def __call__(self, cmd, *a, **k):
        self.calls.append(list(cmd))
        return SimpleNamespace(returncode=self.returncode)


def test_full_pipeline_runs_both():
    calls: list = []
    with patch(PATCH_TARGET, _FakeRun(calls, 0)):
        rc = CLI._eval(SimpleNamespace(model="gemma4:12b", suite=None, dry_run=False),
                       pathlib.Path("/repo"))
    assert rc == 0
    assert len(calls) == 2
    assert any("run_candidates.py" in c for c in calls[0])
    assert "--model" in calls[0] and "gemma4:12b" in calls[0]
    assert any("judge_responses.py" in c for c in calls[1])


def test_dry_run_skips_judge():
    calls: list = []
    with patch(PATCH_TARGET, _FakeRun(calls, 0)):
        rc = CLI._eval(SimpleNamespace(model="m", suite=None, dry_run=True), pathlib.Path("/repo"))
    assert rc == 0
    assert len(calls) == 1
    assert "--dry-run" in calls[0]
    assert any("run_candidates.py" in c for c in calls[0])


def test_suite_passed_through():
    calls: list = []
    with patch(PATCH_TARGET, _FakeRun(calls, 0)):
        CLI._eval(SimpleNamespace(model="m", suite="adversarial", dry_run=True), pathlib.Path("/repo"))
    assert len(calls) == 1
    assert "--suite" in calls[0] and "adversarial" in calls[0]


def test_generation_failure_returns_rc_and_skips_judge():
    calls: list = []
    with patch(PATCH_TARGET, _FakeRun(calls, 2)):
        rc = CLI._eval(SimpleNamespace(model="m", suite=None, dry_run=False), pathlib.Path("/repo"))
    assert rc == 2
    assert len(calls) == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} eval-cmd tests passed.")
