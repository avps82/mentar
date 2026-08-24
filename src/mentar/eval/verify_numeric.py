"""
verify_numeric.py — Deterministic fraction/integer verifier for Mentar.

SAFETY-CRITICAL: per SPEC §15 Layer 2, every numeric/worked step the LLM generates
must be computationally verified BEFORE display.  A wrong-but-confident verification
is a safety failure.  Err on safe-reject over false-pass.

Supports T1.3 (eval-time scoring) and T3.5 (runtime serve-time gate).
Stdlib only — fractions.Fraction + re.  No third-party deps.

Design decisions documented inline:
- Decimals (e.g. "0.5") given to the `int`/`fraction` answer types: SAFE_REJECT.  Not in
  pilot scope for those two types (SPEC §23, fractions.md "Out of scope: decimal/fraction
  conversion").  Accepting decimals silently could produce a false-pass if the LLM gives
  "0.5" when the expected form is "1/2".  R13 (2026-07-19) adds a genuinely separate,
  dedicated `decimal`/`decimal_exact` answer type/checker for content that legitimately
  needs decimal answers (Y5+ measurement/currency) — the `int`/`fraction` decimal-reject
  guards below are UNCHANGED and remain load-bearing; `decimal_exact` is a pure addition,
  not a relaxation of them.
- Unicode vulgar fractions (½ ¼ ¾ etc.): mapped to their a/b equivalents before
  parsing — cheap via a small lookup table and avoids SAFE_REJECT on copy-paste input.
- Mixed numbers ("1 1/2"): parsed as whole + fraction; ambiguous forms with more than
  one space-separated token that look like independent fractions → SAFE_REJECT.
- Negative denominators: Fraction normalises these natively (e.g. 3/-6 → -1/2).
- Zero denominator: SAFE_REJECT (never crash, never accept).
- Multiple plausible candidates of equal precedence at the same position → SAFE_REJECT.
- MEASURED LENIENCY, accepted not fixed (2026-08-25 sweep). Extraction takes the first
  number it finds, so `decimal` accepts "4.0.0" against 4.0, and `int` accepts
  "4;DROP TABLE x" against 4. Both are technically false-passes against the
  err-on-safe-reject rule above. Left alone deliberately: the same leniency is what
  lets a child write "4 apples" or " 4 ", the strings are ones nobody types, and every
  LOAD-BEARING guard was re-verified intact in the same sweep (decimals into
  int/fraction all SAFE_REJECT, zero denominator SAFE_REJECT, ambiguous multi-fraction
  FAIL, 0 false passes across 6145 wrong answers drawn from real items). Tightening a
  safety-critical verifier for a hypothetical input carries more regression risk than
  the leniency carries harm. Recorded so the next reader knows it was measured and
  weighed, not missed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from fractions import Fraction

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class CheckResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    EXTRACT_FAIL = "extract_fail"   # could not locate a candidate answer
    SAFE_REJECT = "safe_reject"     # input malformed / ambiguous — refuse to verify


@dataclass
class CheckOutcome:
    result: CheckResult
    extracted: str | None           # what the verifier pulled out as the candidate
    canonical: str | None           # normalised form (e.g. "1/2") if extracted
    detail: str                     # human-readable explanation


# ---------------------------------------------------------------------------
# Unicode vulgar-fraction table (optional bonus — cheap lookup)
# ---------------------------------------------------------------------------

_UNICODE_FRACTIONS: dict[str, str] = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅕": "1/5",
    "⅖": "2/5",
    "⅗": "3/5",
    "⅘": "4/5",
    "⅙": "1/6",
    "⅚": "5/6",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
    "⅐": "1/7",
    "⅑": "1/9",
    "⅒": "1/10",
}

_UNICODE_FRAC_RE = re.compile("|".join(re.escape(c) for c in _UNICODE_FRACTIONS))


def _expand_unicode_fractions(text: str) -> str:
    """Replace Unicode vulgar-fraction characters with their a/b form."""
    return _UNICODE_FRAC_RE.sub(lambda m: _UNICODE_FRACTIONS[m.group()], text)


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Fraction pattern: optional leading sign, optional whole number, then a/b
# We deliberately do NOT allow spaces inside the numerator/denominator tokens.
# Matches: "1/2", "-3/5", "2/4", "10/3"
_FRAC_PAT = r"-?\d+\s*/\s*-?\d+"

# Mixed-number pattern: whole SP fraction (e.g. "1 1/2", "-2 3/4")
# Requires exactly one space between whole and fraction.
_MIXED_PAT = r"-?\d+\s+\d+\s*/\s*\d+"

# Pure integer (no slash)
_INT_PAT = r"-?\d+"

# <answer> tag extraction
_ANSWER_TAG_RE = re.compile(r"<answer>\s*(.*?)\s*</answer>", re.IGNORECASE | re.DOTALL)

# Multiple-choice letter (A-D) or digit (1-4), possibly in parentheses or quoted
_MC_LETTER_RE = re.compile(r"\b([A-Da-d])\b")
_MC_DIGIT_RE = re.compile(r"\b([1-4])\b")

# Full patterns compiled
_MIXED_RE = re.compile(_MIXED_PAT)
_FRAC_RE = re.compile(_FRAC_PAT)
_INT_RE = re.compile(_INT_PAT)

# Decimal detection — reject these explicitly
_DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")

# A comma sitting BETWEEN two digits is a digit-group separator ("2,500",
# "1,00,000"), never a list separator -- a list is written with a space after
# the comma. See extract_answer for why this must run before extraction.
_DIGIT_GROUP_SEP_RE = re.compile(r"(?<=\d),(?=\d)")


def strip_digit_group_separators(text: str) -> str:
    """Remove digit-GROUP commas ("1,200" -> "1200"), leaving list commas alone.

    Public because TWO modules must agree on this. engine/explain_check.py parses
    the same numerals out of LLM prose, and until 2026-08-18 it did not strip
    them: "1,200 + 300 = 1,500" matched as the claim "200 + 300 = 1", which is
    false, so a CORRECT explanation was discarded as a verified-wrong claim.
    Same root cause as the 2026-08-16 extract_answer fix, in the sibling that
    was missed. One function, so a third caller cannot drift again.
    """
    return _DIGIT_GROUP_SEP_RE.sub("", text)


# ---------------------------------------------------------------------------
# normalise_fraction
# ---------------------------------------------------------------------------

def normalise_fraction(s: str) -> Fraction | None:
    """
    Parse a fraction string and return a normalised Fraction, or None on failure.

    Accepted forms:
      - "1/2", "2/4", "-3/5"       → proper/improper fraction
      - "3"                          → integer (whole number)
      - "1 1/2", "2 3/4"            → mixed number (whole + fraction)
      - Unicode vulgar fractions via _expand_unicode_fractions pre-pass

    SAFE_REJECT (returns None) for:
      - Zero denominator ("1/0", "5/0")
      - Non-integer components ("a/b", "1.5/2")
      - Empty string
      - Anything that doesn't match the above forms
    """
    if not s or not s.strip():
        return None

    s = _expand_unicode_fractions(s.strip())

    # Decimal in the token → reject (not in pilot scope)
    if _DECIMAL_RE.search(s):
        return None

    # Try mixed number first ("1 1/2")
    mixed_m = re.fullmatch(r"\s*(-?\d+)\s+(\d+)\s*/\s*(\d+)\s*", s)
    if mixed_m:
        whole = int(mixed_m.group(1))
        num = int(mixed_m.group(2))
        den = int(mixed_m.group(3))
        if den == 0:
            return None  # SAFE_REJECT
        # mixed number sign: whole carries it; fraction part is always non-negative
        try:
            if whole < 0:
                return Fraction(whole * den - num, den)
            else:
                return Fraction(whole * den + num, den)
        except (ValueError, ZeroDivisionError):
            return None

    # Try plain fraction ("a/b")
    frac_m = re.fullmatch(r"\s*(-?\d+)\s*/\s*(-?\d+)\s*", s)
    if frac_m:
        num = int(frac_m.group(1))
        den = int(frac_m.group(2))
        if den == 0:
            return None  # SAFE_REJECT — zero denominator
        try:
            return Fraction(num, den)
        except (ValueError, ZeroDivisionError):
            return None

    # Try plain integer
    int_m = re.fullmatch(r"\s*(-?\d+)\s*", s)
    if int_m:
        return Fraction(int(int_m.group(1)))

    return None


# ---------------------------------------------------------------------------
# extract_answer
# ---------------------------------------------------------------------------

def extract_answer(text: str, answer_type: str) -> str | None:
    """
    Pull the candidate answer string from free-form LLM output.

    Returns None if no candidate can be unambiguously extracted.

    Strategy by answer_type:
      - "fraction" / "int":
          1. Last <answer>…</answer> tag content if present.
          2. Else last mixed-number pattern (e.g. "1 1/2").
          3. Else last fraction pattern (e.g. "2/4").
          4. Else last integer.
          Ambiguity rule: if two candidates of EQUAL precedence appear at the same
          'last position' (e.g. "1/2 or 3/4"), return None (SAFE_REJECT upstream).
      - "decimal" (R13):
          1. Last <answer>…</answer> tag content if present.
          2. Else last decimal-dotted token (e.g. "2.5").
          3. Else last integer (a bare int is a valid decimal-type answer too).
          Same 'or'-connective ambiguity rule as above.
      - "mc4":
          Last single letter A-D or digit 1-4 (case-insensitive), possibly in parens.
      - Other: None.

    Trailing punctuation (.!?,;:) and whitespace stripped before return.
    """
    if not text or not text.strip():
        return None

    # Expand unicode fractions first
    text_expanded = _expand_unicode_fractions(text)

    # Then remove digit-GROUP separators, before any extraction runs.
    #
    # 2026-08-16: "2,500" was split on the comma and the last-integer rule kept
    # "500" -- so a child who answered 2,500 when the truth was 500 was marked
    # CORRECT. Same for "1,000" -> "000" -> 0 (truth 0 passed) and "12,345" ->
    # "345". A FALSE ACCEPT is the one direction this module exists to prevent:
    # it credits a wrong answer and feeds a wrong win into BKT mastery.
    #
    # The web UI's int widget is type="number", which blocks commas in a
    # browser -- but that is defence-in-depth, not the boundary. The CLI takes
    # free text and this same function verifies LLM output.
    #
    # Comma-between-digits only, so "1/2, 3/4" (comma + SPACE) is untouched and
    # the ambiguity rule still sees two candidates. Handles Indian lakh grouping
    # ("1,00,000") as well as thousands. Assumes a period decimal point, which
    # holds for every country Mentar ships (AU/IN/US/SG).
    text_expanded = strip_digit_group_separators(text_expanded)

    if answer_type == "mc4":
        return _extract_mc(text_expanded)

    if answer_type in ("fraction", "int"):
        return _extract_numeric(text_expanded, answer_type)

    if answer_type == "decimal":
        return _extract_decimal(text_expanded)

    return None


def _strip_punct(s: str) -> str:
    """Strip trailing punctuation and whitespace."""
    return s.rstrip(".!?,;: \t\n")


def _extract_mc(text: str) -> str | None:
    """Extract last MC choice (A-D or 1-4) from text."""
    # Find all letter matches and digit matches
    letter_matches = list(_MC_LETTER_RE.finditer(text))
    digit_matches = list(_MC_DIGIT_RE.finditer(text))

    # Pick whichever type has its last match further right
    last_letter = letter_matches[-1] if letter_matches else None
    last_digit = digit_matches[-1] if digit_matches else None

    if last_letter and last_digit:
        if last_letter.start() > last_digit.start():
            return last_letter.group(1).upper()
        elif last_digit.start() > last_letter.start():
            return last_digit.group(1)
        else:
            # Same position — ambiguous; return letter (letters take priority for MC)
            return last_letter.group(1).upper()
    elif last_letter:
        return last_letter.group(1).upper()
    elif last_digit:
        return last_digit.group(1)
    return None


def _extract_numeric(text: str, answer_type: str) -> str | None:
    """
    Extract a numeric candidate from text.

    Priority:
    1. <answer> tag
    2. Last mixed number
    3. Last fraction
    4. Last integer (for answer_type="int" or as fallback for "fraction")

    Ambiguity: if the last position contains two distinct fraction candidates
    within 5 characters of each other (e.g. "1/2 or 3/4"), return None.
    """
    # 1. Try <answer> tag — use raw text (not expanded) to check for tag presence
    tag_match = _ANSWER_TAG_RE.search(text)
    if tag_match:
        content = _strip_punct(tag_match.group(1).strip())
        return content if content else None

    # 2. Check for decimal — if present, the extraction will surface it; we reject
    #    decimals in normalise_fraction, so we don't block extraction here.

    # 3. Find all mixed-number matches
    mixed_matches = list(_MIXED_RE.finditer(text))

    # 4. Find all fraction matches (exclude those that are part of a mixed number)
    frac_matches = list(_FRAC_RE.finditer(text))
    # Filter out fractions that are the trailing part of a mixed-number match
    mixed_spans = {(m.start(), m.end()) for m in mixed_matches}
    frac_matches_standalone = [
        m for m in frac_matches
        if not any(ms <= m.start() and m.end() <= me for ms, me in mixed_spans)
    ]

    # 5. Find all integer matches (exclude those inside fractions or mixed numbers)
    int_matches = list(_INT_RE.finditer(text))
    # Exclude integers that are substrings of fraction/mixed patterns
    all_numeric_spans = {(m.start(), m.end()) for m in mixed_matches} | \
                        {(m.start(), m.end()) for m in frac_matches}
    int_matches_standalone = [
        m for m in int_matches
        if not any(ms <= m.start() and m.end() <= me for ms, me in all_numeric_spans)
    ]

    # Select by precedence (mixed > fraction > int), using 'last' occurrence
    if mixed_matches:
        last_mixed = mixed_matches[-1]
        # Check for ambiguity: is there another fraction-level candidate within
        # 10 chars after the mixed match that isn't part of it?
        if frac_matches_standalone:
            last_frac = frac_matches_standalone[-1]
            # If both are within 10 chars of each other at the end, ambiguous
            if abs(last_frac.start() - last_mixed.start()) < 10:
                # Could be "1 1/2 or 3/4" — check if there's a connecting word
                between = text[min(last_mixed.end(), last_frac.end()):
                               max(last_mixed.start(), last_frac.start())]
                if re.search(r'\bor\b', between, re.IGNORECASE):
                    return None  # Ambiguous
        return _strip_punct(last_mixed.group())

    if frac_matches_standalone:
        last_frac = frac_matches_standalone[-1]
        # Ambiguity check: two fractions close together at the end
        if len(frac_matches_standalone) >= 2:
            second_last = frac_matches_standalone[-2]
            gap = text[second_last.end():last_frac.start()]
            if re.search(r'\bor\b', gap, re.IGNORECASE):
                return None  # "1/2 or 3/4" → ambiguous
            # Also check if they are very close without connective word
            if last_frac.start() - second_last.end() <= 5:
                return None  # Two fractions with no separator → ambiguous
        return _strip_punct(last_frac.group())

    if int_matches_standalone:
        last_int = int_matches_standalone[-1]
        return _strip_punct(last_int.group())

    return None


# ---------------------------------------------------------------------------
# Canonical string representation
# ---------------------------------------------------------------------------

def _canonical_str(f: Fraction) -> str:
    """Return the simplest string form of a normalised Fraction."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# check — main entry point
