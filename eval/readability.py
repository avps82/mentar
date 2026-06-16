#!/usr/bin/env python3
"""Deterministic readability — a cheap, judge-free age-appropriateness signal.

Complements the LLM judge's `age_appropriate` criterion (reduces single-judge reliance, one of the
alternatives surfaced in docs/MODEL.md). Computes the Flesch-Kincaid Grade Level:

    0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

Syllable count uses the standard vowel-group heuristic (it's an estimate — e.g. silent-`e` words
like "apple" are slightly under-counted; fine for a rough signal). Stdlib only.

(Note: routed to a local model as a "draft" experiment first, but qwen3:14b was too slow to use
interactively — written directly here instead.)
"""

from __future__ import annotations

import re

_VOWELS = "aeiouy"
_WORD_RE = re.compile(r"[A-Za-z]+")
_SENT_RE = re.compile(r"[.!?]+")

# A tutor explanation for a child of ~8-9 (Year 4 / US grade 3-4) should read easy — roughly FK ≤ 5.
YEAR4_MAX_GRADE = 5.0


def count_syllables(word: str) -> int:
    """Estimate syllables in one word via vowel groups (min 1; drop a silent trailing 'e')."""
    w = word.lower()
    if not w:
        return 0
    groups = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in _VOWELS
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel
    if w.endswith("e"):
        groups -= 1
    return max(1, groups)


def flesch_kincaid_grade(text: str) -> float:
    """Flesch-Kincaid Grade Level for ``text``. Returns 0.0 if there are no words."""
    words = _WORD_RE.findall(text)
    n_words = len(words)
    if n_words == 0:
        return 0.0
    n_sentences = len(_SENT_RE.findall(text)) or 1
    n_syll = sum(count_syllables(w) for w in words)
    return round(0.39 * (n_words / n_sentences) + 11.8 * (n_syll / n_words) - 15.59, 2)


def is_age_appropriate(text: str, max_grade: float = YEAR4_MAX_GRADE) -> bool:
    """Heuristic: True if the text reads at or below ``max_grade`` (default Year-4)."""
    return flesch_kincaid_grade(text) <= max_grade


if __name__ == "__main__":  # tiny demo
    for t in ["A quarter is one of four equal pieces of something.",
              "The denominator quantifies the cardinality of equipartitioned subdivisions."]:
        print(f"grade {flesch_kincaid_grade(t):5.1f}  age_ok={is_age_appropriate(t)}  | {t}")
