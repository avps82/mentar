"""explain-mode (2026-08-12) — Item.method_steps, the computed method card that
replaces the bare "here's a similar question and its answer" fallback.

Why this file exists: `docs/design/explain_mode_design.md` §1 records the live
failure — "Explain more" on a percentage node returned only a sibling item's
bare answer, with no derivation shown at all. The maintainer's own example
("What is 50% of 64?") is the acceptance test for Phase 0: prove the card
exists, is attached at draw time (not re-parsed from problem text the way the
step-grid extractors had to be), and is PROVABLY correct — same self-validating
discipline `test_multiplication_self_validates_against_real_verifier` runs for
the step grids (§5): a card that can't produce its own item's answer must fail
CI, not pass review by eyeballing one example.

    python3 tests/engine/test_method_cards.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.au_items import (  # noqa: E402
    gen_decimal_place_value,
    gen_integers_add_sub,
    gen_negative_multiplication,
    gen_negative_numbers,
    gen_percentage_change,
    gen_percentage_of_quantity,
    gen_place_value_2digit,
    gen_place_value_3digit,
    gen_place_value_4digit,
)
from mentar.engine.itemgen import ItemGenerator  # noqa: E402

# Every Type 2 (maths method card) generator migrated so far -- Phase 1,
# docs/design/explain_mode_design.md §3. Extend this tuple as more families
# are migrated; every test below sweeps the whole list, so a new family gets
# the same self-validation for free.
_MIGRATED_INT_MC_GENERATORS = (
    gen_percentage_of_quantity,
    gen_percentage_change,
    gen_negative_numbers,
    gen_integers_add_sub,
    gen_negative_multiplication,
)
_MIGRATED_MC4_GENERATORS = (
    gen_place_value_2digit,
    gen_place_value_3digit,
    gen_place_value_4digit,
    gen_decimal_place_value,
)
_LETTERS = "ABCD"


def test_percentage_of_quantity_card_matches_the_maintainers_own_example():
    """The exact reported failure, reproduced as a positive test: What is 50% of 64?
    Calls the card builder directly with the maintainer's own numbers rather than
    relying on RNG luck to draw them."""
    from mentar.engine.au_items import _percentage_of_quantity_card
    card = _percentage_of_quantity_card(pct=50, quantity=64, answer=32)
    assert card[0] == "PERCENTAGE OF A QUANTITY"  # rule: name the concept
    assert "What is 50% of 64?" in card[1]
    assert card[-1].strip() == "Answer: 32"
    # every intermediate arithmetic claim is independently checkable
    assert "64 × 50 = 3200" in card[4]
    assert "3200 ÷ 100 = 32" in card[4]


def test_every_migrated_int_generator_self_validates_over_many_draws():
    """CI-enforced version of the same guarantee, swept across every migrated
    int-answer generator: the card's final line must state the item's own
    answer -- not eyeballed once, and not just for the Phase 0 pilot family."""
    rng = random.Random(2026)
    for gen in _MIGRATED_INT_MC_GENERATORS:
        for _ in range(200):
            result = gen(rng)
            answer, method_steps = result[3], result[5]
            assert method_steps is not None, gen.__name__
            assert answer in method_steps[-1], (gen.__name__, answer, method_steps[-1])
            assert method_steps[-1].strip().startswith("Answer:"), (gen.__name__, method_steps[-1])
            assert result[2] in method_steps[1], (gen.__name__, "problem text not echoed in card")


def test_every_migrated_mc4_generator_card_states_the_real_correct_choice():
    """Same guarantee, mc4 shape: the card must name the actual correct
    CHOICE TEXT (not just the answer letter, which is meaningless without
    the shuffled options) -- guards against a card computed from the wrong
    variable if choices get reshuffled after the card is built."""
    rng = random.Random(4040)
    for gen in _MIGRATED_MC4_GENERATORS:
        for _ in range(200):
            answer_type, checker, problem, letter, choices, method_steps = gen(rng)
            assert method_steps is not None, gen.__name__
            correct_text = choices[_LETTERS.index(letter)]
            assert correct_text in method_steps[1], (gen.__name__, correct_text, method_steps[1])
            assert correct_text in method_steps[-1], (gen.__name__, correct_text, method_steps[-1])


def test_method_steps_flows_through_item_generator_onto_the_item():
    """End-to-end: ItemGenerator._make must actually attach the 6th tuple
    element to the drawn Item, not just accept it silently. This is the exact
    piece the design doc calls out as the risk a --must-call-style check
    exists for: a defined-but-never-wired field passes every other check and
    silently returns wrong (empty) data. Swept across every migrated int
    generator (mc4 covered separately -- item.answer there is a letter, not
    the choice text the card actually names)."""
    gens = {g.__name__: g for g in _MIGRATED_INT_MC_GENERATORS}
    ig = ItemGenerator(generators=gens, rng=random.Random(7))
    for node_id in gens:
        for _ in range(20):
            item = ig.sample(node_id)
            assert item is not None
            assert item.method_steps is not None, (node_id, item)
            assert item.method_steps[-1].strip().startswith("Answer:")
            assert item.answer in item.method_steps[-1]


def test_unmigrated_generators_are_unaffected():
    """A 4-tuple generator (still the overwhelming majority) must draw exactly
    as before -- method_steps stays None, no behaviour change."""
    from mentar.engine.au_items import gen_add_within_100
    ig = ItemGenerator(generators={"add": gen_add_within_100}, rng=random.Random(3))
    item = ig.sample("add")
    assert item is not None
    assert item.method_steps is None


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