# ---------------------------------------------------------------------------

def check(
    answer_type: str,
    checker: str,
    llm_output: str,
    ground_truth: str,
) -> CheckOutcome:
    """
    Verify an LLM-generated answer against ground truth.

    Parameters
    ----------
    answer_type : str
        One of "int", "fraction", "decimal", "mc4", "free_text" (matches the curriculum
        template's verifier.answer_type).
    checker : str
        One of "int_exact", "fraction_equiv", "decimal_exact", "mc_choice", "none".
    llm_output : str
        The raw LLM-generated text containing (or purportedly containing) the answer.
    ground_truth : str
        The correct answer as a plain string (e.g. "3", "1/2", "A").

    Returns
    -------
    CheckOutcome
        result is PASS / FAIL / EXTRACT_FAIL / SAFE_REJECT.
        Never raises — all errors surface as SAFE_REJECT.
    """
    # Guard: empty input
    if not llm_output or not llm_output.strip():
        return CheckOutcome(
            result=CheckResult.EXTRACT_FAIL,
            extracted=None,
            canonical=None,
            detail="Empty llm_output — nothing to verify.",
        )

    # Dispatch
    try:
        if checker == "none":
            return _check_none()
        elif checker == "int_exact":
            return _check_int_exact(llm_output, ground_truth)
        elif checker == "fraction_equiv":
            return _check_fraction_equiv(llm_output, ground_truth)
        elif checker == "mc_choice":
            return _check_mc_choice(llm_output, ground_truth)
        elif checker == "decimal_exact":
            return _check_decimal_exact(llm_output, ground_truth)
        elif checker == "expression_equiv":
            return _check_expression_equiv(llm_output, ground_truth)
        else:
            return CheckOutcome(
                result=CheckResult.SAFE_REJECT,
                extracted=None,
                canonical=None,
                detail=f"Unknown checker '{checker}' — safe-reject to avoid false-pass.",
            )
    except Exception as exc:  # noqa: BLE001
        # Belt-and-suspenders: any unhandled exception → SAFE_REJECT, not crash
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"Unexpected error during verification: {exc!r} — safe-reject.",
        )


