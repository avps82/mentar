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

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from decimal import Decimal  # noqa: E402

from mentar.engine.arithmetic_steps import (  # noqa: E402
    CARRY,
    DIGIT,
    LINE,
    OPERATOR,
    POINT,
    build_addition_steps,
    extract_addition_operands,
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
