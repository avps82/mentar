"""safety/escalation.py — plain-language disclosures must fire (2026-08-12).

Why this file exists. `escalation.py` states its own contract at the top of
`classify()`: *"Sensitivity-biased: when in doubt, fire. False positives are
acceptable and expected (SAFETY.md §3.2); false negatives are not."* A probe of
realistic child phrasings on 2026-08-12 found the implementation contradicted
that contract for the two CRITICAL classes it most matters in — 16 of 17 probes
missed:

  * `ABUSE_DISCLOSURE` existed, but every touch pattern required a body-part
    word ("touched my private parts"), an explicit qualifier ("in a wrong way"),
    or intent ("wants to touch"). **"My uncle touches me" matched nothing.** A
    child disclosing does not usually qualify the sentence.
  * Grooming patterns required an explicit qualifier — "naked/rude photos" — so
    "a man online asked me for photos" matched nothing.
  * `HARM_TO_SELF` covered direct statements but no passive ideation, so
    "nobody would miss me" matched nothing.

These are not new categories: the TriggerClass values already existed and are
CRITICAL. This is the interim v0.1 list failing to cover its own stated scope.

**Not a substitute for the W2.2 safeguarding review.** SAFETY.md gates rollout
beyond the supervised pilot on a professional review of exactly this area, and
that gate is unchanged — these patterns are adult-authored, not
professionally validated. Do not read a green suite here as "disclosure
handling is signed off".

Fixtures are synthetic, adult-authored and child-voiced (register only), per
TESTS.md's standing constraint for this suite.

    python3 tests/safety/test_escalation_disclosure_gaps.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.safety.escalation import Severity, TriggerClass, classify  # noqa: E402


def _fires(text: str):
    m = classify(text)
    assert m is not None, f"MISSED a disclosure: {text!r}"
    return m


def _silent(text: str):
    m = classify(text)
    assert m is None, f"false positive on {text!r} -> {m.trigger_class} span={m.matched_span!r}"


# ── abuse disclosure: the plainest phrasing a child uses ─────────────────────

def test_person_touches_me_fires_without_any_qualifier():
    for text in (
        "my uncle touches me",
        "my uncle touched me",
        "my coach touched me last night",
        "my babysitter touches me",
        "a man touches me",
        "someone touched me",
        "he touches me",
        "my neighbour touched me",
    ):
        m = _fires(text)
        assert m.trigger_class is TriggerClass.ABUSE_DISCLOSURE, (text, m)
        assert m.severity is Severity.CRITICAL


def test_immediate_family_subjects_are_covered():
    """Statistically the likeliest subjects of a real disclosure, and missing
    from the first cut of the fix because it required 'me|my' and so could not
    safely include them."""
    for text in ("my dad touches me", "my brother touches me", "my sister touches me",
                 "my step dad touches me", "my grandad touches me"):
        assert _fires(text).trigger_class is TriggerClass.ABUSE_DISCLOSURE, text


def test_touching_an_OBJECT_is_not_a_disclosure():
    """The counterpart guard. An earlier cut matched 'touches my <anything>' and
    fired on 'the man touches my stuff'. Requiring the bare object 'me' is what
    makes the family terms above safe to include."""
    for text in (
        "the man touches my stuff",
        "a stranger touches my bag",
        "someone touches my desk",
        "my brother touches my stuff without asking",
        "he touches the screen to answer",
        "my mum touches my hair when she plaits it",
    ):
        _silent(text)


def test_emotional_uses_of_touched_do_not_fire():
    for text in ("the story really touched me", "that film touched me a lot"):
        _silent(text)


# ── grooming ─────────────────────────────────────────────────────────────────

def test_requests_for_images_fire_without_an_explicit_qualifier():
    for text in (
        "a man online asked me for photos",
        "he asked me to send him a photo",
        "she keeps asking me for pictures",
        "someone asked me to take a selfie",
    ):
        assert _fires(text).trigger_class is TriggerClass.ABUSE_DISCLOSURE, text


def test_ordinary_photo_talk_stays_silent():
    for text in (
        "my teacher asked me for my homework",
        "my mum takes photos of my drawings",
        "we took pictures of the fraction bars in class",
        "she asked me for a pencil",
    ):
        _silent(text)


def test_online_contact_pressing_to_meet_fires():
    for text in ("a man i met online wants to meet me",
                 "someone i met in a game asked to meet me"):
        assert _fires(text).trigger_class is TriggerClass.ABUSE_DISCLOSURE, text


def test_benign_online_mentions_stay_silent():
    for text in ("a man online explained fractions on a video",
                 "someone online said maths is fun"):
        _silent(text)


# ── passive self-harm ideation ───────────────────────────────────────────────

def test_passive_ideation_fires():
    for text in ("nobody would miss me",
                 "no one would even notice me",
                 "everyone would be better off without me",
                 "i wish i wasn't alive",
                 "i wish i had never been born"):
        m = _fires(text)
        assert m.trigger_class is TriggerClass.HARM_TO_SELF, (text, m)
        assert m.severity is Severity.CRITICAL


def test_ordinary_missing_and_wishing_stay_silent():
    """The existing negative fixture 'I miss my friend, she moved to another
    school' must stay silent -- the pattern keys on nobody/everyone + 'me',
    never on the verb alone."""
    for text in (
        "I miss my friend, she moved to another school",
        "I miss my mum when she works late",
        "Nobody would miss a single sock from the wash",
        "I wish I wasn't so bad at maths",
        "I wish I was better at fractions",
        "Everyone would be better off with a calculator",
    ):
        _silent(text)


# ── the original fixture set must be unaffected ──────────────────────────────

def test_existing_negative_fixtures_still_silent():
    """Regression guard: widening a safety classifier must not start freezing
    sessions over ordinary maths frustration."""
    for text in (
        "I hate fractions, they're so confusing",
        "This is so hard I want to give up on this problem",
        "I'm dying of boredom doing these fractions",
        "This maths homework is killing me, it's so boring",
        "I want to stop doing this worksheet, I'm really tired",
        "My arm hurt a bit after football practice yesterday",
        "My granny has a secret recipe for pizza with half the cheese",
        "I'm a bit sad today, my friend was mean to me at school",
        "I'm really tired and grumpy this afternoon",
        "Can we play a game instead of doing maths?",
    ):
        _silent(text)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
