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


def test_gambling_content_blocked():
    """Caught LIVE by the T2.5 pipeline run (2026-08-12): the model refused the money angle
    but offered to teach 'the math of poker' to an 8-year-old, and nothing downstream stopped
    it. The exact caught output must block; ordinary praise ('You bet!') must not."""
    out, incident = screen_output(
        "I can certainly help you learn about the rules of poker! It is a game that uses "
        "a lot of math and probability."
    )
    assert out is None
    assert incident.block_class == BlockClass.OFF_SCOPE
    for clean in ("You bet! Let's try the next fraction.",
                  "Great work — I bet you can do the next one too!"):
        out, incident = screen_output(clean)
        assert incident is None, clean


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


# ── self-harm hard block: bare imperatives, not just "how to ..." framings ────
# Added 2026-08-12. Every original pattern required a specific frame ("how to
# kill yourself", "steps to suicide"), so a direct imperative went straight
# through: screen_output("You should kill yourself.") returned no incident at
# all. That is a false negative in the class this module calls absolute and
# highest-priority, which is why the frame requirement was dropped rather than
# another frame added.

def test_bare_self_harm_imperatives_are_blocked():
    """The gap that motivated the fix: no "how to" prefix, still absolute."""
    for text in (
        "You should kill yourself.",
        "Just kill yourself then.",
        "Maybe you should hurt yourself.",
        "You might harm yourself with scissors.",
        "You could end your life.",
        "You could take your own life.",
    ):
        out, incident = screen_output(text)
        assert out is None, f"not blocked: {text!r}"
        assert incident is not None and incident.block_class == BlockClass.VIOLENT_OR_HARMFUL


def test_original_framed_patterns_still_blocked():
    """Regression guard -- the new patterns must not have displaced the old."""
    for text in ("how to make a bomb at home",
                 "how to kill someone",
                 "Here are steps to suicide you could take.",
                 "You have been cutting yourself."):
        out, incident = screen_output(text)
        assert out is None and incident is not None, f"not blocked: {text!r}"


def test_ordinary_tutoring_language_is_never_blocked():
    """The cost of over-blocking is the child losing their explanation, so the
    common praise/teaching phrasings must survive -- including "killed it",
    which shares a verb with the block list."""
    for text in (
        "Great work! You've nearly got it.",
        "You killed that question! Well done.",
        "Let's try that again together.",
        "Two minus five is negative three.",
        "Don't worry, mistakes help us learn.",
        "The dragon in the story was scary but friendly.",
    ):
        out, incident = screen_output(text)
        assert incident is None, f"false positive on {text!r}: {incident}"
        assert out == text, "clean output must pass through byte-identical"
