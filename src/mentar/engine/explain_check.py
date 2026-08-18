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
from fractions import Fraction

from mentar.eval.verify_numeric import (
    normalise_decimal,
    normalise_fraction,
    strip_digit_group_separators,
)

# E2.3 (2026-08-10): decimals added. The original _NUM had no "." handling, so a
# decimal claim ("3.5 + 2.1 = 5.6") never matched _CLAIM_RE at all and SAFETY §6.2's
# verify-or-discard guard was silently inert for every decimal explanation — a gap,
# not a design choice, once R13 shipped decimal answer types (Y5-8 decimal content
# is live). Decimal alternative goes FIRST so "3.5" parses as one token, not "3"+".5".
_NUM = r"(?:\d+\.\d+|\d+\s+\d+/\d+|\d+/\d+|\d+)"
# A SIGNED number. Signed arithmetic is live content (Y7+ integers), and until
# 2026-08-18 no part of a signed claim matched: "5 - 8 = -4" produced no claim at
# all, so the verify-or-discard guard was inert for every signed explanation.
#
# The sign must be allowed on the OPERANDS too, not just the result. Allowing it
# only on the right-hand side would make "-5 + 2 = -3" match as "5 + 2 = -3" --
# turning a CORRECT explanation into a verified-wrong one. That is a worse bug
# than the gap it closes, which is why both ends move together.
_SNUM = rf"(?:[-−]?{_NUM})"
# ponytail: only the plain "/" division operator is not matched — it collides with
# the fraction slash ("3/4 / 1/2"). "÷" and "divided by" are explicitly supported.
_OP = r"(?:[+\-−×x*·⋅÷]|divided\s+by)"
# (?<![\d./]) — don't start a match inside a number (e.g. the "2" in "12"), NOR right
# after a decimal point or fraction slash (E2.3: "3.5/7 + 1.5 = 2" must not yield a
# phantom "5/7..." or "7 + 1.5 = 2" claim — starting mid-token verifies arithmetic the
# author never claimed and could flag a correct explanation as wrong). A token this
# gate skips entirely (a decimal-over-slash mongrel) simply produces NO claim:
# fail-open, same as any other unparseable prose.
# (?!\s*[+\-×÷*x\d]) — reject if the result is followed by an operator or digit,
# which means it's a mid-chain intermediate value, not a final result
# (e.g. "6 + 13 = 12 + 13 = 25" must not match "6 + 13 = 12" as a claim;
# the backtracked "6 + 13 = 1" attempt is also blocked because "1" is followed by "2").
_CLAIM_RE = re.compile(rf"(?<![\d./])({_SNUM})\s*({_OP})\s*({_SNUM})\s*=\s*({_SNUM})(?:\s+R\s+({_NUM}))?(?!\s*[+\-−×÷*x·⋅\d])")

_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    # U+2212 MINUS SIGN. Models emit it constantly, and until 2026-08-18 it was
    # absent here, so "9 − 4 = 6" produced NO claim and went unchecked.
    "−": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "x": lambda a, b: a * b,
    "*": lambda a, b: a * b,
    # Same story for the dot operators; verify_numeric already translates both.
    "·": lambda a, b: a * b,
    "⋅": lambda a, b: a * b,
    "÷": lambda a, b: a / b,
}


@dataclass
class ClaimCheck:
    claim_text: str
    ok: bool | None  # True = verified correct; False = verified WRONG; None = not checkable


def _parse_num(token: str):
    """One claim token -> exact Fraction, or None. Decimal-shaped tokens go through
    normalise_decimal (E2.3) then exact Fraction conversion — NOT through
    normalise_fraction, whose decimal-safe-reject guard is deliberate and untouched
    (it protects the child-ANSWER path; this is the explanation-CLAIM path)."""
    sign = 1
    token = token.strip()
    if token[:1] in ("-", "−"):
        sign, token = -1, token[1:]
    if "." in token:
        d = normalise_decimal(token)
        return sign * Fraction(d) if d is not None else None
    mag = normalise_fraction(token)
    return sign * mag if mag is not None else None


