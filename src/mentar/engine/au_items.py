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
    """AC9M3N01-aligned: what a digit stands for in a 3-digit number."""
    digits = rng.sample(range(1, 10), 3)
    number = digits[0] * 100 + digits[1] * 10 + digits[2]
    pos = rng.randrange(3)                      # 0=hundreds, 1=tens, 2=ones
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
    """AC9M4N01-aligned: what a digit stands for in a 4-digit number. The four
    options are the digit at each of the four places — always distinct (a value
    factors uniquely as digit × 10^p for digit 1-9)."""
    digits = rng.sample(range(1, 10), 4)
    number = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
    pos = rng.randrange(4)
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
