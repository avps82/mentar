"""Australian-curriculum item generators — Year 3 and Year 4 mathematics.

Same contract as engine/itemgen.py: each generator returns
(answer_type, checker, problem, answer[, choices]) with a COMPUTED ground truth, so
the deterministic verifier scores every item and the LLM stays out of the
correctness path. mc4 generators return the structured `choices` 5th element
(A/B/C/D order) that drives the web radio buttons.

Curriculum alignment: node ids in curriculum/templates/AU_ACARA/*.md carry ACARA v9
content-description codes (e.g. AC9M3N01) as alignment REFERENCES only — all
question text, labels and fact tables here are Mentar-authored (ACARA core
content is CC BY 4.0; see docs/CONTENT_LICENSES.md).

Scope guard: answers stay inside the deterministic verifier's grammar
(int / fraction / decimal / mc4 / expression — verify_numeric.py's full grammar
as of B0, 2026-08-11). This docstring previously said "no decimals"; that was
stale even before this edit — AU5-8 generators below already use decimal
(R13 shipped it 2026-07-19) — corrected here while adding expression (Y9+).
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction

from mentar.engine.itemgen import (
    _gen_adding_equal_denom,
    _gen_equivalent_fractions,
    _gen_fraction_as_part_of_whole,
    _gen_unit_fractions,
    _gen_whole_number_division,
)

_LETTERS = "ABCD"


def _mc(problem_stem: str, options: list[str], correct_index: int,
        method_steps: tuple[str, ...] | None = None):
    """An mc4 tuple carrying the STEM (no inline "A) ..." options -- R2.1: the
    web view shows stem + radios; ItemGenerator._make composes the inline
    "A) ..." form centrally for CLI/transcript surfaces) + the structured
    choices list for the web radio buttons. `method_steps` (2026-08-13,
    explain-mode Type 2): optional computed method card, 6th tuple element."""
    return ("mc4", "mc_choice", problem_stem, _LETTERS[correct_index], options, method_steps)


_PLACE_NAMES = ("Ones", "Tens", "Hundreds", "Thousands", "Ten thousands")


def _place_value_table(number) -> tuple[str, ...]:
    """The place-value column table for THIS number.

    `curriculum/visual_scaffolds/maths/place_value.md` carries one of these with
    the digits 3|5|2 baked in. That file is an authoring instruction for the LLM
    ("use ONE of these visual structures"), so its numbers are placeholders --
    and folding it verbatim into a computed card showed a child asked about 463 a
    table reading 3|5|2 (maintainer, 2026-08-16: "WHERE did 352 come from??").
    The template was always meant to be filled with the question's own numbers;
    that step was never built.

    Built here, by the generator that HOLDS the number, for the same reason step
    grids are: the card is computed, so its picture must be computed too.
    Columns are width-matched because the card renders in a monospace <pre>.
    """
    digits = str(int(number))
    n = len(digits)
    if n > len(_PLACE_NAMES):
        return ()
    names = [_PLACE_NAMES[n - 1 - i] for i in range(n)]
    values = [f"({int(d) * 10 ** (n - 1 - i)})" for i, d in enumerate(digits)]
    widths = [max(len(names[i]), len(digits[i]), len(values[i])) for i in range(n)]

    def _row(cells: list[str]) -> str:
        return " | ".join(c.center(w) for c, w in zip(cells, widths, strict=True))

    return (_row(names), _row(list(digits)), _row(values))


def _decimal_place_value_table(number: str) -> tuple[str, ...]:
    """The place-value table for a decimal, built from THIS number.

    Same reason as _place_value_table: maths/decimals.md carries one of these
    with 3.42 baked in, which is a different number from whatever the item drew.
    """
    if "." not in str(number):
        return ()
    whole, frac = str(number).split(".", 1)
    names = [*(_PLACE_NAMES[len(whole) - 1 - i] for i in range(len(whole))), ".",
             *("Tenths", "Hundredths", "Thousandths")[: len(frac)]]
    cells = [*whole, ".", *frac]
    if len(names) != len(cells):
        return ()
    widths = [max(len(n), len(c)) for n, c in zip(names, cells, strict=True)]

    def _row(vals: list[str]) -> str:
        return "| " + " | ".join(v.center(w) for v, w in zip(vals, widths, strict=True)) + " |"

    return (_row(names), _row(cells), f"= {number}".rjust(len(_row(cells))))


def _place_value_card(number, digit: int, place_name: str, multiplier: int, correct: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-13, Phase 1 — docs/design/explain_mode_design.md
    §3 Type 2, place-value family). Generic over any place (tens/hundreds/
    thousands) via the caller-supplied place_name/multiplier -- no per-digit-
    count special-casing needed here."""
    return (
        "PLACE VALUE",
        f"In the number {number}, what is the value of the digit {digit}? → {correct}",
        f"  1. In {number}, the digit {digit} sits in the {place_name} place.",
        f"  2. The {place_name} place is worth ×{multiplier}, so {digit} × {multiplier} = {correct}.",
        f"  Answer: {correct}",
        # Blank line then the table for THIS number -- the picture the scaffold
        # was always meant to supply, with the question's own digits in it.
        "",
        *_place_value_table(number),
    )


# ── Year 3 (AC9M3N01, AC9M3N02, AC9M3N03, AC9M3N04 alignment) ─────────────────

def gen_place_value_3digit(rng: random.Random):
    """AC9M3N01-aligned: what a digit stands for in a 3-digit number. Only
    asks about the hundreds/tens digit -- the ones digit's "value" trivially
    equals itself (digit x 10^0), which tests nothing about place value and
    lets a child pattern-match the question text to the right answer without
    any reasoning (2026-07-19 maintainer feedback)."""
    digits = rng.sample(range(1, 10), 3)
    number = digits[0] * 100 + digits[1] * 10 + digits[2]
    pos = rng.randrange(2)                      # 0=hundreds, 1=tens (ones excluded)
    digit = digits[pos]
    correct = digit * (10 ** (2 - pos))
    options = [str(digit), str(digit * 10), str(digit * 100)]
    # A distinct 4th distractor: the whole number's other digit's value.
    other = digits[(pos + 1) % 3] * (10 ** (2 - ((pos + 1) % 3)))
    options.append(str(other) if str(other) not in options else str(digit * 1000))
    rng.shuffle(options)
    place_name = "hundreds" if pos == 0 else "tens"
    return _mc(
        f"In the number {number}, what is the value of the digit {digit}?",
        options, options.index(str(correct)),
        _place_value_card(number, digit, place_name, 10 ** (2 - pos), correct),
    )


def gen_add_within_1000(rng: random.Random):
    """AC9M3N02-aligned: addition within 1000."""
    a, b = rng.randint(100, 700), rng.randint(50, 299)
    return ("int", "int_exact", f"What is {a} + {b}?", str(a + b))


def gen_sub_within_1000(rng: random.Random):
    """AC9M3N02-aligned: subtraction within 1000 (positive result)."""
    a = rng.randint(200, 999)
    b = rng.randint(50, a - 50)
    return ("int", "int_exact", f"What is {a} − {b}?", str(a - b))


def gen_mult_facts_3_4_5_10(rng: random.Random):
    """AC9M3N03-aligned: multiplication facts for 3, 4, 5 and 10."""
    a = rng.choice([3, 4, 5, 10])
    b = rng.randint(2, 10)
    if rng.random() < 0.5:
        a, b = b, a
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


# ── Year 4 (AC9M4N01, AC9M4N03, AC9M4N05 alignment) ───────────────────────────