def find_claims(text: str) -> list[ClaimCheck]:
    """Extract and verify every `a <op> b = c` claim in *text*."""
    if not text:
        return []
    # Digit-group commas first, for the same reason extract_answer does it: an
    # unstripped "1,200 + 300 = 1,500" matched as "200 + 300 = 1" and reported a
    # CORRECT explanation as a verified-wrong claim, which discarded it and left
    # the child with the canned fallback hint instead (found 2026-08-18).
    text = strip_digit_group_separators(text)
    results = []
    for m in _CLAIM_RE.finditer(text):
        lhs_a, op, lhs_b, rhs, remainder = m.groups()
        a = _parse_num(lhs_a)
        b = _parse_num(lhs_b)
        c = _parse_num(rhs)
        if a is None or b is None or c is None:
            results.append(ClaimCheck(m.group(0), None))
            continue
        op_key = "÷" if op.lower().startswith("divided") else op
        if op_key == "÷" and b == 0:
            results.append(ClaimCheck(m.group(0), None))
            continue
        if remainder is not None and op_key == "÷":
            r_val = normalise_fraction(remainder)
            if r_val is None:
                results.append(ClaimCheck(m.group(0), None))
                continue
            results.append(ClaimCheck(m.group(0), (a == c * b + r_val) and (0 <= r_val < b)))
        else:
            computed = _OPS[op_key](a, b)
            results.append(ClaimCheck(m.group(0), computed == c))
    return results


def has_verified_failure(text: str) -> bool:
    """True if *text* contains at least one arithmetic claim that's provably wrong."""
    return any(c.ok is False for c in find_claims(text))


# ── Algebra block alignment ──────────────────────────────────────────────────

# Matches a step line: 2+ space indent, expression, 2+ spaces, = , content
_STEP_RE = re.compile(r'^( {2,})(\S.*?)\s{2,}=\s+(.+)$')
# Splits the RHS from the ← annotation (2+ spaces before ←)
_ANN_RE = re.compile(r'\s{2,}(←.*)')


def _parse_step(line: str):
    m = _STEP_RE.match(line)
    if not m:
        return None
    indent, lhs, rest = m.group(1), m.group(2).rstrip(), m.group(3)
    ann_m = _ANN_RE.search(rest)
    if ann_m:
        rhs = rest[:ann_m.start()].rstrip()
        ann = ann_m.group(1)
    else:
        rhs = rest.rstrip()
        ann = ''
    return indent, lhs, rhs, ann


def _realign_block(lines: list) -> list:
    parsed = [_parse_step(line) for line in lines]
    valid = [p for p in parsed if p]
    if not valid:
        return lines
    max_lhs = max(len(p[1]) for p in valid)
    annotated = [p for p in valid if p[3]]
    max_rhs = max(len(p[2]) for p in annotated) if annotated else 0
    indent = valid[0][0]
    result = []
    for i, p in enumerate(parsed):
        if p is None:
            result.append(lines[i])
            continue
        _, lhs, rhs, ann = p
        lhs_pad = ' ' * (max_lhs - len(lhs) + 4)
        if ann:
            rhs_pad = ' ' * (max_rhs - len(rhs) + 4)
            result.append(f"{indent}{lhs}{lhs_pad}= {rhs}{rhs_pad}{ann}")
        else:
            result.append(f"{indent}{lhs}{lhs_pad}= {rhs}")
    return result


def realign_algebra_blocks(text: str) -> str:
    """Post-process explanation text: find indented algebra step blocks and
    re-align the = column (pad every LHS to the longest) and ← column
    (pad every annotated RHS to the longest). Returns text unchanged if no
    block is found."""
    if '=' not in text:
        return text
    lines = text.split('\n')
    out: list[str] = []
    i = 0
    while i < len(lines):
        if _STEP_RE.match(lines[i]):
            j = i
            while j < len(lines) and (_STEP_RE.match(lines[j]) or not lines[j].strip()):
                j += 1
            block = lines[i:j]
            if sum(1 for ln in block if _STEP_RE.match(ln)) >= 2:
                block = _realign_block(block)
            out.extend(block)
            i = j
        else:
            out.append(lines[i])
            i += 1
    return '\n'.join(out)

