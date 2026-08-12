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
from fractions import Fraction  # noqa: E402

from mentar.engine.arithmetic_steps import (  # noqa: E402
    BLANK,
    BORROW,
    CARRY,
    DIGIT,
    LINE,
    OPERATOR,
    POINT,
    Cell,
    StepGrid,
    build_addition_steps,
    build_long_division_steps,
    build_multiplication_partial_products_steps,
    build_subtraction_steps,
    extract_addition_operands,
    extract_division_operands,
    extract_multiplication_operands,
    extract_subtraction_operands,
    render_steps_grid_text,
)
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

# ── render_steps_grid_text (plain monospace rendering, 2026-07-24) ──────────
# Replaces the earlier per-cell CSS Grid rendering with a single <pre>-ready
# string. Drafted by gemma4:12b from an exact spec (function logic reviewed
# and correct); its own hand-verified test assertions had two arithmetic
# errors (mid-string vs. trailing whitespace confusion -- rstrip() only
# strips the END of the fully-joined row, not spaces before an earlier
# multi-char cell), so the tests below are rewritten from actually running
# the function, not from gemma's comments.

def test_render_steps_grid_text_line_and_digit_cells():
    grid = StepGrid(
        rows=[
            [Cell("1", DIGIT), Cell("", LINE), Cell("2", DIGIT)],
            [Cell("  + ", OPERATOR), Cell("", LINE), Cell("3", DIGIT)],
        ],
        n_cols=3,
    )
    # Row 0: "1"(rjust 1)="1" + "-"(LINE) + "2"(rjust 1)="2" -> "1-2"
    # Row 1: "  + " is longer than col_width=1 -> emitted as-is (not squeezed),
    # + "-"(LINE) + "3"(rjust 1)="3" -> "  + -3" (rstrip only trims the END,
    # so the interior "  + " keeps its own leading/trailing spaces intact).
    assert render_steps_grid_text(grid, col_width=1) == "1-2\n  + -3"


def test_render_steps_grid_text_wider_columns():
    grid = StepGrid(
        rows=[
            [Cell("  5", DIGIT), Cell("-", LINE), Cell(" 10", DIGIT)],
            [Cell("  1", DIGIT), Cell("-", LINE), Cell(" 20", DIGIT)],
        ],
        n_cols=3,
    )
    assert render_steps_grid_text(grid, col_width=3) == "  5--- 10\n  1--- 20"


def test_render_steps_grid_text_blank_cell_renders_as_spaces():
    grid = StepGrid(rows=[[Cell("", BLANK), Cell("9", DIGIT)]], n_cols=2)
    # BLANK "".rjust(2) = "  ", "9".rjust(2) = " 9" -> "   9" (3 spaces + "9");
    # rstrip only trims trailing whitespace, and "9" is the last character.
    assert render_steps_grid_text(grid, col_width=2) == "   9"


def test_render_steps_grid_text_trailing_blanks_are_stripped():
    grid = StepGrid(rows=[[Cell("5", DIGIT), Cell("", BLANK), Cell("", BLANK)]], n_cols=3)
    assert render_steps_grid_text(grid, col_width=1) == "5"


def test_render_steps_grid_text_matches_division_hand_example():
    """The maintainer's own hand-worked plain-text example, 425 / 4 = 106 R 1,
    including the annotation lines the maintainer added (2026-07-24). Each
    annotation is its OWN line (2026-07-25 fix) -- not appended to the end
    of a numeric row -- so a long annotation sentence wraps instead of
    getting cut off / requiring horizontal scroll in the browser."""
    grid = build_long_division_steps(425, 4, ending="remainder")
    text = render_steps_grid_text(grid, col_width=1)
    lines = text.split("\n")
    assert lines[0].strip() == "106 R 1"
    assert "Quotient is 106, Remainder is 1" in lines[1]
    assert lines[-2].strip() == "1"
    assert "Remainder check: 1 is smaller than 4, so it is correct." in lines[-1]
    assert "4) 425" in text
    assert "Middle Step: 4 x 1 = 4" in text
    assert "Middle Step: 4 x 0 = 0" in text
    assert "Middle Step: 4 x 6 = 24" in text
    assert "Middle Step: 4 - 4 = 0, bring down 2" in text
    assert "Middle Step: 2 - 0 = 2, bring down 5" in text


def test_render_steps_grid_text_multiplication():
    grid = build_multiplication_partial_products_steps(64, 32)
    text = render_steps_grid_text(grid, col_width=1)
    assert "64" in text
    assert "2048" in text.split("\n")[-1]


