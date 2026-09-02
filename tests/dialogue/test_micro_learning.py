"""R11 micro-learning — controller wiring tests.

Covers:
  - interleaving: NODE_SELECT switches away from the node just practised
  - spaced-review injection: a mastered-but-stale node is selected every REVIEW_EVERY_N items
  - staleness clock refresh on BKT update (a reviewed node stops being "stale" in-session)
  - micro-session cap: max_items ends the session warmly from BRANCH_DECISION
  - A19 replay: same rng_seed => same node sequence
"""

from __future__ import annotations

import pathlib
import sys
from datetime import UTC, datetime

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.fringe import REVIEW_EVERY_N

PROMPTS = REPO / "prompts"


def _int_node(expected: str = "5") -> dict:
    return {
        "label": "test skill",
        "answer_type": "int",
        "checker": "int_exact",
        "expected_answer": expected,
        "grounding": {},
        "prerequisites": [],
    }


_TWO_ROOTS = {"alpha": _int_node(), "beta": _int_node()}
_THREE_ROOTS = {"alpha": _int_node(), "beta": _int_node(), "gamma": _int_node()}
_REVIEW_CURRICULUM = {"alpha": _int_node(), "beta": _int_node(), "old_skill": _int_node()}


class _FakeStore:
    """Minimal in-memory store stub."""

    def __init__(self, mastery: dict | None = None):
        self._mastery = mastery or {}

    def get_skill_state(self, learner_id: str, node_id: str):
        v = self._mastery.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id: str, node_id: str, p: float, **kw):
        self._mastery[node_id] = p


def _make_controller(curriculum, **kwargs):
    return SessionController(
        llm_call=lambda msgs: "What is 2 + 3?",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=curriculum,
        db_store=_FakeStore(),
        learner_id="test-learner",
        **kwargs,
    )


# ── Interleaving ──────────────────────────────────────────────────────────


def test_interleaving_switches_node_between_items():
    """With two ready roots, consecutive items alternate concepts (no blocking)."""
    ctrl = _make_controller(_TWO_ROOTS, rng_seed=7)
    ctrl.step(None)
    first = ctrl.current_node_id
    ctrl.step("5")  # correct -> next item
    second = ctrl.current_node_id
    ctrl.step("5")
    third = ctrl.current_node_id
    assert second != first
    assert third != second


# ── Spaced-review injection ───────────────────────────────────────────────


def test_review_injects_stale_mastered_node():
    """Every REVIEW_EVERY_N-th completed item, NODE_SELECT picks a mastered-but-stale node."""
    ctrl = _make_controller(_REVIEW_CURRICULUM, rng_seed=7)
    ctx = ctrl._ctx
    ctx.mastery = {"alpha": 0.2, "beta": 0.2, "old_skill": 0.9}
    ctx.mastery_updated_at = {"alpha": None, "beta": None, "old_skill": "2026-01-01T00:00:00Z"}
    ctx.items_completed = REVIEW_EVERY_N
    ctx.state = FSMState.NODE_SELECT
    ctrl._do_node_select()
    assert ctx.current_node_id == "old_skill"


def test_no_review_when_mastery_is_fresh():
    """A freshly-updated mastered node is NOT stale -> normal fringe selection."""
    ctrl = _make_controller(_REVIEW_CURRICULUM, rng_seed=7)
    ctx = ctrl._ctx
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    ctx.mastery = {"alpha": 0.2, "beta": 0.2, "old_skill": 0.9}
    ctx.mastery_updated_at = {"alpha": None, "beta": None, "old_skill": now}
    ctx.items_completed = REVIEW_EVERY_N
    ctx.state = FSMState.NODE_SELECT
    ctrl._do_node_select()
    assert ctx.current_node_id in {"alpha", "beta"}


def test_bkt_update_refreshes_staleness_clock():
    """Scoring an item stamps mastery_updated_at, so a reviewed node leaves the stale set."""
    ctrl = _make_controller(_TWO_ROOTS, rng_seed=7)
    ctrl.step(None)
    node = ctrl.current_node_id
    ctrl.step("5")
    stamp = ctrl._ctx.mastery_updated_at[node]
    assert stamp is not None
    assert stamp.startswith(str(datetime.now(UTC).year))


# ── Micro-session cap ─────────────────────────────────────────────────────


def test_max_items_ends_session_warmly():
    """max_items completed items -> SESSION_END_COMPLETE with the warm wrap-up."""
    ctrl = _make_controller(_TWO_ROOTS, rng_seed=7, max_items=1)
    ctrl.step(None)
    result = ctrl.step("5")
    assert result.done
    assert result.state == FSMState.SESSION_END_COMPLETE.value
    assert "great session" in result.text.lower()


def test_no_cap_by_default():
    """max_items=None (default) -> a correct answer just advances."""
    ctrl = _make_controller(_TWO_ROOTS, rng_seed=7)
    ctrl.step(None)
    result = ctrl.step("5")
    assert not result.done


# ── A19 replay determinism ────────────────────────────────────────────────


def test_same_seed_same_node_sequence():
    """Two sessions with the same rng_seed visit the same node sequence."""

    def run() -> list[str | None]:
        ctrl = _make_controller(_THREE_ROOTS, rng_seed=123)
        seq = []
        ctrl.step(None)
        seq.append(ctrl.current_node_id)
        for _ in range(3):
            ctrl.step("5")
            seq.append(ctrl.current_node_id)
        return seq

    assert run() == run()
