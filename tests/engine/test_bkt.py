"""T3.3 — BKT per-turn update: cold-start priors + hinted-win discount.

Covers docs/design/W3.3_bkt.md §4 invariants. stdlib-only; also runnable as a
plain `python3 tests/engine/test_bkt.py` smoke check (no pytest required).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from mentar.engine.bkt import P_L0, BktParams, bkt_update, params_for  # noqa: E402


def test_class_priors_resolve():
    assert params_for("mc4").guess == 0.20
    assert params_for("int").guess == 0.05
    assert params_for("fraction").guess == 0.05
    # template override wins
    assert params_for("mc4", {"guess": 0.33}).guess == 0.33


def test_hinted_discount_is_strict():
    p = params_for("mc4")
    cold = bkt_update(0.3, True, False, p)
    hinted = bkt_update(0.3, True, True, p)
    assert cold > hinted  # a hinted win earns strictly less mastery


def test_direction_and_bounds():
    p = params_for("mc4")
    up = bkt_update(0.3, True, False, p)
    down_cond = bkt_update(0.3, False, False, p)
    assert up > 0.3
    assert down_cond < 0.3  # before-learning conditioning pulls a wrong answer down
    for v in (up, down_cond):
        assert 0.0 <= v <= 1.0


def test_seed_from_uninitialised_uses_p_l0():
    p = params_for("mc4")
    a = bkt_update(None, True, False, p)
    b = bkt_update(0.0, True, False, p)
    assert a == b
    assert a > 0.0  # regression guard: never update from a degenerate zero


def test_no_instant_graduation_from_hinted_win():
    # a single hinted-correct from the prior must not cross the 0.85 threshold
    assert bkt_update(P_L0, True, True, params_for("mc4")) < 0.85


def test_determinism():
    p = params_for("int")
    assert bkt_update(0.4, True, False, p) == bkt_update(0.4, True, False, p)


def test_monotone_bounded_run():
    p = params_for("int")
    cur, seq = P_L0, []
    for _ in range(8):
        cur = bkt_update(cur, True, False, p)
        seq.append(cur)
    assert all(seq[i] <= seq[i + 1] + 1e-12 for i in range(len(seq) - 1))
    assert max(seq) <= 1.0


def _smoke():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"SMOKE: all {len(fns)} T3.3 checks pass")


if __name__ == "__main__":
    _smoke()