# ---------------------------------------------------------------------------
# Individual checker implementations
# ---------------------------------------------------------------------------

def _check_none() -> CheckOutcome:
    """Checker 'none' — always PASS (non-checkable free_text answers)."""
    return CheckOutcome(
        result=CheckResult.PASS,
        extracted=None,
        canonical=None,
        detail="Checker 'none': concept is non-checkable; auto-pass.",
    )


def _check_int_exact(llm_output: str, ground_truth: str) -> CheckOutcome:
    """
    Extract the last integer from llm_output and compare to int(ground_truth).
    Malformed ground_truth → SAFE_REJECT.
    """
    # Validate ground_truth
    try:
        gt_val = int(ground_truth.strip())
    except (ValueError, AttributeError):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth '{ground_truth}' is not a valid integer — safe-reject.",
        )

    # Pre-extraction decimal guard: an LLM answer of "0.5" must not silently
    # fall through to the integer extraction (which would grab "5" or "0").
    # Pilot-domain integer answers are whole-number division results.
    if _DECIMAL_RE.search(llm_output):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail="llm_output contains a decimal — pilot expects integer answers; safe-reject.",
        )

    # Extract candidate
    candidate = extract_answer(llm_output, "int")
    if candidate is None:
        return CheckOutcome(
            result=CheckResult.EXTRACT_FAIL,
            extracted=None,
            canonical=None,
            detail="Could not extract an integer candidate from llm_output.",
        )

    # Parse candidate as integer (it might look like a fraction — that's a fail not a reject)
    try:
        cand_val = int(candidate.strip())
    except ValueError:
        # Candidate extracted but not parseable as int (e.g. "3/4") — that's FAIL not SAFE_REJECT
        return CheckOutcome(
            result=CheckResult.FAIL,
            extracted=candidate,
            canonical=None,
            detail=f"Extracted '{candidate}' but could not parse as integer (expected {gt_val}).",
        )

    canonical = str(cand_val)
    result = CheckResult.PASS if cand_val == gt_val else CheckResult.FAIL
    detail = (
        f"Extracted {cand_val!r}, expected {gt_val!r}: {'match' if result == CheckResult.PASS else 'mismatch'}."
    )
    return CheckOutcome(result=result, extracted=candidate, canonical=canonical, detail=detail)


