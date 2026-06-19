"""
tests/engine/test_verifier.py — T3.5 runtime verifier integration tests.

Per SPEC §15 Layer 2 and TESTS.md T3.5:
  "any LLM-generated worked step or answer in pilot domain is computationally checked
   BEFORE display; failure → regenerate or fall back to vetted variant."

This module tests the serve_with_check() pipeline function, which wraps the verifier
for runtime use in src/mentar/engine/.  The verifier itself lives at
src/mentar/eval/verify_numeric.py (shared between eval-time T1.3 and runtime T3.5).

Test cases:
- Correct answer → ('serve', llm_out) — output served to child
- Wrong answer   → ('fallback', reason) — fallback fires; wrong output NOT served
- SAFE_REJECT    → ('fallback', reason) — fallback fires on malformed input
- EXTRACT_FAIL   → ('fallback', reason) — fallback fires when no answer can be found
- Deliberately wrong explanation "2/4 + 1/4 = 4/8" blocked (T3.5 integration case)
"""

from __future__ import annotations

from mentar.eval.verify_numeric import CheckOutcome, CheckResult, check

# ---------------------------------------------------------------------------
# The thin pipeline function (represents the engine's serve-time wrapper).
# In production this lives in src/mentar/engine/; here we define it inline so
# the integration test is self-contained and doesn't depend on unfinished engine code.
# ---------------------------------------------------------------------------

