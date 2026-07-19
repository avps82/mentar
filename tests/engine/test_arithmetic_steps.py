"""Tests for engine/arithmetic_steps.py — deterministic step-by-step arithmetic
grids ("show human working", 2026-07-19 maintainer feedback).

Every builder is a pure function; correctness means the grid's own result row
reconstructs to the real answer, cross-checked against the deterministic
verifier (eval/verify_numeric.check) the same way item generators are
self-validated, not just eyeballed on one hand example.
"""

from __future__ import annotations

import pathlib
import random
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from decimal import Decimal  # noqa: E402

from mentar.engine.arithmetic_steps import (  # noqa: E402
    BORROW,
    CARRY,
    DIGIT,
    LINE,
    OPERATOR,
    POINT,
    QUOTIENT_HIT,
    build_addition_steps,
    build_long_division_steps,
    build_multiplication_partial_products_steps,
    build_subtraction_steps,
    extract_addition_operands,
    extract_division_operands,
    extract_multiplication_operands,
    extract_subtraction_operands,
)
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def _result_from_grid(grid) -> str:
    """Read the digits (and decimal point, if any) back out of the final
    (result) row, in left-to-right order."""
    last_row = grid.rows[-1]
    return "".join(c.text for c in last_row if c.kind in (DIGIT, POINT) and c.text)


def test_addition_hand_example_47_plus_19():
    grid = build_addition_steps(47, 19)
    assert _result_from_grid(grid) == "66"
    # The carry row must show exactly one nonzero carry (into the tens column).
    carry_cells = [c for row in grid.rows for c in row if c.kind == CARRY]
    assert sum(1 for c in carry_cells if c.text) == 1
    assert [c.text for c in carry_cells if c.text] == ["1"]


def test_addition_unequal_length_operands():
    """7 + 19: the shorter operand must NOT crash on padding, and its blank
    leading cell must render empty, not '0' or a stray space character."""
    grid = build_addition_steps(7, 19)
    assert _result_from_grid(grid) == "26"


def test_addition_carry_chain_of_nines():
    """999 + 1 = 1000: carries propagate through every column, including a
    new leading column appearing in the result that neither operand had."""
    grid = build_addition_steps(999, 1)
    assert _result_from_grid(grid) == "1000"


def test_addition_zero():
    grid = build_addition_steps(0, 0)
    assert _result_from_grid(grid) == "0"


def test_addition_no_carries():
    grid = build_addition_steps(100, 100)
    assert _result_from_grid(grid) == "200"
    carry_cells = [c for row in grid.rows for c in row if c.kind == CARRY]
    assert all(not c.text for c in carry_cells)


def test_addition_self_validates_against_real_verifier():
    """Same discipline as the item generators' self-validate tests: build many
    random grids, cross-check the reconstructed result against the real
    deterministic verifier, not just Python's own '+'."""
    rng = random.Random(2026)
    for _ in range(300):
        a, b = rng.randint(0, 99999), rng.randint(0, 99999)
        grid = build_addition_steps(a, b)
        reconstructed = _result_from_grid(grid)
        outcome = check(answer_type="int", checker="int_exact",
                         llm_output=reconstructed, ground_truth=str(a + b))
        assert outcome.result is CheckResult.PASS, (a, b, reconstructed)


def test_addition_grid_shape_is_rectangular():
    """Every row must have exactly n_cols cells -- the web layer's CSS Grid
    depends on this to lay cells out correctly."""
    for a, b in [(47, 19), (7, 19), (999, 1), (0, 0)]:
        grid = build_addition_steps(a, b)
        for row in grid.rows:
            assert len(row) == grid.n_cols, (a, b, row)


def test_addition_operator_column_only_has_plus_once():
    """The '+' symbol appears exactly once, on the second operand's row."""
    grid = build_addition_steps(47, 19)
    op_column_texts = [row[0].text for row in grid.rows if row[0].kind == OPERATOR]
    assert op_column_texts.count("+") == 1


def test_addition_has_exactly_one_line_row():
    grid = build_addition_steps(47, 19)
    line_rows = [row for row in grid.rows if all(c.kind == LINE for c in row)]
    assert len(line_rows) == 1


