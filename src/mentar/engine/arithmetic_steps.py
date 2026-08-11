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
from fractions import Fraction

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


def _render_row_text(row: list[Cell], col_width: int) -> str:
    parts = []
    for cell in row:
        if cell.kind == LINE:
            parts.append("-" * col_width)
        elif len(cell.text) > col_width:
            parts.append(cell.text)
        else:
            parts.append(cell.text.rjust(col_width))
    return "".join(parts).rstrip()


def render_steps_grid_text(grid: StepGrid, col_width: int = 1) -> str:
    """Render a StepGrid as plain monospace text (2026-07-24) -- one line per
    row, one right-justified `col_width`-wide slot per cell -- for a `<pre>`
    block in the web UI, replacing the earlier per-cell CSS Grid divs. A
    `LINE`-kind cell becomes a `col_width`-wide dash-fill (so consecutive
    rule cells read as one continuous rule, no gaps); a cell whose text is
    LONGER than `col_width` (a multi-character annotation like " R 12",
    " 4/5", or "−1") is emitted as-is, never truncated or squeezed. Each
    finished row is right-stripped (trailing whitespace only -- interior
    spacing from earlier columns is preserved), then all rows are joined
    with newlines. Pure function: no I/O, no mutation of `grid`."""
    return "\n".join(_render_row_text(row, col_width) for row in grid.rows)


def render_steps_grid_lines(grid: StepGrid, col_width: int = 1) -> list[dict]:
    """Same rendering as `render_steps_grid_text`, but returns one dict per
    ROW instead of one joined string, each tagged `is_annotation` -- a
    "Middle Step"/scale-explanation/etc. note (2026-07-25) is always a
    single-cell row whose text is a free-text sentence, never digit-grid
    content -- every numeric/rule row always has multiple cells (a lead +
    the digit region). The web layer uses this tag to render annotation
    lines at a SMALLER font size so a long sentence still fits on ONE line
    without wrapping or a horizontal scrollbar (both were tried and
    rejected as looking bad for a "keep it ASCII" display) --
    `render_steps_grid_text` above stays as the plain-string form other
    callers (and most tests) use."""
    return [
        {
            "text": _render_row_text(row, col_width),
            "is_annotation": len(row) == 1 and len(row[0].text) > col_width,
        }
        for row in grid.rows
    ]


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


def extract_decimal_multiplication_operands(problem: str) -> tuple[Decimal, Decimal] | None:
    """Phase A (2026-08-11): the DECIMAL multiplication case
    `extract_multiplication_operands` deliberately rejects.

    A sibling rather than a widening of that function, on purpose: its
    integer-only contract is relied on by its existing caller, and the
    caller -- not the extractor -- is the right place to decide which
    builder to use (the same split `extract_division_operands` already uses
    for its `ending`). Non-negative only; at least one operand must actually
    be non-integer, otherwise the plain integer path already handles it and
    should keep doing so."""
    m = _MULTIPLICATION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b < 0:
        return None
    if a == a.to_integral_value() and b == b.to_integral_value():
        return None  # both whole -- not this path's job
    return a, b


def extract_signed_multiplication_operands(problem: str) -> tuple[int, int] | None:
    """Phase B (2026-08-11): the NEGATIVE-operand integer multiplication case
    `extract_multiplication_operands` deliberately rejects (Y8's
    `gen_negative_multiplication`, e.g. "What is -8 × 3?").

    Integers only -- a signed DECIMAL product would need both this sign rule
    and Phase A's place-value handling, no shipped generator produces one, and
    guessing at the combination is how the decimal-multiplication gap got
    missed in the first place. At least one operand must be negative, so the
    plain integer path keeps every case it already handles."""
    m = _MULTIPLICATION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a != a.to_integral_value() or b != b.to_integral_value():
        return None
    if a >= 0 and b >= 0:
        return None  # nothing signed about it -- not this path's job
    return int(a), int(b)


