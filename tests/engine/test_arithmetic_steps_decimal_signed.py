"""engine/arithmetic_steps.py — Phases A+B: decimal and signed multiplication.

Split into its own file the way test_verify_numeric_expression.py was, since
these are additive paths with their own contract: they handle exactly the two
multiplication shapes `extract_multiplication_operands` deliberately refuses.

Contract under test:
  1. The three multiplication extractors PARTITION the space — no input is
     accepted by two of them. This is what makes the controller's chain order
     not load-bearing; if it ever stops being true, the chain becomes
     order-dependent silently.
  2. Every grid's displayed result equals the real product. Verified over many
     real generator draws, not hand-picked examples — the decimal-multiplication
     gap was originally missed precisely because the text shape looks identical
     to the always-eligible integer case.
  3. The existing integer and division paths are untouched.

    python3 tests/engine/test_arithmetic_steps_decimal_signed.py
"""

from __future__ import annotations

import pathlib
import random
import re
import sys
from decimal import Decimal

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.arithmetic_steps import (  # noqa: E402
    LINE,
    build_multiplication_decimal_steps,
    build_multiplication_partial_products_steps,
    build_signed_multiplication_steps,
    extract_decimal_multiplication_operands,
    extract_division_operands,
    extract_multiplication_operands,
    extract_signed_multiplication_operands,
    render_steps_grid_text,
)
from mentar.engine.au_items import (  # noqa: E402
    gen_mult_decimal_by_decimal,
    gen_mult_decimals,
    gen_negative_multiplication,
)

# ── 1. the extractors must partition, not overlap ────────────────────────────

def test_multiplication_extractors_are_mutually_exclusive():
    """No problem may be claimed by more than one multiplication extractor."""
    cases = [
        "What is 6 × 7?", "What is 3.4 × 20?", "What is 2.4 × 3.6?",
        "What is -8 × 3?", "What is -3 × -4?", "What is 0 × 5?",
        "What is 12 ÷ 3?", "What is 4 + 5?", "What is 2/5 × 3?",
    ]
    for problem in cases:
        claims = [
            name for name, fn in (
                ("int", extract_multiplication_operands),
                ("decimal", extract_decimal_multiplication_operands),
                ("signed", extract_signed_multiplication_operands),
            ) if fn(problem) is not None
        ]
        assert len(claims) <= 1, f"{problem!r} claimed by {claims}"


def test_whole_valued_decimals_stay_on_the_integer_path():
    """"20" is an integer; the decimal path must not poach a plain int × int."""
    assert extract_decimal_multiplication_operands("What is 6 × 7?") is None
    assert extract_multiplication_operands("What is 6 × 7?") == (6, 7)


def test_signed_path_ignores_all_non_negative_input():
    assert extract_signed_multiplication_operands("What is 6 × 7?") is None
    assert extract_signed_multiplication_operands("What is -8 × 3?") == (-8, 3)


# ── 2. the grids must be arithmetically right ────────────────────────────────

def _result_line(grid) -> str:
    return render_steps_grid_text(grid).strip().splitlines()[-1].strip()


def test_decimal_grid_result_matches_the_real_product_over_many_draws():
    """The original gap was found only by running real draws; keep doing that."""
    rng = random.Random(20260811)
    for gen in (gen_mult_decimals, gen_mult_decimal_by_decimal):
        for _ in range(300):
            _at, _ck, problem, answer = gen(rng)
            operands = extract_decimal_multiplication_operands(problem)
            if operands is None:
                continue  # a draw that landed whole -- integer path's job
            grid = build_multiplication_decimal_steps(*operands)
            shown = _result_line(grid)
            assert Decimal(shown) == Decimal(answer), (problem, shown, answer)


def test_decimal_places_are_summed_not_maxed():
    """2.4 × 3.6 has 1+1=2 places (8.64). Using max() -- add/sub's rule --
    would give 8.6 and be wrong; that asymmetry is why decimals were
    originally excluded rather than guessed at."""
    grid = build_multiplication_decimal_steps(Decimal("2.4"), Decimal("3.6"))
    assert _result_line(grid) == "8.64"


