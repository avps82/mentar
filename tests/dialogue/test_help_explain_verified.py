"""A14 — Help explanations are verified before serving (SAFETY §6.2 Level 2).

Contract: a stubbed LLM emitting a wrong arithmetic claim ("3/4 + 1/4 = 2/4")
never reaches TurnResult.text; a correct worked example passes unchanged; if
every bounded attempt is wrong, the deterministic fallback hint is served.

Inline smoke runner:
    python3 tests/dialogue/test_help_explain_verified.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import SessionController
from mentar.engine.itembank import Item

PROMPTS = REPO / "prompts"
_CURRICULUM = {
    "unit_fractions": {
        "concept": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "1/3", "grounding": {}, "prerequisites": [],
    }
}

# A checkable item bank so the INITIAL question comes from here, not the (stubbed)
# LLM — isolates the arithmetic-claim check to the Help-explanation LLM call.
_ITEM = Item(id="it1", node="unit_fractions", problem="What is one third of 9?",
             answer="3", answer_type="int", checker="int_exact")


class _FixedBank:
    def has(self, node_id):
        return True

    def sample(self, node_id):
        return _ITEM

    def example(self, node_id, exclude_id=None):
        return _ITEM


class _FakeStore:
    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass


def _ctrl(llm_fn):
    return SessionController(
        llm_call=llm_fn, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L1",
        item_bank=_FixedBank(),
    )


def test_wrong_claim_never_reaches_child():
    """Every attempt emits the SAME wrong claim -> exhausts the retry budget -> falls
    back to the deterministic hint, never the wrong arithmetic."""
    ctrl = _ctrl(lambda m: "So 3/4 + 1/4 = 2/4, easy!")
    ctrl.step(None)
    result = ctrl.step("?")
    assert "3/4 + 1/4 = 2/4" not in result.text


def test_correct_worked_example_passes_unchanged():
    ctrl = _ctrl(lambda m: "Think of it this way: 1/4 + 1/4 = 2/4, which is the same as 1/2.")
    ctrl.step(None)
    result = ctrl.step("?")
    assert "1/4 + 1/4 = 2/4" in result.text


def test_prose_without_claims_passes_unchanged():
    ctrl = _ctrl(lambda m: "Think of a fraction like slices of a shared pizza.")
    ctrl.step(None)
    result = ctrl.step("?")
    assert "slices of a shared pizza" in result.text


def test_second_attempt_correct_after_first_wrong():
    """First generation is wrong, second (retry, bounded) is correct — the good
    one is served."""
    calls = {"n": 0}

    def llm_fn(messages):
        calls["n"] += 1
        if calls["n"] == 1:
            return "So 3/4 + 1/4 = 2/4."
        return "Actually, 3/4 + 1/4 = 1 whole."

    ctrl = _ctrl(llm_fn)
    ctrl.step(None)
    result = ctrl.step("?")
    assert "3/4 + 1/4 = 2/4" not in result.text
    assert "3/4 + 1/4 = 1 whole" in result.text


if __name__ == "__main__":
    test_wrong_claim_never_reaches_child()
    print("  ✓ test_wrong_claim_never_reaches_child")
    test_correct_worked_example_passes_unchanged()
    print("  ✓ test_correct_worked_example_passes_unchanged")
    test_prose_without_claims_passes_unchanged()
    print("  ✓ test_prose_without_claims_passes_unchanged")
    test_second_attempt_correct_after_first_wrong()
    print("  ✓ test_second_attempt_correct_after_first_wrong")
