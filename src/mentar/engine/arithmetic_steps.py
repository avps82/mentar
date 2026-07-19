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
BORROW = "borrow"
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
_SUBTRACTION_RE = re.compile(rf"What is ({_NUM}) [−-] ({_NUM})\?")


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


def extract_subtraction_operands(problem: str) -> tuple[Decimal, Decimal] | None:
    """Pull the two operands out of a subtraction question WE generated (e.g.
    "What is 47 − 19?"). Returns None for anything outside plain non-negative
    column subtraction WITH a non-negative result: negative operands are
    excluded for the same reason as addition (see module docstring), and a
    result that would go negative (b > a) is ALSO excluded -- the borrow
    method here is the unsigned early-years algorithm; a negative result
    needs integer/number-line reasoning instead (Y7's gen_integers_add_sub
    can produce exactly this, e.g. "What is 5 - 12?")."""
    m = _SUBTRACTION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b < 0 or b > a:
        return None
    return a, b


def _frac_digits(d: Decimal) -> int:
    """How many digits after the decimal point `d` needs, e.g. Decimal('3.40')
    -> 2. 0 for a whole number."""
    exponent = d.normalize().as_tuple().exponent
    return max(0, -exponent) if isinstance(exponent, int) else 0


@dataclass(frozen=True)
class _Layout:
    width: int
    padded_a: str   # zero-padded -- for the ARITHMETIC (a leading virtual zero is a no-op)
    padded_b: str
    display_a: str  # space-padded, ones-digit-guaranteed -- for DISPLAY (see below)
    display_b: str
    display_result: str
    point_at: int | None


def _layout(str_a: str, str_b: str, str_result: str, frac_digits: int) -> _Layout:
    """Shared column-width bookkeeping for both column-carry addition and
    column-borrow subtraction: how wide the grid needs to be, and the
    display (leading-zero-blanked) form of each row. Two things a naive
    `rjust(width)` gets wrong, both fixed here:
    - When EVERY value's whole part is zero (e.g. 0.2 + 0.3), the integer
      strings alone (str(2), str(3), str(5)) carry no record of that whole
      part at all -- width must be widened to fit at least the ones-place
      column, or there's nowhere to put it.
    - Blanking every leading zero for display would blank the ones digit
      too when it happens to be zero (e.g. subtraction's 1.2 - 0.5 = 0.7),
      producing ".7" instead of "0.7" -- the ones-place column is exempted
      from blanking whenever a decimal point is present.
    """
    width = max(len(str_a), len(str_b), len(str_result))
    if frac_digits:
        width = max(width, frac_digits + 1)

    padded_a = str_a.rjust(width, "0")
    padded_b = str_b.rjust(width, "0")

    def _display(str_x: str) -> str:
        chars = list(str_x.rjust(width))
        if frac_digits:
            ones_idx = width - frac_digits - 1
            if chars[ones_idx] == " ":
                chars[ones_idx] = "0"
        return "".join(chars)

    point_at = width - frac_digits if frac_digits else None
    return _Layout(
        width=width, padded_a=padded_a, padded_b=padded_b,
        display_a=_display(str_a), display_b=_display(str_b),
        display_result=_display(str_result), point_at=point_at,
    )


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

    lay = _layout(str(int_a), str(int_b), str(int_result), frac_digits)
    width = lay.width

    carry_above = [0] * width  # carry_above[col] = the carry digit shown ABOVE this column
    carry = 0
    for col in range(width - 1, -1, -1):
        total = int(lay.padded_a[col]) + int(lay.padded_b[col]) + carry
        carry = total // 10
        if carry and col > 0:
            carry_above[col - 1] = carry

    def _insert_point(cells: list[Cell]) -> list[Cell]:
        if lay.point_at is None:
            return cells
        return cells[:lay.point_at] + [Cell(".", POINT)] + cells[lay.point_at:]

    carry_row = _insert_point([Cell(str(c) if c else "", CARRY) for c in carry_above])
    a_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_a])
    b_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_b])
    result_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_result])
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


def build_subtraction_steps(a: Decimal | int, b: Decimal | int) -> StepGrid:
    """Column subtraction, right-to-left, with borrow marks shown only where a
    borrow actually occurs. Mirrors the maintainer's own worked example
    (47 − 19 -> a "−1" mark above the tens column, since the ones column
    (7 − 9) had to borrow from it): a borrow generated while processing
    column N is recorded on column N-1, the SAME indexing build_addition_steps
    uses for its carry row, just for the opposite reason (a column that lent
    a 1, not one that overflowed into the next). Borrows chain leftward
    through zero digits exactly like carries do (e.g. 500 − 8). Caller must
    guarantee a >= b (see extract_subtraction_operands) -- this is the
    unsigned early-years algorithm, not integer subtraction."""
    a_dec, b_dec = Decimal(a), Decimal(b)
    frac_digits = max(_frac_digits(a_dec), _frac_digits(b_dec))
    scale = Decimal(10) ** frac_digits

    int_a = int((a_dec * scale).to_integral_value())
    int_b = int((b_dec * scale).to_integral_value())
    int_result = int_a - int_b

    lay = _layout(str(int_a), str(int_b), str(int_result), frac_digits)
    width = lay.width

    # This loop's only job is to find WHERE borrows happened -- int_result
    # (already computed above via plain Decimal subtraction) is the ground
    # truth for the displayed digits, so there's no separate per-column
    # result to track here.
    borrow_above = [0] * width  # borrow_above[col] = a borrow was taken FROM this column
    borrow_in = 0
    for col in range(width - 1, -1, -1):
        top = int(lay.padded_a[col]) - borrow_in
        bottom = int(lay.padded_b[col])
        if top < bottom:
            borrow_in = 1
            if col > 0:
                borrow_above[col - 1] = 1
        else:
            borrow_in = 0

    def _insert_point(cells: list[Cell]) -> list[Cell]:
        if lay.point_at is None:
            return cells
        return cells[:lay.point_at] + [Cell(".", POINT)] + cells[lay.point_at:]

    borrow_row = _insert_point([Cell("−1" if c else "", BORROW) for c in borrow_above])
    a_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_a])
    b_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_b])
    result_row = _insert_point([Cell(ch if ch != " " else "", DIGIT) for ch in lay.display_result])
    n_cols = len(a_row) + 1  # +1 for the leading operator column
    line_row = [Cell("", LINE) for _ in range(n_cols)]

    rows = [
        [Cell("", OPERATOR)] + borrow_row,
        [Cell("", OPERATOR)] + a_row,
        [Cell("−", OPERATOR)] + b_row,
        line_row,
        [Cell("", OPERATOR)] + result_row,
    ]
    return StepGrid(rows=rows, n_cols=n_cols)
