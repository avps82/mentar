"""T2 — _is_stale_mastery: forgetting-window detection (pure helper).

Verifies a skill's mastery timestamp is flagged stale only when older than
STALE_MASTERY_DAYS; missing/unparseable timestamps are never stale.

Inline smoke runner:
    python3 tests/dialogue/test_stale_mastery.py
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.dialogue.controller import STALE_MASTERY_DAYS, _is_stale_mastery  # noqa: E402

NOW = datetime(2026, 6, 19, 12, 0, 0, tzinfo=UTC)


def test_none_and_empty():
    assert _is_stale_mastery(None, now=NOW) is False
    assert _is_stale_mastery("", now=NOW) is False


def test_recent_not_stale():
    ts = (NOW - timedelta(days=1)).isoformat()
    assert _is_stale_mastery(ts, now=NOW) is False


def test_old_is_stale():
    ts = (NOW - timedelta(days=STALE_MASTERY_DAYS + 1)).isoformat()
    assert _is_stale_mastery(ts, now=NOW) is True


def test_boundary_not_stale():
    # strictly greater-than: exactly STALE_MASTERY_DAYS old is NOT stale
    ts = (NOW - timedelta(days=STALE_MASTERY_DAYS)).isoformat()
    assert _is_stale_mastery(ts, now=NOW) is False


def test_z_suffix_parsed():
    # 2026-06-01 is 18 days before NOW (> 14) -> stale; also checks 'Z' parsing
    assert _is_stale_mastery("2026-06-01T12:00:00Z", now=NOW) is True


def test_unparseable():
    assert _is_stale_mastery("not-a-date", now=NOW) is False


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} stale-mastery tests passed.")