def _check_fraction_equiv(llm_output: str, ground_truth: str) -> CheckOutcome:
    """
    Extract a fraction/integer from llm_output, normalise both to Fraction,
    and compare for equivalence.

    Decimals in llm_output or ground_truth → SAFE_REJECT.
    Zero denominator → SAFE_REJECT.
    Unparseable → SAFE_REJECT (ground_truth) or EXTRACT_FAIL (candidate).
    """
    # Check for decimal in ground_truth → SAFE_REJECT (config error)
    if _DECIMAL_RE.search(ground_truth):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth '{ground_truth}' contains a decimal — not in pilot scope; safe-reject.",
        )

    # Check for decimal in llm_output BEFORE extraction. Without this, "0.5" falls
    # through to the trailing-integer fallback in _extract_numeric and produces a
    # confident-wrong FAIL ("5" extracted, compared to "1/2"). Decimals are out of
    # pilot scope (SPEC §23) — safe-reject any decimal-shaped LLM output.
    if _DECIMAL_RE.search(llm_output):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail="llm_output contains a decimal — not in pilot scope; safe-reject.",
        )

    # Parse ground_truth
    gt_frac = normalise_fraction(ground_truth.strip())
    if gt_frac is None:
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth '{ground_truth}' could not be normalised to a fraction — safe-reject.",
        )

    # Extract candidate from LLM output
    candidate = extract_answer(llm_output, "fraction")

    if candidate is None:
        # Check if extraction returned None due to ambiguity (two fractions with 'or')
        # vs. genuinely no fraction found — both are EXTRACT_FAIL at this level
        # (the ambiguity check inside extract_answer returns None for both)
        # We need to distinguish: if there ARE fraction-like tokens but we couldn't
        # choose, that's SAFE_REJECT; if there are none, that's EXTRACT_FAIL.
        # Heuristic: if there's a fraction pattern anywhere in the text, it's ambiguous.
        expanded = _expand_unicode_fractions(llm_output)
        has_frac = bool(_FRAC_RE.search(expanded)) or bool(_MIXED_RE.search(expanded))
        if has_frac:
            return CheckOutcome(
                result=CheckResult.SAFE_REJECT,
                extracted=None,
                canonical=None,
                detail="Multiple fraction candidates found but could not unambiguously select one — safe-reject.",
            )
        return CheckOutcome(
            result=CheckResult.EXTRACT_FAIL,
            extracted=None,
            canonical=None,
            detail="No fraction or integer candidate found in llm_output.",
        )

    # Detect decimal in extracted candidate
    if _DECIMAL_RE.search(candidate):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=candidate,
            canonical=None,
            detail=f"Extracted candidate '{candidate}' contains a decimal — not in pilot scope; safe-reject.",
        )

    # Normalise candidate
    cand_frac = normalise_fraction(candidate)
    if cand_frac is None:
        # Includes zero-denominator case
        if re.search(r"/\s*0\b", candidate):
            return CheckOutcome(
                result=CheckResult.SAFE_REJECT,
                extracted=candidate,
                canonical=None,
                detail=f"Extracted '{candidate}' has zero denominator — safe-reject.",
            )
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=candidate,
            canonical=None,
            detail=f"Extracted '{candidate}' could not be normalised — safe-reject.",
        )

    canonical = _canonical_str(cand_frac)
    gt_canonical = _canonical_str(gt_frac)
    result = CheckResult.PASS if cand_frac == gt_frac else CheckResult.FAIL
    detail = (
        f"Extracted '{candidate}' → {canonical}; "
        f"expected '{ground_truth}' → {gt_canonical}: "
        f"{'equivalent' if result == CheckResult.PASS else 'not equivalent'}."
    )
    return CheckOutcome(result=result, extracted=candidate, canonical=canonical, detail=detail)


