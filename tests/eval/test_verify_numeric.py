"""
tests/eval/test_verify_numeric.py — Unit tests for the deterministic fraction verifier.

Satisfies T1.3 requirements:
- ≥25 hand-written test cases (well above the T1.3 minimum of 20)
- Extraction-failure rate <5% on a 30-case corpus (measured in test_extraction_corpus)
- Covers: equivalence, improper/mixed, comparison, int_exact, mc_choice, malformed inputs,
  unicode vulgar fractions, and the extraction-failure-rate corpus assertion.

Decimal decision: SAFE_REJECT.
Decimals are explicitly out of pilot scope (fractions.md "Out of scope: decimal/fraction
conversion"). Accepting "0.5" when "1/2" is expected could silently pass a wrong form.
We reject and document the case in test_decimal_rejected.

Unicode decision: ACCEPTED via lookup table.
A small mapping table in verify_numeric.py converts ½ ¼ ¾ etc. to their a/b form before
any parsing. This is cheap and avoids spurious SAFE_REJECTs on copy-paste input from a child.
"""

from __future__ import annotations

from fractions import Fraction

from mentar.eval.verify_numeric import (
    CheckResult,
    check,
    extract_answer,
    normalise_fraction,
)

# ===========================================================================
# normalise_fraction — unit tests
# ===========================================================================

class TestNormaliseFraction:
    """Tests for the normalise_fraction helper."""

    def test_simple_half(self):
        assert normalise_fraction("1/2") == Fraction(1, 2)

    def test_equivalent_two_fourths(self):
        assert normalise_fraction("2/4") == Fraction(1, 2)

    def test_improper(self):
        assert normalise_fraction("5/3") == Fraction(5, 3)

    def test_whole_number(self):
        assert normalise_fraction("3") == Fraction(3)

    def test_zero(self):
        assert normalise_fraction("0") == Fraction(0)

    def test_mixed_number(self):
        """1 1/2 → 3/2"""
        assert normalise_fraction("1 1/2") == Fraction(3, 2)

    def test_mixed_number_zero_whole(self):
        """0 0/1 → 0"""
        assert normalise_fraction("0 0/1") == Fraction(0)

    def test_negative_fraction(self):
        assert normalise_fraction("-3/5") == Fraction(-3, 5)

    def test_negative_denominator_normalised(self):
        """Fraction handles negative denominators natively: 3/-6 → -1/2"""
        assert normalise_fraction("3/-6") == Fraction(-1, 2)

    def test_zero_denominator_safe_reject(self):
        """Zero denominator must return None (safe-reject)."""
        assert normalise_fraction("1/0") is None

    def test_zero_denominator_larger(self):
        assert normalise_fraction("5/0") is None

    def test_empty_string(self):
        assert normalise_fraction("") is None

    def test_whitespace_only(self):
        assert normalise_fraction("   ") is None

    def test_non_numeric(self):
        assert normalise_fraction("a/b") is None

    def test_decimal_rejected(self):
        """Decimals are not in pilot scope — must return None."""
        assert normalise_fraction("0.5") is None
        assert normalise_fraction("1.5/2") is None

    def test_unicode_half(self):
        """½ → 1/2"""
        assert normalise_fraction("½") == Fraction(1, 2)

    def test_unicode_quarter(self):
        """¼ → 1/4"""
        assert normalise_fraction("¼") == Fraction(1, 4)

    def test_three_thirds(self):
        """3/3 = 1"""
        assert normalise_fraction("3/3") == Fraction(1)

    def test_large_equivalent(self):
        """6/9 = 2/3"""
        assert normalise_fraction("6/9") == Fraction(2, 3)

    def test_negative_mixed(self):
        """-2 3/4 → -11/4"""
        assert normalise_fraction("-2 3/4") == Fraction(-11, 4)

    def test_whitespace_around_slash(self):
        """'1 / 2' should parse (spaces around slash)."""
        assert normalise_fraction("1 / 2") == Fraction(1, 2)


# ===========================================================================
# extract_answer — unit tests
# ===========================================================================

