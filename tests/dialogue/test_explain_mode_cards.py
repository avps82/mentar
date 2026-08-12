"""explain-mode (2026-08-12) — method cards wired into HELP_ELABORATE, mirroring
"Show human working"'s wiring test shape (test_show_human_working.py) for the
new Type 2/4 tier: a node without a step grid but whose live item carries a
computed `method_steps` card also skips the LLM on Explain-more.

Covers:
  - an "Explain more" press on a method-card-eligible node (percentage-of)
    skips the LLM and produces the real card, not prose
  - the initial Help modality explanation is UNCHANGED (still LLM prose) --
    same placement discipline the step grids use
  - the sibling-draw worked_example fed to the FIRST Help prompt now contains
    the card's lines instead of a bare "(Answer: X)" string when the sibling
    has one -- the actual root-cause fix for the reported gap
  - the card does not leak across a fresh question
  - a node with NEITHER a step grid nor a method card falls through unchanged
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController  # noqa: E402
from mentar.engine.au_items import gen_percentage_of_quantity  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.engine.science_items import SCIENCE_GENERATORS  # noqa: E402

PROMPTS = REPO / "prompts"
SCAFFOLDS = REPO / "curriculum" / "visual_scaffolds"

_PERCENTAGE_CURRICULUM = {
    "percentage_of_quantity": {
        "label": "percentage of a quantity", "answer_type": "int", "checker": "int_exact",
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
    """Same shape as test_show_human_working.py's, plus the actual outgoing
    messages -- needed here to prove the worked-example TEXT changed, not just
    that a call happened."""

    def __init__(self):
        self.calls = 0
        self.reply = "A prose explanation about percentages."
        self.last_messages: list[dict] | None = None

    def __call__(self, messages):
        self.calls += 1
        self.last_messages = messages
        return self.reply


def _percentage_bank():
    return ItemGenerator(generators={"percentage_of_quantity": gen_percentage_of_quantity})


def _fraction_bank():
    from mentar.engine.itemgen import _gen_unit_fractions
    return ItemGenerator(generators={"unit_fractions": _gen_unit_fractions})


def test_elaborate_on_percentage_node_produces_a_real_method_card():
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    assert ctrl.current_answer_type == "int"
    llm_calls_before_help = llm.calls
    ctrl.step("?")  # child-initiated help -> LLM prose (unchanged initial explanation)
    assert llm.calls > llm_calls_before_help, "initial Help explanation must still use the LLM"
    assert ctrl.elaborate_method_card is None, "no elaborate press yet"
    assert ctrl.elaborate_steps_grid is None, "percentages are not step-grid eligible"

    calls_before_elaborate = llm.calls
    ctrl.step("more")  # Explain more -> method-card-eligible node -> card, no LLM call
    assert llm.calls == calls_before_elaborate, "the method card must skip the LLM entirely"
    card = ctrl.elaborate_method_card
    assert card is not None
    assert card[0] == "PERCENTAGE OF A QUANTITY"
    assert card[-1].strip().startswith("Answer:")
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value


def test_first_help_prompt_gets_a_real_card_not_a_bare_answer():
    """The actual root-cause fix: the sibling worked_example fed to the FIRST
    Help LLM prompt must now contain method-card lines, not the old
    '{problem} (Answer: {answer})' string with zero derivation -- the exact
    shape the maintainer's screenshot showed failing."""
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")  # first Help press -> LLM called with the worked_example slot filled
    assert llm.last_messages is not None
    prompt_text = " ".join(m.get("content", "") for m in llm.last_messages)
    # The card's headline and its concept name -- proof the derivation, not
    # just a bare answer, reached the prompt.
    assert "PERCENTAGE OF A QUANTITY" in prompt_text
    assert "out of every 100" in prompt_text
    assert "(Answer:" not in prompt_text, "must not still be the bare fallback string"


def test_method_card_does_not_leak_across_a_fresh_question():
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")
    ctrl.step("more")
    assert ctrl.elaborate_method_card is not None

    correct = ctrl._ctx.current_item.answer
    ctrl.step(correct)
    assert ctrl.elaborate_method_card is None, "a fresh question must clear the stale card"


def test_elaborate_on_science_node_folds_in_the_ascii_diagram():
    """Phase 3a (2026-08-13): the bare Type-4 card is fact-plus-gloss text
    only -- for science specifically (the whole reason Tier 1 visuals exist,
    docs/design/explain_mode_design.md §3 Type 4), the concept's authored
    ASCII diagram must be folded into the SAME bare display, not left
    stranded in a scaffold file the bare-card path never reads."""
    curriculum = {
        "au4_science_magnetic_materials": {
            "label": "Materials attracted to a magnet", "answer_type": "mc4",
            "checker": "mc_choice", "expected_answer": "A", "grounding": {}, "prerequisites": [],
        },
    }
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=curriculum, db_store=_FakeStore(), learner_id="L",
        item_bank=ItemGenerator(generators={
            "au4_science_magnetic_materials": SCIENCE_GENERATORS["au4_science_magnetic_materials"],
        }),
        rng_seed=7, scaffold_dir=SCAFFOLDS, subject="science",
    )
    ctrl.step(None)
    ctrl.step("?")
    ctrl.step("more")
    card = ctrl.elaborate_method_card
    assert card is not None
    assert card[0] == "MAGNETISM"
    text = "\n".join(card)
    # the fact-card content is still there...
    assert "→" in text  # the card's own arrow-format lines
    # ...AND the authored diagram is folded in beneath it.
    assert "ATTRACTED TO A MAGNET" in text
    assert "NOT ATTRACTED TO A MAGNET" in text
    # meta-instructions aimed at an LLM must NEVER reach the child.
    assert "Guidelines for the question text" not in text
    assert "use ONE of these" not in text


def test_a_node_with_neither_grid_nor_card_falls_through_unchanged():
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_FRACTION_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_fraction_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")
    calls_before_elaborate = llm.calls
    ctrl.step("more")
    assert ctrl.elaborate_steps_grid is None
    assert ctrl.elaborate_method_card is None
    assert llm.calls > calls_before_elaborate, "must fall through to the LLM-prose elaborate path"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
