"""T3.3 — BKT per-turn update: cold-start priors + hinted-win discount.

Covers docs/design/W3.3_bkt.md §4 invariants. stdlib-only; also runnable as a
plain `python3 tests/engine/test_bkt.py` smoke check (no pytest required).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from mentar.engine.bkt import P_L0, bkt_update, params_for  # noqa: E402


def test_class_priors_resolve():
    assert params_for("mc4").guess == 0.25
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


def test_wrong_streak_from_cold_start_never_raises_above_prior():
    """A20 (BKT Option B): a wrong-answer streak from cold start must never
    raise mastery above the prior — was: rises then plateaus (~10% -> 21% ->
    22%), counterintuitive for a parent-facing %. Now: stays flat or drops."""
    p = params_for("mc4")
    cur = P_L0
    for _ in range(8):
        nxt = bkt_update(cur, False, False, p)
        assert nxt <= cur + 1e-12, f"mastery rose on a wrong answer: {cur} -> {nxt}"
        cur = nxt


def test_hinted_win_and_correct_paths_unchanged_by_option_b():
    """A20 must not touch the CORRECT-answer paths, hinted or not."""
    p = params_for("mc4")
    assert bkt_update(0.3, True, False, p) > 0.3          # correct, unaided
    assert bkt_update(0.3, True, True, p) > 0.3            # correct, hinted
    # A hinted correct still earns strictly less than a cold correct.
    assert bkt_update(0.3, True, True, p) < bkt_update(0.3, True, False, p)


def test_a_wrong_answer_never_earns_learns_credit_hinted_or_not():
    """2026-08-16. This asserted the opposite until today: that a hinted WRONG
    "still gets the learns credit -- A20 only gates the *unaided* incorrect
    case". That implemented A20's spec BODY and violated A20's own ACCEPTANCE
    CRITERION ("a wrong-answer streak from cold start never raises mastery above
    the prior -- was: rises then plateaus ~22%"), which is exactly what the
    hinted path still did: 0.10 -> 0.2231, measured end-to-end.

    It is also the COMMON path, not a corner: FLOW.md routes
    HELP_RECHECK_SCORE -> BKT_UPDATE(hinted), so a struggling child's wrong
    answers are usually hinted. The maintainer resolved the contradiction in
    favour of the acceptance criterion.
    """
    for answer_type in ("mc4", "int"):
        p = params_for(answer_type)
        # Wrong is wrong: the hint changes nothing about a failed attempt.
        assert bkt_update(0.3, False, True, p) == bkt_update(0.3, False, False, p)

        for hinted in (True, False):
            cur = P_L0
            for _ in range(8):
                nxt = bkt_update(cur, False, hinted, p)
                assert nxt <= cur + 1e-12, (
                    f"{answer_type} hinted={hinted}: mastery rose on a wrong "
                    f"answer, {cur} -> {nxt}"
                )
                cur = nxt
            assert cur <= P_L0, f"{answer_type} hinted={hinted}: ended above the prior"


def test_a_collapsed_skill_still_recovers_when_the_child_gets_it_right():
    """The risk the 2026-08-16 gate change creates, pinned.

    Denying learns credit to every wrong answer lets a long wrong streak drive
    mastery to ~1e-11. The module header warns that at exactly 0 "no correct
    answer can ever move mastery" -- so a child who bombs a skill and then
    learns it must still be able to climb back, or the fix would be worse than
    the bug. The learns term on a CORRECT observation is what rescues it.
    """
    for answer_type in ("int", "mc4"):
        p = params_for(answer_type)
        cur = P_L0
        for _ in range(10):
            cur = bkt_update(cur, False, True, p)      # ten hinted-wrong
        assert cur < 1e-6, "precondition: the streak collapsed mastery"

        traj = [cur := bkt_update(cur, True, False, p) for _ in range(6)]
        assert traj[0] > P_L0, "one correct answer must lift it back over the prior"
        assert traj[-1] >= 0.85, f"{answer_type}: never recovers to mastery: {traj}"
        assert all(traj[i] <= traj[i + 1] + 1e-12 for i in range(len(traj) - 1))


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