def extract_signed_addition_operands(problem: str) -> tuple[int, int, str] | None:
    """Phase C (2026-08-12): integer add/sub that the UNSIGNED column method
    cannot do -- either operand negative, or a subtraction whose result goes
    negative ("What is 5 - 12?", which `extract_subtraction_operands` rejects
    by design because borrow-columns cannot represent it).

    Returns `(a, b, op)` with `op` in `{"+", "-"}` -- the operator is kept
    rather than folded into `b` because the grid SHOWS the original question
    before rewriting it, and a child needs to see their own sum first.

    Integers only. Anything the plain path already handles is left to it, so
    the three add/sub extractors partition the space the same way the three
    multiplication ones do."""
    m = _ADDITION_RE.search(problem)
    op = "+"
    if not m:
        m = _SUBTRACTION_RE.search(problem)
        op = "-"
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a != a.to_integral_value() or b != b.to_integral_value():
        return None  # signed DECIMAL add/sub needs place-value handling too; no
                     # shipped generator produces one, so it is not guessed at
    ia, ib = int(a), int(b)
    if op == "+" and ia >= 0 and ib >= 0:
        return None  # plain column addition's job
    if op == "-" and ia >= 0 and ib >= 0 and ib <= ia:
        return None  # plain column subtraction's job
    return ia, ib, op


def extract_division_operands(problem: str) -> tuple[Decimal, Decimal] | None:
    """Pull the two operands out of a division question WE generated (e.g.
    "What is 225 ÷ 5?"). Negative operands and a zero divisor are excluded
    outright. Unlike the pre-2026-07-24 version, this no longer probes
    `build_long_division_steps` for "does it terminate" -- that question is
    now `ending`-dependent (a division that doesn't divide evenly is fine
    under ending="remainder"/"fraction", but can still raise under
    ending="decimal" if it doesn't terminate within the synthesized-digit
    cap). The caller knows which ending it wants (from the item's
    answer_type) and catches ValueError itself at that point -- see
    `dialogue/controller.py::_build_steps_grid_if_eligible`."""
    m = _DIVISION_RE.search(problem)
    if not m:
        return None
    try:
        a, b = Decimal(m.group(1)), Decimal(m.group(2))
    except InvalidOperation:
        return None
    if a < 0 or b <= 0:
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


def build_multiplication_decimal_steps(a: Decimal | int, b: Decimal | int) -> StepGrid:
    """Phase A (2026-08-11): decimal multiplication, taught the standard way --
    ignore the points, multiply as whole numbers, then place the point back
    counting total decimal places from the right.

    Reuses `build_multiplication_partial_products_steps` UNCHANGED on the
    scaled integers rather than re-deriving its carry logic, then rewrites
    only the two operand rows (back to the numbers as the child was given
    them, points intact) and the result row (point re-inserted). The
    partial-product rows in between are deliberately left as pure integers
    with no point -- that is exactly what the method asks the child to do,
    and showing a point there would misrepresent the step.

    Note the decimal-place arithmetic is a SUM, not the `max` that add/sub's
    shared `_layout` uses: 2.4 x 3.6 has 1 + 1 = 2 decimal places (8.64), where
    2.4 + 3.6 would have max(1, 1) = 1. Getting these two confused is the
    reason `extract_multiplication_operands` refused decimals in the first
    place instead of guessing."""
    a_dec, b_dec = Decimal(a), Decimal(b)
    frac_a, frac_b = _frac_digits(a_dec), _frac_digits(b_dec)
    frac_total = frac_a + frac_b

    int_a = int((a_dec.scaleb(frac_a)).to_integral_value())
    int_b = int((b_dec.scaleb(frac_b)).to_integral_value())

    grid = build_multiplication_partial_products_steps(int_a, int_b)
    rows = [list(r) for r in grid.rows]
    n_cols = grid.n_cols
    width = n_cols - 1  # leading operator column

    def _digits_row(text: str, operator: str) -> list[Cell]:
        padded = text.rjust(width)
        return [Cell(operator, OPERATOR)] + [
            Cell(ch if ch != " " else "", POINT if ch == "." else DIGIT) for ch in padded
        ]

    # Operand rows: show what the child was actually asked, not the scaled ints.
    rows[0] = _digits_row(str(a_dec), "")
    rows[1] = _digits_row(str(b_dec), "×")

    # Result row (always last): same digits, point re-inserted from the right.
    result_digits = str(int_a * int_b)
    if frac_total:
        padded = result_digits.rjust(frac_total + 1, "0")  # 0.08 needs its leading 0
        result_text = f"{padded[:-frac_total]}.{padded[-frac_total:]}"
    else:
        result_text = result_digits
    rows[-1] = _digits_row(result_text, "")

    # Re-inserting the point makes some rows one cell wider than the grid the
    # integer builder produced, so every other row needs padding to match. Pad
    # with a cell of the ROW'S OWN kind, not a blank digit: a LINE row padded
    # with a digit cell renders as "- ---" (a gap punched through the rule)
    # instead of a continuous "----".
    widest = max(len(r) for r in rows)
    for r in rows:
        pad_kind = LINE if r and all(c.kind == LINE for c in r) else DIGIT
        while len(r) < widest:
            r.insert(1, Cell("", pad_kind))
    return StepGrid(rows=rows, n_cols=widest)