class TestExtractAnswer:
    """Tests for the extract_answer helper."""

    def test_answer_tag_preferred(self):
        text = "I think the answer is 3/4. <answer>1/2</answer>"
        assert extract_answer(text, "fraction") == "1/2"

    def test_last_fraction_no_tag(self):
        text = "The student wrote 2/4 and then corrected to 1/2."
        result = extract_answer(text, "fraction")
        assert result == "1/2"

    def test_mixed_number_extracted(self):
        text = "So the total is 1 1/2 cups."
        result = extract_answer(text, "fraction")
        assert result == "1 1/2"

    def test_integer_fallback(self):
        text = "The answer is 12."
        result = extract_answer(text, "int")
        assert result == "12"

    def test_trailing_space_stripped(self):
        text = "The answer is 12   "
        result = extract_answer(text, "int")
        assert result == "12"

    def test_trailing_punctuation_stripped(self):
        text = "the answer is 12."
        result = extract_answer(text, "int")
        assert result == "12"

    def test_ambiguous_two_fractions_or_rejected(self):
        """'1/2 or 3/4' → None (ambiguous)."""
        text = "It could be 1/2 or 3/4."
        result = extract_answer(text, "fraction")
        assert result is None

    def test_empty_input(self):
        assert extract_answer("", "fraction") is None

    def test_whitespace_only(self):
        assert extract_answer("   ", "fraction") is None

    def test_mc_letter(self):
        assert extract_answer("Answer: B", "mc4") == "B"

    def test_mc_letter_lowercase(self):
        assert extract_answer("I think it's c", "mc4") == "C"

    def test_mc_in_parens(self):
        assert extract_answer("My choice is (A)", "mc4") == "A"

    def test_mc_digit(self):
        assert extract_answer("The answer is 3", "mc4") == "3"

    def test_unicode_fraction_extracted(self):
        """½ should be expanded and then extracted."""
        text = "The fraction is ½."
        result = extract_answer(text, "fraction")
        assert result == "1/2"


# ===========================================================================
# check — int_exact
# ===========================================================================

class TestCheckIntExact:
    """Tests for the int_exact checker."""

    def test_exact_match(self):
        out = check("int", "int_exact", "Each child gets 3 apples.", "3")
        assert out.result == CheckResult.PASS
        assert out.extracted == "3"
        assert out.canonical == "3"

    def test_trailing_space_in_output(self):
        out = check("int", "int_exact", "The answer is 12  ", "12")
        assert out.result == CheckResult.PASS

    def test_embedded_sentence(self):
        out = check("int", "int_exact", "So each friend gets 4 pencils.", "4")
        assert out.result == CheckResult.PASS

    def test_wrong_integer(self):
        out = check("int", "int_exact", "The answer is 5.", "4")
        assert out.result == CheckResult.FAIL

    def test_empty_output(self):
        out = check("int", "int_exact", "", "4")
        assert out.result == CheckResult.EXTRACT_FAIL

    def test_bad_ground_truth(self):
        out = check("int", "int_exact", "The answer is 4.", "abc")
        assert out.result == CheckResult.SAFE_REJECT

    def test_no_integer_in_output(self):
        out = check("int", "int_exact", "I don't know.", "4")
        assert out.result == CheckResult.EXTRACT_FAIL


# ===========================================================================
# check — fraction_equiv
# ===========================================================================