def gen_place_value_4digit(rng: random.Random):
    """AC9M4N01-aligned: what a digit stands for in a 4-digit number. Only
    asks about thousands/hundreds/tens digits -- the ones digit's "value"
    trivially equals itself, excluded for the same reason as the 3-digit
    generator (2026-07-19 maintainer feedback). The four options are the
    digit at each of the four places — always distinct (a value factors
    uniquely as digit × 10^p for digit 1-9)."""
    digits = rng.sample(range(1, 10), 4)
    number = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
    pos = rng.randrange(3)                      # 0=thousands,1=hundreds,2=tens (ones excluded)
    digit = digits[pos]
    correct = digit * (10 ** (3 - pos))
    options = [str(digit * (10 ** p)) for p in range(4)]
    rng.shuffle(options)
    place_name = ("thousands", "hundreds", "tens")[pos]
    return _mc(
        f"In the number {number}, what is the value of the digit {digit}?",
        options, options.index(str(correct)),
        _place_value_card(number, digit, place_name, 10 ** (3 - pos), correct),
    )


def gen_mult_facts_to_10x10(rng: random.Random):
    """AC9M4N05-aligned: multiplication facts to 10 × 10."""
    a, b = rng.randint(2, 10), rng.randint(2, 10)
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


def gen_division_facts(rng: random.Random):
    """AC9M4N05-aligned: division facts derived from the times tables."""
    b, q = rng.randint(2, 10), rng.randint(2, 10)
    a = b * q
    return ("int", "int_exact", f"What is {a} ÷ {b}?", str(q))


# ── Year 2 (AC9M2N01/N02/N03/N04 alignment) ───────────────────────────────────
# R14a, 2026-07-19. Scope note: no decimal content at Year 2 (too early); Year 5/6
# below are the pilot's first use of the R13 "decimal" answer type.

def gen_place_value_2digit(rng: random.Random):
    """AC9M2N01-aligned: identify the value of the TENS digit in a two-digit
    number. Always the tens digit, never the ones digit -- the ones digit's
    "value" trivially equals itself (digit x 10^0), which tests nothing about
    place value and lets a child pattern-match the question text to the right
    answer without any reasoning (2026-07-19 maintainer feedback: for "In the
    number 37, what is the value of the digit 7?" the mathematically correct
    answer IS 7 -- not a scoring bug -- but it's a degenerate question)."""
    digits = rng.sample(range(1, 10), 2)
    number = digits[0] * 10 + digits[1]
    digit = digits[0]
    correct = digit * 10
    options = [str(digits[0]), str(digits[1]), str(digits[0] * 10), str(digits[1] * 10)]
    rng.shuffle(options)
    return _mc(
        f"In the number {number}, what is the value of the digit {digit}?",
        options, options.index(str(correct)),
        _place_value_card(number, digit, "tens", 10, correct),
    )


def gen_add_within_100(rng: random.Random):
    """AC9M2N02-aligned: addition of two numbers, sum under 100."""
    a = rng.randint(10, 50)
    b = rng.randint(10, 49)
    return ("int", "int_exact", f"What is {a} + {b}?", str(a + b))


def gen_sub_within_100(rng: random.Random):
    """AC9M2N02-aligned: subtraction within 100, positive result."""
    a = rng.randint(20, 99)
    b = rng.randint(1, a - 1)
    return ("int", "int_exact", f"What is {a} − {b}?", str(a - b))


def gen_mult_facts_2_5_10(rng: random.Random):
    """AC9M2N03-aligned: multiplication facts for 2, 5 and 10."""
    a = rng.choice([2, 5, 10])
    b = rng.randint(2, 10)
    if rng.random() < 0.5:
        a, b = b, a
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


def gen_halves_quarters(rng: random.Random):
    """AC9M2N04-aligned: halves and quarters of a whole (denominator restricted
    to {2, 4} -- Year 3+ introduces the fuller unit-fraction range)."""
    d = rng.choice([2, 4])
    card = (
        "UNIT FRACTIONS",
        f"A pizza is cut into {d} equal slices. What fraction is ONE slice? → 1/{d}",
        f"  1. The whole pizza is split into {d} equal slices.",
        f"  2. ONE slice out of {d} equal slices is written as 1/{d}.",
        f"  Answer: 1/{d}",
    )
    return (
        "fraction", "fraction_equiv",
        f"A pizza is cut into {d} equal slices. What fraction is ONE slice?", f"1/{d}", None, card,
    )


# ── Year 5 (AC9M5N01/N02/N06 alignment) ───────────────────────────────────────
# Decimal generators use decimal.Decimal exclusively, never float -- avoids
# binary float precision artifacts (e.g. "3.4000000000000004").

def _one_dp(tenths: int) -> Decimal:
    """A one-decimal-place Decimal built from an integer count of tenths, e.g.
    _one_dp(40) -> Decimal('4.0'). NOT Decimal(tenths) / 10 -- division silently
    drops the trailing zero on an exact result (Decimal(40) / 10 == Decimal('4'),
    not '4.0'), which reads oddly next to a genuinely one-decimal-place sibling
    value in the same question."""
    return Decimal(f"{tenths // 10}.{tenths % 10}")

def gen_decimal_place_value(rng: random.Random):
    """AC9M5N01-aligned: identify the place value of the tenths digit."""
    whole = rng.randint(1, 9)
    tenths = rng.randint(1, 9)
    number = f"{whole}.{tenths}"
    options = [f"{tenths} ones", f"{tenths} tenths", f"{tenths} hundredths", f"{tenths} tens"]
    correct = f"{tenths} tenths"
    rng.shuffle(options)
    card = (
        "DECIMAL PLACE VALUE",
        f"In {number}, what does the {tenths} represent? → {correct}",
        "  1. Straight after the decimal point is the TENTHS place.",
        f"  2. The digit {tenths} sits right after the point, so it represents {correct}.",
        f"  Answer: {correct}",
        # The table for THIS number -- see _decimal_place_value_table.
        "",
        *_decimal_place_value_table(number),
    )
    return _mc(f"In {number}, what does the {tenths} represent?", options, options.index(correct), card)


def gen_add_sub_decimals(rng: random.Random):
    """AC9M5N02-aligned: adding/subtracting decimals to one decimal place.
    Subtraction bounds guarantee a positive result by construction."""
    if rng.random() < 0.5:
        a = _one_dp(rng.randint(10, 89))
        b = _one_dp(rng.randint(10, 89))
        return ("decimal", "decimal_exact", f"What is {a} + {b}?", str(a + b))
    a_tenths = rng.randint(20, 99)
    b_tenths = rng.randint(10, a_tenths - 10)
    a, b = _one_dp(a_tenths), _one_dp(b_tenths)
    return ("decimal", "decimal_exact", f"What is {a} - {b}?", str(a - b))


def gen_mult_fraction_whole(rng: random.Random):
    """AC9M5N06-aligned: multiplying a proper fraction by a whole number.
    Result is left unreduced -- fraction_equiv accepts any equivalent form."""
    n = rng.randint(1, 4)
    d = rng.randint(n + 1, 10)
    whole = rng.randint(2, 5)
    new_n = n * whole
    card = (
        "MULTIPLYING A FRACTION BY A WHOLE NUMBER",
        f"What is {n}/{d} × {whole}? → {new_n}/{d}",
        f"  1. Multiply the numerator by the whole number: {n} × {whole} = {new_n}.",
        f"  2. Keep the denominator the same: {d}.",
        f"  3. So {n}/{d} × {whole} = {new_n}/{d}.",
        f"  Answer: {new_n}/{d}",
    )
    return ("fraction", "fraction_equiv", f"What is {n}/{d} × {whole}?", f"{new_n}/{d}", None, card)