# ---------------------------------------------------------------------------
# decimal answer type (R13, 2026-07-19) — a genuinely separate, additive path.
# Does NOT touch normalise_fraction's or _check_int_exact/_check_fraction_equiv's
# decimal-reject guards above; those stay exactly as they were.
# ---------------------------------------------------------------------------

# Strict pre-parse gate: fullmatch only, no exponent/NaN/Infinity. Decimal(s) on
# its own would silently ACCEPT "NaN", "Infinity", and "5E2" -- none of which a
# child would type and none of which should ever compare equal to a ground
# truth. This regex, not Decimal's own leniency, is the actual safety boundary.
_DECIMAL_STRICT_RE = re.compile(r"-?\d+(\.\d+)?$")
_DECIMAL_TOKEN_RE = re.compile(r"-?\d+\.\d+")


def normalise_decimal(s: str) -> Decimal | None:
    """Parse a strict decimal (or bare integer) string, or None on failure."""
    if not s or not s.strip():
        return None
    s = s.strip()
    if not _DECIMAL_STRICT_RE.fullmatch(s):
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _extract_decimal(text: str) -> str | None:
    """Extract a decimal (priority) or bare-integer (fallback) candidate, same
    last-occurrence + 'or'-ambiguity rules as _extract_numeric."""
    tag_match = _ANSWER_TAG_RE.search(text)
    if tag_match:
        res = tag_match.group(1).strip()
        return _strip_punct(res) if res else None

    dec_matches = list(_DECIMAL_TOKEN_RE.finditer(text))
    if dec_matches:
        last = dec_matches[-1]
        if len(dec_matches) > 1:
            prev = dec_matches[-2]
            between = text[prev.end():last.start()]
            if re.search(r"\bor\b", between, re.IGNORECASE) or (last.start() - prev.end() <= 5):
                return None
        return _strip_punct(last.group())

    int_matches = list(_INT_RE.finditer(text))
    if int_matches:
        last = int_matches[-1]
        if len(int_matches) > 1:
            prev = int_matches[-2]
            between = text[prev.end():last.start()]
            if re.search(r"\bor\b", between, re.IGNORECASE) or (last.start() - prev.end() <= 5):
                return None
        return _strip_punct(last.group())

    return None