def build_signed_multiplication_steps(a: int, b: int) -> StepGrid:
    """Phase B (2026-08-11): integer multiplication where at least one operand
    is negative -- the case the unsigned column method deliberately excludes.

    Structure: state the SIGN RULE first, then do the magnitude multiplication
    with the existing (unchanged) partial-products builder, then apply the sign
    to the result. The sign row sits ABOVE the arithmetic per the design doc's
    recommended default -- state the rule, then use it -- and moving it below is
    a two-line change if the maintainer prefers the other convention.

    Zero is handled explicitly rather than left to the sign rule: 0 is neither
    positive nor negative, so claiming "same signs -> positive" for -7 x 0 would
    be teaching something false. No shipped generator produces it
    (`gen_negative_multiplication` draws magnitudes from 2..12), but this is a
    general-purpose builder."""
    magnitude_grid = build_multiplication_partial_products_steps(abs(a), abs(b))
    rows = [list(r) for r in magnitude_grid.rows]
    n_cols = magnitude_grid.n_cols

    product = a * b
    if product == 0:
        rule = "0 × anything = 0"
    elif (a < 0) == (b < 0):
        rule = "same signs → answer is POSITIVE"
    else:
        rule = "different signs → answer is NEGATIVE"

    def _full_width(text: str, kind: str) -> list[Cell]:
        cells = [Cell(text, kind)] + [Cell("", BLANK) for _ in range(n_cols - 1)]
        return cells

    header = [
        _full_width(f"{a} × {b}", OPERATOR),
        _full_width(rule, CARRY),
        _full_width(f"first multiply {abs(a)} × {abs(b)}:", OPERATOR),
    ]
    footer = [
        _full_width(f"so {a} × {b} = {product}", OPERATOR),
    ]
    return StepGrid(rows=header + rows + footer, n_cols=n_cols)


