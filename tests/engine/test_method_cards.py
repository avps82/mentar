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

from mentar.engine.au_items import gen_percentage_change, gen_percentage_of_quantity  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402


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


def test_percentage_of_quantity_self_validates_over_many_draws():
    """CI-enforced version of the same guarantee: 500 real draws, the card's
    final line must equal the item's own answer -- not eyeballed once."""
    rng = random.Random(2026)
    for _ in range(500):
        answer_type, checker, problem, answer, choices, method_steps = gen_percentage_of_quantity(rng)
        assert method_steps is not None
        assert method_steps[-1].strip() == f"Answer: {answer}"
        assert problem in method_steps[1]


def test_percentage_change_self_validates_over_many_draws():
    rng = random.Random(99)
    for _ in range(500):
        answer_type, checker, problem, answer, choices, method_steps = gen_percentage_change(rng)
        assert method_steps is not None
        assert method_steps[-1].strip() == f"Answer: ${answer}"
        assert problem in method_steps[1]


def test_method_steps_flows_through_item_generator_onto_the_item():
    """End-to-end: ItemGenerator._make must actually attach the 6th tuple
    element to the drawn Item, not just accept it silently. This is the exact
    piece the design doc calls out as the risk a --must-call-style check
    exists for: a defined-but-never-wired field passes every other check and
    silently returns wrong (empty) data."""
    gens = {"pct_of": gen_percentage_of_quantity, "pct_change": gen_percentage_change}
    ig = ItemGenerator(generators=gens, rng=random.Random(7))
    for node_id in gens:
        for _ in range(20):
            item = ig.sample(node_id)
            assert item is not None
            assert item.method_steps is not None, (node_id, item)
            assert item.method_steps[-1].strip().startswith("Answer:")
            assert item.answer in item.method_steps[-1]


def test_unmigrated_generators_are_unaffected():
    """A 4-tuple generator (the overwhelming majority, still) must draw exactly
    as before -- method_steps stays None, no behaviour change."""
    from mentar.engine.au_items import gen_negative_numbers
    ig = ItemGenerator(generators={"neg": gen_negative_numbers}, rng=random.Random(3))
    item = ig.sample("neg")
    assert item is not None
    assert item.method_steps is None


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