def _percentage_of_quantity_card(pct: int, quantity: int, answer: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-12, Phase 0 pilot — docs/design/explain_mode_design.md
    §3 Type 2): the maintainer's own failing example ("What is 50% of 64?") as the
    acceptance test. Uses the GENERAL definition of percent (x out of 100) rather
    than per-value tricks (halves/quarters) -- fewer special cases to author and
    review, correct for every pct/quantity this or any future percent-of generator
    draws, and self-validating: the final line's number is `answer`, checked
    against the item's own ground truth by a pytest fixture, not eyeballed."""
    product = quantity * pct
    return (
        "PERCENTAGE OF A QUANTITY",
        f"What is {pct}% of {quantity}? → {answer}",
        f'  1. "{pct}%" means {pct} out of every 100.',
        f"  2. So {pct}% of {quantity} = {quantity} × {pct} ÷ 100.",
        f"  3. {quantity} × {pct} = {product}, and {product} ÷ 100 = {answer}.",
        f"  Answer: {answer}",
        "",
        *_percent_grid(pct),
    )


def _percent_grid(pct: int) -> tuple[str, ...]:
    """A 10x10 hundred-grid with `pct` cells shaded -- the picture for THIS
    percentage.

    maths/percentages.md carries this shape with 20% baked in. A hundred-grid is
    the whole point of the concept ("per cent" = per hundred), so the shaded
    count must be the item's own.
    """
    if not 0 <= pct <= 100:
        return ()
    rows = []
    for r in range(10):
        row = "".join("█" if r * 10 + c < pct else "□" for c in range(10))
        rows.append(row)
    return (*rows, f"{pct} of 100 squares shaded = {pct}%")


def gen_percentage_of_quantity(rng: random.Random):
    """AC9M5N02-aligned: a percentage of a quantity, constructed so it always
    divides exactly (no rounding decisions needed)."""
    pct = rng.choice([10, 25, 50, 75])
    if pct == 10:
        quantity = rng.randint(1, 20) * 10
    elif pct == 50:
        quantity = rng.randint(1, 50) * 2
    else:
        quantity = rng.randint(1, 20) * 4
    answer = quantity * pct // 100
    return (
        "int", "int_exact", f"What is {pct}% of {quantity}?", str(answer), None,
        _percentage_of_quantity_card(pct, quantity, answer),
    )


def gen_negative_numbers(rng: random.Random):
    """AC9M5N01-aligned: negative numbers via a temperature-drop context."""
    temp = rng.randint(-2, 8)
    drop = rng.randint(5, 15)
    answer = temp - drop
    card = (
        "NEGATIVE NUMBERS",
        f"The temperature was {temp}°C and dropped by {drop}°C. What is the new temperature? → {answer}°C",
        f"  1. Dropping means going DOWN, so subtract: {temp} − {drop}.",
        f"  2. {temp} − {drop} = {answer} (past zero and into negative numbers)." if answer < 0
        else f"  2. {temp} − {drop} = {answer}.",
        f"  Answer: {answer}°C",
    )
    return (
        "int", "int_exact",
        f"The temperature was {temp}°C and dropped by {drop}°C. What is the new temperature?",
        str(answer), None, card,
    )


def gen_division_remainder_as_fraction(rng: random.Random):
    """AC9M5N05-adjacent: whole-number division that does NOT divide evenly
    -- the leftover expressed as a reduced mixed number (e.g. "28 4/5").
    Divisor and remainder are constructed directly (remainder always
    1..divisor-1, guaranteed nonzero) so `build_long_division_steps`'s
    ending="fraction" always has something to reduce; dividend is built
    FROM quotient/divisor/remainder, same "computed ground truth" posture
    as every other generator here."""
    divisor = rng.randint(2, 20)
    quotient = rng.randint(10, 40)
    remainder = rng.randint(1, divisor - 1)
    dividend = quotient * divisor + remainder
    frac = Fraction(remainder, divisor)
    answer = f"{quotient} {frac.numerator}/{frac.denominator}"
    return ("fraction", "fraction_equiv", f"What is {dividend} ÷ {divisor}?", answer)


def gen_division_remainder_as_decimal(rng: random.Random):
    """Whole-number division that does NOT divide evenly, but the decimal
    quotient terminates within a couple of places -- divisor restricted to
    values whose only prime factors are 2 and 5, so long division into
    decimals always terminates (matches what
    `build_long_division_steps`'s ending="decimal" can actually render --
    it raises rather than guess at a repeating decimal)."""
    divisor = rng.choice([2, 4, 5, 8, 10, 16, 20, 25])
    quotient = rng.randint(10, 40)
    remainder = rng.randint(1, divisor - 1)
    dividend = quotient * divisor + remainder
    answer = str(Decimal(dividend) / Decimal(divisor))
    return ("decimal", "decimal_exact", f"What is {dividend} ÷ {divisor}?", answer)


# ── Year 6 (AC9M6N01/N02/N03/M01 alignment) ───────────────────────────────────