def test_leading_zero_result_keeps_its_zero():
    """0.2 × 0.4 = 0.08 -- the product's digits ("8") are shorter than the
    decimal places needed, so the row must be zero-padded, not rendered ".08"
    or "8"."""
    grid = build_multiplication_decimal_steps(Decimal("0.2"), Decimal("0.4"))
    assert _result_line(grid) == "0.08"


def test_operand_rows_show_the_numbers_as_asked_not_the_scaled_integers():
    text = render_steps_grid_text(build_multiplication_decimal_steps(Decimal("3.4"), Decimal("20")))
    first_two = text.splitlines()[:2]
    assert "3.4" in first_two[0], first_two
    assert "20" in first_two[1], first_two


def test_rule_row_is_not_punched_through_when_the_point_widens_the_grid():
    """Regression: padding a LINE row with a digit-kind cell rendered "- ---"
    (a gap in the rule) instead of a continuous "-----"."""
    text = render_steps_grid_text(build_multiplication_decimal_steps(Decimal("3.4"), Decimal("20")))
    rules = [ln for ln in text.splitlines() if set(ln.strip()) == {"-"}]
    assert rules, f"no continuous rule row found in:\n{text}"


def test_line_rows_stay_uniformly_line_kind():
    grid = build_multiplication_decimal_steps(Decimal("2.4"), Decimal("3.6"))
    for row in grid.rows:
        kinds = {c.kind for c in row}
        if LINE in kinds:
            assert kinds == {LINE}, f"mixed-kind rule row: {kinds}"


# ── 3. signed multiplication ─────────────────────────────────────────────────

def test_signed_grid_result_matches_the_real_product_over_many_draws():
    """Note gen_negative_multiplication picks EACH operand's sign independently,
    so ~25% of draws are both-positive and belong to the plain integer path --
    that is the 25.5% eligibility the pre-fix audit measured, not a gap. Skip
    those here rather than assert every draw is signed (an earlier cut of this
    test did assert that, and was simply wrong about the generator)."""
    rng = random.Random(20260811)
    seen_signed = 0
    for _ in range(300):
        _at, _ck, problem, answer = gen_negative_multiplication(rng)
        operands = extract_signed_multiplication_operands(problem)
        if operands is None:
            assert extract_multiplication_operands(problem) is not None, problem
            continue
        seen_signed += 1
        grid = build_signed_multiplication_steps(*operands)
        assert render_steps_grid_text(grid).strip().splitlines()[-1].strip().endswith(str(answer))
    assert seen_signed > 100, f"expected plenty of signed draws, saw {seen_signed}"


def test_sign_rule_wording_matches_the_operands():
    same = render_steps_grid_text(build_signed_multiplication_steps(-3, -4))
    diff = render_steps_grid_text(build_signed_multiplication_steps(-8, 3))
    assert "POSITIVE" in same and "= 12" in same
    assert "NEGATIVE" in diff and "= -24" in diff


def test_zero_is_not_described_by_the_sign_rule():
    """0 is neither positive nor negative -- claiming "same signs → POSITIVE"
    for -7 × 0 would teach something false."""
    text = render_steps_grid_text(build_signed_multiplication_steps(-7, 0))
    assert "POSITIVE" not in text and "NEGATIVE" not in text
    assert text.strip().splitlines()[-1].strip().endswith("= 0")


def test_signed_grid_states_the_rule_before_the_arithmetic():
    lines = render_steps_grid_text(build_signed_multiplication_steps(-8, 3)).splitlines()
    rule_at = next(i for i, ln in enumerate(lines) if "signs" in ln)
    answer_at = next(i for i, ln in enumerate(lines) if ln.strip().startswith("so "))
    assert rule_at < answer_at


# ── 4. nothing pre-existing moved ────────────────────────────────────────────

def test_existing_integer_and_division_paths_unchanged():
    assert extract_multiplication_operands("What is 64 × 32?") == (64, 32)
    assert _result_line(build_multiplication_partial_products_steps(64, 32)) == "2048"
    assert extract_division_operands("What is 225 ÷ 5?") == (Decimal(225), Decimal(5))


