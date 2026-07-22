"""explain_check.py — verify arithmetic claims embedded in free-form LLM text.

Spec: docs/SAFETY.md §6.2 Level 2 (verify numeric steps in Help re-explanations,
discard + regenerate on failure — SPEC's own "hallucination = safety failure" bar,
previously only enforced on child *answers* via eval/verify_numeric.check(), never
on the LLM's own worked-example prose).

Finds `a <op> b = c` claims (integers, fractions, mixed numbers, and division) in explanation
text and verifies each computationally, reusing verify_numeric.normalise_fraction
for parsing (same decimal-safe-reject, zero-denominator-safe-reject behaviour).

Pure + stdlib-only. Never raises — an unparseable claim is not a failure (prose
passes through unchecked; only a claim we CAN parse and get wrong is a failure).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mentar.eval.verify_numeric import normalise_fraction

_NUM = r"(?:\d+\s+\d+/\d+|\d+/\d+|\d+)"
# ponytail: only the plain "/" division operator is not matched — it collides with
# the fraction slash ("3/4 / 1/2"). "÷" and "divided by" are explicitly supported.
_OP = r"(?:[+\-×x*÷]|divided\s+by)"
# (?<!\d) — don't start a match inside a number (e.g. the "2" in "12").
# (?!\s*[+\-×÷*x\d]) — reject if the result is followed by an operator or digit,
# which means it's a mid-chain intermediate value, not a final result
# (e.g. "6 + 13 = 12 + 13 = 25" must not match "6 + 13 = 12" as a claim;
# the backtracked "6 + 13 = 1" attempt is also blocked because "1" is followed by "2").
_CLAIM_RE = re.compile(rf"(?<!\d)({_NUM})\s*({_OP})\s*({_NUM})\s*=\s*({_NUM})(?!\s*[+\-×÷*x\d])")

_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "x": lambda a, b: a * b,
    "*": lambda a, b: a * b,
    "÷": lambda a, b: a / b,
}


@dataclass
class ClaimCheck:
    claim_text: str
    ok: bool | None  # True = verified correct; False = verified WRONG; None = not checkable


def find_claims(text: str) -> list[ClaimCheck]:
    """Extract and verify every `a <op> b = c` claim in *text*."""
    if not text:
        return []
    results = []
    for m in _CLAIM_RE.finditer(text):
        lhs_a, op, lhs_b, rhs = m.groups()
        a = normalise_fraction(lhs_a)
        b = normalise_fraction(lhs_b)
        c = normalise_fraction(rhs)
        if a is None or b is None or c is None:
            results.append(ClaimCheck(m.group(0), None))
            continue
        op_key = "÷" if op.lower().startswith("divided") else op
        if op_key == "÷" and b == 0:
            results.append(ClaimCheck(m.group(0), None))
            continue
        computed = _OPS[op_key](a, b)
        results.append(ClaimCheck(m.group(0), computed == c))
    return results


def has_verified_failure(text: str) -> bool:
    """True if *text* contains at least one arithmetic claim that's provably wrong."""
    return any(c.ok is False for c in find_claims(text))