def _order_of_ops_card(a: int, op_low: str, high_expr: str, high_val: int, result: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-13, Phase 1): shared by gen_order_of_operations and
    gen_order_of_ops_negatives, which are identical past `a`'s sign range --
    one card builder, no duplication."""
    return (
        "ORDER OF OPERATIONS",
        f"What is {a} {op_low} {high_expr}? → {result}",
        "  1. Multiplication and division come BEFORE addition and subtraction.",
        f"  2. Work out {high_expr} = {high_val} first.",
        f"  3. Then {a} {op_low} {high_val} = {result}.",
        f"  Answer: {result}",
    )


def gen_order_of_operations(rng: random.Random):
    """AC9M6N01-aligned: a two-term expression where the higher-precedence
    operator (×/÷) is evaluated before the lower one (+/−)."""
    op_low = rng.choice(["+", "-"])
    a = rng.randint(20, 60)
    if rng.random() < 0.5:
        b, c = rng.randint(2, 9), rng.randint(2, 9)
        high_val = b * c
        high_expr = f"{b} × {c}"
    else:
        c = rng.randint(2, 9)
        q = rng.randint(2, 9)
        b = c * q
        high_val = q
        high_expr = f"{b} ÷ {c}"
    result = a + high_val if op_low == "+" else a - high_val
    expr = f"{a} {op_low} {high_expr}"
    return ("int", "int_exact", f"What is {expr}?", str(result), None,
             _order_of_ops_card(a, op_low, high_expr, high_val, result))


def gen_mult_decimals(rng: random.Random):
    """AC9M6N02-aligned: a one-decimal-place value times a whole number."""
    a = _one_dp(rng.randint(10, 50))
    b = rng.randint(2, 9)
    return ("decimal", "decimal_exact", f"What is {a} × {b}?", str(a * b))


def gen_div_decimals(rng: random.Random):
    """AC9M6N02-aligned: the dividend is constructed FROM a clean quotient, so
    the division is always exact -- never a repeating/rounded result."""
    quotient = _one_dp(rng.randint(10, 50))
    divisor = rng.randint(2, 9)
    dividend = quotient * divisor
    return ("decimal", "decimal_exact", f"What is {dividend} ÷ {divisor}?", str(quotient))


def _rectangle_diagram(length: int, width: int, unit: str = "cm") -> tuple[str, ...]:
    """A rectangle drawn to THIS item's dimensions, labelled on two sides.

    maths/area_perimeter.md carries this shape with a fixed 4cm side. Scaled 2
    characters per unit of length and one line per unit of width, so the picture
    is proportional to the numbers the child is working with -- a 12x2 rectangle
    should look long and thin, not square. Capped for the generator's ranges
    (length 3-12, width 2-10), which stays inside a phone's monospace width.
    """
    if not (1 <= length <= 14 and 1 <= width <= 12):
        return ()
    inner = length * 2
    top = "┌" + "─" * inner + "┐"
    bottom = "└" + "─" * inner + "┘"
    rows = []
    for i in range(width):
        label = f"  {width} {unit}" if i == width // 2 else ""
        rows.append("│" + " " * inner + "│" + label)
    base = f"{length} {unit}".center(inner + 2)
    return (top, *rows, bottom, base)


def gen_area_perimeter(rng: random.Random):
    """AC9M6M01-aligned: area or perimeter of a rectangle, chosen at random."""
    length = rng.randint(3, 12)
    width = rng.randint(2, 10)
    if rng.random() < 0.5:
        area = length * width
        card = (
            "AREA OF A RECTANGLE",
            f"A rectangle is {length}cm by {width}cm. What is its area, in square centimetres? → {area}",
            "  1. Area of a rectangle = length × width.",
            f"  2. {length} × {width} = {area}.",
            f"  Answer: {area}",
            "",
            *_rectangle_diagram(length, width),
        )
        return (
            "int", "int_exact",
            f"A rectangle is {length}cm by {width}cm. What is its area, in square centimetres?",
            str(area), None, card,
        )
    total = length + width
    perimeter = 2 * total
    card = (
        "PERIMETER OF A RECTANGLE",
        f"A rectangle is {length}cm by {width}cm. What is its perimeter, in centimetres? → {perimeter}",
        "  1. Perimeter of a rectangle = 2 × (length + width).",
        f"  2. 2 × ({length} + {width}) = 2 × {total} = {perimeter}.",
        f"  Answer: {perimeter}",
        "",
        *_rectangle_diagram(length, width),
    )
    return (
        "int", "int_exact",
        f"A rectangle is {length}cm by {width}cm. What is its perimeter, in centimetres?",
        str(perimeter), None, card,
    )


# Curated, hand-verified fact table -- every pair terminates cleanly as a
# decimal, so this node is a lookup, not a computed conversion (removes any
# division-precision risk entirely).
_FRACTION_DECIMAL_PAIRS = [
    ("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"),
    ("1/5", "0.2"), ("2/5", "0.4"), ("3/5", "0.6"), ("4/5", "0.8"),
    ("1/10", "0.1"), ("3/10", "0.3"), ("7/10", "0.7"),
    ("1/20", "0.05"), ("3/20", "0.15"),
]


def gen_fraction_decimal_equiv(rng: random.Random):
    """AC9M6N03-aligned: convert a common fraction to its decimal equivalent.

    explain-mode (2026-08-13, Phase 1): the card shows real division (n ÷ d)
    as the method even though the generator itself is a lookup table -- n/d
    genuinely DOES equal n÷d regardless of implementation, and every pair in
    _FRACTION_DECIMAL_PAIRS is picked specifically because that division
    terminates cleanly (see the table's own comment), so the shown method
    always matches the looked-up answer. (`gen_division_remainder_as_fraction`/
    `_decimal`, the other two generators in this "conversions" family, are
    already Type 1 -- their problem text is written to feed
    build_long_division_steps on Explain-more, so a method card there would
    never be shown; deliberately not migrated.)"""
    frac, dec = rng.choice(_FRACTION_DECIMAL_PAIRS)
    n, d = frac.split("/")
    card = (
        "FRACTIONS AS DECIMALS",
        f"Write {frac} as a decimal. → {dec}",
        f"  1. {frac} means {n} divided by {d}.",
        f"  2. {n} ÷ {d} = {dec}.",
        f"  Answer: {dec}",
    )
    return ("decimal", "decimal_exact", f"Write {frac} as a decimal.", dec, None, card)


# ── Year 7 (AC9M7N/A alignment) ───────────────────────────────────────────────
# R15, 2026-07-19.

def _integer_op_card(a: int, b: int, op: str, answer: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-13, Phase 1): generic over both operators and
    all four sign combinations -- "moving along the number line" is the ONE
    rule that covers +/− with any sign of a/b, so no per-combo special
    wording is needed beyond which direction/distance it names."""
    if op == "+":
        rule = (f"Adding a positive number moves you UP the number line by {b}." if b >= 0
                 else f"Adding a negative number moves you DOWN the number line by {abs(b)} "
                      f"(same as subtracting {abs(b)}).")
    else:
        rule = (f"Subtracting a positive number moves you DOWN the number line by {b}." if b >= 0
                 else f"Subtracting a negative number moves you UP the number line by {abs(b)} "
                      f"(same as adding {abs(b)}).")
    return (
        "ADDING AND SUBTRACTING INTEGERS",
        f"What is {a} {op} {b}? → {answer}",
        f"  1. Start at {a} on the number line.",
        f"  2. {rule}",
        f"  Answer: {answer}",
    )


def gen_integers_add_sub(rng: random.Random):
    """AC9M7N01-aligned: add or subtract two integers, either may be negative."""
    a = rng.randint(-15, 15)
    b = rng.randint(-15, 15)
    if rng.random() < 0.5:
        answer = a + b
        return ("int", "int_exact", f"What is {a} + {b}?", str(answer), None,
                 _integer_op_card(a, b, "+", answer))
    answer = a - b
    return ("int", "int_exact", f"What is {a} - {b}?", str(answer), None,
             _integer_op_card(a, b, "-", answer))


def gen_order_of_ops_negatives(rng: random.Random):
    """AC9M7N01-aligned: order of operations where the leading term may be negative."""
    op_low = rng.choice(["+", "-"])
    a = rng.randint(-20, 20)
    if rng.random() < 0.5:
        b, c = rng.randint(2, 9), rng.randint(2, 9)
        high_val = b * c
        high_expr = f"{b} × {c}"
    else:
        c = rng.randint(2, 9)
        q = rng.randint(2, 9)
        b = c * q
        high_val = q
        high_expr = f"{b} ÷ {c}"
    result = a + high_val if op_low == "+" else a - high_val
    expr = f"{a} {op_low} {high_expr}"
    return ("int", "int_exact", f"What is {expr}?", str(result), None,
             _order_of_ops_card(a, op_low, high_expr, high_val, result))


def _unlike_denom_fraction_card(n1: int, d1: int, n2: int, d2: int, result: Fraction) -> tuple[str, ...]:
    """Explain-mode (2026-08-13, Phase 1): cross-multiplication common
    denominator (d1 × d2 -- always a valid common denominator, whether or
    not it's the LOWEST one), then a simplify step ONLY when the raw
    cross-multiplied sum differs from `result` (already reduced by
    fractions.Fraction) -- self-validating either way, since the final
    line is always `result` itself, never re-derived separately."""
    common = d1 * d2
    over1, over2 = n1 * d2, n2 * d1
    raw_num = over1 + over2
    lines = [
        "ADDING FRACTIONS WITH DIFFERENT DENOMINATORS",
        f"What is {n1}/{d1} + {n2}/{d2}? → {result.numerator}/{result.denominator}",
        f"  1. Find a common denominator: {d1} × {d2} = {common}.",
        f"  2. Rewrite each fraction over {common}: {n1}/{d1} = {over1}/{common}, "
        f"and {n2}/{d2} = {over2}/{common}.",
        f"  3. Add the numerators: {over1}/{common} + {over2}/{common} = {raw_num}/{common}.",
    ]
    if (raw_num, common) != (result.numerator, result.denominator):
        lines.append(f"  4. Simplify: {raw_num}/{common} = {result.numerator}/{result.denominator}.")
    lines.append(f"  Answer: {result.numerator}/{result.denominator}")
    return tuple(lines)


def gen_unlike_denom_fractions(rng: random.Random):
    """AC9M7N04-aligned: adding two fractions with different denominators.
    fractions.Fraction reduces automatically -- the answer is always canonical."""
    n1, d1 = rng.randint(1, 4), rng.randint(2, 6)
    n2, d2 = rng.randint(1, 4), rng.randint(2, 6)
    result = Fraction(n1, d1) + Fraction(n2, d2)
    return (
        "fraction", "fraction_equiv", f"What is {n1}/{d1} + {n2}/{d2}?",
        f"{result.numerator}/{result.denominator}", None,
        _unlike_denom_fraction_card(n1, d1, n2, d2, result),
    )


def gen_one_step_equations(rng: random.Random):
    """AC9M7A02-aligned: solving a one-step linear equation for x."""
    a = rng.randint(1, 20)
    x_true = rng.randint(1, 20)
    b = x_true + a
    card = (
        "SOLVING A ONE-STEP EQUATION",
        f"If x + {a} = {b}, what is x? → {x_true}",
        f'  1. To get x alone, undo the "+ {a}" by subtracting {a} from BOTH sides.',
        f"  2. x + {a} − {a} = {b} − {a}, so x = {x_true}.",
        f"  Answer: {x_true}",
    )
    return ("int", "int_exact", f"If x + {a} = {b}, what is x?", str(x_true), None, card)


def gen_mult_decimal_by_decimal(rng: random.Random):
    """AC9M7N06-aligned: multiplying two one-decimal-place numbers."""
    a = _one_dp(rng.randint(10, 50))
    b = _one_dp(rng.randint(10, 50))
    return ("decimal", "decimal_exact", f"What is {a} × {b}?", str(a * b))


# ── Year 8 (AC9M8N/A alignment) ───────────────────────────────────────────────

def gen_two_step_equations(rng: random.Random):
    """AC9M8A02-aligned: solving a two-step linear equation for x."""
    x_true = rng.randint(1, 15)
    coef = rng.randint(2, 5)
    a = rng.randint(1, 20)
    b = coef * x_true + a
    after_subtract = b - a
    card = (
        "SOLVING A TWO-STEP EQUATION",
        f"If {coef}x + {a} = {b}, what is x? → {x_true}",
        f'  1. First undo the "+ {a}": subtract {a} from BOTH sides. '
        f"{coef}x = {b} − {a} = {after_subtract}.",
        f'  2. Then undo the "× {coef}": divide BOTH sides by {coef}. '
        f"x = {after_subtract} ÷ {coef} = {x_true}.",
        f"  Answer: {x_true}",
    )
    return ("int", "int_exact", f"If {coef}x + {a} = {b}, what is x?", str(x_true), None, card)


def _square_array(n: int) -> tuple[str, ...]:
    """An n x n array of cells -- what "squared" actually means, drawn for THIS n.

    maths/squares_roots.md carries this with 4 baked in. The picture is the whole
    argument the card makes in words ("multiply by ITSELF, not by 2"): a child
    who sees 6 rows of 6 cannot read 6² as 12. Skipped above 12 so the block
    stays inside a phone's screen; the generator draws up to 15.
    """
    if not 1 <= n <= 12:
        return ()
    return (*("□" * n for _ in range(n)), f"{n} rows of {n} = {n * n}")


def gen_squares(rng: random.Random):
    """AC9M8N01-aligned: squaring a small integer."""
    n = rng.randint(2, 15)
    problem = f"What is {n} squared ({n}²)?"
    card = (
        "SQUARING A NUMBER",
        f"{problem} → {n * n}",
        "  1. \"Squared\" means multiply the number by ITSELF, not by 2.",
        f"  2. {n}² = {n} × {n} = {n * n}.",
        f"  ({n} × 2 = {n * 2} is doubling — a different thing.)",
        f"  Answer: {n * n}",
        "",
        *_square_array(n),
    )
    return ("int", "int_exact", problem, str(n * n), None, card)


def _negative_multiplication_card(a: int, b: int, answer: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-13, Phase 1): the sign rule stated first (matching
    the maintainer's own precedent for the step-grid's signed multiplication
    phase — "sign rule stated first, zero handled explicitly"), then the
    unsigned computation."""
    same_sign = (a < 0) == (b < 0)
    sign_word = "the SAME sign" if same_sign else "DIFFERENT signs"
    result_word = "positive" if same_sign else "negative"
    return (
        "MULTIPLYING NEGATIVE NUMBERS",
        f"What is {a} × {b}? → {answer}",
        "  1. Sign rule: same signs make a positive answer, different signs make a negative answer.",
        f"  2. {a} and {b} have {sign_word}, so the answer is {result_word}.",
        f"  3. {abs(a)} × {abs(b)} = {abs(a) * abs(b)}, so {a} × {b} = {answer}.",
        f"  Answer: {answer}",
    )


def gen_negative_multiplication(rng: random.Random):
    """AC9M8N01-aligned: multiplying two integers, either sign."""
    a = rng.choice([-1, 1]) * rng.randint(2, 12)
    b = rng.choice([-1, 1]) * rng.randint(2, 12)
    answer = a * b
    return ("int", "int_exact", f"What is {a} × {b}?", str(answer), None,
             _negative_multiplication_card(a, b, answer))


def _percentage_change_card(base: int, pct: int, increase: int, new_val: int) -> tuple[str, ...]:
    """Explain-mode (2026-08-12, Phase 0): same "percent = x out of 100" general
    definition as _percentage_of_quantity_card, plus the one extra step this
    shape needs -- add the increase back onto the original."""
    return (
        "PERCENTAGE INCREASE",
        f"A price of ${base} increases by {pct}%. What is the new price? → ${new_val}",
        f"  1. Find {pct}% of ${base}: {base} × {pct} ÷ 100 = {increase}.",
        f"  2. \"Increases by\" means add that on: ${base} + ${increase} = ${new_val}.",
        f"  Answer: ${new_val}",
    )


def gen_percentage_change(rng: random.Random):
    """AC9M8N03-aligned: a percentage increase, constructed to be exact."""
    base = rng.randint(1, 20) * 10
    pct = rng.choice([10, 20, 50])
    increase = base * pct // 100
    new_val = base + increase
    return (
        "int", "int_exact",
        f"A price of ${base} increases by {pct}%. What is the new price?", str(new_val), None,
        _percentage_change_card(base, pct, increase, new_val),
    )


def gen_div_decimal_by_decimal(rng: random.Random):
    """AC9M8N05-aligned: dividend constructed FROM a clean quotient, so the
    division of one decimal by another is always exact."""
    quotient = _one_dp(rng.randint(10, 50))
    divisor = _one_dp(rng.randint(10, 50))
    dividend = quotient * divisor
    return ("decimal", "decimal_exact", f"What is {dividend} ÷ {divisor}?", str(quotient))


# ── Registries (node_id -> generator) ─────────────────────────────────────────
# Fraction nodes reuse the pilot's verified generator functions — identical maths,
# ACARA-aligned node ids.

AU_YEAR3_GENERATORS = {
    "au3_place_value": gen_place_value_3digit,          # AC9M3N01
    "au3_addition": gen_add_within_1000,                # AC9M3N02
    "au3_subtraction": gen_sub_within_1000,             # AC9M3N02
    "au3_mult_facts": gen_mult_facts_3_4_5_10,          # AC9M3N03
    "au3_unit_fractions": _gen_unit_fractions,          # AC9M3N04
    "au3_fraction_of_whole": _gen_fraction_as_part_of_whole,  # AC9M3N04
}

AU_YEAR4_GENERATORS = {
    "au4_place_value": gen_place_value_4digit,          # AC9M4N01
    "au4_mult_facts": gen_mult_facts_to_10x10,          # AC9M4N05
    "au4_division_facts": gen_division_facts,           # AC9M4N05
    "au4_sharing_division": _gen_whole_number_division,  # AC9M4N05 (word problems)
    "au4_equivalent_fractions": _gen_equivalent_fractions,  # AC9M4N03
    "au4_adding_fractions": _gen_adding_equal_denom,    # AC9M4N04 (same-denominator)
}

AU_YEAR2_GENERATORS = {
    "au2_place_value": gen_place_value_2digit,          # AC9M2N01
    "au2_addition": gen_add_within_100,                 # AC9M2N02
    "au2_subtraction": gen_sub_within_100,              # AC9M2N02
    "au2_mult_facts_2_5_10": gen_mult_facts_2_5_10,     # AC9M2N03
    "au2_halves_quarters": gen_halves_quarters,         # AC9M2N04
}

AU_YEAR5_GENERATORS = {
    "au5_decimal_place_value": gen_decimal_place_value,        # AC9M5N01
    "au5_add_sub_decimals": gen_add_sub_decimals,               # AC9M5N02
    "au5_mult_fraction_whole": gen_mult_fraction_whole,         # AC9M5N06
    "au5_percentage_of_quantity": gen_percentage_of_quantity,   # AC9M5N02
    "au5_negative_numbers": gen_negative_numbers,               # AC9M5N01
    "au5_division_remainder_as_fraction": gen_division_remainder_as_fraction,  # AC9M5N05
    "au5_division_remainder_as_decimal": gen_division_remainder_as_decimal,    # AC9M5N05
}

AU_YEAR6_GENERATORS = {
    "au6_order_of_operations": gen_order_of_operations,         # AC9M6N01
    "au6_mult_decimals": gen_mult_decimals,                     # AC9M6N02
    "au6_div_decimals": gen_div_decimals,                       # AC9M6N02
    "au6_area_perimeter": gen_area_perimeter,                   # AC9M6M01
    "au6_fraction_decimal_equiv": gen_fraction_decimal_equiv,   # AC9M6N03
}

AU_YEAR7_GENERATORS = {
    "au7_integers_add_sub": gen_integers_add_sub,                # AC9M7N01
    "au7_order_of_ops_negatives": gen_order_of_ops_negatives,    # AC9M7N01
    "au7_unlike_denom_fractions": gen_unlike_denom_fractions,    # AC9M7N04
    "au7_one_step_equations": gen_one_step_equations,            # AC9M7A02
    "au7_mult_decimal_by_decimal": gen_mult_decimal_by_decimal,  # AC9M7N06
}

AU_YEAR8_GENERATORS = {
    "au8_two_step_equations": gen_two_step_equations,            # AC9M8A02
    "au8_squares": gen_squares,                                  # AC9M8N01
    "au8_negative_multiplication": gen_negative_multiplication,  # AC9M8N01
    "au8_percentage_change": gen_percentage_change,              # AC9M8N03
    "au8_div_decimal_by_decimal": gen_div_decimal_by_decimal,    # AC9M8N05
}

# ── Year 9 (AC9M9A02 alignment) — first answer_type="expression" content ──
#
# B0 (2026-08-11) added a sympy-backed expression_equiv checker: PASS iff
# simplify(candidate - truth) == 0, so 2(x+3) scores equal to 2x+6. That
# equivalence is exactly right for "does this expression describe the same
# relationship" — and exactly WRONG for "did you perform the named operation":
# a task phrased "Expand 3(x+4)" would let the unexpanded original itself
# pass (it IS equivalent to the expanded form), so it never verifies the work
# was actually done. Every generator below is deliberately phrased so the
# answer must be DERIVED from a setup the prompt does not hand over in
# algebraically-equivalent form (a word phrase, or two separate expressions
# to combine) — retyping the prompt's own text can never equal the answer.
# "Expand X" / "factorise X" / "simplify X" single-expression-transform tasks
# are NOT safe for this checker and are deliberately not attempted here.

def _linear_expr(coef: int, const: int, var: str) -> str:
    """Format `coef*var + const` the way a child would WRITE it, so the shown
    ground truth never reads "6*x + 0" (2026-08-12 content review). The verifier
    is expression_equiv so "6*x + 0" would still score, but it's the answer the
    child sees, and a dangling "+ 0" teaches a sloppy habit. Drops a zero
    constant and renders a negative constant as "- n" rather than "+ -n"."""
    if coef == 1:
        term = var
    elif coef == -1:
        term = f"-{var}"
    else:
        term = f"{coef}*{var}"
    if const == 0:
        return term
    return f"{term} + {const}" if const > 0 else f"{term} - {abs(const)}"


def gen_word_to_expression(rng: random.Random):
    """"Three more than twice a number n" -> "2n + 3". Forces translation from
    words, not transformation of an already-algebraic prompt."""
    coef = rng.randint(2, 6)
    const = rng.randint(1, 10)
    var = rng.choice("nxy")
    templates = [
        (f"{const} more than {coef} times a number {var}", f"{coef}*{var} + {const}",
         (f'  1. "{coef} times a number {var}" means {coef} × {var}, written {coef}{var}.',
          f'  2. "{const} more than" means add {const}: {coef}{var} + {const}.')),
        (f"{coef} times a number {var}, minus {const}", f"{coef}*{var} - {const}",
         (f'  1. "{coef} times a number {var}" means {coef} × {var}, written {coef}{var}.',
          f'  2. "minus {const}" means subtract {const}: {coef}{var} - {const}.')),
    ]
    phrase, expr, steps = rng.choice(templates)
    card = ("WRITING EXPRESSIONS FROM WORDS",
            f"Write an algebraic expression for: {phrase}. → {expr}", *steps, f"  Answer: {expr}")
    return ("expression", "expression_equiv",
            f"Write an algebraic expression for: {phrase}.", expr, None, card)


def gen_combine_expressions(rng: random.Random):
    """Given a = Ax+B, b = Cx+D, what is a + b? Forces real combination -- the
    prompt never states the answer's own algebraic form."""
    var = rng.choice("xy")
    a1, a0 = rng.randint(2, 8), rng.randint(1, 9)
    b1, b0 = rng.randint(2, 8), rng.randint(1, 9)
    sum1, sum0 = a1 + b1, a0 + b0
    answer = f"{sum1}*{var} + {sum0}"
    card = (
        "COMBINING LIKE TERMS",
        f"If a = {a1}{var} + {a0} and b = {b1}{var} + {b0}, what is a + b? → {answer}",
        f"  1. Add the {var}-terms together: {a1}{var} + {b1}{var} = {sum1}{var}.",
        f"  2. Add the number terms together: {a0} + {b0} = {sum0}.",
        f"  3. So a + b = {answer}.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv",
            f"If a = {a1}{var} + {a0} and b = {b1}{var} + {b0}, what is a + b? "
            "Give your answer as a simplified expression.",
            answer, None, card)


def _labelled_rectangle(width_label: str, length_label: str) -> tuple[str, ...]:
    """A rectangle labelled with EXPRESSIONS rather than measurements.

    maths/algebraic_area_perimeter.md carries "width = x / length = x + 4" as a
    text pair with 4 baked in. These questions describe a shape in WORDS only --
    the child never sees one -- so the picture is doing real work here: it is
    what turns "width x, length (x + n)" into something you can count sides on.
    Fixed proportions, because x has no size.
    """
    inner = max(len(length_label) + 4, 14)
    return (
        "┌" + "─" * inner + "┐",
        "│" + " " * inner + "│",
        "│" + " " * inner + "│  " + width_label,
        "│" + " " * inner + "│",
        "└" + "─" * inner + "┘",
        length_label.center(inner + 2),
    )


def gen_rectangle_perimeter_expression(rng: random.Random):
    """Width x, length x+n -> simplified perimeter expression. The setup is a
    WORD description of a shape, not an expression the child could just echo."""
    n = rng.randint(1, 9)
    doubled_n = 2 * n
    answer = f"4*x + {doubled_n}"
    card = (
        "PERIMETER AS AN EXPRESSION",
        f"A rectangle has width x and length (x + {n}). "
        f"Write a simplified expression for its perimeter. → {answer}",
        f"  1. Perimeter = 2 × (width + length) = 2 × (x + (x + {n})).",
        f"  2. Add width and length first: x + (x + {n}) = 2x + {n}.",
        f"  3. Multiply by 2: 2 × (2x + {n}) = {answer}.",
        f"  Answer: {answer}",
        "",
        *_labelled_rectangle("x", f"x + {n}"),
    )
    return ("expression", "expression_equiv",
            f"A rectangle has width x and length (x + {n}). Write a simplified "
            "expression for its perimeter.",
            answer, None, card)


def gen_rectangle_area_expression(rng: random.Random):
    """Width x, length x+n -> area expression (deliberately left in factored
    form x*(x+n) as ground truth; expression_equiv accepts any equivalent
    expanded form too, e.g. x^2+{n}x, since both are correct answers to
    "an expression for the area", not a "must show expanded" instruction)."""
    n = rng.randint(1, 9)
    answer = f"x*(x + {n})"
    card = (
        "AREA AS AN EXPRESSION",
        f"A rectangle has width x and length (x + {n}). Write an expression for its area. → {answer}",
        "  1. Area = width × length.",
        f"  2. = x × (x + {n}) = {answer}.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv",
            f"A rectangle has width x and length (x + {n}). Write an expression "
            "for its area.",
            answer, None, card)


AU_YEAR9_GENERATORS = {
    "au9_word_to_expression": gen_word_to_expression,                        # AC9M9A02
    "au9_combine_expressions": gen_combine_expressions,                      # AC9M9A02
    "au9_rectangle_perimeter_expression": gen_rectangle_perimeter_expression,  # AC9M9A02
    "au9_rectangle_area_expression": gen_rectangle_area_expression,          # AC9M9A02
}

# ── Year 10 (AC9M10A02 alignment) ──────────────────────────────────────────
# Same derive-not-transform safety discipline as Year 9 (see that section's
# docstring) -- every answer must come from a word/shape setup the prompt
# does not hand over in already-equivalent form.

def gen_distributive_word_to_expression(rng: random.Random):
    """"The sum of x and n, all multiplied by k" -> k*(x+n). Tests the
    distributive-law READING (the whole sum is multiplied), not just term
    translation -- one step harder than Y9's word_to_expression."""
    var = rng.choice("xy")
    n = rng.randint(2, 9)
    k = rng.randint(2, 6)
    answer = f"{k}*({var} + {n})"
    card = (
        "THE DISTRIBUTIVE LAW FROM WORDS",
        f"Write an algebraic expression for: the sum of {var} and {n}, all multiplied by {k}. → {answer}",
        f'  1. "The sum of {var} and {n}" means the WHOLE group ({var} + {n}) together.',
        f'  2. "All multiplied by {k}" means the whole group is multiplied: {k} × ({var} + {n}).',
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv",
            f"Write an algebraic expression for: the sum of {var} and {n}, all multiplied by {k}.",
            answer, None, card)


def gen_combine_three_expressions(rng: random.Random):
    """a, b, c given; asks for a + b - c. Introduces SUBTRACTION-combining
    (Y9 only had addition) -- genuinely new arithmetic, not just more terms."""
    var = rng.choice("xy")
    a1, a0 = rng.randint(2, 9), rng.randint(1, 9)
    b1, b0 = rng.randint(2, 9), rng.randint(1, 9)
    c1, c0 = rng.randint(2, 5), rng.randint(1, 9)  # c1>=2: avoid "1x" printing as a coefficient
    answer = _linear_expr(a1 + b1 - c1, a0 + b0 - c0, var)
    # Same "don't print a bare 1x" convention _linear_expr uses for the final
    # answer, applied to the intermediate step too (in the BARE "3x" style
    # this card's other terms already use, not _linear_expr's "3*x" -- that
    # asterisk form is for the expression_equiv answer string, not human
    # reading) -- a draw with a1+b1-c1==1 would otherwise show "...= 1x" on
    # the step but "x" on the answer line, a mismatch found by a 2000-draw
    # sweep, not eyeballed.
    x_coef = a1 + b1 - c1
    x_coef_display = var if x_coef == 1 else f"-{var}" if x_coef == -1 else f"{x_coef}{var}"
    card = (
        "COMBINING LIKE TERMS (ADD AND SUBTRACT)",
        f"If a = {a1}{var} + {a0}, b = {b1}{var} + {b0} and c = {c1}{var} + {c0}, "
        f"what is a + b - c? → {answer}",
        f"  1. Combine the {var}-terms: {a1}{var} + {b1}{var} - {c1}{var} = {x_coef_display}.",
        f"  2. Combine the number terms: {a0} + {b0} - {c0} = {a0 + b0 - c0}.",
        f"  3. So a + b - c = {answer}.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv",
            f"If a = {a1}{var} + {a0}, b = {b1}{var} + {b0} and c = {c1}{var} + {c0}, "
            "what is a + b - c? Give your answer as a simplified expression.",
            answer, None, card)


def gen_square_expression(rng: random.Random):
    """Side (x+n) -> area as a squared expression, deliberately LEFT
    unexpanded as ground truth (any equivalent expanded trinomial also
    passes) -- sets up Year 11's binomial-product content."""
    var = rng.choice("xy")
    n = rng.randint(1, 8)
    problem = f"A square has side length ({var} + {n}). Write an expression for its area."
    answer = f"({var} + {n})**2"
    # The card leads with the FORMULA, not the answer (maintainer, 2026-08-19:
    # "the formula needs to be shown in between. That step reinforces the
    # formula and its application"). Line 1 still echoes the question -- the
    # registry sweep in tests/engine/test_method_cards.py pins that -- but the
    # "→ answer" reveal is gone, so a child reads the method before the result.
    card = (
        "AREA OF A SQUARE WITH AN ALGEBRAIC SIDE",
        problem,
        "  Area of a square = side × side",
        f"  1. Both sides are the same here: ({var} + {n}) × ({var} + {n}).",
        f"  2. Written as a square: ({var} + {n})**2.",
        f"  Expanding to {var}**2 + {2 * n}{var} + {n * n} is also correct — same value, either form.",
        f"  Answer: {answer}",
    )
    # ...and the same formula stands in for the generic "(answer like 2x + 6)"
    # cue, which would otherwise point at a LINEAR shape for a squared answer.
    return ("expression", "expression_equiv", problem, answer, None, card,
            "(Area of a square = side × side)")


def gen_combined_rectangles_perimeter(rng: random.Random):
    """Two IDENTICAL rectangles -> combined perimeter. Requires recognising
    "combined" means double the single-rectangle perimeter, not just
    restating one rectangle's own perimeter."""
    var = rng.choice("xy")
    n = rng.randint(1, 9)
    # single perimeter = 2*(var + (var+n)) = 4*var + 2n; combined = double that
    problem = (f"Two identical rectangles each have width {var} and length ({var} + {n}). "
               "Write a simplified expression for their COMBINED perimeter (both rectangles together).")
    answer = f"{8}*{var} + {4 * n}"
    card = (
        "COMBINED PERIMETER",
        f"{problem} → {answer}",
        f"  1. One rectangle's perimeter = 2 × (width + length) = 2 × ({var} + {var} + {n}).",
        f"  2. That is 2 × (2{var} + {n}) = 4{var} + {2 * n}.",
        f"  3. TWO identical rectangles, so double it: 2 × (4{var} + {2 * n}) = {answer}.",
        "  The word COMBINED is the whole question — one rectangle's perimeter is only half.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


AU_YEAR10_GENERATORS = {
    "au10_distributive_word_to_expression": gen_distributive_word_to_expression,  # AC9M10A02
    "au10_combine_three_expressions": gen_combine_three_expressions,              # AC9M10A02
    "au10_square_expression": gen_square_expression,                              # AC9M10A02
    "au10_combined_rectangles_perimeter": gen_combined_rectangles_perimeter,      # AC9M10A02
}

# ── Year 11 (AC9M11A02-shaped) ─────────────────────────────────────────────

def gen_binomial_product_area(rng: random.Random):
    """Rectangle with DIFFERENT binomial width/length -> area as their
    product, left unexpanded as ground truth (equivalent expanded trinomial
    also passes). The genuine new content: multiplying two binomials, not
    just one variable term."""
    var = rng.choice("xy")
    a = rng.randint(1, 7)
    b = rng.randint(1, 7)
    problem = (f"A rectangle has width ({var} + {a}) and length ({var} + {b}). "
               "Write an expression for its area.")
    answer = f"({var} + {a})*({var} + {b})"
    card = (
        "AREA WITH TWO BINOMIAL SIDES",
        f"{problem} → {answer}",
        "  1. Area of a rectangle = width × length.",
        f"  2. Multiply the two brackets: ({var} + {a}) × ({var} + {b}).",
        "  3. Expanded, each part of the first bracket meets each part of the second:",
        f"     {var}×{var} = {var}**2 · {var}×{b} = {b}{var} · {a}×{var} = {a}{var} · {a}×{b} = {a * b}",
        f"     giving {var}**2 + {a + b}{var} + {a * b}. Either form is correct.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


def gen_word_to_quadratic_expression(rng: random.Random):
    """"The square of a number x, plus k times the number, minus n" ->
    x**2 + k*x - n. Tests "square of" translation -- new vocabulary, not
    just a longer linear phrase."""
    var = rng.choice("xy")
    k = rng.randint(2, 9)
    n = rng.randint(1, 9)
    problem = (f"Write an algebraic expression for: the square of a number {var}, "
               f"plus {k} times the number, minus {n}.")
    answer = f"{var}**2 + {k}*{var} - {n}"
    card = (
        "WORDS INTO A QUADRATIC EXPRESSION",
        f"{problem} → {answer}",
        "  Take the phrase one piece at a time:",
        f"    \"the square of a number {var}\"  →  {var}**2",
        f"    \"plus {k} times the number\"     →  + {k}{var}",
        f"    \"minus {n}\"                     →  - {n}",
        f"  Join them in the order given: {answer}",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


def gen_combine_quadratic_linear(rng: random.Random):
    """a (quadratic) + b (linear) -> combined expression. Genuinely new:
    combining terms of DIFFERENT degree, not just same-degree linear terms."""
    var = rng.choice("xy")
    a2, a1 = rng.randint(2, 4), rng.randint(2, 9)  # both >=2: avoid "1x"/"1x**2" printing
    b1, b0 = rng.randint(2, 9), rng.randint(1, 9)  # b1>=2: avoid "1x" printing
    problem = (f"If a = {a2}{var}**2 + {a1}{var} and b = {b1}{var} + {b0}, what is a + b? "
               "Give your answer as a simplified expression.")
    answer = f"{a2}*{var}**2 + {a1 + b1}*{var} + {b0}"
    card = (
        "COMBINING TERMS OF DIFFERENT DEGREE",
        f"{problem} → {answer}",
        f"  1. Only LIKE terms combine. {var}**2 and {var} are not like terms.",
        f"  2. {var}**2 terms: only a has one → {a2}{var}**2 stays as it is.",
        f"  3. {var} terms: {a1}{var} + {b1}{var} = {a1 + b1}{var}.",
        f"  4. Number terms: only b has one → {b0}.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


def gen_difference_of_expressions(rng: random.Random):
    """Two-part word problem (a number, and a second number defined FROM the
    first) -> the SECOND minus the FIRST. Requires deriving both quantities
    then subtracting -- the prompt never states the difference directly."""
    var = rng.choice("xy")
    k = rng.randint(2, 6)
    n = rng.randint(1, 9)
    problem = (f"A number is {var}. A second number is {k} times {var}, minus {n}. "
               "Write an expression for the SECOND number minus the FIRST number.")
    answer = _linear_expr(k - 1, -n, var)
    card = (
        "SECOND NUMBER MINUS THE FIRST",
        f"{problem} → {answer}",
        f"  1. Write both numbers down: first is {var}, second is {k}{var} - {n}.",
        f"  2. The question asks SECOND - FIRST: ({k}{var} - {n}) - {var}.",
        f"  3. Combine the {var} terms: {k}{var} - {var} = {k - 1}{var}.",
        f"  4. The -{n} is unchanged, so the result is {answer}.",
        "  Order matters here: first minus second would give the opposite sign.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


AU_YEAR11_GENERATORS = {
    "au11_binomial_product_area": gen_binomial_product_area,                # AC9M11A02
    "au11_word_to_quadratic_expression": gen_word_to_quadratic_expression,  # AC9M11A02
    "au11_combine_quadratic_linear": gen_combine_quadratic_linear,          # AC9M11A02
    "au11_difference_of_expressions": gen_difference_of_expressions,       # AC9M11A02
}

# ── Year 12 (AC9M12A02-shaped) — algebra applied to a modelled scenario ────

def gen_revenue_expression(rng: random.Random):
    """Price × quantity-sold (quantity itself an expression in the price
    variable) -> a genuine quadratic revenue model, not just a rectangle
    re-skinned -- real-world application is the Year 12-appropriate step up."""
    var = rng.choice("xy")
    k = rng.randint(2, 4)  # >=2 so the quantity term always prints a visible coefficient
    n = rng.randint(1, 9)
    problem = (f"A shop sells items for ${var} each. On a day they sell ({k}{var} + {n}) items. "
               "Write an expression for the total revenue (price times number sold).")
    answer = f"{var}*({k}*{var} + {n})"
    card = (
        "REVENUE AS AN EXPRESSION",
        f"{problem} → {answer}",
        "  1. Revenue = price × number sold. That is the model.",
        f"  2. Price is {var}; number sold is ({k}{var} + {n}).",
        f"  3. Multiply them: {var} × ({k}{var} + {n}).",
        f"     Expanded that is {k}{var}**2 + {n}{var} — either form is correct.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


def gen_combine_two_quadratics(rng: random.Random):
    """a + b, both quadratic -- harder same-degree combination than Y11's
    quadratic-plus-linear."""
    var = rng.choice("xy")
    a2, a1, a0 = rng.randint(2, 5), rng.randint(2, 9), rng.randint(1, 9)  # a2,a1>=2: avoid "1x"/"1x**2"
    b2, b1, b0 = rng.randint(2, 5), rng.randint(2, 9), rng.randint(1, 9)  # b2,b1>=2: same reason
    problem = (f"If a = {a2}{var}**2 + {a1}{var} + {a0} and b = {b2}{var}**2 + {b1}{var} + {b0}, "
               "what is a + b? Give your answer as a simplified expression.")
    answer = f"{a2 + b2}*{var}**2 + {a1 + b1}*{var} + {a0 + b0}"
    card = (
        "ADDING TWO QUADRATICS",
        f"{problem} → {answer}",
        "  Add each kind of term separately — like with like:",
        f"    {var}**2 terms:  {a2}{var}**2 + {b2}{var}**2 = {a2 + b2}{var}**2",
        f"    {var} terms:     {a1}{var} + {b1}{var} = {a1 + b1}{var}",
        f"    number terms:  {a0} + {b0} = {a0 + b0}",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


def gen_compound_shape_area(rng: random.Random):
    """Rectangle area MINUS a removed square section -> a genuine two-step
    (multiply, then subtract) compound-shape derivation; the prompt states
    only the pieces, never the combined expression."""
    var = rng.choice("xy")
    n = rng.randint(2, 9)
    s = rng.randint(1, 4)
    problem = (f"A garden is rectangular with width {var} and length ({var} + {n}), but a square "
               f"section of side {s} is removed from one corner for a path. Write an expression "
               "for the remaining garden area.")
    answer = f"{var}*({var} + {n}) - {s * s}"
    card = (
        "COMPOUND SHAPE: WHOLE MINUS THE PIECE REMOVED",
        f"{problem} → {answer}",
        f"  1. Whole rectangle first: width × length = {var} × ({var} + {n}).",
        f"  2. The removed square: side × side = {s} × {s} = {s * s}.",
        f"  3. Remaining = whole - removed = {answer}.",
        "  Take the whole shape first, then subtract — never try to measure the odd shape directly.",
        f"  Answer: {answer}",
    )
    return ("expression", "expression_equiv", problem, answer, None, card)


AU_YEAR12_GENERATORS = {
    "au12_revenue_expression": gen_revenue_expression,          # AC9M12A02
    "au12_combine_two_quadratics": gen_combine_two_quadratics,  # AC9M12A02
    "au12_compound_shape_area": gen_compound_shape_area,        # AC9M12A02
}
