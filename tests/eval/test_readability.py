"""Tests for eval/readability.py (deterministic Flesch-Kincaid age-appropriateness signal).

Inline smoke runner: python3 tests/eval/test_readability.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "eval"))

import readability as rb  # noqa: E402


def test_count_syllables():
    assert rb.count_syllables("the") == 1          # silent-e drops to 0 -> floored to 1
    assert rb.count_syllables("cake") == 1         # a + silent e
    assert rb.count_syllables("banana") == 3
    assert rb.count_syllables("education") == 4     # e-du-ca-tion (io = one group)
    assert rb.count_syllables("") == 0
    assert rb.count_syllables("rhythm") >= 1        # 'y' counts; never 0


def test_grade_empty_and_no_punctuation():
    assert rb.flesch_kincaid_grade("") == 0.0
    assert rb.flesch_kincaid_grade("   \n ") == 0.0
    # no sentence punctuation -> sentences falls back to 1 (no crash)
    g = rb.flesch_kincaid_grade("share twelve apples among three friends")
    assert isinstance(g, float)


def test_simple_reads_easier_than_complex():
    simple = "A quarter is one of four equal pieces of a thing."
    complex_ = "The denominator quantifies the cardinality of equipartitioned subdivisions."
    assert rb.flesch_kincaid_grade(simple) < rb.flesch_kincaid_grade(complex_)


def test_age_appropriate_flag():
    assert rb.is_age_appropriate("Cut the cake into four equal bits. Each bit is one fourth.")
    assert not rb.is_age_appropriate(
        "The denominator quantifies the cardinality of equipartitioned subdivisions of a referent.")


def _smoke():
    assert rb.count_syllables("banana") == 3 and rb.count_syllables("the") == 1
    assert rb.flesch_kincaid_grade("") == 0.0
    s = rb.flesch_kincaid_grade("A quarter is one of four equal pieces.")
    c = rb.flesch_kincaid_grade("The denominator quantifies equipartitioned subdivisions.")
    assert s < c, (s, c)
    assert rb.is_age_appropriate("Each slice is one fourth of the pizza.")
    print(f"[smoke] simple grade={s} < complex grade={c}; flags OK")
    print("[smoke] test_readability.py PASS")


if __name__ == "__main__":
    _smoke()
