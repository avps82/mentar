""""Show human working" (2026-07-19 maintainer feedback) — deterministic
step-by-step arithmetic wired into HELP_ELABORATE (R12.5).

Covers:
  - an "Explain more" press on a step-eligible node (plain addition) skips
    the LLM and produces a real StepGrid, not prose
  - the initial Help modality explanations are UNCHANGED (still LLM prose) —
    step-display only activates on the elaborate press, per the maintainer's
    explicit placement ask
  - a non-eligible node (fraction) falls through to the unchanged LLM path
  - the grid does not leak across a fresh question
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.arithmetic_steps import StepGrid
from mentar.engine.itemgen import ItemGenerator

PROMPTS = REPO / "prompts"

_ADDITION_CURRICULUM = {
    "addition": {
        "label": "addition", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "5", "grounding": {}, "prerequisites": [],
    },
}

_FRACTION_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "1/3", "grounding": {}, "prerequisites": [],
    },
}


class _FakeStore:
    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass


class _PromptCapturingLlm:
    def __init__(self):
        self.calls = 0
        self.reply = "A prose explanation about addition."

    def __call__(self, messages):
        self.calls += 1
        return self.reply


def _addition_bank():
    from mentar.engine.itemgen import _gen_addition
    return ItemGenerator(generators={"addition": _gen_addition})


def test_elaborate_on_addition_node_produces_a_real_step_grid():
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_ADDITION_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_addition_bank(), rng_seed=7,
    )
    ctrl.step(None)
    assert ctrl.current_answer_type == "int"
    llm_calls_before_help = llm.calls
    ctrl.step("?")  # child-initiated help -> LLM prose (unchanged initial explanation)
    assert llm.calls > llm_calls_before_help, "initial Help explanation must still use the LLM"
    assert ctrl.elaborate_steps_grid is None, "no elaborate press yet"

    calls_before_elaborate = llm.calls
    ctrl.step("more")  # Explain more -> step-eligible node -> grid, no LLM call
    assert llm.calls == calls_before_elaborate, "step-display must skip the LLM entirely"
    grid = ctrl.elaborate_steps_grid
    assert isinstance(grid, StepGrid)
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value


def test_elaborate_on_fraction_node_still_uses_llm_prose():
    """A non-step-eligible node shape falls through unchanged to the existing
    LLM-prose elaborate behaviour (R12.5, built earlier the same day)."""
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_FRACTION_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")
    calls_before_elaborate = llm.calls
    ctrl.step("more")
    assert llm.calls > calls_before_elaborate, "non-eligible nodes must still use the LLM"
    assert ctrl.elaborate_steps_grid is None


def test_steps_grid_does_not_leak_across_a_fresh_question():
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_ADDITION_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_addition_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")
    ctrl.step("more")
    assert ctrl.elaborate_steps_grid is not None

    # Correctly answer the re-check -> BRANCH_DECISION -> a fresh PRESENT.
    correct = ctrl._ctx.current_item.answer
    ctrl.step(correct)
    assert ctrl.elaborate_steps_grid is None, "a fresh question must clear the stale grid"