def test_no_grid_prints_a_bare_1_coefficient_or_stray_point():
    """Cheap shape check across many draws: no doubled points, no trailing point."""
    rng = random.Random(7)
    for gen in (gen_mult_decimals, gen_mult_decimal_by_decimal):
        for _ in range(200):
            _at, _ck, problem, _ans = gen(rng)
            ops = extract_decimal_multiplication_operands(problem)
            if ops is None:
                continue
            text = render_steps_grid_text(build_multiplication_decimal_steps(*ops))
            assert ".." not in text
            for ln in text.splitlines():
                assert not re.search(r"\.\s*$", ln), (problem, ln)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")


# ── 5. Phase C: signed addition/subtraction ──────────────────────────────────
# Closes the last of the draw-dependent nodes (16 -> 4 -> 0). Built as the design
# doc's option 2 (same-sign/different-sign rule reusing the existing unsigned
# builders) rather than option 1 (a number-line rendering primitive); if the
# maintainer prefers the number line, build_signed_addition_steps is the single
# thing to replace -- the extractor and wiring stay.

def test_signed_add_extractor_takes_only_what_the_plain_path_refuses():
    from mentar.engine.arithmetic_steps import extract_signed_addition_operands as sx
    assert sx("What is -8 + 3?") == (-8, 3, "+")
    assert sx("What is -8 + -3?") == (-8, -3, "+")
    assert sx("What is -4 - 6?") == (-4, 6, "-")
    # a subtraction going negative -- refused by the unsigned borrow method
    assert sx("What is 5 - 12?") == (5, 12, "-")
    # ...and everything the plain path already handles stays there
    assert sx("What is 7 + 5?") is None
    assert sx("What is 12 - 5?") is None
    assert sx("What is 6 × 7?") is None


def test_signed_add_results_are_correct_across_the_generator():
    """Every draw of the real Y7 generator, ground truth checked against the
    grid's final line. 20.5% used to reach a grid; all of them should now."""
    from mentar.engine.arithmetic_steps import (
        build_signed_addition_steps,
        extract_addition_operands,
        extract_signed_addition_operands,
        extract_subtraction_operands,
    )
    from mentar.engine.au_items import gen_integers_add_sub

    rng = random.Random(20260812)
    plain = signed = 0
    for _ in range(400):
        _at, _ck, problem, answer = gen_integers_add_sub(rng)
        ops = extract_signed_addition_operands(problem)
        if ops is None:
            # must then be handled by one of the plain extractors -- never neither
            assert (extract_addition_operands(problem) is not None
                    or extract_subtraction_operands(problem) is not None), problem
            plain += 1
            continue
        signed += 1
        shown = _result_line(build_signed_addition_steps(*ops))
        assert shown.endswith(str(answer)), (problem, shown, answer)
    assert plain and signed, f"expected both paths exercised (plain={plain} signed={signed})"


def test_same_and_different_sign_rules_are_stated_correctly():
    from mentar.engine.arithmetic_steps import build_signed_addition_steps as B
    same = render_steps_grid_text(B(-8, -3, "+"))
    diff = render_steps_grid_text(B(-8, 3, "+"))
    assert "same signs" in same and same.strip().endswith("-11")
    assert "different signs" in diff and diff.strip().endswith("-5")


def test_subtraction_is_rewritten_as_an_addition_for_the_child_to_see():
    """The rule is stated over two signed addends, so the rewrite step must be
    visible rather than the question silently transforming."""
    from mentar.engine.arithmetic_steps import build_signed_addition_steps as B
    text = render_steps_grid_text(B(5, 12, "-"))
    assert "5 - 12" in text                      # their own question, first
    assert "5 + (-12)" in text                   # the rewrite, shown
    assert text.strip().endswith("-7")


def test_equal_magnitudes_cancel_to_zero():
    from mentar.engine.arithmetic_steps import build_signed_addition_steps as B
    assert _result_line(B(-5, 5, "+")).endswith("0")
    assert _result_line(B(5, 5, "-")).endswith("0")