def _canonical_decimal_str(d: Decimal) -> str:
    """Fixed-point canonical string (never exponential) with trailing zeros stripped."""
    return format(d.normalize(), "f")


def _check_decimal_exact(llm_output: str, ground_truth: str) -> CheckOutcome:
    """Extract a decimal/integer from llm_output and compare exactly to ground_truth."""
    gt_dec = normalise_decimal(ground_truth.strip())
    if gt_dec is None:
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth {ground_truth!r} could not be normalised to a decimal — safe-reject.",
        )

    candidate = extract_answer(llm_output, "decimal")
    if candidate is None:
        # Distinguish "genuinely nothing decimal-shaped" (EXTRACT_FAIL) from "a
        # decimal-shaped token IS present but extraction couldn't pick one
        # unambiguously" (SAFE_REJECT) -- same heuristic _check_fraction_equiv
        # uses for fractions. Only the decimal-dotted tier signals ambiguity
        # here; the bare-int fallback tier is too common in ordinary prose to
        # use as an ambiguity signal on its own.
        if _DECIMAL_TOKEN_RE.search(_expand_unicode_fractions(llm_output)):
            return CheckOutcome(
                result=CheckResult.SAFE_REJECT,
                extracted=None,
                canonical=None,
                detail="Multiple decimal candidates found but could not unambiguously select one — safe-reject.",
            )
        return CheckOutcome(
            result=CheckResult.EXTRACT_FAIL,
            extracted=None,
            canonical=None,
            detail="No decimal or integer candidate found in llm_output.",
        )

    cand_dec = normalise_decimal(candidate)
    if cand_dec is None:
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=candidate,
            canonical=None,
            detail=f"Extracted {candidate!r} could not be normalised — safe-reject.",
        )

    canonical = _canonical_decimal_str(cand_dec)
    gt_canonical = _canonical_decimal_str(gt_dec)
    result = CheckResult.PASS if cand_dec == gt_dec else CheckResult.FAIL
    detail = (
        f"Extracted {candidate!r} -> {canonical}; expected {ground_truth!r} -> "
        f"{gt_canonical}: {'match' if result == CheckResult.PASS else 'mismatch'}."
    )
    return CheckOutcome(result=result, extracted=candidate, canonical=canonical, detail=detail)


