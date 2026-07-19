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
_MULTIPLICATION_RE = re.compile(rf"What is ({_NUM}) × ({_NUM})\?")
_DIVISION_RE = re.compile(rf"What is ({_NUM}) ÷ ({_NUM})\?")


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


def extract_multiplication_operands(problem: str) -> tuple[int, int] | None:
    """Pull the two operands out of a multiplication question WE generated
    (e.g. "What is 64 × 32?"). Phase 3 scope is deliberately narrower than
    add/sub: INTEGER operands only -- decimal multiplication
    (`gen_mult_decimals`, `gen_mult_decimal_by_decimal`) needs its own
    place-value handling (the result's decimal places = the SUM of the
    operands' decimal places, not the max like add/sub) and is deferred,
    not silently dropped (see docs/PHASE0_STATUS.md backlog). Negative
    operands excluded same as add/sub (Y8's gen_negative_multiplication)."""
    m = _MULTIPLICATION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b < 0 or a != a.to_integral_value() or b != b.to_integral_value():
        return None
    return int(a), int(b)


def extract_division_operands(problem: str) -> tuple[Decimal, Decimal] | None:
    """Pull the two operands out of a division question WE generated (e.g.
    "What is 225 ÷ 5?"). Negative operands and a zero divisor are excluded
    outright. The remaining eligibility question -- does this division
    actually terminate using only the dividend's OWN given digits, the way
    `build_long_division_steps` processes it (see that function's docstring
    for why it doesn't synthesize extra trailing zero digits) -- is
    answered by just attempting the build and catching its ValueError,
    rather than duplicating the bus-stop algorithm here as a second
    "is this exact" check. All three shipped division generators
    (`gen_division_facts`, `gen_div_decimals`, `gen_div_decimal_by_decimal`)
    construct the dividend FROM the quotient, so this always succeeds for
    real content -- the guard exists for correctness, not because it's
    expected to reject anything shipped today."""
    m = _DIVISION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b <= 0:
        return None
    try:
        build_long_division_steps(a, b)
    except ValueError:
        return None
    return a, b


def _frac_digits(d: Decimal) -> int:
    """How many digits after the decimal point `d` needs, e.g. Decimal('3.40')
    -> 2. 0 for a whole number. Deliberately does NOT call .normalize() --
    normalize collapses trailing zeros based on mathematical value
    (Decimal('17.0').normalize() == Decimal('17'), exponent 0), which would
    silently drop a decimal point that's genuinely present in the PROBLEM
    TEXT (e.g. a division dividend constructed as quotient * divisor,
    "17.0", which prints with its trailing zero -- collapsing it here would
    misalign a decimal grid built from that same text)."""
    exponent = d.as_tuple().exponent
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


