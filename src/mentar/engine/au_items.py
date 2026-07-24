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
(int / fraction / mc4) — no decimals (the verifier safe-rejects them by design).
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


def _mc(problem_stem: str, options: list[str], correct_index: int):
    """An mc4 tuple carrying the STEM (no inline "A) ..." options -- R2.1: the
    web view shows stem + radios; ItemGenerator._make composes the inline
    "A) ..." form centrally for CLI/transcript surfaces) + the structured
    choices list for the web radio buttons."""
    return ("mc4", "mc_choice", problem_stem, _LETTERS[correct_index], options)


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
    return _mc(
        f"In the number {number}, what is the value of the digit {digit}?",
        options, options.index(str(correct)),
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
    return _mc(
        f"In the number {number}, what is the value of the digit {digit}?",
        options, options.index(str(correct)),
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
    return _mc(f"In the number {number}, what is the value of the digit {digit}?", options, options.index(str(correct)))


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
    return ("fraction", "fraction_equiv", f"A pizza is cut into {d} equal slices. What fraction is ONE slice?", f"1/{d}")


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
    return _mc(f"In {number}, what does the {tenths} represent?", options, options.index(correct))


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
    return ("fraction", "fraction_equiv", f"What is {n}/{d} × {whole}?", f"{n * whole}/{d}")


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
    return ("int", "int_exact", f"What is {pct}% of {quantity}?", str(answer))


def gen_negative_numbers(rng: random.Random):
    """AC9M5N01-aligned: negative numbers via a temperature-drop context."""
    temp = rng.randint(-2, 8)
    drop = rng.randint(5, 15)
    return ("int", "int_exact", f"The temperature was {temp}°C and dropped by {drop}°C. What is the new temperature?", str(temp - drop))


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

def gen_order_of_operations(rng: random.Random):
    """AC9M6N01-aligned: a two-term expression where the higher-precedence
    operator (×/÷) is evaluated before the lower one (+/−)."""
    op_low = rng.choice(["+", "-"])
    a = rng.randint(20, 60)
    if rng.random() < 0.5:
        b, c = rng.randint(2, 9), rng.randint(2, 9)
        high_val = b * c
        expr = f"{a} {op_low} {b} × {c}"
    else:
        c = rng.randint(2, 9)
        q = rng.randint(2, 9)
        b = c * q
        high_val = q
        expr = f"{a} {op_low} {b} ÷ {c}"
    result = a + high_val if op_low == "+" else a - high_val
    return ("int", "int_exact", f"What is {expr}?", str(result))


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


def gen_area_perimeter(rng: random.Random):
    """AC9M6M01-aligned: area or perimeter of a rectangle, chosen at random."""
    length = rng.randint(3, 12)
    width = rng.randint(2, 10)
    if rng.random() < 0.5:
        return ("int", "int_exact", f"A rectangle is {length}cm by {width}cm. What is its area, in square centimetres?", str(length * width))
    return ("int", "int_exact", f"A rectangle is {length}cm by {width}cm. What is its perimeter, in centimetres?", str(2 * (length + width)))


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
    """AC9M6N03-aligned: convert a common fraction to its decimal equivalent."""
    frac, dec = rng.choice(_FRACTION_DECIMAL_PAIRS)
    return ("decimal", "decimal_exact", f"Write {frac} as a decimal.", dec)


# ── Year 7 (AC9M7N/A alignment) ───────────────────────────────────────────────
# R15, 2026-07-19.

def gen_integers_add_sub(rng: random.Random):
    """AC9M7N01-aligned: add or subtract two integers, either may be negative."""
    a = rng.randint(-15, 15)
    b = rng.randint(-15, 15)
    if rng.random() < 0.5:
        return ("int", "int_exact", f"What is {a} + {b}?", str(a + b))
    return ("int", "int_exact", f"What is {a} - {b}?", str(a - b))


def gen_order_of_ops_negatives(rng: random.Random):
    """AC9M7N01-aligned: order of operations where the leading term may be negative."""
    op_low = rng.choice(["+", "-"])
    a = rng.randint(-20, 20)
    if rng.random() < 0.5:
        b, c = rng.randint(2, 9), rng.randint(2, 9)
        high_val = b * c
        expr = f"{a} {op_low} {b} × {c}"
    else:
        c = rng.randint(2, 9)
        q = rng.randint(2, 9)
        b = c * q
        high_val = q
        expr = f"{a} {op_low} {b} ÷ {c}"
    result = a + high_val if op_low == "+" else a - high_val
    return ("int", "int_exact", f"What is {expr}?", str(result))


def gen_unlike_denom_fractions(rng: random.Random):
    """AC9M7N04-aligned: adding two fractions with different denominators.
    fractions.Fraction reduces automatically -- the answer is always canonical."""
    n1, d1 = rng.randint(1, 4), rng.randint(2, 6)
    n2, d2 = rng.randint(1, 4), rng.randint(2, 6)
    result = Fraction(n1, d1) + Fraction(n2, d2)
    return ("fraction", "fraction_equiv", f"What is {n1}/{d1} + {n2}/{d2}?", f"{result.numerator}/{result.denominator}")


def gen_one_step_equations(rng: random.Random):
    """AC9M7A02-aligned: solving a one-step linear equation for x."""
    a = rng.randint(1, 20)
    x_true = rng.randint(1, 20)
    b = x_true + a
    return ("int", "int_exact", f"If x + {a} = {b}, what is x?", str(x_true))


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
    return ("int", "int_exact", f"If {coef}x + {a} = {b}, what is x?", str(x_true))


def gen_squares(rng: random.Random):
    """AC9M8N01-aligned: squaring a small integer."""
    n = rng.randint(2, 15)
    return ("int", "int_exact", f"What is {n} squared ({n}²)?", str(n * n))


def gen_negative_multiplication(rng: random.Random):
    """AC9M8N01-aligned: multiplying two integers, either sign."""
    a = rng.choice([-1, 1]) * rng.randint(2, 12)
    b = rng.choice([-1, 1]) * rng.randint(2, 12)
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


def gen_percentage_change(rng: random.Random):
    """AC9M8N03-aligned: a percentage increase, constructed to be exact."""
    base = rng.randint(1, 20) * 10
    pct = rng.choice([10, 20, 50])
    increase = base * pct // 100
    new_val = base + increase
    return ("int", "int_exact", f"A price of ${base} increases by {pct}%. What is the new price?", str(new_val))


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
