"""tests/eval/test_verify_numeric_decimal.py — R13: decimal answer type.

Tests the new answer_type="decimal" / checker="decimal_exact" grammar in
eval/verify_numeric.py. Purely additive -- does not change int/fraction
behaviour (TestExistingCheckersUnaffected pins that as a visible marker,
mirroring assertions already covered in tests/eval/test_verify_numeric.py
and tests/engine/test_verifier.py, both left untouched by this wave).
"""

from __future__ import annotations

from decimal import Decimal

from mentar.eval.verify_numeric import CheckResult, check, normalise_decimal


class TestNormaliseDecimal:
    def test_simple_decimal(self):
        assert normalise_decimal("2.5") == Decimal("2.5")

    def test_negative_decimal(self):
        assert normalise_decimal("-3.25") == Decimal("-3.25")

    def test_bare_integer_string(self):
        assert normalise_decimal("7") == Decimal("7")

    def test_zero(self):
        assert normalise_decimal("0") == Decimal("0")

    def test_trailing_zero_equivalence(self):
        assert normalise_decimal("0.50") == normalise_decimal("0.5")
        assert normalise_decimal("0.50") == Decimal("0.5")

    def test_int_and_decimal_equivalence(self):
        assert normalise_decimal("2") == normalise_decimal("2.0")

    def test_empty_string(self):
        assert normalise_decimal("") is None

    def test_whitespace_only(self):
        assert normalise_decimal("   ") is None

    def test_non_numeric(self):
        assert normalise_decimal("abc") is None

    def test_nan_rejected(self):
        """Decimal("NaN") would otherwise parse successfully -- must be
        rejected before ever reaching Decimal()."""
        assert normalise_decimal("NaN") is None

    def test_infinity_rejected(self):
        assert normalise_decimal("Infinity") is None

    def test_exponent_notation_rejected(self):
        """Exponent notation must not be silently accepted as a plain decimal."""
        assert normalise_decimal("5E2") is None

    def test_comma_decimal_separator_rejected(self):
        """No locale-aware parsing -- comma as decimal separator is rejected, not guessed."""
        assert normalise_decimal("0,5") is None

    def test_fraction_string_rejected(self):
        assert normalise_decimal("1/2") is None

    def test_leading_plus_rejected(self):
        assert normalise_decimal("+5") is None


class TestCheckDecimalExact:
    def test_exact_match_passes(self):
        assert check("decimal", "decimal_exact", "The answer is 2.5", "2.5").result == CheckResult.PASS

    def test_wrong_value_fails(self):
        assert check("decimal", "decimal_exact", "The answer is 3.5", "2.5").result == CheckResult.FAIL

    def test_trailing_zero_ground_truth_still_passes(self):
        assert check("decimal", "decimal_exact", "The answer is 0.5", "0.50").result == CheckResult.PASS

    def test_bare_int_answer_matches_decimal_ground_truth(self):
        assert check("decimal", "decimal_exact", "The answer is 2", "2.0").result == CheckResult.PASS

    def test_answer_tag_used(self):
        res = check("decimal", "decimal_exact", "Working: 10 / 4 = 2.5. <answer>2.5</answer>", "2.5")
        assert res.result == CheckResult.PASS
        assert res.extracted == "2.5"

    def test_ambiguous_or_decimals_safe_reject(self):
        assert check("decimal", "decimal_exact", "It is 2.5 or 3.5.", "2.5").result == CheckResult.SAFE_REJECT

    def test_malformed_ground_truth_safe_reject(self):
        assert check("decimal", "decimal_exact", "The answer is 2.5.", "not_a_number").result == CheckResult.SAFE_REJECT

    def test_nan_ground_truth_safe_reject(self):
        assert check("decimal", "decimal_exact", "The answer is 2.5.", "NaN").result == CheckResult.SAFE_REJECT

    def test_empty_output_extract_fail(self):
        assert check("decimal", "decimal_exact", "", "2.5").result == CheckResult.EXTRACT_FAIL

    def test_no_number_in_output_extract_fail(self):
        assert check("decimal", "decimal_exact", "That is a really good question!", "2.5").result == CheckResult.EXTRACT_FAIL

    def test_negative_decimal_roundtrip(self):
        assert check("decimal", "decimal_exact", "The temperature is -3.5 degrees.", "-3.5").result == CheckResult.PASS


class TestExistingCheckersUnaffected:
    """Regression-intent marker -- the decimal_exact path must never relax the
    int/fraction decimal-reject guards. Same assertions already pinned in the
    untouched tests/eval/test_verify_numeric.py / tests/engine/test_verifier.py."""

    def test_fraction_checker_still_rejects_decimal_ground_truth(self):
        assert check("fraction", "fraction_equiv", "The answer is 1/2.", "0.5").result == CheckResult.SAFE_REJECT

    def test_int_checker_still_rejects_decimal_output(self):
        assert check("int", "int_exact", "0.5", "3").result == CheckResult.SAFE_REJECT