class TestCheckFractionEquiv:
    """Tests for the fraction_equiv checker."""

    # --- Equivalence ---

    def test_two_fourths_equals_one_half(self):
        """2/4 ≡ 1/2 → PASS"""
        out = check("fraction", "fraction_equiv", "The answer is 2/4.", "1/2")
        assert out.result == CheckResult.PASS
        assert out.canonical == "1/2"

    def test_three_ninths_equals_one_third(self):
        """3/9 ≡ 1/3 → PASS"""
        out = check("fraction", "fraction_equiv", "So 3/9.", "1/3")
        assert out.result == CheckResult.PASS

    def test_six_over_four_equals_three_halves(self):
        """6/4 ≡ 3/2 → PASS"""
        out = check("fraction", "fraction_equiv", "6/4 of the pie", "3/2")
        assert out.result == CheckResult.PASS

    def test_exact_match(self):
        out = check("fraction", "fraction_equiv", "The answer is 3/4.", "3/4")
        assert out.result == CheckResult.PASS

    def test_wrong_fraction(self):
        out = check("fraction", "fraction_equiv", "The answer is 1/4.", "1/2")
        assert out.result == CheckResult.FAIL

    # --- Improper / mixed ---

    def test_improper_vs_improper_same(self):
        """5/3 vs 5/3 → PASS"""
        out = check("fraction", "fraction_equiv", "The answer is 5/3.", "5/3")
        assert out.result == CheckResult.PASS

    def test_improper_vs_mixed_equivalent(self):
        """5/3 ≡ 1 2/3 → PASS"""
        out = check("fraction", "fraction_equiv", "So it's 1 2/3.", "5/3")
        assert out.result == CheckResult.PASS

    def test_mixed_vs_mixed(self):
        """1 1/2 vs 3/2 → PASS"""
        out = check("fraction", "fraction_equiv", "The total is 1 1/2.", "3/2")
        assert out.result == CheckResult.PASS

    def test_whole_number_fraction(self):
        """4/4 = 1 → PASS"""
        out = check("fraction", "fraction_equiv", "The answer is 4/4.", "1")
        assert out.result == CheckResult.PASS

    # --- Addition / subtraction answers (verifier checks final answer, not arithmetic) ---

    def test_add_equal_denom_correct(self):
        """2/8 + 3/8 = 5/8: LLM gives 5/8 → PASS"""
        out = check("fraction", "fraction_equiv",
                    "You ate 2 slices and 3 more, so 5/8 of the pizza.", "5/8")
        assert out.result == CheckResult.PASS

    def test_sub_equal_denom_correct(self):
        """7/10 - 2/10 = 5/10 = 1/2: LLM gives 5/10 → PASS (equiv to 1/2)"""
        out = check("fraction", "fraction_equiv", "There is 5/10 left.", "1/2")
        assert out.result == CheckResult.PASS

    def test_wrong_add_answer(self):
        """LLM gives wrong 4/8 when 5/8 expected → FAIL"""
        out = check("fraction", "fraction_equiv", "The total is 4/8.", "5/8")
        assert out.result == CheckResult.FAIL

    # --- Malformed inputs ---

    def test_zero_denominator_safe_reject(self):
        """1/0 → SAFE_REJECT"""
        out = check("fraction", "fraction_equiv", "1/0 is the answer.", "1/2")
        assert out.result == CheckResult.SAFE_REJECT

    def test_non_fraction_extract_fail(self):
        """'a/b' is not a valid fraction → EXTRACT_FAIL (no numeric candidate)"""
        out = check("fraction", "fraction_equiv", "The answer is a/b.", "1/2")
        # extract_answer won't match 'a/b' as a valid fraction-looking pattern
        # since a and b aren't digits, so it falls through to EXTRACT_FAIL
        assert out.result in (CheckResult.EXTRACT_FAIL, CheckResult.SAFE_REJECT)

    def test_empty_output_extract_fail(self):
        out = check("fraction", "fraction_equiv", "", "1/2")
        assert out.result == CheckResult.EXTRACT_FAIL

    def test_ambiguous_or_fraction_safe_reject(self):
        """'1/2 or 3/4' → SAFE_REJECT (ambiguous candidates)"""
        out = check("fraction", "fraction_equiv", "It is 1/2 or 3/4.", "1/2")
        assert out.result == CheckResult.SAFE_REJECT

    def test_decimal_ground_truth_safe_reject(self):
        """Ground truth '0.5' (decimal) → SAFE_REJECT; not in pilot scope."""
        out = check("fraction", "fraction_equiv", "The answer is 1/2.", "0.5")
        assert out.result == CheckResult.SAFE_REJECT

    def test_bad_ground_truth_safe_reject(self):
        out = check("fraction", "fraction_equiv", "The answer is 1/2.", "not_a_fraction")
        assert out.result == CheckResult.SAFE_REJECT

    # --- Unicode ---

    def test_unicode_half_extracted(self):
        """LLM outputs ½ → parsed as 1/2 → PASS vs ground_truth '1/2'"""
        out = check("fraction", "fraction_equiv", "The answer is ½.", "1/2")
        assert out.result == CheckResult.PASS

    # --- Answer tag ---

    def test_answer_tag_used(self):
        out = check("fraction", "fraction_equiv",
                    "Working: 1/4 + 1/4 = 2/4. <answer>1/2</answer>", "1/2")
        assert out.result == CheckResult.PASS
        assert out.extracted == "1/2"


# ===========================================================================
# check — mc_choice
# ===========================================================================

class TestCheckMcChoice:
    """Tests for the mc_choice checker."""

    def test_letter_match(self):
        out = check("mc4", "mc_choice", "I think the answer is B.", "B")
        assert out.result == CheckResult.PASS

    def test_letter_case_insensitive(self):
        out = check("mc4", "mc_choice", "The answer is b.", "B")
        assert out.result == CheckResult.PASS

    def test_letter_wrong(self):
        out = check("mc4", "mc_choice", "It's C.", "B")
        assert out.result == CheckResult.FAIL

    def test_digit_choice(self):
        out = check("mc4", "mc_choice", "My answer is 3.", "3")
        assert out.result == CheckResult.PASS

    def test_bad_gt_safe_reject(self):
        out = check("mc4", "mc_choice", "A", "Z")
        assert out.result == CheckResult.SAFE_REJECT

    def test_no_choice_found(self):
        out = check("mc4", "mc_choice", "I have no idea.", "B")
        assert out.result == CheckResult.EXTRACT_FAIL


