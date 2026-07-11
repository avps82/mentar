"""W5.6 — the continuous-assent line shows once on the first turn, never repeated.
A4 — the AI-transparency line (SAFETY §5.5) shows alongside it, same pattern.

Inline smoke: python3 tests/dialogue/test_assent.py
"""
from __future__ import annotations

from pathlib import Path

from mentar.dialogue.controller import ASSENT_LINE, TRANSPARENCY_LINE, SessionController
from mentar.engine.itembank import Item

_PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
_ITEM = Item(id="it1", node="n1", problem="What is 1+1?", answer="2",
             answer_type="int", checker="int_exact")


class _Bank:
    def has(self, n):  # noqa: ANN001
        return True

    def sample(self, n):  # noqa: ANN001
        return _ITEM

    def example(self, n, exclude_id=None):  # noqa: ANN001
        return _ITEM


class _Store:
    def get_skill_state(self, learner_id, node_id):  # noqa: ANN001
        return None

    def update_skill_state(self, learner_id, node_id, p):  # noqa: ANN001
        pass


def _ctrl() -> SessionController:
    return SessionController(
        llm_call=lambda messages: "ok",
        prompt_dir=_PROMPTS,
        grounding_cfg={},
        curriculum={"n1": {"label": "n1", "answer_type": "int", "checker": "int_exact",
                           "expected_answer": "2", "grounding": {}, "prerequisites": []}},
        db_store=_Store(),
        learner_id="L",
        item_bank=_Bank(),
    )


def test_assent_line_shown_once_on_first_turn():
    c = _ctrl()
    r1 = c.step(None)
    assert ASSENT_LINE in r1.text, "assent line missing from the first turn"
    r2 = c.step("2")
    assert ASSENT_LINE not in (r2.text or ""), "assent line wrongly repeated on a later turn"


def test_transparency_line_shown_once_on_first_turn():
    """A4: the AI-transparency line appears exactly once, on the first turn."""
    c = _ctrl()
    r1 = c.step(None)
    assert TRANSPARENCY_LINE in r1.text, "transparency line missing from the first turn"
    assert r1.text.count(TRANSPARENCY_LINE) == 1
    r2 = c.step("2")
    assert TRANSPARENCY_LINE not in (r2.text or ""), "transparency line wrongly repeated"


if __name__ == "__main__":
    test_assent_line_shown_once_on_first_turn()
    print("  ✓ assent line shown once on first turn")
    test_transparency_line_shown_once_on_first_turn()
    print("  ✓ transparency line shown once on first turn")