# ── Decimal support ─────────────────────────────────────────────────────────

def test_addition_decimal_hand_example():
    grid = build_addition_steps(Decimal("3.4"), Decimal("2.6"))
    assert _result_from_grid(grid) == "6.0"


def test_addition_decimal_carry_across_the_point():
    """0.5 + 0.7 = 1.2 -- the trickiest case: a carry generated in the
    tenths column must land correctly in the ONES column, on the other
    side of the decimal point."""
    grid = build_addition_steps(Decimal("0.5"), Decimal("0.7"))
    assert _result_from_grid(grid) == "1.2"


def test_addition_decimal_no_carry():
    grid = build_addition_steps(Decimal("5.0"), Decimal("2.9"))
    assert _result_from_grid(grid) == "7.9"


def test_addition_decimal_exactly_one_point_per_row():
    grid = build_addition_steps(Decimal("3.4"), Decimal("2.6"))
    for row in grid.rows:
        if any(c.kind == LINE for c in row):
            continue  # the rule row has no point
        points = [c for c in row if c.kind == POINT]
        assert len(points) == 1, row


def test_addition_decimal_whole_part_is_zero():
    """0.2 + 0.3 = 0.5 -- every operand AND the result has a zero whole
    part, so the plain integer-scaling (2 + 3 = 5) carries no record of a
    ones-place column at all. Must still render '0.5', not '.5'."""
    grid = build_addition_steps(Decimal("0.2"), Decimal("0.3"))
    assert _result_from_grid(grid) == "0.5"


def test_addition_decimal_self_validates_against_real_verifier():
    rng = random.Random(2027)
    for _ in range(200):
        a = Decimal(rng.randint(0, 9999)) / 10
        b = Decimal(rng.randint(0, 9999)) / 10
        grid = build_addition_steps(a, b)
        reconstructed = _result_from_grid(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=str(a + b))
        assert outcome.result is CheckResult.PASS, (a, b, reconstructed)


# ── extract_addition_operands ────────────────────────────────────────────────

def test_extract_matches_real_addition_phrasing():
    assert extract_addition_operands("What is 47 + 19?") == (Decimal("47"), Decimal("19"))


def test_extract_matches_decimal_addition():
    assert extract_addition_operands("What is 3.4 + 2.6?") == (Decimal("3.4"), Decimal("2.6"))


def test_extract_rejects_negative_operands():
    """Column-carry addition is the UNSIGNED method taught in early years --
    negative-operand nodes (Y7 integers) fall back to LLM prose instead of a
    grid that doesn't match how the concept is actually taught."""
    assert extract_addition_operands("What is -8 + 3?") is None
    assert extract_addition_operands("What is 8 + -3?") is None


def test_extract_rejects_fraction_addition():
    assert extract_addition_operands("What is 2/5 + 3/5?") is None
    assert extract_addition_operands("What is 1/3 + 1/4?") is None


def test_extract_rejects_order_of_operations():
    assert extract_addition_operands("What is -3 + 4 × 2?") is None


def test_extract_rejects_non_addition_nodes():
    assert extract_addition_operands("What is 25% of 80?") is None
    assert extract_addition_operands("If x + 5 = 12, what is x?") is None
    assert extract_addition_operands("What is 6 squared (6²)?") is None


# ── Subtraction ───────────────────────────────────────────────────────────────

def test_subtraction_hand_example_47_minus_19():
    """The maintainer's own worked example: a single borrow mark, '−1' above
    the tens column (the ones column, 7 − 9, had to borrow from it)."""
    grid = build_subtraction_steps(47, 19)
    assert _result_from_grid(grid) == "28"
    borrow_cells = [c for row in grid.rows for c in row if c.kind == BORROW]
    assert [c.text for c in borrow_cells if c.text] == ["−1"]


def test_subtraction_no_borrow():
    grid = build_subtraction_steps(88, 23)
    assert _result_from_grid(grid) == "65"
    borrow_cells = [c for row in grid.rows for c in row if c.kind == BORROW]
    assert all(not c.text for c in borrow_cells)