def build_signed_addition_steps(a: int, b: int, op: str = "+") -> StepGrid:
    """Phase C (2026-08-12): signed integer addition/subtraction, taught by the
    same-sign / different-sign rule.

    Chosen over a number-line rendering deliberately (design doc §4 option 2):
    the rule method reuses the EXISTING, already-reviewed
    `build_addition_steps` / `build_subtraction_steps` on the magnitudes, in
    exactly the shape Phase B established for signed multiplication, instead of
    opening a new 1D-with-an-arc rendering surface and its own CSS. If the
    maintainer prefers the number line, this function is the thing to replace --
    the extractor and the wiring stay as they are.

    Shape, for "What is 5 - 12?":

        5 - 12
        rewrite as an addition:  5 + (-12)
        different signs → subtract the smaller from the larger, keep the bigger's sign
          12
        -  5
        ----
           7
        so 5 - 12 = -7

    Subtraction is rewritten to addition first because the rule is stated over
    two signed addends; showing that step keeps the child's own question visible
    rather than silently transforming it."""
    addend = b if op == "+" else -b
    total = a + addend
    same_signs = (a < 0) == (addend < 0)

    if same_signs:
        rule = "same signs \u2192 add the magnitudes, keep the sign"
        inner = build_addition_steps(abs(a), abs(addend))
    else:
        rule = "different signs \u2192 subtract the smaller from the larger, keep the bigger's sign"
        hi, lo = max(abs(a), abs(addend)), min(abs(a), abs(addend))
        inner = build_subtraction_steps(hi, lo)

    rows = [list(r) for r in inner.rows]
    n_cols = inner.n_cols

    def _line(text: str, kind: str) -> list[Cell]:
        return [Cell(text, kind)] + [Cell("", BLANK) for _ in range(n_cols - 1)]

    header = [_line(f"{a} {op} {b}", OPERATOR)]
    if op == "-":
        header.append(_line(f"rewrite as an addition:  {a} + ({addend})", OPERATOR))
    header.append(_line(rule, CARRY))
    footer = [_line(f"so {a} {op} {b} = {total}", OPERATOR)]
    return StepGrid(rows=header + rows + footer, n_cols=n_cols)


