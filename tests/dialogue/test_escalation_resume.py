"""Escalation freeze -> parent resume/end transition (control-plane separation).

Regression for the gap flagged in PR #5: ESCALATION_FREEZE is absorbing for step()
(child input cannot unfreeze a session), but the parent's resume/end via
parent_acknowledge() MUST transition out of the freeze.

Inline smoke: python3 tests/dialogue/test_escalation_resume.py
"""
from __future__ import annotations

from pathlib import Path

from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.itembank import Item

_PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
_ITEM = Item(
    id="it1", node="n1", problem="What is 1+1?", answer="2",
    answer_type="int", checker="int_exact",
)


class _FixedBank:
    def has(self, node_id):  # noqa: ANN001
        return True

    def sample(self, node_id):  # noqa: ANN001
        return _ITEM

    def example(self, node_id, exclude_id=None):  # noqa: ANN001
        return _ITEM


class _BareStore:
    def get_skill_state(self, learner_id, node_id):  # noqa: ANN001
        return None

    def update_skill_state(self, learner_id, node_id, p):  # noqa: ANN001
        pass

    def write_escalation(self, learner_id, trigger_class, trigger_text_verbatim, **kwargs):  # noqa: ANN001
        return 1


def _ctrl() -> SessionController:
    return SessionController(
        llm_call=lambda messages: "ok",
        prompt_dir=_PROMPTS,
        grounding_cfg={},
        curriculum={
            "n1": {
                "concept": "n1", "answer_type": "int", "checker": "int_exact",
                "expected_answer": "2", "grounding": {}, "prerequisites": [],
            }
        },
        db_store=_BareStore(),
        learner_id="L",
        item_bank=_FixedBank(),
    )


def test_freeze_absorbs_child_input_then_parent_resumes():
    c = _ctrl()
    c.step(None)                                   # present first item
    r = c.step("I want to die")                    # distress -> freeze
    assert r.escalated and c.state == FSMState.ESCALATION_FREEZE.value
    # Child input during the freeze is absorbed (cannot unfreeze).
    r = c.step("please continue")
    assert r.escalated and c.state == FSMState.ESCALATION_FREEZE.value
    # Parent resumes -> out of the freeze, next question presented.
    r = c.parent_acknowledge("resume")
    assert not r.escalated
    assert c.state != FSMState.ESCALATION_FREEZE.value
    assert r.text, "resume should present the next question"


def test_parent_end_terminates_session():
    c = _ctrl()
    c.step(None)
    c.step("I want to die")
    r = c.parent_acknowledge("end")
    assert r.done and c.state == FSMState.SESSION_END_BY_PARENT.value


def test_parent_ack_is_noop_when_not_frozen():
    c = _ctrl()
    c.step(None)                                   # AWAIT_ANSWER, not frozen
    r = c.parent_acknowledge("resume")
    assert not r.escalated                          # no-op, no crash, no transition
    assert c.state == FSMState.AWAIT_ANSWER.value


if __name__ == "__main__":
    test_freeze_absorbs_child_input_then_parent_resumes()
    print("  ✓ freeze absorbs child input; parent resumes")
    test_parent_end_terminates_session()
    print("  ✓ parent end terminates")
    test_parent_ack_is_noop_when_not_frozen()
    print("  ✓ parent ack no-op when not frozen")