# ===========================================================================
# check — none (free_text)
# ===========================================================================

class TestCheckNone:
    def test_always_pass(self):
        out = check("free_text", "none", "Anything at all here.", "")
        assert out.result == CheckResult.PASS

    def test_empty_still_pass(self):
        out = check("free_text", "none", "Some text", "ignored")
        assert out.result == CheckResult.PASS


# ===========================================================================
# check — unknown checker
# ===========================================================================

class TestCheckUnknownChecker:
    def test_unknown_checker_safe_reject(self):
        out = check("fraction", "nonexistent_checker", "1/2", "1/2")
        assert out.result == CheckResult.SAFE_REJECT


# ===========================================================================
# T1.3 Extraction-failure rate corpus test
# ≥30 cases; assert <5% extraction failure rate
# ===========================================================================

# Each tuple: (llm_output, answer_type, should_extract: bool)
# "should_extract" = True means we expect extract_answer to return a non-None value.
# We measure: fraction of cases where should_extract=True but extract_answer returned None.

_EXTRACTION_CORPUS: list[tuple[str, str, bool]] = [
    # --- Fraction extractions (should succeed) ---
    ("The answer is 1/2.", "fraction", True),
    ("So the result is 3/4.", "fraction", True),
    ("Total: 5/8 of the pizza.", "fraction", True),
    ("She ate 2/3 of the cake.", "fraction", True),
    ("He walked 1 1/2 km.", "fraction", True),
    ("The fraction is 0/5.", "fraction", True),
    ("Result: 4/4.", "fraction", True),
    ("Working: a + b = 2/4. <answer>1/2</answer>", "fraction", True),
    ("The piece is ½ of the whole.", "fraction", True),
    ("It measures ¾.", "fraction", True),
    ("So 6/9 of the bar is left.", "fraction", True),
    ("The answer is 7/10.", "fraction", True),
    ("She has 3/7 remaining.", "fraction", True),
    ("That gives us 5/3.", "fraction", True),
    ("I get 2 3/4.", "fraction", True),
    # --- Integer extractions (should succeed) ---
    ("Each person gets 4.", "int", True),
    ("The total is 12 pencils.", "int", True),
    ("You have 0 left.", "int", True),
    ("She has 100 marbles.", "int", True),
    ("The answer: 6.", "int", True),
    # --- MC extractions (should succeed) ---
    ("My answer is B.", "mc4", True),
    ("(C) is the correct choice.", "mc4", True),
    ("I pick 2.", "mc4", True),
    ("Answer: D", "mc4", True),
    ("choice: a", "mc4", True),
    # --- Intentional extraction failures (should NOT succeed, should_extract=False) ---
    ("", "fraction", False),                        # empty
    ("I don't know.", "fraction", False),            # no fraction
    ("a/b or x/y", "fraction", False),              # non-numeric fraction-like — no numeric
    ("   ", "int", False),                          # whitespace only
    ("No clue here.", "mc4", False),                # no MC choice
]


class TestExtractionCorpus:
    """
    T1.3 requirement: extraction-failure rate <5% on cases where extraction is expected.
    """

    def test_extraction_failure_rate(self):
        expected_successes = [case for case in _EXTRACTION_CORPUS if case[2]]
        failures = []
        for llm_output, answer_type, _ in expected_successes:
            result = extract_answer(llm_output, answer_type)
            if result is None:
                failures.append((llm_output, answer_type))

        total = len(expected_successes)
        failure_count = len(failures)
        failure_rate = failure_count / total if total > 0 else 0.0

        assert total >= 25, f"Corpus too small: {total} expected-success cases (need ≥25)"
        assert failure_rate < 0.05, (
            f"Extraction failure rate {failure_rate:.1%} ({failure_count}/{total}) "
            f"exceeds 5% limit.\nFailed cases:\n"
            + "\n".join(f"  {o!r} ({t})" for o, t in failures)
        )

    def test_expected_no_extraction(self):
        """Cases marked should_extract=False must return None."""
        non_extracts = [case for case in _EXTRACTION_CORPUS if not case[2]]
        for llm_output, answer_type, _ in non_extracts:
            result = extract_answer(llm_output, answer_type)
            assert result is None, (
                f"Expected None for {llm_output!r} (type={answer_type}), got {result!r}"
            )

    def test_corpus_has_30_cases(self):
        assert len(_EXTRACTION_CORPUS) >= 30, (
            f"Corpus only has {len(_EXTRACTION_CORPUS)} cases; need ≥30 (T1.3)"
        )
