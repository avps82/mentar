"""T-A13 wiring — the output guard actually runs inside SessionController._make_safe_llm.

Contract: an LLM output matching a hard-block or off-scope pattern never reaches
TurnResult.text (the child), and an incident row is written via write_escalation.
A clean LLM output is unaffected.

Inline smoke runner:
    python3 tests/safety/test_output_guard_wiring.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import SessionController
from mentar.engine.itembank import Item
from mentar.safety.output_guard import NEUTRAL_REDIRECT

PROMPTS = REPO / "prompts"
_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "1/3", "grounding": {}, "prerequisites": [],
    }
}

# A checkable item bank so the INITIAL question comes from here, not the (stubbed,
# possibly-blocked) LLM — isolates the guard check to the Help-explanation LLM call.
_ITEM = Item(id="it1", node="unit_fractions", problem="What is one third of 9?",
             answer="3", answer_type="int", checker="int_exact")


class _FixedBank:
    def has(self, node_id):
        return True

    def sample(self, node_id):
        return _ITEM

    def example(self, node_id, exclude_id=None):
        return _ITEM


class _RecordingStore:
    def __init__(self):
        self.incidents: list[dict] = []

    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p, **kw):
        pass

    def write_escalation(
        self, learner_id, trigger_class, trigger_text_verbatim,
        severity=None, session_id=None, turn_index=None, session_outcome=None,
    ):
        self.incidents.append({
            "trigger_class": trigger_class,
            "trigger_text_verbatim": trigger_text_verbatim,
            "severity": severity,
            "session_outcome": session_outcome,
        })
        return len(self.incidents)


def _ctrl(store, llm_fn):
    return SessionController(
        llm_call=llm_fn, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=store, learner_id="L1", item_bank=_FixedBank(),
    )


def test_blocked_output_never_reaches_child():
    store = _RecordingStore()
    ctrl = _ctrl(store, lambda m: "Here are steps to suicide you could take.")
    ctrl.step(None)                          # -> AWAIT_ANSWER
    result = ctrl.step("?")                  # -> Help loop, calls the LLM

    assert "suicide" not in result.text.lower()
    assert NEUTRAL_REDIRECT in result.text
    assert len(store.incidents) == 1
    row = store.incidents[0]
    assert row["trigger_class"] == "output_blocked:violent_or_harmful"
    assert row["severity"] == "critical"
    assert row["session_outcome"] == "output_blocked"
    assert len(row["trigger_text_verbatim"]) <= 80  # short matched span, not the full output


def test_clean_output_unaffected():
    store = _RecordingStore()
    ctrl = _ctrl(store, lambda m: "Think of it like sharing a pizza into equal slices.")
    ctrl.step(None)
    result = ctrl.step("?")

    assert "pizza" in result.text
    assert store.incidents == []


if __name__ == "__main__":
    test_blocked_output_never_reaches_child()
    print("  ✓ test_blocked_output_never_reaches_child")
    test_clean_output_unaffected()
    print("  ✓ test_clean_output_unaffected")
