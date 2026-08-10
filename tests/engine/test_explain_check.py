"""T-A14 — arithmetic claim verification in free-form explanation text.

Spec: docs/SAFETY.md §6.2 Level 2.
Module under test: src/mentar/engine/explain_check.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.explain_check import find_claims, has_verified_failure, realign_algebra_blocks


def test_correct_fraction_claim_passes():
    text = "When you add fractions: 1/4 + 1/4 = 2/4, which is the same as 1/2."
    assert not has_verified_failure(text)
    claims = find_claims(text)
    assert any(c.ok is True for c in claims)


def test_wrong_fraction_claim_fails():
    text = "So 3/4 + 1/4 = 2/4, easy!"
    assert has_verified_failure(text)


def test_correct_integer_claim_passes():
    assert not has_verified_failure("Since 10 / 5 isn't a claim here, but 4 + 6 = 10 is true.")


def test_wrong_integer_claim_fails():
    assert has_verified_failure("We know that 4 + 6 = 11, so...")


def test_mixed_number_claim():
    assert not has_verified_failure("1 1/2 + 1/2 = 2 exactly.")
    assert has_verified_failure("1 1/2 + 1/2 = 3 which is wrong.")


def test_no_claims_in_plain_prose_passes():
    text = "Think of a fraction like slices of a pizza shared equally among friends."
    assert not has_verified_failure(text)
    assert find_claims(text) == []


def test_decimal_claims_are_now_verified():
    """E2.3 (2026-08-10): OVERTURNS this test's previous assertion. The old
    behaviour ("decimals out of pilot scope, no claim extracted") predated R13 —
    decimal answer types and Y5-8 decimal content are live, so SAFETY §6.2's
    verify-or-discard guard must cover decimal claims too. A wrong decimal claim
    in an explanation is now a verified failure, not invisible."""
    # Correct decimal claims pass (exact Fraction arithmetic — no float epsilon).
    assert not has_verified_failure("0.5 + 0.5 = 1.0")
    assert not has_verified_failure("3.5 + 2.1 = 5.6")
    assert not has_verified_failure("0.1 + 0.2 = 0.3")  # would FAIL under float math
    assert not has_verified_failure("2.5 × 4 = 10")
    # Wrong decimal claims are now caught.
    assert has_verified_failure("3.5 + 2.1 = 5.7")
    assert has_verified_failure("0.5 + 0.5 = 1.1")
    assert has_verified_failure("7.5 - 2.5 = 4.9")
    # Mixed decimal/integer claims verify too.
    claims = find_claims("First 1.5 + 1.5 = 3, then 3 + 1 = 4.")
    assert [c.ok for c in claims] == [True, True]


def test_multiplication_claim():
    assert not has_verified_failure("2 × 3 = 6 is correct.")
    assert has_verified_failure("2 × 3 = 7 is wrong.")


def test_correct_division_symbol_claim_passes():
    assert not has_verified_failure("We know that 12 ÷ 4 = 3, so...")


def test_wrong_division_symbol_claim_fails():
    assert has_verified_failure("We know that 12 ÷ 4 = 2, so...")


def test_divided_by_phrase_claim():
    assert not has_verified_failure("12 divided by 4 = 3 exactly.")
    assert has_verified_failure("12 divided by 4 = 2, which is wrong.")


def test_fraction_slash_still_not_treated_as_division():
    """The plain "/" stays unparsed as an operator — it's fraction notation,
    not division (unlike "÷"/"divided by", which are unambiguous)."""
    text = "3/4 is a fraction, not a division claim on its own."
    assert find_claims(text) == []
    assert not has_verified_failure(text)


def test_division_by_zero_claim_is_unparseable_not_a_failure():
    """Fail-open, same as any other unparseable claim — never raises."""
    text = "5 ÷ 0 = 0, oops."
    claims = find_claims(text)
    assert len(claims) == 1
    assert claims[0].ok is None
    assert not has_verified_failure(text)


def test_realign_algebra_blocks_fixes_arrow_and_equals_columns():
    # Simulates the actual misalignment the model produced:
    # both RHS expressions are 6 chars but got different gap before ←
    messy = (
        "Let's keep balanced ⚖️\n"
        "\n"
        "  2x + 8        = 36\n"
        "  2x + 8 - 8    = 36 - 8   ← subtract 8 from both sides\n"
        "  2x            = 28\n"
        "  2x ÷ 2        = 28 ÷ 2     ← divide both sides by 2\n"
        "  x             = 14\n"
        "\n"
        "Now you try it! ✏️"
    )
    fixed = realign_algebra_blocks(messy)
    lines = fixed.split('\n')
    arrow_lines = [l for l in lines if '←' in l]
    assert len(arrow_lines) == 2
    # Both ← must be at the exact same character position
    positions = [l.index('←') for l in arrow_lines]
    assert positions[0] == positions[1], f"← at cols {positions} — not aligned"
    # All = in step lines must be at the same column
    step_lines = [l for l in lines if '=' in l and l.startswith('  ') and 'Now' not in l and 'Let' not in l]
    eq_positions = [l.index('=') for l in step_lines if not l.strip().startswith('Check')]
    assert len(set(eq_positions)) == 1, f"= at multiple cols: {eq_positions}"


def test_realign_algebra_blocks_leaves_prose_unchanged():
    prose = "The answer is x = 5 because we subtracted 3 from both sides."
    assert realign_algebra_blocks(prose) == prose


def test_realign_algebra_blocks_noop_when_no_equals():
    text = "Think of slices of pizza shared among friends."
    assert realign_algebra_blocks(text) == text


def test_division_remainder_correct():
    assert not has_verified_failure("12 ÷ 5 = 2 R 2")
    assert not has_verified_failure("15 ÷ 4 = 3 R 3")
    assert not has_verified_failure("15 divided by 4 = 3 R 3")


def test_division_remainder_wrong():
    assert has_verified_failure("12 ÷ 5 = 2 R 3")
    assert has_verified_failure("12 ÷ 5 = 3 R 2")


def test_division_remainder_claim_extraction():
    claims = find_claims("12 ÷ 5 = 2 R 2")
    assert len(claims) == 1
    assert claims[0].ok is True


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} explain-check tests passed.")
