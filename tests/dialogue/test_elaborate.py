"""R12.4/R12.5 — explanation variety context + the "Explain more" (elaborate) flow.

Covers:
  - "more" at the re-check enters HELP_ELABORATE and renders help_elaborate.md
    over the previous explanation (variety context threaded, not dropped)
  - elaborations are capped (ELABORATE_CAP) — beyond it, a gentle nudge, no loop
  - "more" with NO explanation live is scored like any other input (no dead state)
  - can_elaborate drives the web button: True only at the re-check with an
    explanation live and cap not reached
  - a fresh question resets the variety/elaborate context
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import (
    ELABORATE_CAP,
    FSMState,
    SessionController,
)

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


class _FakeStore:
    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass


class _PromptCapturingLlm:
    """Returns a canned explanation; records every prompt it was sent."""

    def __init__(self):
        self.prompts: list[str] = []
        self.reply = "A pizza has 3 equal slices. One slice is 1/3. 2 ÷ 2 = 1"

    def __call__(self, messages):
        self.prompts.append(messages[-1]["content"])
        return self.reply


def _to_recheck(llm=None):
    """Drive a fresh session into HELP_RECHECK_AWAIT via a child help request."""
    llm = llm or _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")  # help -> explain -> recheck await
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value
    return ctrl, llm


def test_more_elaborates_same_explanation():
    ctrl, llm = _to_recheck()
    first_explanation = ctrl._ctx.last_explanation
    assert first_explanation  # an explanation is live

    result = ctrl.step("more")
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value  # back at the re-check
    assert result.text  # a new explanation came back
    # The elaborate prompt carried the PREVIOUS explanation as context.
    assert any(first_explanation.splitlines()[0] in p for p in llm.prompts[-2:]), (
        "help_elaborate.md must receive {{previous_explanation}}"
    )
    # And it used the elaborate template (its distinctive instruction).
    assert any("MORE about it" in p for p in llm.prompts[-2:])


def test_elaborate_is_capped():
    ctrl, _ = _to_recheck()
    for _ in range(ELABORATE_CAP):
        ctrl.step("more")
        assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value
    # One past the cap: gentle nudge, question still live, NO new elaboration.
    result = ctrl.step("more")
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value
    assert "give the question a try" in result.text.lower()


def test_more_without_explanation_is_just_an_answer():
    """At AWAIT_ANSWER (no explanation live) 'more' must not enter elaborate —
    it goes through normal scoring (unreadable for a fraction -> re-ask nudge)."""
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        rng_seed=7,
    )
    ctrl.step(None)
    assert ctrl.state == FSMState.AWAIT_ANSWER.value
    ctrl.step("more")
    assert ctrl.state == FSMState.AWAIT_ANSWER.value  # re-ask, not HELP_ELABORATE


def test_can_elaborate_property():
    ctrl, _ = _to_recheck()
    assert ctrl.can_elaborate is True
    for _ in range(ELABORATE_CAP):
        ctrl.step("more")
    assert ctrl.can_elaborate is False  # cap reached -> web button hidden


def test_variety_context_resets_on_new_question():
    ctrl, _ = _to_recheck()
    assert ctrl._ctx.last_explanation
    ctrl.step("1/3")  # correct recheck -> advances; next PRESENT resets context
    assert ctrl._ctx.last_explanation == ""
    assert ctrl._ctx.elaborate_count == 0


def test_modality_templates_receive_previous_explanation():
    """R12.4: a second Help round's modality prompt carries the first
    explanation as do-differently context."""
    ctrl, llm = _to_recheck()
    first = ctrl._ctx.last_explanation
    ctrl.step("?")  # another help round (new modality) from the re-check
    assert any(first.splitlines()[0] in p for p in llm.prompts[-2:]), (
        "help_<modality>.md must receive {{previous_explanation}} on later rounds"
    )
