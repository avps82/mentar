"""W3.3 §3.3 — one BKT observation per attempt, not per re-check (2026-09-02).

With the shipped numeric priors (guess 0.05, slip 0.10) a single wrong answer
takes mastery 0.84 -> 0.36, and the Help loop re-checks the SAME item up to
HELP_RETRY_CAP times, each re-check previously a fresh BKT observation: four
correlated wrongs on ONE item took 0.70 -> 0.0003. The rule now: the first
scored attempt on an item is always observed (hinted or not); a later hinted
WRONG on that item is logged but not observed; a hinted CORRECT always is.

Mutation check: revert the `item_observed` gate in _do_help_recheck_score and
the first test fails on the call count.

    python3 -m pytest tests/dialogue/test_bkt_observations.py
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController  # noqa: E402
from mentar.engine.bkt import P_L0, bkt_update, params_for  # noqa: E402

PROMPTS = REPO / "prompts"

_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}
WRONG, RIGHT = "2/3", "1/3"


class _RecordingStore:
    def __init__(self):
        self.calls: list[tuple[str, float]] = []
        self._m: dict[str, float] = {}

    def get_skill_state(self, learner_id, node_id):
        v = self._m.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id, node_id, p, **kw):
        self.calls.append((node_id, p))
        self._m[node_id] = p


def _make():
    store = _RecordingStore()
    ctrl = SessionController(
        llm_call=lambda msgs: "An explanation.",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=_CURRICULUM,
        db_store=store,
        learner_id="test-learner",
        rng_seed=11,
    )
    return ctrl, store


def test_a_wrong_then_two_hinted_rechecks_produce_two_observations_not_four():
    """wrong (observed) -> hinted wrong (logged only) -> hinted right (observed)."""
    ctrl, store = _make()
    ctrl.step(None)                     # PRESENT -> AWAIT_ANSWER
    ctrl.step(WRONG)                    # SCORE wrong -> BKT (1) -> auto-help -> RECHECK_AWAIT
    assert len(store.calls) == 1
    ctrl.step(WRONG)                    # hinted wrong on an observed item: no BKT
    assert len(store.calls) == 1, "a correlated hinted wrong must not be a second observation"
    ctrl.step(RIGHT)                    # hinted correct: the resolution IS observed
    assert len(store.calls) == 2

    params = params_for("fraction")
    expected = bkt_update(bkt_update(P_L0, False, False, params), True, True, params)
    assert store.calls[-1][1] == pytest.approx(expected)


def test_help_before_answering_makes_the_first_recheck_the_observation():
    """The FIRST attempt is observed even when it is hinted; only later hinted
    wrongs on the same item are skipped."""
    ctrl, store = _make()
    ctrl.step(None)
    ctrl.step("?")                      # Help pressed before any answer
    assert store.calls == []
    ctrl.step(WRONG)                    # first attempt on the item -- hinted, wrong, OBSERVED
    assert len(store.calls) == 1
    ctrl.step(WRONG)                    # second hinted wrong -- not observed
    assert len(store.calls) == 1
    params = params_for("fraction")
    assert store.calls[0][1] == pytest.approx(bkt_update(P_L0, False, True, params))


def test_the_flag_resets_on_a_new_item():
    """A new PRESENT must re-arm the first-attempt rule, or the second item's
    first wrong would be silently dropped."""
    ctrl, store = _make()
    ctrl.step(None)
    ctrl.step(WRONG)
    ctrl.step(RIGHT)                    # resolves item 1 -> BRANCH_DECISION -> ... next PRESENT
    n = len(store.calls)
    assert ctrl._ctx.item_observed is False or ctrl.current_node_id is None, (
        "flag must be cleared when a new item is presented"
    )
    if ctrl.current_node_id:            # a second item was presented
        ctrl.step(WRONG)
        assert len(store.calls) == n + 1, "the first wrong on a NEW item must be observed"


def test_help_on_a_probe_makes_the_first_probe_attempt_the_observation():
    """A probe item is a NEW item. Two cold-corrects fire the probe; the child
    asks for help on it; the first re-check on the PROBE item is that item's
    first scored attempt and must be observed -- the flag from the previous
    item must not carry over (gap found in the 2026-09-02 review)."""
    ctrl, store = _make()
    ctrl.step(None)
    ctrl.step(RIGHT)                    # item 1: observed (1)
    ctrl.step(RIGHT)                    # item 2: observed (2) -> mastery >= 0.85 -> probe fires
    assert len(store.calls) == 2
    assert ctrl._ctx.state is FSMState.PROBE_AWAIT_ANSWER, "precondition: the probe fired"
    ctrl.step("?")                      # help on the probe -> Help loop on the probe item
    ctrl.step(WRONG)                    # first attempt on the probe item: OBSERVED
    assert len(store.calls) == 3, "the probe item's first attempt must be observed"
    ctrl.step(WRONG)                    # correlated: not observed
    assert len(store.calls) == 3
