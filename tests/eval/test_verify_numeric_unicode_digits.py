"""eval/verify_numeric.py — non-ASCII digits are accepted at their TRUE value.

Why this file exists: an adversarial sweep on 2026-08-12 found that a child
typing `٣` (Arabic-Indic three) or `３` (fullwidth three) is marked CORRECT for a
ground truth of `3`. That looks alarming until you check the other direction —
`٤` against `3` correctly FAILS, and `٣` against `4` correctly FAILS. The verifier
is reading these at their real numeric value, not pattern-matching a digit
somewhere in the string. So it is lenient in the SAFE direction: it accepts a
correct answer written in another numeral system, and never turns a wrong answer
into a right one.

**This behaviour is deliberate-by-consequence and must not be "hardened" away.**
Restricting the verifier to ASCII `[0-9]` would start rejecting correct answers
from a child using an Arabic-Indic or fullwidth keyboard — a real regression, and
the opposite of the accessibility posture the project claims. SAFETY.md §1.2's
English-only scope boundary is about the *trigger bank and handoff wording*, not
about which numerals a child may type.

These tests pin both directions so a future strictness pass has to make the
tradeoff knowingly rather than silently.

    python3 tests/eval/test_verify_numeric_unicode_digits.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def _int(out: str, gt: str):
    return check(answer_type="int", checker="int_exact", llm_output=out, ground_truth=gt).result


def _dec(out: str, gt: str):
    return check(answer_type="decimal", checker="decimal_exact", llm_output=out, ground_truth=gt).result


def test_non_ascii_digits_pass_when_the_value_is_right():
    """A correct answer stays correct whatever numeral system it is typed in."""
    assert _int("٣", "3") is CheckResult.PASS      # U+0663 arabic-indic three
    assert _int("３", "3") is CheckResult.PASS      # U+FF13 fullwidth three
    assert _int("۵", "5") is CheckResult.PASS      # U+06F5 extended-arabic five
    assert _dec("٣", "3") is CheckResult.PASS
    assert _dec("３", "3") is CheckResult.PASS


def test_non_ascii_digits_fail_when_the_value_is_wrong():
    """The safety-critical direction: leniency must never manufacture a PASS.

    If these ever start passing, the verifier has stopped reading the value and
    started pattern-matching, and a child can be told a wrong answer is right."""
    assert _int("٤", "3") is not CheckResult.PASS   # four vs three
    assert _int("٣", "4") is not CheckResult.PASS   # three vs four
    assert _int("３", "4") is not CheckResult.PASS


def test_non_digit_numerals_are_safely_refused_not_guessed():
    """Roman numerals and vulgar fractions are NOT decimal digits. The verifier
    must refuse them rather than guess an interpretation."""
    assert _int("Ⅲ", "3") is CheckResult.EXTRACT_FAIL      # U+2162 roman three
    assert _int("½", "0.5") is CheckResult.SAFE_REJECT     # decimal in an int slot


def test_the_existing_strictness_guarantees_still_hold():
    """Adjacent guarantees the sweep also checked -- kept here so a change to
    numeral handling can't quietly relax them."""
    assert _int("1e1", "10") is not CheckResult.PASS        # no exponent notation
    assert _int("3.0", "3") is CheckResult.SAFE_REJECT      # decimal in an int slot
    assert _int("3 or 4", "3") is not CheckResult.PASS      # ambiguous
    assert _dec("Infinity", "0.3") is not CheckResult.PASS
    assert _dec("NaN", "0.3") is not CheckResult.PASS


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
