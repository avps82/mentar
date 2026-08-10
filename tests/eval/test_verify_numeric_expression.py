"""tests/eval/test_verify_numeric_expression.py — B0: expression answer type.

Tests the new answer_type="expression" / checker="expression_equiv" grammar in
eval/verify_numeric.py (sympy-backed symbolic equivalence for Y9+ algebra).
Purely additive — does not change int/fraction/decimal/mc4 behaviour
(TestExistingCheckersUnaffected pins that, mirroring the R13 decimal wave's
same marker class).

The pre-parse gate is SAFETY-CRITICAL: sympify/parse_expr is an eval-shaped
surface, and the gate (allowlist + single-letter-names + length cap), not
sympy's leniency, is the boundary. TestHostileInputsSafeRejected is the
regression net for that boundary — extend it, never weaken it.
"""

from __future__ import annotations

import sys
from unittest import mock

from mentar.eval.verify_numeric import CheckResult, _parse_expression, check


def _chk(llm_output: str, ground_truth: str):
    return check(
        answer_type="expression", checker="expression_equiv",
        llm_output=llm_output, ground_truth=ground_truth,
    )


class TestEquivalencePasses:
    def test_expanded_vs_factored(self):
        assert _chk("2x + 6", "2(x+3)").result is CheckResult.PASS

    def test_factored_vs_expanded(self):
        assert _chk("2(x+3)", "2x + 6").result is CheckResult.PASS

    def test_identical(self):
        assert _chk("3x + 1", "3x + 1").result is CheckResult.PASS

    def test_caret_exponent(self):
        assert _chk("x^2 + 2x + 1", "(x+1)^2").result is CheckResult.PASS

    def test_python_exponent(self):
        assert _chk("x**2 - 1", "(x-1)(x+1)").result is CheckResult.PASS

    def test_term_order_irrelevant(self):
        assert _chk("6 + 2x", "2x + 6").result is CheckResult.PASS

    def test_two_variables(self):
        assert _chk("a b + a c", "a(b + c)").result is CheckResult.PASS

    def test_plain_number_expression(self):
        assert _chk("12", "12").result is CheckResult.PASS

    def test_fractional_coefficient(self):
        assert _chk("x/2 + 1", "(x + 2)/2").result is CheckResult.PASS

    def test_answer_tag_extraction(self):
        assert _chk("So we get <answer>2x + 6</answer>", "2(x+3)").result is CheckResult.PASS


class TestNonEquivalenceFails:
    def test_wrong_constant(self):
        assert _chk("2x + 5", "2(x+3)").result is CheckResult.FAIL

    def test_wrong_coefficient(self):
        assert _chk("3x + 6", "2(x+3)").result is CheckResult.FAIL

    def test_wrong_sign(self):
        assert _chk("x^2 - 2x + 1", "(x+1)^2").result is CheckResult.FAIL

    def test_different_variable_is_not_equivalent(self):
        # y is not x — a child answering in the wrong variable is wrong, not right.
        assert _chk("2y + 6", "2(x+3)").result is CheckResult.FAIL


class TestHostileInputsSafeRejected:
    """The gate is the safety boundary — every one of these must SAFE_REJECT
    (or EXTRACT_FAIL for emptiness), and none may ever reach sympy's parser
    with dangerous content. Extend this class, never weaken it."""

    def test_function_call_blocked(self):
        assert _chk("factorial(100000)", "2x").result is CheckResult.SAFE_REJECT

    def test_multi_letter_name_blocked(self):
        assert _chk("exp(x)", "2x").result is CheckResult.SAFE_REJECT

    def test_dunder_blocked(self):
        assert _chk("__import__", "2x").result is CheckResult.SAFE_REJECT

    def test_underscore_blocked(self):
        assert _chk("_x + 1", "2x").result is CheckResult.SAFE_REJECT

    def test_comma_blocked(self):
        assert _chk("f(x, y)", "2x").result is CheckResult.SAFE_REJECT

    def test_quotes_blocked(self):
        assert _chk("'x' + 'y'", "2x").result is CheckResult.SAFE_REJECT

    def test_equals_sign_blocked(self):
        # An equation is not an expression — reject rather than guess a side.
        assert _chk("x = 3", "3").result is CheckResult.SAFE_REJECT

    def test_length_cap(self):
        assert _chk("x + " * 50 + "x", "2x").result is CheckResult.SAFE_REJECT

    def test_brackets_and_braces_blocked(self):
        assert _chk("[x for x in range(9)]", "2x").result is CheckResult.SAFE_REJECT
        assert _chk("{x: 1}", "2x").result is CheckResult.SAFE_REJECT

    def test_empty_is_extract_fail(self):
        assert _chk("", "2x").result is CheckResult.EXTRACT_FAIL

    def test_hostile_ground_truth_safe_rejected(self):
        # A misauthored template must fail safe, not execute.
        assert _chk("2x", "__import__('os')").result is CheckResult.SAFE_REJECT

    def test_gate_rejects_before_parse(self):
        # Belt-and-suspenders: the gate alone (no sympy involved) rejects these.
        for hostile in ("factorial(9)", "a__b", "x;y", "lambda x: x", "x÷y"):
            assert _parse_expression(hostile) is None, hostile


class TestMissingSympySafeRejects:
    def test_import_error_is_safe_reject_not_crash(self):
        with mock.patch.dict(sys.modules, {"sympy": None, "sympy.parsing.sympy_parser": None}):
            out = _chk("2x + 6", "2(x+3)")
        assert out.result is CheckResult.SAFE_REJECT
        assert "sympy" in out.detail


class TestExistingCheckersUnaffected:
    """Additive-only marker (same class the R13 decimal wave pinned): the
    int/fraction/decimal/mc4 paths behave exactly as before."""

    def test_int_path_untouched(self):
        assert check(answer_type="int", checker="int_exact",
                     llm_output="7", ground_truth="7").result is CheckResult.PASS

    def test_fraction_decimal_reject_untouched(self):
        assert check(answer_type="fraction", checker="fraction_equiv",
                     llm_output="0.5", ground_truth="1/2").result is CheckResult.SAFE_REJECT

    def test_decimal_path_untouched(self):
        assert check(answer_type="decimal", checker="decimal_exact",
                     llm_output="2.50", ground_truth="2.5").result is CheckResult.PASS

    def test_unknown_checker_still_safe_rejects(self):
        assert check(answer_type="expression", checker="not_a_checker",
                     llm_output="2x", ground_truth="2x").result is CheckResult.SAFE_REJECT


if __name__ == "__main__":
    import inspect
    n = 0
    for cls_name, cls in sorted(globals().items()):
        if inspect.isclass(cls) and cls_name.startswith("Test"):
            inst = cls()
            for name in sorted(dir(inst)):
                if name.startswith("test_"):
                    getattr(inst, name)()
                    n += 1
                    print(f"  ✓ {cls_name}.{name}")
    print(f"\n{n} expression-verifier tests passed.")
