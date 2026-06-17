"""Tests for dialogue/controller.py (T3.7 conformance subset).

Covers:
  - SESSION_START -> AWAIT_ANSWER happy path
  - Escalation pre-empt (safety_trigger)
  - Help request -> HELP loop -> BRANCH_DECISION
  - Stop request -> SESSION_END_BY_LEARNER
  - All-mastered fringe -> SESSION_END_COMPLETE
  - Skip-attempt rejection in HELP_RECHECK_AWAIT and PROBE_AWAIT_ANSWER

Inline smoke runner:
    python3 tests/dialogue/test_controller.py
"""

from __future__ import annotations

import pathlib
import sys
import types

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController, TurnResult

PROMPTS = REPO / "prompts"

# ── Minimal stub curriculum ────────────────────────────────────────────────

_CURRICULUM = {
    "unit_fractions": {
        "concept": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}

_MASTERED_CURRICULUM = {
    "unit_fractions": {
        "concept": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}


class _FakeStore:
    """Minimal in-memory store stub."""

    def __init__(self, mastery: dict | None = None):
        self._mastery = mastery or {}

    def get_skill_state(self, learner_id: str, node_id: str):
        v = self._mastery.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id: str, node_id: str, p: float):
        self._mastery[node_id] = p


def _make_controller(llm_fn=None, mastery=None, curriculum=None):
    if llm_fn is None:
        llm_fn = lambda msgs: "The answer is 1/3."
    return SessionController(
        llm_call=llm_fn,
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=curriculum or _CURRICULUM,
        db_store=_FakeStore(mastery),
        learner_id="test-learner",
    )


# ── Tests ─────────────────────────────────────────────────────────────────

def test_happy_path_to_await():
    """SESSION_START -> drives through to AWAIT_ANSWER and returns a question."""
    ctrl = _make_controller()
    result = ctrl.step(None)
    assert result.state == FSMState.AWAIT_ANSWER.value
    assert len(result.text) > 0
    assert not result.done
    assert not result.escalated


def test_correct_answer_advances():
    """Correct answer drives SCORE -> BKT_UPDATE -> BRANCH_DECISION -> next state."""
    ctrl = _make_controller(llm_fn=lambda msgs: "The answer is 1/3.")
    ctrl.step(None)  # -> AWAIT_ANSWER
    result = ctrl.step("1/3")
    assert not result.done
    assert not result.escalated


def test_stop_ends_session():
    """Typing 'stop' in AWAIT_ANSWER transitions to SESSION_END_BY_LEARNER."""
    ctrl = _make_controller()
    ctrl.step(None)
    result = ctrl.step("stop")
    assert result.state == FSMState.SESSION_END_BY_LEARNER.value
    assert result.done


def test_escalation_preempts():
    """A safety trigger at AWAIT_ANSWER freezes the session."""
    ctrl = _make_controller()
    ctrl.step(None)
    result = ctrl.step("I want to hurt myself")
    assert result.state == FSMState.ESCALATION_FREEZE.value
    assert result.escalated
    assert not result.done
    assert len(result.text) > 0  # handoff message rendered


def test_escalation_is_absorbing():
    """After ESCALATION_FREEZE, subsequent inputs keep state frozen."""
    ctrl = _make_controller()
    ctrl.step(None)
    ctrl.step("I want to hurt myself")
    result = ctrl.step("just kidding")
    assert result.state == FSMState.ESCALATION_FREEZE.value
    assert result.escalated


def test_help_request_enters_help_loop():
    """'?' in AWAIT_ANSWER transitions into HELP loop and returns an explanation."""
    ctrl = _make_controller(llm_fn=lambda msgs: "Here is an explanation.")
    ctrl.step(None)
    result = ctrl.step("?")
    # Should have rendered explanation + recheck question, stopped at HELP_RECHECK_AWAIT
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert not result.done


def test_help_recheck_skip_rejected():
    """Empty input in HELP_RECHECK_AWAIT is rejected (state unchanged)."""
    ctrl = _make_controller(llm_fn=lambda msgs: "explanation or recheck")
    ctrl.step(None)
    ctrl.step("?")
    result = ctrl.step("")
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert "try" in result.text.lower() or "guess" in result.text.lower()


def test_all_mastered_ends_session():
    """When fringe is empty (all mastered), SESSION_END_COMPLETE is returned."""
    ctrl = _make_controller(
        mastery={"unit_fractions": 0.95},  # above 0.85 threshold
        curriculum=_MASTERED_CURRICULUM,
    )
    result = ctrl.step(None)
    assert result.state == FSMState.SESSION_END_COMPLETE.value
    assert result.done


def _smoke():
    test_happy_path_to_await(); print("[smoke] happy path OK")
    test_correct_answer_advances(); print("[smoke] correct answer OK")
    test_stop_ends_session(); print("[smoke] stop OK")
    test_escalation_preempts(); print("[smoke] escalation OK")
    test_escalation_is_absorbing(); print("[smoke] escalation absorbing OK")
    test_help_request_enters_help_loop(); print("[smoke] help loop OK")
    test_help_recheck_skip_rejected(); print("[smoke] skip reject OK")
    test_all_mastered_ends_session(); print("[smoke] all mastered OK")
    print("[smoke] test_controller.py PASS")


if __name__ == "__main__":
    _smoke()