def serve_with_check(
    llm_out: str,
    expected: str,
    checker: str,
    answer_type: str,
) -> tuple[str, str]:
    """
    Minimal serve-time pipeline:
      1. Run the deterministic verifier.
      2. If PASS  → return ('serve', llm_out)
      3. Otherwise → return ('fallback', <detail string>)

    This matches the SPEC §15 L2 pattern: check before display; on failure,
    regenerate or fall back to vetted variant (here: just the fallback signal).

    Returns
    -------
    ('serve', llm_out)   — safe to display to the child
    ('fallback', reason) — do NOT display; use vetted variant or regenerate
    """
    outcome: CheckOutcome = check(answer_type, checker, llm_out, expected)
    if outcome.result == CheckResult.PASS:
        return ("serve", llm_out)
    # Any non-PASS (FAIL, EXTRACT_FAIL, SAFE_REJECT) → fallback
    return ("fallback", outcome.detail)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestServeWithCheck:
    """Integration tests for the runtime verifier pipeline."""

    # --- Correct answers → serve ---

    def test_correct_fraction_served(self):
        """Correct fraction 3/4 → served to child."""
        action, payload = serve_with_check(
            "You ate 2/8 + 1/8, so 3/8 of the pizza. The answer is 3/4.",
            "3/4",
            "fraction_equiv",
            "fraction",
        )
        assert action == "serve"
        assert payload  # non-empty

    def test_correct_equivalent_fraction_served(self):
        """2/4 is equivalent to 1/2 → PASS → serve."""
        action, _ = serve_with_check(
            "The answer is 2/4.",
            "1/2",
            "fraction_equiv",
            "fraction",
        )
        assert action == "serve"

    def test_correct_integer_served(self):
        """12 pencils shared among 4 = 3 each → PASS → serve."""
        action, _ = serve_with_check(
            "Each friend gets 3 pencils.",
            "3",
            "int_exact",
            "int",
        )
        assert action == "serve"

    def test_correct_mc_choice_served(self):
        action, _ = serve_with_check(
            "The correct choice is B.",
            "B",
            "mc_choice",
            "mc4",
        )
        assert action == "serve"

    def test_none_checker_always_served(self):
        """free_text with checker='none' always passes → serve."""
        action, _ = serve_with_check(
            "The answer can be anything.",
            "",
            "none",
            "free_text",
        )
        assert action == "serve"

    # --- T3.5 integration case: deliberately wrong explanation blocked ---

    def test_wrong_addition_explanation_blocked(self):
        """
        T3.5 canonical case:
        LLM claims "2/4 + 1/4 = 4/8" — wrong answer (correct is 3/4).
        The verifier must BLOCK this (fallback), not serve it to the child.
        """
        wrong_explanation = (
            "When you add fractions, you add both the top AND the bottom numbers. "
            "So 2/4 + 1/4 = 4/8. The answer is 4/8."
        )
        action, reason = serve_with_check(
            wrong_explanation,
            "3/4",   # correct answer is 3/4 (or equivalently 2/4+1/4 = 3/4)
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback", (
            "Wrong explanation '2/4 + 1/4 = 4/8' should be BLOCKED, not served to a child. "
            f"Got action={action!r}, reason={reason!r}"
        )
        assert reason, "Fallback must provide a non-empty reason."

    def test_wrong_fraction_blocked(self):
        """Correct answer 1/2 but LLM gives 1/4 → fallback."""
        action, reason = serve_with_check(
            "The piece is 1/4 of the whole.",
            "1/2",
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback"
        assert reason

    def test_wrong_integer_blocked(self):
        """Correct answer 4 but LLM says 5 → fallback."""
        action, reason = serve_with_check(
            "Each child gets 5 pencils.",
            "4",
            "int_exact",
            "int",
        )
        assert action == "fallback"

    # --- SAFE_REJECT → fallback ---

    def test_zero_denominator_fallback(self):
        """'1/0' is a zero-denominator → SAFE_REJECT → fallback (never serve)."""
        action, reason = serve_with_check(
            "The answer is 1/0.",
            "1/2",
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback"
        assert reason

    def test_ambiguous_or_fraction_fallback(self):
        """'1/2 or 3/4' is ambiguous → SAFE_REJECT → fallback."""
        action, reason = serve_with_check(
            "The answer is 1/2 or 3/4.",
            "1/2",
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback"

    def test_decimal_answer_safe_reject_fallback(self):
        """Decimal ground_truth '0.5' → SAFE_REJECT → fallback."""
        action, reason = serve_with_check(
            "The answer is 1/2.",
            "0.5",   # decimal GT not in pilot scope
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback"

    # --- EXTRACT_FAIL → fallback ---

    def test_no_answer_in_output_fallback(self):
        """LLM output has no fraction or integer → EXTRACT_FAIL → fallback."""
        action, reason = serve_with_check(
            "That is a really good question!",
            "1/2",
            "fraction_equiv",
            "fraction",
        )
        assert action == "fallback"

    def test_empty_output_fallback(self):
        """Empty LLM output → EXTRACT_FAIL → fallback (never crash)."""
        action, reason = serve_with_check(
            "",
            "3",
            "int_exact",
            "int",
        )
        assert action == "fallback"

    # --- Robustness: pipeline never crashes ---

    def test_none_input_does_not_crash(self):
        """Even if someone passes an empty string, we get fallback, not an exception."""
        action, reason = serve_with_check("", "1/2", "fraction_equiv", "fraction")
        assert action == "fallback"

    def test_garbage_checker_does_not_crash(self):
        """Unknown checker type → SAFE_REJECT → fallback, never crash."""
        action, reason = serve_with_check(
            "The answer is 1/2.",
            "1/2",
            "invented_checker",
            "fraction",
        )
        assert action == "fallback"


class TestServeReturnTypes:
    """Smoke tests verifying the return-type contract of serve_with_check."""

    def test_return_is_tuple_of_two(self):
        result = serve_with_check("The answer is 3.", "3", "int_exact", "int")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_serve_or_fallback(self):
        for llm_out, expected in [("The answer is 3.", "3"), ("wrong", "99")]:
            action, _ = serve_with_check(llm_out, expected, "int_exact", "int")
            assert action in ("serve", "fallback")

    def test_fallback_reason_is_nonempty_string(self):
        action, reason = serve_with_check("wrong answer", "99", "int_exact", "int")
        assert action == "fallback"
        assert isinstance(reason, str)
        assert len(reason) > 0