def test_subtraction_borrow_chain_through_zeros():
    """500 − 8 = 492: the borrow must cascade left through the zero tens
    digit into the hundreds column, marking BOTH columns."""
    grid = build_subtraction_steps(500, 8)
    assert _result_from_grid(grid) == "492"
    borrow_cells = [c for row in grid.rows for c in row if c.kind == BORROW]
    assert sum(1 for c in borrow_cells if c.text) == 2


def test_subtraction_equal_operands_is_zero():
    grid = build_subtraction_steps(19, 19)
    assert _result_from_grid(grid) == "0"


def test_subtraction_unequal_length_operands():
    grid = build_subtraction_steps(100, 7)
    assert _result_from_grid(grid) == "93"


def test_subtraction_operator_is_minus_sign():
    grid = build_subtraction_steps(47, 19)
    op_column_texts = [row[0].text for row in grid.rows if row[0].kind == OPERATOR]
    assert op_column_texts.count("−") == 1


def test_subtraction_self_validates_against_real_verifier():
    rng = random.Random(2028)
    for _ in range(300):
        a = rng.randint(0, 99999)
        b = rng.randint(0, a)
        grid = build_subtraction_steps(a, b)
        reconstructed = _result_from_grid(grid)
        outcome = check(answer_type="int", checker="int_exact",
                         llm_output=reconstructed, ground_truth=str(a - b))
        assert outcome.result is CheckResult.PASS, (a, b, reconstructed)


def test_subtraction_decimal_borrow_across_the_point():
    """1.2 − 0.5 = 0.7: the tenths column (2 − 5) must borrow from the ones
    column across the decimal point."""
    grid = build_subtraction_steps(Decimal("1.2"), Decimal("0.5"))
    assert _result_from_grid(grid) == "0.7"


def test_subtraction_decimal_self_validates_against_real_verifier():
    rng = random.Random(2029)
    for _ in range(200):
        a = Decimal(rng.randint(0, 9999)) / 10
        b = Decimal(rng.randint(0, int(a * 10))) / 10
        grid = build_subtraction_steps(a, b)
        reconstructed = _result_from_grid(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=str(a - b))
        assert outcome.result is CheckResult.PASS, (a, b, reconstructed)


def test_extract_subtraction_matches_real_phrasing():
    assert extract_subtraction_operands("What is 47 − 19?") == (Decimal("47"), Decimal("19"))
    assert extract_subtraction_operands("What is 47 - 19?") == (Decimal("47"), Decimal("19"))


def test_extract_subtraction_rejects_negative_operands():
    assert extract_subtraction_operands("What is -8 - 3?") is None


def test_extract_subtraction_rejects_negative_result():
    """5 - 12 = -7 -- the unsigned borrow method doesn't apply; falls back
    to LLM prose (this is exactly what Y7's gen_integers_add_sub can produce)."""
    assert extract_subtraction_operands("What is 5 - 12?") is None


def test_extract_subtraction_allows_equal_operands():
    assert extract_subtraction_operands("What is 19 - 19?") == (Decimal("19"), Decimal("19"))


def test_extract_subtraction_rejects_non_subtraction_nodes():
    assert extract_subtraction_operands("What is 2/5 - 1/5?") is None
    assert extract_subtraction_operands("What is 47 + 19?") is None


# ── Multiplication (partial products) ───────────────────────────────────────

def test_multiplication_hand_example_64_times_32():
    """The maintainer's own worked example: partial products 128 and 1920,
    summed with exactly one carry (hundreds -> thousands)."""
    grid = build_multiplication_partial_products_steps(64, 32)
    assert _result_from_grid(grid) == "2048"
    carry_cells = [c for row in grid.rows for c in row if c.kind == CARRY]
    assert [c.text for c in carry_cells if c.text] == ["1"]
    # The two partial products must appear verbatim, in ones-place-first order.
    digit_rows = [
        "".join(c.text for c in row if c.kind == DIGIT)
        for row in grid.rows if any(c.kind == DIGIT for c in row)
    ]
    assert "128" in digit_rows
    assert "1920" in digit_rows
    assert digit_rows.index("128") < digit_rows.index("1920")


def test_multiplication_single_digit_multiplier_has_no_sum_step():
    """7 x 8 = 56: only ONE partial product, so it IS the answer -- no
    separate carry/summation rows should appear."""
    grid = build_multiplication_partial_products_steps(7, 8)
    assert _result_from_grid(grid) == "56"
    carry_cells = [c for row in grid.rows for c in row if c.kind == CARRY]
    assert not carry_cells