# ---------------------------------------------------------------------------
# expression answer type (B0, 2026-08-11) — a genuinely separate, additive path
# for Y9+ algebra, exactly the R13 pattern: zero edits to the int/fraction/
# decimal checkers above; their guards stay untouched.
#
# SAFETY: sympy's sympify/parse_expr is an eval-shaped surface — unrestricted
# input can reach function calls and dunder attributes. The gate below, NOT
# sympy's own leniency, is the actual safety boundary (same posture as R13's
# _DECIMAL_STRICT_RE before Decimal()):
#   * whole-string allowlist: digits, letters, + - * / ^ ( ) . and whitespace —
#     no commas (function args), no underscores (dunders), no quotes, no '='
#   * every alphabetic run must be a SINGLE letter — kills every function/
#     attribute name ("factorial", "exp", "__class__") while keeping x, y, 2ab
#   * hard length cap — no parser DoS from pathological input
# Anything the gate passes that sympy still can't parse -> SAFE_REJECT (never
# raises). sympy itself is imported LAZILY so this module keeps importing
# without it (same deferred-import pattern as grounding/reader.py's libzim);
# a missing sympy -> SAFE_REJECT with an explicit detail, never a crash.
# ---------------------------------------------------------------------------

_EXPR_ALLOWED_RE = re.compile(r"^[0-9a-zA-Z+\-*/^() \t.]{1,100}$")
_EXPR_MULTILETTER_RE = re.compile(r"[a-zA-Z]{2,}")

# Multiplication signs a child can SEE and therefore type. Method cards render
# multiplication as × (2026-08-16); before that a card could show "6 × (x + 7)"
# on one line and "6*(x + 7)" on the next, and a child copying the × form got
# SAFE_REJECT because × is not in the allowlist above.
#
# Normalised to "*" BEFORE that allowlist rather than added to it: the gate stays
# exactly as strict about every other non-ASCII character, which is the property
# it exists for. Same reasoning as the unicode-DIGIT handling -- accept what a
# correct answer can legitimately look like, without widening what may reach sympy.
_EXPR_MUL_SIGNS = str.maketrans({"×": "*", "·": "*", "⋅": "*"})


