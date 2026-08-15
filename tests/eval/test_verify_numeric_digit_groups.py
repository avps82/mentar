"""eval/verify_numeric.py — thousands separators must not credit a wrong answer.

Why this file exists: a probe on 2026-08-16 found the verifier's one genuinely
damaging failure mode — a FALSE ACCEPT. `extract_answer` reached the
"last integer" rule with the comma still in the string, so a grouped number was
read as its LAST GROUP only:

    "2,500"      -> "500"      truth 500     -> PASS   (child answered 2,500)
    "1,000"      -> "000" (0)  truth 0       -> PASS
    "12,345"     -> "345"      truth 345     -> PASS
    "1,000,000"  -> "000" (0)  truth 0       -> PASS

A wrong answer scored as right is worse than a right answer scored as wrong: it
feeds a false win into BKT mastery, so the engine concludes the child has a skill
they do not have and stops teaching it. It also failed in the ordinary direction
("1,000" against truth 1000 was marked wrong).

The web int widget is `type="number"`, which blocks commas in a browser — but
that is defence-in-depth, not the boundary (the maintainer's own framing). The
CLI takes free text, and this same function verifies LLM output.

Fix: strip commas sitting BETWEEN digits, before extraction, at the single choke
point every checker routes through. Indian lakh grouping is covered by the same
rule; a period decimal point is assumed, which holds for every country Mentar
ships (AU/IN/US/SG).

    python3 -m pytest tests/eval/test_verify_numeric_digit_groups.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.eval.verify_numeric import CheckResult, check, extract_answer  # noqa: E402


def _result(llm_output: str, ground_truth: str) -> CheckResult:
    return check("int", "int_exact", llm_output, ground_truth).result


# ── the false accepts, pinned so they can never come back ────────────────────

def test_grouped_number_is_not_credited_as_its_last_group():
    """The bug: answering 2,500 when the truth is 500 was marked CORRECT."""
    for typed, truth in (("2,500", "500"), ("1,000", "0"),
                         ("12,345", "345"), ("1,000,000", "0")):
        assert _result(typed, truth) is not CheckResult.PASS, (
            f"FALSE ACCEPT: {typed!r} credited against truth {truth!r}"
        )


def test_grouped_number_scores_correct_when_it_is_correct():
    for typed, truth in (("1,000", "1000"), ("2,500", "2500"),
                         ("12,345", "12345"), ("1,00,000", "100000")):
        assert _result(typed, truth) is CheckResult.PASS, (
            f"{typed!r} should equal {truth!r}"
        )


def test_extraction_reads_the_whole_grouped_number():
    assert extract_answer("1,000", "int") == "1000"
    assert extract_answer("1,00,000", "int") == "100000"     # Indian lakh grouping
    assert extract_answer("the answer is 12,345.", "int") == "12345"


# ── the separator rule must not eat list commas ──────────────────────────────

def test_comma_plus_space_is_still_a_list_and_stays_ambiguous():
    """Only comma-BETWEEN-digits is a group separator. A list is written with a
    space after the comma, so the equal-precedence ambiguity rule still fires."""
    assert extract_answer("1/2, 3/4", "fraction") is None


def test_decimals_are_untouched():
    assert extract_answer("2.5", "decimal") == "2.5"
    assert check("decimal", "decimal_exact", "0.50", "0.5").result is CheckResult.PASS


def test_decimal_safe_reject_still_bites_for_int_answers():
    """The pre-extraction decimal guard is safety-critical; stripping group
    separators must not create a path around it."""
    assert check("int", "int_exact", "0.5", "1").result is CheckResult.SAFE_REJECT


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
