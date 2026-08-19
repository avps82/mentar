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
    # The hundred-grid is appended AFTER the answer (2026-08-16) -- a picture
    # of it, built from the item's own percentage -- so check the answer LINE.
    answer_lines = [x for x in card if x.strip().lower().startswith("answer:")]
    assert len(answer_lines) == 1, card
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


def test_fallback_hint_shows_a_card_in_the_card_box_not_pasted_into_prose():
    """2026-08-14 (maintainer-reported): with the LLM unavailable, the first Help
    press pasted the sibling's method-card LINES into the prose bubble, and the next
    Explain-more press showed the same shape of content in the monospace card box --
    the same card, two completely different looks. Card content goes in the card."""
    ctrl = SessionController(
        llm_call=lambda messages: "",  # LLM unavailable -> _fallback_hint
        prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    result = ctrl.step("?")
    card = ctrl.elaborate_method_card
    assert card is not None and card[0] == "PERCENTAGE OF A QUANTITY"
    assert "PERCENTAGE OF A QUANTITY" not in result.text, "card lines must not be inlined as prose"
    assert result.text.strip(), "still a lead-in sentence"


def test_a_node_with_neither_grid_nor_card_falls_through_unchanged():
    """The fall-through path, exercised with a SYNTHETIC cardless generator.

    2026-08-15: this used the pilot's unit-fractions node, which now carries a
    card -- as does every other node in the corpus (0 prose-only, measured by
    tools/audit_explain_paths.py). The path still has to work, because a
    4-tuple generator remains legal and any new one starts that way, so the test
    now builds the condition instead of borrowing a node that happens to have it.
    """
    def cardless(rng):
        # Deliberately NOT arithmetic: "What is 2 + 2?" is step-grid eligible, so
        # it would exercise the grid path instead of the fall-through (caught by
        # this very assertion when first written that way).
        return ("int", "int_exact", "How many legs does a spider have?", "8")

    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_FRACTION_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=ItemGenerator(generators={"unit_fractions": cardless}), rng_seed=7,
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


def test_the_working_is_offered_only_once_per_question():
    """Maintainer, 2026-08-19: the working ENDS IN THE ANSWER, so once shown the
    offer (can_elaborate -> the "Show me the working" button) must disappear for
    that question -- including after a further wrong answer, whose fresh Help
    round clears the card and would otherwise resurrect the offer. It returns
    with the next question."""
    ctrl = SessionController(
        llm_call=_PromptCapturingLlm(), prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")                              # Help -> offer live
    assert ctrl.can_elaborate, "precondition: offer live after Help"

    ctrl.step("more")                           # the working (card) is shown
    assert ctrl.elaborate_method_card is not None, "precondition: card shown"
    assert not ctrl.can_elaborate, "the working was shown -- no second offer"

    ctrl.step("999999")                         # wrong again
    # Superseded same-day by the re-show fix: a wrong answer after the working
    # now RE-SHOWS the card (see test_wrong_answer_after_the_working_reshows...)
    # rather than starting a fresh LLM round that would have cleared it. Either
    # way, the OFFER must stay gone -- the answer is already on screen.
    assert ctrl.elaborate_method_card is not None
    assert not ctrl.can_elaborate, (
        "the offer resurfaced for a question whose answer was already revealed"
    )

    answer = ctrl._ctx.current_item.answer      # correct -> NEXT question
    ctrl.step(str(answer))
    ctrl.step("?")
    assert ctrl.can_elaborate, "a NEW question must offer the working again"


def test_wrong_answer_after_the_working_reshows_it_without_an_llm_loop():
    """Maintainer, 2026-08-19: after the working (which ends in the answer) has
    been shown, a further WRONG answer used to start a fresh LLM explain loop,
    burying the revealed answer under new prose. It must instead re-show the
    same deterministic working with a pointing lead-in — zero LLM calls."""
    llm = _PromptCapturingLlm()
    ctrl = SessionController(
        llm_call=llm, prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    ctrl.step("?")
    ctrl.step("more")                          # working shown
    assert ctrl.elaborate_method_card is not None
    calls = llm.calls

    r = ctrl.step("999999")                    # parseable and WRONG
    assert llm.calls == calls, "a wrong answer after the working must not call the LLM"
    assert ctrl.elaborate_method_card is not None, "the working must be re-shown"
    assert "Look again" in r.text, r.text[:120]
    assert ctrl.state == FSMState.HELP_RECHECK_AWAIT.value

    # ...and the child can still finish: typing the shown answer succeeds.
    answer = ctrl._ctx.current_item.answer
    r = ctrl.step(str(answer))
    assert ctrl.state != FSMState.ESCALATION_FREEZE.value
    assert "Look again" not in r.text


def test_trim_truncated_tail_unit_cases():
    """Bug: a backend hitting its output-token cap returns prose cut mid-
    sentence ('Because a') with no error signal, and it reached a child's
    screen verbatim (maintainer, 2026-08-19)."""
    from mentar.dialogue.controller import _trim_truncated_tail as trim

    body = "A) moving: kinetic energy.\n\nBecause a"
    assert trim(body) == "A) moving: kinetic energy."
    assert trim("First sentence. Second cut mid") == "First sentence."
    # Endings that must be left alone.
    for ok in ("A full sentence.", "Ends with an emoji 🌟", "Try this:",
               "a question?", "wow!"):
        assert trim(ok) == ok, ok
    # No earlier boundary: keep the stump rather than blanking the explanation.
    assert trim("just words no boundary") == "just words no boundary"
    # SECOND report (2026-08-19, after rebuild): the cap swallowed a list item,
    # leaving a bare "2." as the final line -- which ends in "." and defeated
    # the sentence rule alone. The marker-only line is dropped; a LEGITIMATE
    # completed list is untouched.
    rep = "This matches the Third Law! 🏊‍♂️\n\n2."
    assert trim(rep) == "This matches the Third Law! 🏊‍♂️"
    assert trim("List:\n1. done.\n2. also done.") == "List:\n1. done.\n2. also done."
    assert trim("intro line\n-") == "intro line"
    # Compound: mid-word cut exposes a bare marker, both must go.
    assert trim("Great! 🏊‍♂️\n\n2. A swim") == "Great! 🏊‍♂️"


def test_a_truncated_llm_explanation_is_trimmed_before_the_child_sees_it():
    class _TruncatingLlm:
        calls = 0
        def __call__(self, messages):
            self.calls += 1
            return "One slice is one third of the pizza. Because a"

    ctrl = SessionController(
        llm_call=_TruncatingLlm(), prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_PERCENTAGE_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        item_bank=_percentage_bank(), rng_seed=7,
    )
    ctrl.step(None)
    r = ctrl.step("?")
    assert "Because a" not in r.text, "the truncation stump reached the child"
    assert "one third of the pizza." in r.text