def _parse_expression(s: str):
    """Gate + parse one expression string -> sympy expr, or None (SAFE_REJECT).

    Child-friendly input forms: implicit multiplication ("2x", "2(x+3)") and
    caret exponents ("x^2") are accepted via sympy's standard transformations.
    """
    if not s or not s.strip():
        return None
    s = s.strip().translate(_EXPR_MUL_SIGNS)
    if not _EXPR_ALLOWED_RE.fullmatch(s):
        return None
    if _EXPR_MULTILETTER_RE.search(s):
        return None  # multi-letter name — function/attribute shaped; reject
    try:
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            parse_expr,
            standard_transformations,
        )
    except ImportError:
        return None
    try:
        return parse_expr(
            s,
            transformations=standard_transformations
            + (implicit_multiplication_application, convert_xor),
            evaluate=True,
        )
    except Exception:  # noqa: BLE001 — any parse failure is a SAFE_REJECT, never a crash
        return None


def _check_expression_equiv(llm_output: str, ground_truth: str) -> CheckOutcome:
    """Symbolic equivalence: PASS iff simplify(candidate - truth) == 0, so
    2(x+3) === 2x+6 and (x+1)^2 === x^2+2x+1. The candidate is the whole
    (stripped) llm_output, or the last <answer> tag's content when present —
    an expression can't be reliably fished out of surrounding prose the way a
    lone integer can, and the child's typed answer IS the whole input."""
    try:
        import sympy
    except ImportError:
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail="sympy not installed — expression checking unavailable; safe-reject.",
        )

    gt_expr = _parse_expression(ground_truth)
    if gt_expr is None:
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth {ground_truth!r} failed the expression gate — safe-reject.",
        )

    tag_match = _ANSWER_TAG_RE.search(llm_output)
    candidate = (tag_match.group(1) if tag_match else llm_output).strip()
    cand_expr = _parse_expression(candidate)
    if cand_expr is None:
        # Distinguish "gate/parse rejected it" (SAFE_REJECT — something
        # expression-shaped may be there but we refuse to guess) from
        # "nothing but whitespace" (EXTRACT_FAIL).
        if not candidate:
            return CheckOutcome(
                result=CheckResult.EXTRACT_FAIL,
                extracted=None,
                canonical=None,
                detail="Empty candidate — nothing to verify.",
            )
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=candidate,
            canonical=None,
            detail=f"Candidate {candidate!r} failed the expression gate/parse — safe-reject.",
        )

    try:
        equivalent = sympy.simplify(cand_expr - gt_expr) == 0
    except Exception as exc:  # noqa: BLE001
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=candidate,
            canonical=None,
            detail=f"simplify failed: {exc!r} — safe-reject.",
        )
    canonical = str(sympy.expand(cand_expr))
    result = CheckResult.PASS if equivalent else CheckResult.FAIL
    return CheckOutcome(
        result=result,
        extracted=candidate,
        canonical=canonical,
        detail=(
            f"Candidate {candidate!r} -> {canonical}; expected {ground_truth!r}: "
            f"{'equivalent' if equivalent else 'not equivalent'}."
        ),
    )


def _check_mc_choice(llm_output: str, ground_truth: str) -> CheckOutcome:
    """
    Extract the last MC choice (A-D or 1-4) from llm_output and compare
    case-insensitively to ground_truth.

    Malformed ground_truth → SAFE_REJECT.
    """
    # Validate ground_truth: must be A-D or 1-4
    gt = ground_truth.strip()
    if not re.fullmatch(r"[A-Da-d1-4]", gt):
        return CheckOutcome(
            result=CheckResult.SAFE_REJECT,
            extracted=None,
            canonical=None,
            detail=f"ground_truth '{gt}' is not a valid MC choice (A-D or 1-4) — safe-reject.",
        )

    candidate = extract_answer(llm_output, "mc4")
    if candidate is None:
        return CheckOutcome(
            result=CheckResult.EXTRACT_FAIL,
            extracted=None,
            canonical=None,
            detail="Could not extract an MC choice from llm_output.",
        )

    # Normalise: letters → uppercase, digits stay as-is
    cand_norm = candidate.upper() if candidate.isalpha() else candidate
    gt_norm = gt.upper() if gt.isalpha() else gt

    result = CheckResult.PASS if cand_norm == gt_norm else CheckResult.FAIL
    detail = (
        f"Extracted '{candidate}' (normalised '{cand_norm}'), "
        f"expected '{gt}' (normalised '{gt_norm}'): "
        f"{'match' if result == CheckResult.PASS else 'mismatch'}."
    )
    return CheckOutcome(result=result, extracted=candidate, canonical=cand_norm, detail=detail)
