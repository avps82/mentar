"""A7 — the system prompt's {{subject}}/{{scope_line}} slots reflect the active
subject, not a hardcoded "fractions" (REVIEW §2.1: a science session's system
text contained "fractions").
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
    "photosynthesis": {
        "concept": "photosynthesis", "answer_type": "mc4", "checker": "mc_choice",
        "expected_answer": "A", "grounding": {}, "prerequisites": [],
    }
}
_ITEM = Item(id="s1", node="photosynthesis", problem="Q?", answer="A",
             answer_type="mc4", checker="mc_choice")


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


def test_science_subject_renders_science_not_fractions():
    ctrl = SessionController(
        llm_call=lambda m: "explanation", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_FixedBank(), subject="science",
    )
    system_text = ctrl._render_system_prompt("photosynthesis", "")
    assert "science" in system_text.lower()
    assert "fractions" not in system_text.lower()


def test_default_subject_is_maths_not_hardcoded_fractions():
    """Without an explicit subject, the default is the generic 'maths' — not
    the old hardcoded 'fractions', so an unconfigured caller doesn't claim a
    scope it may not have."""
    ctrl = SessionController(
        llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_FixedBank(),
    )
    system_text = ctrl._render_system_prompt("photosynthesis", "")
    assert "maths" in system_text.lower()
    assert "fractions" not in system_text.lower()


def test_system_prompt_reaches_the_real_llm_call_for_a_science_turn():
    """End-to-end: the science-subject system text (not "fractions") is what
    actually gets sent as the system message during a real Help turn."""
    captured = {}

    def spy_llm(messages):
        captured["system"] = messages[0]["content"]
        return "A gentle science explanation."

    ctrl = SessionController(
        llm_call=spy_llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_FixedBank(), subject="science",
    )
    ctrl.step(None)
    ctrl.step("?")  # triggers Help -> _do_help_explain -> calls spy_llm

    assert "system" in captured
    assert "science" in captured["system"].lower()
    assert "fractions" not in captured["system"].lower()


if __name__ == "__main__":
    test_science_subject_renders_science_not_fractions()
    print("  ✓ test_science_subject_renders_science_not_fractions")
    test_default_subject_is_maths_not_hardcoded_fractions()
    print("  ✓ test_default_subject_is_maths_not_hardcoded_fractions")
    test_system_prompt_reaches_the_real_llm_call_for_a_science_turn()
    print("  ✓ test_system_prompt_reaches_the_real_llm_call_for_a_science_turn")