def _result_from_grid(grid) -> str:
    """Read the digits (and decimal point, if any) back out of the final
    (result) row, in left-to-right order. Skips trailing single-cell
    annotation rows (division's "Quotient is..." line, multiplication's
    single-partial-product caption) -- a single-cell row is never a real
    digit row in this codebase's convention."""
    rows = [r for r in grid.rows if len(r) > 1]
    last_row = rows[-1]
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


def test_multiplication_single_partial_product_gets_an_explanatory_caption():
    """Maintainer-flagged (2026-08-12): a single-partial-product grid (e.g.
    7 x 10) rendered as just the bare fact with no visible 'steps' -- 'not
    much of explanation is happening'. Both single-digit-multiplier and
    trailing-zero-multiplier cases now carry a trailing single-cell caption
    row (same convention as division's annotation rows) explaining in words
    what the collapsed grid shows."""
    grid = build_multiplication_partial_products_steps(7, 10)
    caption = grid.rows[-1]
    assert len(caption) == 1
    assert "7 x 10 = 7 x 1 with 1 zero" in caption[0].text

    grid2 = build_multiplication_partial_products_steps(6, 7)
    caption2 = grid2.rows[-1]
    assert len(caption2) == 1
    assert "single multiplication fact" in caption2[0].text

    # A genuine multi-partial-product grid (64 x 32) gets NO caption -- the
    # summed partial-product rows already show the steps visibly.
    grid3 = build_multiplication_partial_products_steps(64, 32)
    assert len(grid3.rows[-1]) == grid3.n_cols


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
    """Every DIGIT row is exactly n_cols wide. A single-partial-product result
    also carries a trailing single-cell annotation row (2026-08-12, same
    convention as division's "Quotient is..." line) -- deliberately NOT
    n_cols wide, same as every other annotation row in this module."""
    for a, b in [(64, 32), (7, 8), (50, 20), (0, 5), (123, 45)]:
        grid = build_multiplication_partial_products_steps(a, b)
        for row in grid.rows:
            if len(row) == 1:
                continue
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
# Rebuilt 2026-07-24: standard leading-zero-suppressed chunking (432/15 reads
# "28", not "028"), plus "remainder"/"fraction"/"decimal" endings for a
# division that doesn't divide evenly. Verified against the maintainer's own
# 425/4 = 106 R 1 hand-worked alignment example and 432/15 shown in all three
# ending styles.

def _quotient_row(grid):
    """The quotient row is the first row containing a DIGIT/POINT cell --
    NOT always grid.rows[0], since a decimal-divisor division (2026-07-24)
    prepends a scale-explanation row ("2.53 / 1.1 becomes 25.3 / 11...")
    ahead of it."""
    return next(row for row in grid.rows if any(c.kind in (DIGIT, POINT) for c in row))


def _quotient_from_grid(grid) -> str:
    """Division's result (the quotient, plus any "R n"/"num/den" suffix).
    Excludes the trailing "<-- Quotient is..." annotation cell (2026-07-24)
    -- that's plain-text-only reader guidance, not part of the answer."""
    return "".join(c.text for c in _quotient_row(grid) if c.text and "<--" not in c.text)


def _bare_quotient(grid) -> str:
    """Same as _quotient_from_grid but without an OPERATOR-kind suffix cell
    (the "R n" / "num/den" tail) -- for comparing just the digit/point part."""
    return "".join(c.text for c in _quotient_row(grid) if c.kind in (DIGIT, POINT) and c.text)


def test_division_hand_example_225_div_5():
    """The 2026-07-19 worked example, 225 / 5 -- under the new convention the
    quotient reads "45", no forced leading zero."""
    grid = build_long_division_steps(225, 5)
    assert _bare_quotient(grid) == "45"


def test_division_original_motivating_example_8_96_div_3_2():
    """The maintainer's ORIGINAL example from the very first note: a
    decimal-by-decimal division requiring the scale-to-whole-divisor step."""
    grid = build_long_division_steps(Decimal("8.96"), Decimal("3.2"))
    assert _bare_quotient(grid) == "2.8"
    assert Decimal(_bare_quotient(grid)) == Decimal("2.8")


def test_division_decimal_divisor_explains_the_scale_step():
    """Regression (2026-07-24, maintainer-reported bug): a decimal divisor is
    scaled to a whole number internally (2.53 / 1.1 -> 25.3 / 11), but the
    scaled numbers were shown with NO explanation of where they came from --
    a reader sees "11" and has no idea why, since they asked about "1.1".
    A leading line must spell out the scale step using the ORIGINAL
    (unscaled) operands."""
    grid = build_long_division_steps(Decimal("2.53"), Decimal("1.1"), ending="decimal")
    text = render_steps_grid_text(grid, col_width=1)
    assert "2.53 ÷ 1.1 = 25.3 ÷ 11" in text
    assert "x10 both sides" in text
    assert _bare_quotient(grid) == "2.3"


