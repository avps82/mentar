"""Deterministic step-by-step arithmetic grids — "show human working" (2026-07-19
maintainer feedback: Help/Explain gave prose about arithmetic, never the actual
school algorithm a child is taught: column addition/subtraction with carry/
borrow, long multiplication, long division).

Every builder here is a PURE function of its operands — same "computed ground
truth, LLM never decides correctness" posture as every item generator
(engine/au_items.py etc.), and the same reasoning A14
(engine/explain_check.py) already encodes: an LLM asked to "show its steps"
for arithmetic is exactly the failure class this project guards against.
These grids are provably correct by construction; nothing here is LLM output.

A StepGrid is a right-aligned 2D layout: rows top-to-bottom, cells
left-to-right, one cell per grid column. The web layer renders this via CSS
Grid (one <div> per cell), NOT through the LLM markdown-lite pipeline (U-32) —
this content never touches free-form model text.

Scope note: the column-carry method here is specifically the UNSIGNED
addition algorithm taught in early years. Negative operands (Y7's integer
addition, e.g. "-8 + 3") are deliberately NOT step-eligible -- that's a
different pedagogical case (number-line reasoning, not column carries) and
extraction returns None for them, falling back to the existing LLM-prose
explanation rather than rendering a grid that doesn't match how the concept
is actually taught.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

# Cell kinds -- drive the CSS class the web layer applies per cell.
CARRY = "carry"
DIGIT = "digit"
OPERATOR = "operator"
BLANK = "blank"
LINE = "line"          # a full-width horizontal rule row
POINT = "point"         # a decimal point


@dataclass(frozen=True)
class Cell:
    text: str
    kind: str


@dataclass(frozen=True)
class StepGrid:
    rows: list[list[Cell]]
    n_cols: int


# ── Operand extraction ────────────────────────────────────────────────────────
# NOT parsing arbitrary/LLM text -- these regexes only ever see problem text
# WE generated (item generators' own f-strings), so the small set of exact
# phrasings below is the complete, known input space, not a best-effort guess.
# Both minus-sign characters appear across the codebase's generators (U+2212
# "−" in the older functions, ASCII "-" in newer ones) -- match either.
_NUM = r"-?\d+(?:\.\d+)?"
_ADDITION_RE = re.compile(rf"What is ({_NUM}) \+ ({_NUM})\?")


def extract_addition_operands(problem: str) -> tuple[Decimal, Decimal] | None:
    """Pull the two operands out of an addition question WE generated (e.g.
    "What is 47 + 19?"). Returns None for anything that isn't a plain
    non-negative column addition: fraction additions ("2/5 + 3/5") don't
    match (the number pattern stops at "/"), order-of-operations expressions
    don't match (no lone "N + M?" substring), and negative operands are
    explicitly excluded (see module docstring -- different pedagogical case).
    A non-match means "this node doesn't participate in step-display", not an
    error -- the caller falls back to the existing LLM-prose explanation."""
    m = _ADDITION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b < 0:
        return None
    return a, b


def _frac_digits(d: Decimal) -> int:
    """How many digits after the decimal point `d` needs, e.g. Decimal('3.40')
    -> 2. 0 for a whole number."""
    exponent = d.normalize().as_tuple().exponent
    return max(0, -exponent) if isinstance(exponent, int) else 0


def build_addition_steps(a: Decimal | int, b: Decimal | int) -> StepGrid:
    """Column addition, right-to-left, with a carry row shown only where a
    carry actually occurs. Example: 47 + 19 -> carry row "1" above the tens
    column, operand rows 47/19, a rule, result row 66. Decimal operands are
    supported by scaling both to integers by the shared number of decimal
    places, running the identical integer column algorithm, then
    re-inserting a POINT cell at display time -- avoids a second,
    decimal-specific carry algorithm entirely."""
    a_dec, b_dec = Decimal(a), Decimal(b)
    frac_digits = max(_frac_digits(a_dec), _frac_digits(b_dec))
    scale = Decimal(10) ** frac_digits

    int_a = int((a_dec * scale).to_integral_value())
    int_b = int((b_dec * scale).to_integral_value())
    int_result = int_a + int_b

    str_a, str_b, str_result = str(int_a), str(int_b), str(int_result)
    width = max(len(str_a), len(str_b), len(str_result))

    # Pad with '0' for the ARITHMETIC (a leading virtual zero doesn't change
    # the sum); pad with space for DISPLAY so leading zeros never show.
    padded_a = str_a.rjust(width, "0")
    padded_b = str_b.rjust(width, "0")
    display_a = str_a.rjust(width)
    display_b = str_b.rjust(width)

    result_digits = [0] * width
    carry_above = [0] * width  # carry_above[col] = the carry digit shown ABOVE this column
    carry = 0
    for col in range(width - 1, -1, -1):
        total = int(padded_a[col]) + int(padded_b[col]) + carry
        result_digits[col] = total % 10
        carry = total // 10
        if carry and col > 0:
            carry_above[col - 1] = carry

    # Where (from the left) does the decimal point sit, if anywhere?
    point_at = width - frac_digits if frac_digits else None

    def _insert_point(cells: list[Cell]) -> list[Cell]:
        if point_at is None:
            return cells
        return cells[:point_at] + [Cell(".", POINT)] + cells[point_at:]

    carry_row = _insert_point([Cell(str(c) if c else "", CARRY) for c in carry_above])
    a_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in display_a])
    b_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in display_b])
    result_row = _insert_point([Cell(str(d), DIGIT) for d in result_digits])
    n_cols = len(a_row) + 1  # +1 for the leading operator column
    line_row = [Cell("", LINE) for _ in range(n_cols)]

    rows = [
        [Cell("", OPERATOR)] + carry_row,
        [Cell("", OPERATOR)] + a_row,
        [Cell("+", OPERATOR)] + b_row,
        line_row,
        [Cell("", OPERATOR)] + result_row,
    ]
    return StepGrid(rows=rows, n_cols=n_cols)