def test_multiplication_trailing_zero_multiplier_skips_the_zero_digit():
    """50 x 20 = 1000: the tens digit of 20 is the ONLY nonzero digit, so
    there's a single partial product (1000) and no summation step."""
    grid = build_multiplication_partial_products_steps(50, 20)
    assert _result_from_grid(grid) == "1000"
    carry_cells = [c for row in grid.rows for c in row if c.kind == CARRY]
    assert not carry_cells


def test_multiplication_by_zero():
    assert _result_from_grid(build_multiplication_partial_products_steps(0, 5)) == "0"
    assert _result_from_grid(build_multiplication_partial_products_steps(5, 0)) == "0"


def test_multiplication_three_digit_multiplier():
    grid = build_multiplication_partial_products_steps(123, 45)
    assert _result_from_grid(grid) == "5535"


def test_multiplication_self_validates_against_real_verifier():
    rng = random.Random(2030)
    for _ in range(300):
        a, b = rng.randint(0, 999), rng.randint(0, 999)
        grid = build_multiplication_partial_products_steps(a, b)
        reconstructed = _result_from_grid(grid)
        outcome = check(answer_type="int", checker="int_exact",
                         llm_output=reconstructed, ground_truth=str(a * b))
        assert outcome.result is CheckResult.PASS, (a, b, reconstructed)


def test_multiplication_grid_shape_is_rectangular():
    for a, b in [(64, 32), (7, 8), (50, 20), (0, 5), (123, 45)]:
        grid = build_multiplication_partial_products_steps(a, b)
        for row in grid.rows:
            assert len(row) == grid.n_cols, (a, b, row)


def test_extract_multiplication_matches_real_phrasing():
    assert extract_multiplication_operands("What is 64 × 32?") == (64, 32)


def test_extract_multiplication_rejects_negative_operands():
    assert extract_multiplication_operands("What is -3 × 4?") is None


def test_extract_multiplication_rejects_decimal_operands():
    """Decimal multiplication (gen_mult_decimals, gen_mult_decimal_by_decimal)
    needs its own place-value handling (result decimal places = SUM of the
    operands', not max) -- deferred, not silently mis-rendered."""
    assert extract_multiplication_operands("What is 4.5 × 2?") is None
    assert extract_multiplication_operands("What is 1.2 × 3.4?") is None


def test_extract_multiplication_rejects_non_multiplication_nodes():
    assert extract_multiplication_operands("What is 47 + 19?") is None
    assert extract_multiplication_operands("What is 6 squared (6²)?") is None


# ── Long division (bus-stop) ─────────────────────────────────────────────────

def _quotient_from_grid(grid) -> str:
    """Unlike add/sub/mult, division's result (the quotient) is the FIRST
    row, not the last. Quotient digits carry kind DIGIT (a "0" step) or
    QUOTIENT_HIT (a nonzero step) -- both must be read back."""
    top_row = grid.rows[0]
    return "".join(c.text for c in top_row if c.kind in (DIGIT, POINT, QUOTIENT_HIT) and c.text)


def test_division_hand_example_225_div_5():
    """The maintainer's own 5-step worked example, matched to a reference
    image: EVERY digit is drawn, including the leading "0" -- the raw
    quotient reads "045" (the mechanical process), which is still the
    numeric value 45 (the maintainer's own "045 -> 45" framing)."""
    grid = build_long_division_steps(225, 5)
    assert _quotient_from_grid(grid) == "045"
    assert int(_quotient_from_grid(grid)) == 45


def test_division_original_motivating_example_8_96_div_3_2():
    """The maintainer's ORIGINAL example from the very first note: a
    decimal-by-decimal division requiring the scale-to-whole-divisor step."""
    grid = build_long_division_steps(Decimal("8.96"), Decimal("3.2"))
    assert _quotient_from_grid(grid) == "02.8"
    assert Decimal(_quotient_from_grid(grid)) == Decimal("2.8")