def test_division_whole_divisor_has_no_scale_note():
    """A whole-number divisor needs no scaling, so no scale-explanation line
    should appear at all (only decimal divisors trigger it)."""
    grid = build_long_division_steps(432, 15, ending="remainder")
    text = render_steps_grid_text(grid, col_width=1)
    assert "becomes" not in text


def test_division_decimal_dividend_whole_divisor():
    grid = build_long_division_steps(Decimal("17.0"), 5)
    assert _bare_quotient(grid) == "3.4"
    assert Decimal(_bare_quotient(grid)) == Decimal("3.4")


def test_division_internal_zero_quotient_digit_is_shown():
    """408 / 4 = 102 -- the middle "0" is an INTERNAL zero (a step whose
    quotient digit genuinely is 0, after the window has already started),
    not a suppressed leading zero -- it must still show."""
    grid = build_long_division_steps(408, 4)
    assert _bare_quotient(grid) == "102"


def test_division_single_digit_quotient():
    """30 / 5 = 6 -- the dividend has TWO digits ("30"), but the leading
    zero-suppression means the quotient reads bare "6", not "06"."""
    grid = build_long_division_steps(30, 5)
    assert _bare_quotient(grid) == "6"


def _last_digit_row(grid):
    """The last row containing a DIGIT cell -- robust to an annotation row
    (2026-07-25: its own line, not appended text) following the real final
    numeric row."""
    return next(row for row in reversed(grid.rows) if any(c.kind == DIGIT for c in row))


def test_division_exact_no_remainder_shows_final_zero():
    grid = build_long_division_steps(225, 5)
    last_row = _last_digit_row(grid)
    remainder_text = "".join(c.text for c in last_row if c.kind == DIGIT and c.text)
    assert remainder_text == "0"


def test_division_by_larger_number_still_terminates():
    grid = build_long_division_steps(896, 8)
    assert _bare_quotient(grid) == "112"


def test_division_hand_example_425_div_4_remainder():
    """The maintainer's own hand-worked alignment check: 425 / 4 = 106 R 1.
    Exercises the zero-padded bring-down row (the internal "0" quotient
    digit's bring-down reads "02", not bare "2") and the inline "R 1" suffix."""
    grid = build_long_division_steps(425, 4, ending="remainder")
    assert _quotient_from_grid(grid) == "106 R 1"
    last_row = _last_digit_row(grid)
    remainder_text = "".join(c.text for c in last_row if c.kind == DIGIT and c.text)
    assert remainder_text == "1"


def test_division_remainder_ending_432_div_15():
    """The maintainer's reference image, panel 1: 432 / 15 = 28 R 12."""
    grid = build_long_division_steps(432, 15, ending="remainder")
    assert _quotient_from_grid(grid) == "28 R 12"


def test_division_plain_text_columns_align_with_a_2digit_divisor():
    """Regression (2026-07-24, maintainer-caught): the header row's ") "
    bracket cell is 2 characters wide, so every OTHER row's lead-in must
    also be 2 characters wider than the divisor -- else subtraction/
    bring-down digits drift one column left of the dividend digits they
    belong under. Checks REAL column positions in the rendered text, not
    just cell content (no earlier test caught this)."""
    grid = build_long_division_steps(432, 15, ending="remainder")
    text = render_steps_grid_text(grid, col_width=1)
    lines = text.split("\n")
    header = next(l for l in lines if l.strip().startswith("15)"))
    # The numeric "30" row and its "Middle Step: 15 x 2" annotation are now
    # separate lines (2026-07-25) -- find the numeric one specifically (no
    # "<--" marker) rather than a line containing both substrings.
    thirty_line = next(l for l in lines if "30" in l and "<--" not in l and l.strip().startswith("−"))
    # "43" (the first two dividend digits) and "30" (what's subtracted from
    # them) must occupy the SAME two columns.
    dividend_43_col = header.index("43")
    thirty_col = thirty_line.index("30")
    assert dividend_43_col == thirty_col, (header, thirty_line)
    assert any("Middle Step: 15 x 2 = 30" in l for l in lines)


def test_division_fraction_ending_432_div_15():
    """Reference image, panel 2: 432 / 15 = 28 4/5 (12/15 reduced)."""
    grid = build_long_division_steps(432, 15, ending="fraction")
    assert _quotient_from_grid(grid) == "28 4/5"


