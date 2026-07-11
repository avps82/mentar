"""A9 — loud-fail at startup when a curriculum node has a checker but no
item-source coverage (would otherwise silently mis-score against
expected_answer, a transfer-seed QUESTION string, not a real answer).
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import SessionController

PROMPTS = REPO / "prompts"

_CURRICULUM_UNCOVERED = {
    "unit_fractions": {
        "label": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "What is one third of nine?",  # a transfer-seed QUESTION, not "3"
        "grounding": {}, "prerequisites": [],
    },
}

_CURRICULUM_FREE_TEXT = {
    "open_reflection": {
        "label": "open reflection", "answer_type": "free_text", "checker": "none",
        "expected_answer": "", "grounding": {}, "prerequisites": [],
    },
}


class _EmptyBank:
    """Covers nothing — every node falls through to the LLM-question fallback."""

    def has(self, node_id):
        return False


class _FixedBank:
    def has(self, node_id):
        return True

    def sample(self, node_id):
        raise NotImplementedError

    def example(self, node_id, exclude_id=None):
        raise NotImplementedError


def test_uncovered_checkable_node_raises_with_item_bank():
    with pytest.raises(RuntimeError, match="unit_fractions"):
        SessionController(
            llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
            curriculum=_CURRICULUM_UNCOVERED, db_store=object(), learner_id="L",
            item_bank=_EmptyBank(),
        )


def test_covered_node_does_not_raise():
    ctrl = SessionController(
        llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM_UNCOVERED, db_store=object(), learner_id="L",
        item_bank=_FixedBank(),
    )
    assert ctrl is not None


def test_free_text_checker_none_never_raises_even_uncovered():
    """checker: none nodes are never scored against expected_answer — no risk,
    no raise, regardless of item-bank coverage."""
    ctrl = SessionController(
        llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM_FREE_TEXT, db_store=object(), learner_id="L",
        item_bank=_EmptyBank(),
    )
    assert ctrl is not None


def test_item_bank_none_does_not_raise():
    """item_bank=None is the deliberate legacy/test fallback — not itself a
    misconfigured production subject, so it's exempt from this check (the real
    production entry points, web/app.py and cli/__main__.py, always pass a
    real item source)."""
    ctrl = SessionController(
        llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM_UNCOVERED, db_store=object(), learner_id="L",
        item_bank=None,
    )
    assert ctrl is not None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} uncovered-node tests passed.")
