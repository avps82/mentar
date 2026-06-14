"""T5.x — proactive-probe outcome classification (W3.4 false-confidence table).

Covers docs/SPEC.md §14.4 + src/mentar/engine/probe_classify.py. stdlib-only;
also runnable as `python3 tests/engine/test_probe_classify.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from mentar.engine.probe_classify import ProbeClass, classify_probe  # noqa: E402


def test_clean_pass():
    assert classify_probe(True, None, 0.9, False, False) is ProbeClass.CLEAN_PASS


def test_single_failure_recovered_is_slip():
    assert classify_probe(False, True, 0.9, False, False) is ProbeClass.SLIP_SUSPECT


def test_false_confidence_when_both_fail_high_mastery_no_help():
    assert classify_probe(False, False, 0.9, False, False) is ProbeClass.FALSE_CONFIDENCE


def test_help_pressed_blocks_false_confidence():
    # Help was pressed → not silent over-confidence → not false_confidence
    assert classify_probe(False, False, 0.9, True, False) is ProbeClass.SLIP_SUSPECT


def test_forgetting_checked_before_false_confidence():
    # stale mastery wins even when mastery>=threshold and no help
    assert classify_probe(False, False, 0.9, False, True) is ProbeClass.FORGETTING_SUSPECT


def test_low_mastery_both_fail_is_expected_miss():
    assert classify_probe(False, False, 0.4, False, False) is ProbeClass.SLIP_SUSPECT


def test_threshold_boundary_is_inclusive():
    assert classify_probe(False, False, 0.85, False, False) is ProbeClass.FALSE_CONFIDENCE


def _smoke():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"SMOKE: all {len(fns)} probe-classify checks pass")


if __name__ == "__main__":
    _smoke()
