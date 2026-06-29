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
    from mentar.dialogue.controller import PRAISE_VARIANTS
    ctrl = _make_controller(llm_fn=lambda msgs: "Next question text.")
    ctrl.step(None)
    result = ctrl.step("1/3")
    assert any(v in result.text for v in PRAISE_VARIANTS)


def test_wrong_answer_is_told_and_enters_help():
    """A wrong answer is told it's wrong and auto-routed into Help (note 4b).

    Regression: the verifier scored silently (no right/wrong feedback), and even
    after the feedback fix a wrong answer just advanced to a new question. Now a
    wrong unaided answer scaffolds: feedback -> Help loop (does NOT reveal answer).
    """
    from mentar.dialogue.controller import WRONG_VARIANTS
    ctrl = _make_controller(llm_fn=lambda msgs: "explanation/recheck")
    ctrl.step(None)
    result = ctrl.step("2/5")                 # wrong (expected 1/3)
    assert any(v in result.text for v in WRONG_VARIANTS)      # told it's wrong (any variant)
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value  # auto-help, not advanced
    assert "1/3" not in result.text           # answer NOT revealed — they work to it


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


def test_help_explanation_not_swallowed_and_one_question():
    """A Help turn shows the explanation (not swallowed) and re-tries the SAME
    question — exactly ONE question to answer, not a new different one."""
    calls = {"n": 0}
    def counting_llm(msgs):
        calls["n"] += 1
        return f"LLM_MSG_{calls['n']}"
    ctrl = _make_controller(llm_fn=counting_llm)
    ctrl.step(None)                      # present (LLM_MSG_1) -> current_question
    result = ctrl.step("?")              # Q) LLM_MSG_1 + explain (LLM_MSG_2) + "Now you try it!"
    assert result.state == FSMState.HELP_RECHECK_AWAIT.value
    assert "LLM_MSG_2" in result.text                    # explanation shown, not swallowed
    assert "Now you try it" in result.text               # re-try the same question
    # only ONE question presented (the original, shown once as Q) — no second new one.
    assert result.text.count("Q) ") == 1


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


def test_mc_gibberish_asks_for_a_letter_same_question():
    """On a multiple-choice question, unreadable input asks for a letter and
    re-asks the SAME question (not a vague 'couldn't read' + a different one)."""
    import random as _random

    from mentar.engine.itemgen import ItemGenerator
    from mentar.engine.science_items import SCIENCE_GENERATORS
    curr = {"classify_animals": {
        "concept": "Animal groups", "answer_type": "mc4", "checker": "mc_choice",
        "expected_answer": "", "grounding": {}, "prerequisites": []}}
    ctrl = SessionController(
        llm_call=lambda m: "(unused)", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=curr, db_store=_FakeStore(), learner_id="t",
        item_bank=ItemGenerator(generators=SCIENCE_GENERATORS, rng=_random.Random(1)),
    )
    ctrl.step(None)
    question = ctrl._ctx.current_question
    result = ctrl.step("aaaa")                        # gibberish -> EXTRACT_FAIL
    assert result.state == FSMState.AWAIT_ANSWER.value
    assert "A, B, C or D" in result.text             # clear MC guidance
    assert question in result.text                    # SAME question kept on screen
    assert ctrl._ctx.last_scored_correct is None      # neither correct nor wrong


def test_help_recheck_shows_answer_format_hint():
    """'Now you try it!' shows the expected answer SHAPE from the known answer type
    (deterministic, must match the verifier) — '_/_' for fractions, a letter for MC."""
    import random as _random

    from mentar.engine.itemgen import ItemGenerator
    from mentar.engine.science_items import SCIENCE_GENERATORS

    # fraction node -> "_/_"
    ctrl = _make_controller(llm_fn=lambda m: "expl")  # unit_fractions (answer_type fraction)
    ctrl.step(None)
    r = ctrl.step("?")
    assert "_/_" in r.text

    # mc4 node -> letter guidance
    curr = {"classify_animals": {
        "concept": "Animal groups", "answer_type": "mc4", "checker": "mc_choice",
        "expected_answer": "", "grounding": {}, "prerequisites": []}}
    ctrl2 = SessionController(
        llm_call=lambda m: "expl", prompt_dir=PROMPTS, grounding_cfg={}, curriculum=curr,
        db_store=_FakeStore(), learner_id="t",
        item_bank=ItemGenerator(generators=SCIENCE_GENERATORS, rng=_random.Random(1)))
    ctrl2.step(None)
    r2 = ctrl2.step("?")
    assert "A, B, C or D" in r2.text


def test_mastered_node_advances_not_endless_probe():
    """Regression: once a node hit mastery, the FSM re-probed it EVERY turn (silent,
    no feedback, wrong answers slipped through). A probe must resolve + advance.
    Single-node curriculum: mastering it must COMPLETE the session, not loop."""
    ctrl = _make_controller()                 # single unit_fractions node, answer 1/3
    ctrl.step(None)
    probe_seen = 0
    for _ in range(15):
        if ctrl._ctx.state.value == FSMState.PROBE_AWAIT_ANSWER.value:
            probe_seen += 1
        r = ctrl.step("1/3")                  # always correct
        if r.done:
            break
    assert ctrl._ctx.state.value == FSMState.SESSION_END_COMPLETE.value
    assert probe_seen <= 2, f"stuck re-probing ({probe_seen}x)"


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
    test_help_explanation_not_swallowed_and_one_question(); print("[smoke] help explanation shown OK")
    test_stop_in_help_recheck_ends_session(); print("[smoke] stop in help recheck OK")
    test_stop_in_probe_ends_session(); print("[smoke] stop in probe OK")
    test_all_mastered_ends_session(); print("[smoke] all mastered OK")
    print("[smoke] test_controller.py PASS")


if __name__ == "__main__":
    _smoke()