def build_long_division_steps(
    dividend: Decimal | int,
    divisor: Decimal | int,
    *,
    ending: str = "remainder",
    max_decimal_places: int = 6,
) -> StepGrid:
    """Bus-stop ("long") division -- rebuilt 2026-07-24 to match the
    standard school algorithm exactly (maintainer reference: 432 / 15 shown
    in three ending styles, cross-checked against a hand-worked
    425 / 4 = 106 R 1 alignment example). Unlike the 2026-07-19 version,
    quotient digits are NOT forced one-per-input-digit: the first "window"
    of dividend digits grows silently until it first reaches >= divisor
    (the standard leading-zero suppression -- 432/15 reads "28", not
    "028"), then every subsequent step consumes exactly one more digit and
    ALWAYS emits a quotient digit, including a genuine internal zero
    (408/4 -> "102" keeps its middle "0" -- that is not a leading zero).

    A division that doesn't divide evenly within the GIVEN digits is
    controlled by `ending`:
      - "remainder" (default): stop once the given digits run out; if the
        remainder is nonzero, append " R {remainder}" to the quotient row
        (e.g. "28 R 12"). Always succeeds for any non-negative dividend and
        positive divisor.
      - "fraction": same stopping point; append " {num}/{den}" -- the
        remainder/divisor reduced via fractions.Fraction (e.g. "28 4/5").
        Always succeeds.
      - "decimal": keep dividing past the given precision by synthesizing
        "0" digits (bringing them down exactly like a real digit) until the
        remainder reaches 0 or `max_decimal_places` synthesized digits have
        been used. Raises ValueError if it still hasn't terminated by the
        cap (a repeating decimal) -- this builder never rounds/truncates a
        wrong answer into looking exact.

    A non-integer divisor is still scaled to a whole number first (multiply
    both operands by the same power of 10 -- e.g. 8.96 / 3.2 -> 89.6 / 32),
    same as before."""
    if ending not in ("remainder", "fraction", "decimal"):
        raise ValueError(f"unknown ending: {ending!r}")

    dividend_dec, divisor_dec = Decimal(dividend), Decimal(divisor)
    scale_pow = _frac_digits(divisor_dec)
    # .scaleb() shifts the decimal point cleanly (adjusts the exponent only)
    # -- unlike multiplying by Decimal(10) ** scale_pow, which ADDS
    # exponents and multiplies significands, silently baking in an extra
    # trailing zero of "precision" that was never actually in the dividend.
    scaled_dividend = dividend_dec.scaleb(scale_pow)
    divisor_int = int(divisor_dec.scaleb(scale_pow).to_integral_value())
    divisor_str = str(divisor_int)
    divisor_width = len(divisor_str)

    dividend_frac_digits = _frac_digits(scaled_dividend)
    digits = list(str(int(scaled_dividend.scaleb(dividend_frac_digits).to_integral_value())))
    given_n = len(digits)
    point_at = given_n - dividend_frac_digits if dividend_frac_digits else None

    # Each step: (display_start, display_end inclusive, bring_down_str or
    # None for the first step, product_str, q_digit, window_value). Extra
    # fields (q_digit, window_value -- the value BEFORE subtracting this
    # step's product) exist only to drive the "Middle Step" annotations
    # below; display_start/end are the dividend-region column indices this
    # step's rule/subtraction spans.
    steps: list[tuple[int, int, str | None, str, int, int]] = []
    quotient_by_pos: dict[int, str] = {}
    remainder = 0
    started = False
    window_start = 0
    i = 0
    while True:
        if i >= len(digits):
            if ending == "decimal" and remainder != 0 and (len(digits) - given_n) < max_decimal_places:
                digits.append("0")
            else:
                break
        remainder_before_digit = remainder
        remainder = remainder * 10 + int(digits[i])
        window_value = remainder
        if started or remainder >= divisor_int:
            q, remainder = divmod(remainder, divisor_int)
            quotient_by_pos[i] = str(q)
            if started:
                bring_down_str = f"{remainder_before_digit:0{divisor_width}d}" + digits[i]
                display_start = i - divisor_width
            else:
                bring_down_str = None
                display_start = window_start
            steps.append((display_start, i, bring_down_str, str(q * divisor_int), q, window_value))
            started = True
            window_start = i + 1
        i += 1

    if not started:
        # Whole given dividend < divisor (e.g. 4 / 15): force a single "0"
        # quotient digit spanning all given digits, matching how a child
        # would read "0 remainder 4" rather than nothing at all.
        quotient_by_pos[len(digits) - 1] = "0"
        steps.append((0, len(digits) - 1, None, "0", 0, int("".join(digits))))
        remainder = int("".join(digits))

    if ending == "decimal" and remainder != 0:
        raise ValueError("division does not terminate within max_decimal_places")

    n = len(digits)
    if point_at is None and n > given_n:
        point_at = given_n  # decimal point introduced by synthesized continuation

    # If EVERY emitted quotient digit sits at/after the decimal point (the
    # window never closed anywhere in the integer part -- e.g. 10.2/34,
    # which only resolves once the "2" is folded in), the integer part
    # would render as a bare "." with nothing before it. Force a "0" in the
    # ones place, matching conventional "0.3" notation -- display-only, no
    # window actually closed there.
    if point_at is not None and point_at > 0 and all(p >= point_at for p in quotient_by_pos):
        quotient_by_pos[point_at - 1] = "0"

    suffix_cells: list[Cell] = []
    if remainder != 0 and ending == "remainder":
        suffix_cells = [Cell(f" R {remainder}", OPERATOR)]
    elif remainder != 0 and ending == "fraction":
        frac = Fraction(remainder, divisor_int)
        suffix_cells = [Cell(f" {frac.numerator}/{frac.denominator}", OPERATOR)]

    n_cols = divisor_width + 2 + n + (1 if point_at is not None else 0) + len(suffix_cells)

    def _at_point(cells: list[Cell], point_cell: Cell) -> list[Cell]:
        if point_at is None:
            return cells
        return cells[:point_at] + [point_cell] + cells[point_at:]

    def _region_row(digits_by_pos: dict[int, tuple[str, str]], point_cell: Cell) -> list[Cell]:
        """digits_by_pos maps position -> (text, kind)."""
        cells = [Cell(*digits_by_pos.get(i, ("", DIGIT))) for i in range(n)]
        return _at_point(cells, point_cell)

    # +2 (not +1) matches the header row's ") " bracket cell, which is 2
    # characters wide once rendered (a trailing space for readability) --
    # every other row's lead must be the SAME total width or its dividend
    # region drifts one column left of where the header row's actually is.
    blank_lead = [Cell("", BLANK)] * (divisor_width + 2)
    minus_lead = [Cell("", BLANK)] * (divisor_width - 1) + [Cell("−", OPERATOR)] + [Cell("", BLANK)] * 2

    # Bare quotient text (no "R n"/fraction suffix) -- used by the "Quotient
    # is..." annotation below, same reconstruction the reader (and the test
    # helper) uses: join DIGIT/POINT cells in column order, skipping blanks.
    quotient_only_row = _region_row(
        {i: (d, DIGIT) for i, d in quotient_by_pos.items()}, Cell(".", POINT)
    )
    quotient_str = "".join(c.text for c in quotient_only_row if c.text)

    quotient_annotation: list[list[Cell]] = []
    if ending == "remainder":
        quotient_annotation = [[Cell(
            f"  <-- Quotient is {quotient_str}, Remainder is {remainder}", OPERATOR
        )]]

    quotient_row = blank_lead + quotient_only_row + suffix_cells

    vinculum_row = blank_lead + _at_point([Cell("", LINE) for _ in range(n)], Cell("", BLANK))

    divisor_cells = [Cell(ch, DIGIT) for ch in divisor_str]
    dividend_by_pos = {i: (digits[i], DIGIT) for i in range(n)}
    # ")" not "|" -- a vertical bar risks looking identical to the digit "1"
    # in some monospace fonts (flagged by the maintainer), a real legibility
    # concern for a children's product where every digit must read unambiguously.
    header_row = divisor_cells + [Cell(") ", OPERATOR)] + _region_row(dividend_by_pos, Cell(".", POINT))

    rows: list[list[Cell]] = []
    if scale_pow > 0:
        # A decimal divisor was scaled to a whole number (multiply BOTH
        # operands by the same power of 10 -- the quotient is unchanged).
        # Without this line the reader sees the SCALED numbers (e.g. "11"
        # instead of the "1.1" they asked about) with no explanation of
        # where they came from (2026-07-24 maintainer-reported bug).
        multiplier = 10 ** scale_pow
        rows.append([Cell(
            f"{dividend_dec} ÷ {divisor_dec} = {scaled_dividend} ÷ {divisor_int} (x{multiplier} both sides)",
            OPERATOR,
        )])
    rows += [quotient_row] + quotient_annotation + [vinculum_row, header_row]
    prev_product, prev_window_value = None, None
    for display_start, display_end, bring_down_str, product_str, q_digit, window_value in steps:
        if bring_down_str is not None:
            bring_positions = {
                display_start + k: (c, DIGIT) for k, c in enumerate(bring_down_str)
            }
            new_digit = bring_down_str[-1]
            rows.append(blank_lead + _region_row(bring_positions, Cell("", BLANK)))
            rows.append([Cell(
                f"  <-- Middle Step: {prev_window_value} - {prev_product} = {prev_window_value - prev_product},"
                f" bring down {new_digit}",
                OPERATOR,
            )])
        product_by_pos = {
            display_end - len(product_str) + 1 + k: (c, DIGIT)
            for k, c in enumerate(product_str)
        }
        rows.append(minus_lead + _region_row(product_by_pos, Cell("", BLANK)))
        rows.append([Cell(f"  <-- Middle Step: {divisor_int} x {q_digit} = {product_str}", OPERATOR)])
        rows.append(blank_lead + _at_point(
            [Cell("", LINE) if display_start <= pos <= display_end else Cell("", BLANK) for pos in range(n)],
            Cell("", BLANK),
        ))
        prev_product, prev_window_value = int(product_str), window_value

    # Final leftover row: the raw remainder after the last step (0 for an
    # exact division, or the actual leftover for "remainder"/"fraction"
    # endings) -- natural width, no zero-padding, right-aligned at the last
    # digit position, same convention as every intermediate product row.
    final_str = str(remainder)
    final_by_pos = {
        n - len(final_str) + k: (c, DIGIT) for k, c in enumerate(final_str)
    }
    rows.append(blank_lead + _region_row(final_by_pos, Cell("", BLANK)))
    if ending == "remainder":
        rows.append([Cell(
            f"  <-- Remainder check: {remainder} is smaller than {divisor_int}, so it is correct.",
            OPERATOR,
        )])

    return StepGrid(rows=rows, n_cols=n_cols)