def build_multiplication_partial_products_steps(a: int, b: int) -> StepGrid:
    """Partial-products method -- the maintainer's own worked example,
    64 x 32: decompose the SECOND factor by place value, multiply each
    place's value by `a` as a single "known fact" (deliberately NO carry
    marks -- that's the whole point of this method, per the maintainer's
    own note), then sum the partial products via ordinary column addition
    WITH carries (reusing the same left-shifted carry indexing as
    build_addition_steps). One partial-product row per nonzero digit of
    `b`, ones-place first (top), matching the maintainer's own ordering
    ("(64 x 2) + (64 x 30)"). Phase 3 scope: non-negative INTEGERS only
    (see extract_multiplication_operands)."""
    str_b = str(b)
    n_digits_b = len(str_b)
    partials = [
        a * int(str_b[n_digits_b - 1 - place]) * (10 ** place)
        for place in range(n_digits_b)
        if str_b[n_digits_b - 1 - place] != "0"
    ] or [0]

    result = a * b
    str_partials = [str(p) for p in partials]
    width = max(len(str(a)), len(str_b), len(str(result)), *(len(p) for p in str_partials))

    def _display(s: str) -> list[Cell]:
        return [Cell(ch if ch != " " else "", DIGIT) for ch in s.rjust(width)]

    n_cols = width + 1  # +1 for the leading operator column
    line_row = [Cell("", LINE) for _ in range(n_cols)]
    rows = [
        [Cell("", OPERATOR)] + _display(str(a)),
        [Cell("×", OPERATOR)] + _display(str_b),
        line_row,
    ]

    if len(partials) > 1:
        # A genuine summation step -- reuse addition's carry algorithm,
        # N-ary instead of 2-ary. The carry mark sits directly above the
        # partial-product block it belongs to, same as addition's carry row
        # sits above its two operand rows.
        padded_partials = [p.rjust(width, "0") for p in str_partials]
        carry_above = [0] * width
        carry = 0
        for col in range(width - 1, -1, -1):
            total = sum(int(p[col]) for p in padded_partials) + carry
            carry = total // 10
            if carry and col > 0:
                carry_above[col - 1] = carry
        rows.append([Cell("", OPERATOR)] + [Cell(str(c) if c else "", CARRY) for c in carry_above])
        rows += [[Cell("", OPERATOR)] + _display(p) for p in str_partials]
        rows.append(line_row)
        rows.append([Cell("", OPERATOR)] + _display(str(result)))
    else:
        rows += [[Cell("", OPERATOR)] + _display(p) for p in str_partials]
    return StepGrid(rows=rows, n_cols=n_cols)