def test_division_decimal_ending_432_div_15():
    """Reference image, panel 3: 432 / 15 = 28.8 (continues past the given
    whole-number precision by synthesizing a decimal ".0" and dividing on)."""
    grid = build_long_division_steps(432, 15, ending="decimal")
    assert _bare_quotient(grid) == "28.8"
    last_row = grid.rows[-1]
    remainder_text = "".join(c.text for c in last_row if c.kind == DIGIT and c.text)
    assert remainder_text == "0"


def test_division_remainder_and_fraction_endings_always_succeed():
    """Unlike "decimal", "remainder" and "fraction" never need to raise --
    they stop at the given digits' precision regardless of whether the
    division divides evenly."""
    build_long_division_steps(1, 3, ending="remainder")
    build_long_division_steps(1, 3, ending="fraction")


def test_division_decimal_ending_raises_on_repeating_decimal():
    """1 / 3 = 0.333... never terminates -- "decimal" ending must raise
    rather than loop forever or silently truncate to a wrong quotient."""
    with pytest.raises(ValueError):
        build_long_division_steps(1, 3, ending="decimal")


def test_division_whole_dividend_smaller_than_divisor():
    """4 / 20 (or 4 / 15): the given dividend alone never reaches the
    divisor, so under "remainder"/"fraction" the quotient is a bare "0"
    plus the leftover -- no longer a ValueError (2026-07-19's version
    rejected this; the new remainder/fraction endings handle it directly)."""
    grid = build_long_division_steps(4, 20, ending="remainder")
    assert _bare_quotient(grid) == "0"
    grid = build_long_division_steps(4, 15, ending="fraction")
    assert _bare_quotient(grid) == "0"


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
        reconstructed = _bare_quotient(grid)
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
        reconstructed = _bare_quotient(grid)
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
        reconstructed = _bare_quotient(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=str(quotient))
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed)


def test_division_remainder_as_fraction_self_validates_against_real_verifier():
    """Mirrors gen_division_remainder_as_fraction: dividend deliberately NOT
    a multiple of divisor -- every reduced mixed-number answer must still
    verify as fraction-equivalent."""
    rng = random.Random(2034)
    for _ in range(300):
        divisor = rng.randint(2, 20)
        quotient = rng.randint(10, 40)
        remainder = rng.randint(1, divisor - 1)
        dividend = quotient * divisor + remainder
        grid = build_long_division_steps(dividend, divisor, ending="fraction")
        frac = Fraction(remainder, divisor)
        ground_truth = f"{quotient} {frac.numerator}/{frac.denominator}"
        reconstructed = _quotient_from_grid(grid)
        outcome = check(answer_type="fraction", checker="fraction_equiv",
                         llm_output=reconstructed, ground_truth=ground_truth)
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed, ground_truth)


def test_division_remainder_as_decimal_self_validates_against_real_verifier():
    """Mirrors gen_division_remainder_as_decimal: divisor restricted to
    factors of 2/5 so the decimal always terminates within the cap."""
    rng = random.Random(2035)
    for _ in range(300):
        divisor = rng.choice([2, 4, 5, 8, 10, 16, 20, 25])
        quotient = rng.randint(10, 40)
        remainder = rng.randint(1, divisor - 1)
        dividend = quotient * divisor + remainder
        grid = build_long_division_steps(dividend, divisor, ending="decimal")
        ground_truth = str(Decimal(dividend) / Decimal(divisor))
        reconstructed = _bare_quotient(grid)
        outcome = check(answer_type="decimal", checker="decimal_exact",
                         llm_output=reconstructed, ground_truth=ground_truth)
        assert outcome.result is CheckResult.PASS, (dividend, divisor, reconstructed, ground_truth)


def test_extract_division_matches_real_phrasing():
    assert extract_division_operands("What is 225 ÷ 5?") == (Decimal("225"), Decimal("5"))


def test_extract_division_rejects_negative_or_zero_divisor():
    assert extract_division_operands("What is -10 ÷ 5?") is None
    assert extract_division_operands("What is 10 ÷ 0?") is None


def test_extract_division_accepts_non_terminating_since_ending_decides():
    """2026-07-24: eligibility is no longer decided here -- a division that
    doesn't divide evenly (like 1 / 3) is a valid extraction; whether it can
    actually be RENDERED depends on the `ending` the caller picks, checked
    at build_long_division_steps time instead (see dialogue/controller.py)."""
    assert extract_division_operands("What is 1 ÷ 3?") == (Decimal("1"), Decimal("3"))


def test_extract_division_rejects_non_division_nodes():
    assert extract_division_operands("What is 47 + 19?") is None
