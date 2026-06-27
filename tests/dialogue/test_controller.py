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

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController

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


def test_correct_answer_gives_praise():
    """A correct answer is acknowledged (not silently advanced)."""
    ctrl = _make_controller(llm_fn=lambda msgs: "Next question text.")
    ctrl.step(None)
    result = ctrl.step("1/3")
    low = result.text.lower()
    assert any(w in low for w in ("right", "correct", "well done", "great job"))


def test_wrong_answer_marked_with_correct_answer():
    """A wrong answer is told it's wrong AND given the correct answer (not silent).

    Regression: the deterministic verifier scored silently — the child was never
    told right/wrong and wrong answers just advanced.
    """
    ctrl = _make_controller(llm_fn=lambda msgs: "Next question text.")
    ctrl.step(None)
    result = ctrl.step("2/5")                 # wrong (expected 1/3)
    low = result.text.lower()
    assert "not quite" in low
    assert "1/3" in result.text               # the verified correct answer


def test_gibberish_is_reprompted_not_scored():
    """Unreadable input (SAFE_REJECT) is re-prompted, never scored as wrong."""
    ctrl = _make_controller(llm_fn=lambda msgs: "Another question.")
    ctrl.step(None)
    result = ctrl.step("jjjd")
    assert result.state == FSMState.AWAIT_ANSWER.value
    assert "couldn't" in result.text.lower() or "try" in result.text.lower()
    assert ctrl._ctx.last_scored_correct is None   # never scored


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


def test_help_explanation_not_swallowed():
    """A Help turn returns BOTH the explanation and the re-check question (not just the last)."""
    calls = {"n": 0}
    def counting_llm(msgs):
        calls["n"] += 1
        return f"LLM_MSG_{calls['n']}"
    ctrl = _make_controller(llm_fn=counting_llm)
    ctrl.step(None)                      # present (LLM_MSG_1)
    result = ctrl.step("?")              # help_explain (LLM_MSG_2) + recheck present (LLM_MSG_3)
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert "LLM_MSG_2" in result.text and "LLM_MSG_3" in result.text


def test_stop_in_help_recheck_ends_session():
    """'stop' during a Help re-check ends the session (not treated as an answer)."""
    ctrl = _make_controller(llm_fn=lambda msgs: "explanation or recheck")
    ctrl.step(None)
    ctrl.step("?")                       # -> HELP_RECHECK_AWAIT
    result = ctrl.step("stop")
    assert result.state == FSMState.SESSION_END_BY_LEARNER.value
    assert result.done


def test_stop_in_probe_ends_session():
    """'stop' during a Probe ends the session (not treated as an answer)."""
    ctrl = _make_controller()
    ctrl.step(None)                      # establishes current_node_id
    ctrl._ctx.state = FSMState.PROBE_AWAIT_ANSWER   # jump into probe await
    result = ctrl.step("stop")
    assert result.state == FSMState.SESSION_END_BY_LEARNER.value
    assert result.done


def test_help_at_recheck_not_scored_as_answer():
    """'?' during a Help re-check must NOT be scored — it gives another Help round.

    Regression for the defect where _do_help_recheck_await lacked the help guard,
    so '?'/'help' was captured as help_answer and run through the verifier.
    """
    ctrl = _make_controller(llm_fn=lambda msgs: "explanation or recheck")
    ctrl.step(None)
    ctrl.step("?")                                   # -> HELP_RECHECK_AWAIT (round 1)
    result = ctrl.step("?")                          # ask for help AGAIN at the re-check
    # Routed back through the Help loop (another modality), not scored:
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert ctrl._ctx.help_answer != "?"              # never captured as an answer
    assert ctrl._ctx.help_scored_correct is None     # never scored


def test_help_at_probe_enters_help_not_scored():
    """'?'/'help' during a Probe gives help (enters the Help loop), never scored.

    Regression: _do_probe_await_answer first lacked the guard (scored help as an
    answer), then dead-ended with a re-prompt that hid the question. It must route
    to the Help loop so the child gets a hint and a question.
    """
    for token in ("?", "help"):
        ctrl = _make_controller(llm_fn=lambda msgs: "explanation or recheck")
        ctrl.step(None)
        ctrl._ctx.state = FSMState.PROBE_AWAIT_ANSWER
        result = ctrl.step(token)
        assert result.state == FSMState.HELP_RECHECK_AWAIT.value  # in the Help loop
        assert result.text.strip()                   # a hint/question was shown
        assert ctrl._ctx.probe_answer != token       # not captured as an answer
        assert ctrl._ctx.probe_scored_correct is None  # never scored


def test_help_gives_fallback_hint_when_llm_empty():
    """If the LLM returns nothing, Help still gives a deterministic hint (not blank).

    Regression: when the Help explanation LLM failed, the child got no hint (and
    the web turn could blank out).
    """
    ctrl = _make_controller(llm_fn=lambda msgs: "")
    ctrl.step(None)
    result = ctrl.step("?")
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert result.text.strip()                       # a hint was produced
    assert "step" in result.text.lower()             # fallback phrasing


def test_llm_exception_does_not_crash():
    """A raising LLM backend degrades gracefully (no exception → no 500)."""
    def boom(msgs):
        raise RuntimeError("backend down")
    ctrl = _make_controller(llm_fn=boom)
    ctrl.step(None)                                  # present (LLM safe-wrapped)
    result = ctrl.step("?")                          # Help -> fallback hint, no raise
    assert not result.escalated
    assert result.text.strip()


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
    test_help_explanation_not_swallowed(); print("[smoke] help explanation shown OK")
    test_stop_in_help_recheck_ends_session(); print("[smoke] stop in help recheck OK")
    test_stop_in_probe_ends_session(); print("[smoke] stop in probe OK")
    test_all_mastered_ends_session(); print("[smoke] all mastered OK")
    print("[smoke] test_controller.py PASS")


if __name__ == "__main__":
    _smoke()