def test_division_decimal_dividend_whole_divisor():
    grid = build_long_division_steps(Decimal("17.0"), 5)
    assert _quotient_from_grid(grid) == "03.4"
    assert Decimal(_quotient_from_grid(grid)) == Decimal("3.4")


def test_division_internal_zero_quotient_digit_is_shown():
    """896 / 8 = 112 -- no internal zero here, but 408 / 4 = 102 has one:
    once a step has started, an internal zero quotient digit must still get
    its own drawn work row (per the algorithm, not per this specific
    assertion -- checked via the reconstructed quotient string)."""
    grid = build_long_division_steps(408, 4)
    assert _quotient_from_grid(grid) == "102"


def test_division_single_digit_quotient():
    """30 / 5 = 6, but the dividend has TWO digits ("30"), so the raw
    quotient is "06" -- one digit per input digit, per the new convention."""
    grid = build_long_division_steps(30, 5)
    assert _quotient_from_grid(grid) == "06"
    assert int(_quotient_from_grid(grid)) == 6


def test_division_exact_no_remainder_shows_final_zero():
    grid = build_long_division_steps(225, 5)
    last_row = grid.rows[-1]
    remainder_text = "".join(c.text for c in last_row if c.kind == DIGIT and c.text)
    assert remainder_text == "0"


def test_division_by_larger_number_still_terminates():
    grid = build_long_division_steps(896, 8)
    assert _quotient_from_grid(grid) == "112"


def test_division_non_terminating_raises():
    """1 / 3 = 0.333... never terminates -- must raise, not loop forever or
    silently truncate to a wrong quotient."""
    with pytest.raises(ValueError):
        build_long_division_steps(1, 3)


def test_division_insufficient_given_precision_raises():
    """4 / 20 = 0.2 exactly, but the dividend "4" as WRITTEN carries no
    decimal digits to carry the process into -- this builder deliberately
    does not synthesize extra trailing zeros (see its docstring), so this
    must raise rather than guess."""
    with pytest.raises(ValueError):
        build_long_division_steps(4, 20)


def test_division_self_validates_against_real_verifier():
    """Same discipline as every other builder: construct dividends FROM a
    clean quotient (matching how gen_division_facts/gen_div_decimals build
    their content), so every case is guaranteed exact."""
    rng = random.Random(2031)
    for _ in range(300):
        divisor = rng.randint(2, 999)
        quotient = rng.randint(0, 999)
        dividend = divisor * quotient
        grid = build_long_division_steps(dividend, divisor)
        reconstructed = _quotient_from_grid(grid)
        outcome = check(answer_type="int", checker="int_exact",
                         llm_output=reconstructed, ground_truth=str(quotient))
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed)


def test_division_decimal_self_validates_against_real_verifier():
    rng = random.Random(2032)
    for _ in range(200):
        divisor = rng.randint(2, 99)
        quotient = Decimal(rng.randint(1, 999)) / 10
        dividend = quotient * divisor
        grid = build_long_division_steps(dividend, divisor)
        reconstructed = _quotient_from_grid(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=str(quotient))
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed)


def test_division_decimal_by_decimal_self_validates_against_real_verifier():
    """Mirrors gen_div_decimal_by_decimal: dividend AND divisor both
    one-decimal-place -- exercises the scale-to-whole-divisor step on every
    single case, not just the one hand example."""
    rng = random.Random(2033)
    for _ in range(200):
        divisor = Decimal(rng.randint(10, 99)) / 10
        quotient = Decimal(rng.randint(10, 99)) / 10
        dividend = quotient * divisor
        grid = build_long_division_steps(dividend, divisor)
        reconstructed = _quotient_from_grid(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=str(quotient))
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed)


def test_extract_division_matches_real_phrasing():
    assert extract_division_operands("What is 225 ÷ 5?") == (Decimal("225"), Decimal("5"))


def test_extract_division_rejects_negative_or_zero_divisor():
    assert extract_division_operands("What is -10 ÷ 5?") is None
    assert extract_division_operands("What is 10 ÷ 0?") is None


def test_extract_division_rejects_non_terminating():
    assert extract_division_operands("What is 1 ÷ 3?") is None


def test_extract_division_rejects_non_division_nodes():
    assert extract_division_operands("What is 47 + 19?") is None
