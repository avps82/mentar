"""T-A14 — arithmetic claim verification in free-form explanation text.

Spec: docs/SAFETY.md §6.2 Level 2.
Module under test: src/mentar/engine/explain_check.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.explain_check import find_claims, has_verified_failure


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


def test_decimal_claim_is_unparseable_not_a_failure():
    """Decimals are out of pilot scope — the claim regex doesn't even recognise
    a decimal token as a number, so no claim is extracted (pass through, not
    a failure) rather than a false FAIL."""
    text = "0.5 + 0.5 = 1.0"
    assert find_claims(text) == []
    assert not has_verified_failure(text)


def test_multiplication_claim():
    assert not has_verified_failure("2 × 3 = 6 is correct.")
    assert has_verified_failure("2 × 3 = 7 is wrong.")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} explain-check tests passed.")
