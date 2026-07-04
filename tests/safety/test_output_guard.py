"""T-A13 — output-side safety gate (safety/output_guard.py).

Spec: docs/SAFETY.md §2.1 (hard content blocks), §2.2 (curriculum scope).
Module under test: src/mentar/safety/output_guard.py

Inline smoke runner:
    python3 tests/safety/test_output_guard.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.safety.output_guard import BlockClass, screen_output


def test_clean_output_passes_byte_identical():
    text = "A fraction like 1/3 means one part out of three equal parts."
    out, incident = screen_output(text)
    assert out == text          # byte-identical, no mutation
    assert incident is None


def test_empty_output_passes_through():
    out, incident = screen_output("")
    assert out == ""
    assert incident is None


def test_sexual_content_minors_blocked():
    out, incident = screen_output("Let's talk about children having sex.")
    assert out is None
    assert incident is not None
    assert incident.block_class == BlockClass.SEXUAL_CONTENT_MINORS


def test_violent_harmful_blocked():
    out, incident = screen_output("Here are steps to suicide you could take.")
    assert out is None
    assert incident.block_class == BlockClass.VIOLENT_OR_HARMFUL


def test_adult_content_blocked():
    out, incident = screen_output("Here's how to get cocaine from a dealer.")
    assert out is None
    assert incident.block_class == BlockClass.ADULT_CONTENT


def test_off_scope_blocked():
    out, incident = screen_output("Let's discuss who you should vote for in the election.")
    assert out is None
    assert incident.block_class == BlockClass.OFF_SCOPE


def test_matched_span_not_full_text():
    """The incident carries a short matched span, not the full (possibly long,
    possibly explicit) output — the audit trail shouldn't durably store it."""
    long_text = "background words " * 50 + "how to make a bomb" + " more words " * 50
    out, incident = screen_output(long_text)
    assert out is None
    assert len(incident.matched_span) <= 80


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} output-guard tests passed.")