def build_long_division_steps(dividend: Decimal | int, divisor: Decimal | int) -> StepGrid:
    """Bus-stop ("long") division -- the maintainer's own 5-step worked
    example, 225 / 5: divisor and dividend separated by ')' under a
    vinculum; process dividend digits left to right over a running
    remainder. A leading digit smaller than the divisor produces quotient
    digit 0 -- by textbook convention this ISN'T given its own work row
    until the first NONZERO quotient digit appears, after which every step
    is drawn (including a later internal zero, e.g. 408 / 4).

    A non-integer divisor is scaled to a whole number first (multiply both
    operands by the same power of 10 -- the standard technique). This
    covers the maintainer's ORIGINAL motivating example, 8.96 / 3.2: scale
    by 10 -> 89.6 / 32, then the same digit-by-digit process, carrying the
    decimal point straight down into the quotient at the SAME digit
    position it sits in the (scaled) dividend.

    Raises ValueError if the dividend's OWN given digits aren't enough to
    reach an exact (remainder-0) result -- this does NOT synthesize extra
    trailing zero digits to keep dividing forever (both to avoid an
    infinite loop on a non-terminating division, and because every shipped
    generator constructs the dividend FROM the quotient, so its given
    precision is always already exactly enough). See
    extract_division_operands, which uses this exception as the
    eligibility check rather than duplicating the algorithm."""
    dividend_dec, divisor_dec = Decimal(dividend), Decimal(divisor)
    scale_pow = _frac_digits(divisor_dec)
    # .scaleb() shifts the decimal point cleanly (adjusts the exponent only)
    # -- unlike multiplying by Decimal(10) ** scale_pow, which ADDS
    # exponents and multiplies significands, silently baking in an extra
    # trailing zero of "precision" that was never actually in the dividend
    # (e.g. Decimal('8.96') * Decimal(10) == Decimal('89.60'), 2 dp, not
    # the clean 1 dp shift "89.6" that scaleb gives).
    scaled_dividend = dividend_dec.scaleb(scale_pow)
    divisor_int = int(divisor_dec.scaleb(scale_pow).to_integral_value())

    dividend_frac_digits = _frac_digits(scaled_dividend)
    dividend_digit_str = str(int(scaled_dividend.scaleb(dividend_frac_digits).to_integral_value()))
    n = len(dividend_digit_str)
    point_at = n - dividend_frac_digits if dividend_frac_digits else None

    quotient_digits = []
    steps = []  # (end_idx, product_str, remainder_str)
    remainder = 0
    started = False
    for i, ch in enumerate(dividend_digit_str):
        remainder = remainder * 10 + int(ch)
        q_digit = remainder // divisor_int
        product = q_digit * divisor_int
        remainder -= product
        quotient_digits.append(q_digit)
        if q_digit != 0 or started:
            started = True
            steps.append((i, str(product), str(remainder)))
    if remainder != 0:
        raise ValueError("division does not terminate within the given dividend's precision")

    divisor_str = str(divisor_int)
    divisor_width = len(divisor_str)
    n_cols = divisor_width + 1 + n + (1 if point_at is not None else 0)

    def _at_point(cells: list[Cell], point_cell: Cell) -> list[Cell]:
        if point_at is None:
            return cells
        return cells[:point_at] + [point_cell] + cells[point_at:]

    def _region_row(digits_by_pos: dict[int, str], kind: str, point_cell: Cell) -> list[Cell]:
        return _at_point([Cell(digits_by_pos.get(i, ""), kind) for i in range(n)], point_cell)

    blank_lead = [Cell("", BLANK)] * (divisor_width + 1)
    minus_lead = [Cell("", BLANK)] * (divisor_width - 1) + [Cell("−", OPERATOR)] + [Cell("", BLANK)]

    # Quotient row: leading zero digits (before the first drawn step) are
    # blanked, same "never show a leading zero" convention as add/sub/mult --
    # but the LAST digit must always show (whole quotient is 0), and so must
    # the ones-place digit immediately before the point when there is one
    # (e.g. 10.2 / 34 = 0.3 -- must read "0.3", not ".3").
    # (A dividend < 1, e.g. "0.34 / 2", would need point_at == 0 -- no
    # ones-place column exists to force-show at all in that case. None of
    # the shipped division generators ever produce a dividend < 1, so this
    # is an intentionally out-of-scope edge case, not silently mishandled:
    # guarded here rather than indexing quotient_digits[-1] by accident.)
    first_shown = min(steps[0][0], n - 1) if steps else n - 1
    if point_at:
        first_shown = min(first_shown, point_at - 1)
    quotient_by_pos = {i: str(quotient_digits[i]) for i in range(first_shown, n)}
    quotient_row = blank_lead + _region_row(quotient_by_pos, DIGIT, Cell(".", POINT))

    # The point column stays a plain blank continuation on the rule, not an
    # actual "." glyph.
    vinculum_row = blank_lead + _at_point([Cell("", LINE) for _ in range(n)], Cell("", BLANK))

    divisor_cells = [Cell(ch, DIGIT) for ch in divisor_str]
    dividend_by_pos = {i: dividend_digit_str[i] for i in range(n)}
    header_row = divisor_cells + [Cell(")", OPERATOR)] + _region_row(dividend_by_pos, DIGIT, Cell(".", POINT))

    rows = [quotient_row, vinculum_row, header_row]
    for end_idx, product_str, remainder_str in steps:
        product_by_pos = {end_idx - len(product_str) + 1 + k: c for k, c in enumerate(product_str)}
        remainder_by_pos = {end_idx - len(remainder_str) + 1 + k: c for k, c in enumerate(remainder_str)}
        # Working rows treat the point column as a plain blank continuation,
        # not an actual "." glyph -- these are intermediate integer
        # quantities (a product/remainder is never itself "decimal"), even
        # though they sit at dividend-region columns that may straddle
        # where the point falls in the dividend/quotient rows above.
        rows.append(minus_lead + _region_row(product_by_pos, DIGIT, Cell("", BLANK)))
        rows.append(blank_lead + _at_point(
            [Cell("", LINE) if i in product_by_pos else Cell("", BLANK) for i in range(n)],
            Cell("", BLANK),
        ))
        rows.append(blank_lead + _region_row(remainder_by_pos, DIGIT, Cell("", BLANK)))

    return StepGrid(rows=rows, n_cols=n_cols)
