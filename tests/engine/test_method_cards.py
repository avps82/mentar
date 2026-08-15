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
    gen_area_perimeter,
    gen_binomial_product_area,
    gen_combine_expressions,
    gen_combine_quadratic_linear,
    gen_combine_three_expressions,
    gen_combine_two_quadratics,
    gen_combined_rectangles_perimeter,
    gen_compound_shape_area,
    gen_decimal_place_value,
    gen_difference_of_expressions,
    gen_distributive_word_to_expression,
    gen_fraction_decimal_equiv,
    gen_halves_quarters,
    gen_integers_add_sub,
    gen_mult_fraction_whole,
    gen_negative_multiplication,
    gen_negative_numbers,
    gen_one_step_equations,
    gen_order_of_operations,
    gen_order_of_ops_negatives,
    gen_percentage_change,
    gen_percentage_of_quantity,
    gen_place_value_2digit,
    gen_place_value_3digit,
    gen_place_value_4digit,
    gen_rectangle_area_expression,
    gen_rectangle_perimeter_expression,
    gen_revenue_expression,
    gen_square_expression,
    gen_two_step_equations,
    gen_unlike_denom_fractions,
    gen_word_to_expression,
    gen_word_to_quadratic_expression,
)
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

_MIGRATED_EXPRESSION_GENERATORS = (
    gen_word_to_expression,
    gen_combine_expressions,
    gen_rectangle_perimeter_expression,
    gen_rectangle_area_expression,
    gen_distributive_word_to_expression,
    gen_combine_three_expressions,
    # The quadratic-heavy Y10-12 family, deferred on 2026-08-13 as "higher
    # error-risk, held for a session with room to verify each one" and migrated
    # 2026-08-15. These were the last 66 prose-only nodes in the corpus.
    gen_square_expression,
    gen_combined_rectangles_perimeter,
    gen_binomial_product_area,
    gen_word_to_quadratic_expression,
    gen_combine_quadratic_linear,
    gen_difference_of_expressions,
    gen_revenue_expression,
    gen_combine_two_quadratics,
    gen_compound_shape_area,
)

# Every Type 2 (maths method card) generator migrated so far -- Phase 1,
# docs/design/explain_mode_design.md §3. Not just int-answer despite the
# name -- fraction-answer generators fit the same shape (this test only
# checks substring containment of the answer string, type-agnostic). Extend
# this tuple as more families are migrated; every test below sweeps the
# whole list, so a new family gets the same self-validation for free.
_MIGRATED_INT_MC_GENERATORS = (
    gen_percentage_of_quantity,
    gen_percentage_change,
    gen_negative_numbers,
    gen_integers_add_sub,
    gen_negative_multiplication,
    gen_one_step_equations,
    gen_two_step_equations,
    gen_order_of_operations,
    gen_order_of_ops_negatives,
    gen_halves_quarters,
    gen_mult_fraction_whole,
    gen_unlike_denom_fractions,
    gen_area_perimeter,
    gen_fraction_decimal_equiv,
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


def test_every_migrated_expression_generator_self_validates_over_many_draws():
    """Same registry-sweep discipline for Type 2's expression-answer family
    (algebra). The card embeds the generator's OWN `answer` string verbatim
    (never re-derives it independently), so a substring check is already
    rigorous here -- but see the next test for an ADDITIONAL cross-check
    against the real expression_equiv verifier, for the intermediate
    arithmetic specifically."""
    rng = random.Random(3030)
    trailing_instruction = " Give your answer as a simplified expression."
    for gen in _MIGRATED_EXPRESSION_GENERATORS:
        for _ in range(200):
            result = gen(rng)
            problem, answer, method_steps = result[2], result[3], result[5]
            assert method_steps is not None, gen.__name__
            assert answer in method_steps[-1], (gen.__name__, answer, method_steps[-1])
            # Some cards drop the UI instruction suffix for brevity -- the
            # QUESTION itself must still be echoed either way.
            core_problem = problem.removesuffix(trailing_instruction)
            assert core_problem in method_steps[1], (gen.__name__, core_problem, method_steps[1])


def test_expression_cards_final_answer_passes_the_real_verifier():
    """Cross-check against verify_numeric.check (expression_equiv, sympy-based)
    rather than trusting string equality -- catches a card whose displayed
    answer is textually present but not what the real verifier would accept
    (e.g. a stray sign or a malformed operator), which a substring check
    alone cannot."""
    rng = random.Random(5050)
    for gen in _MIGRATED_EXPRESSION_GENERATORS:
        for _ in range(50):
            result = gen(rng)
            answer = result[3]
            outcome = check(answer_type="expression", checker="expression_equiv",
                             llm_output=answer, ground_truth=answer)
            assert outcome.result is CheckResult.PASS, (gen.__name__, answer, outcome)


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


def test_alternative_forms_a_card_offers_are_genuinely_equivalent():
    """Several quadratic cards tell a child "expanding to ... is also correct".
    That is a promise about what the app will accept, so each alternative is
    cross-checked against the item's own ground truth with the real sympy
    verifier. A card that offered a wrong "also correct" form would teach an
    answer the verifier then marks wrong -- worse than offering nothing.

    (Implicit multiplication is deliberate in these lines: "y**2 + 16y + 64" is
    how a child writes it, and the verifier accepts it -- checked here, not
    assumed.)"""
    import re

    rng = random.Random(4242)
    expr_only = re.compile(r"[0-9xy*+\-/()\s]{4,}")
    checked = 0
    for gen in _MIGRATED_EXPRESSION_GENERATORS:
        for _ in range(40):
            result = gen(rng)
            answer, card = result[3], (result[5] if len(result) > 5 else None)
            if not card:
                continue
            for line in card:
                for phrase in ("Expanding to", "Expanded that is", "giving"):
                    if phrase not in line:
                        continue
                    frag = re.split(r"\s+(?:is|—|--)\s|\.\s|$",
                                    line.split(phrase, 1)[1])[0].strip().rstrip(".")
                    if not frag or not expr_only.fullmatch(frag):
                        continue
                    checked += 1
                    outcome = check(answer_type="expression", checker="expression_equiv",
                                    llm_output=frag, ground_truth=answer)
                    assert outcome.result is CheckResult.PASS, (gen.__name__, frag, answer)
    assert checked >= 50, f"expected the alternative-form lines to be exercised, saw {checked}"
