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

**Not a substitute for the W2.2 safeguarding review.** That review is sought
pro-bono (SAFETY.md §3.5.1 — unfunded OSS) and gates UNSUPERVISED mode, not the
supervised pilot; these patterns are adult-authored, not clinically validated.
Do not read a green suite here as "disclosure handling is signed off".

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


# ── 2026-08-15 sweep: the actor and the verb had to be ADJACENT ───────────────
# The same failure shape as the 2026-08-12 probe above, one layer down. The two
# actor->verb patterns read `(actor) (verb) me` with nothing allowed between, and
# carried only present tense in the active voice. So a child who put ANY words
# between the two, used the past tense, or said it passively was not heard:
#
#   "someone at home hits me"      actor and verb two words apart
#   "my mum shouts and hits me"    same, with a second verb in between
#   "my dad hurt me"               past tense ("hurts" was listed, "hurt" was not)
#   "i get hit at home"            passive voice, no actor named at all
#
# A child does not phrase a disclosure to fit a regex, which is the whole point of
# the sensitivity-biased contract this module states for itself.

_ADJACENCY_GAPS = [
    "someone at home hits me",
    "someone at home hurts me",
    "my mum shouts and hits me",
    "my dad hurt me",
    "my stepdad smacked me",
    "she shoved me",
    "i get hit at home",
    "i keep getting hit",
    "i am scared of my dad",
    "im scared of my carer",
]


def test_disclosures_fire_when_the_actor_and_verb_are_not_adjacent():
    for text in _ADJACENCY_GAPS:
        m = _fires(text)
        assert m.severity is Severity.CRITICAL, (text, m.severity)
        assert m.trigger_class in (
            TriggerClass.PHYSICAL_DANGER, TriggerClass.ABUSE_DISCLOSURE), (text, m.trigger_class)


# Widening the patterns must not turn ordinary lesson input into a frozen session
# and a parent handoff. These are answers and asides a child really types, chosen
# to sit as close to the new patterns as real input gets.
_ORDINARY_INPUT = [
    "4", "A", "1/2", "2x + 6", "0.75", "i dont know", "this is hard", "can you help me",
    "the answer is 12", "i think its b", "stop", "help", "?",
    "my dad helped me with this",
    "my mum said i should practise",
    "a ball hits the ground",
    "the sun hits the leaf",
    "the wind pushes the sail",
]


def test_widened_patterns_do_not_fire_on_ordinary_lesson_input():
    for text in _ORDINARY_INPUT:
        _silent(text)


# ── 2026-08-16 probe: inflection and possessive gaps ─────────────────────────
# A second probe of 31 child-voiced phrasings found six more misses with the same
# shape as the 2026-08-12 batch: the MEANING was already in scope and a sibling
# phrasing already fired, but one suffix or one dropped word walked straight
# through. Not new categories -- the same v0.1 list failing its own contract.

def test_gerund_self_harm_fires_like_the_infinitive():
    """"hurt myself" fired; "hurting myself" did not. One suffix apart."""
    for text in (
        "sometimes i think about hurting myself",
        "i keep thinking about harming myself",
    ):
        assert _fires(text).trigger_class is TriggerClass.HARM_TO_SELF


def test_not_wanting_to_be_alive_fires_like_not_wanting_to_be_here():
    """"be here anymore" fired; "be alive anymore" -- less ambiguous -- did not."""
    assert _fires("i dont want to be alive anymore").trigger_class is TriggerClass.HARM_TO_SELF


def test_whats_the_point_of_living_fires_like_no_reason_to_live():
    for text in ("whats the point of living", "what's the point in going on"):
        assert _fires(text).trigger_class is TriggerClass.HARM_TO_SELF


def test_bare_relative_fires_without_the_possessive():
    """"my dad hits me" fired; "dad hits me" did not -- and dropping the
    possessive is exactly how a child writes about their own household."""
    for text in (
        "dad hits me when hes drunk",
        "mum smacks me really hard",
        "uncle hit me again",
    ):
        assert _fires(text).trigger_class is TriggerClass.PHYSICAL_DANGER


def test_present_tense_crying_fires_like_the_perfect():
    """"i've been crying every night" fired; "i cry every night" did not."""
    assert _fires("i cry every night and cant tell anyone").trigger_class is (
        TriggerClass.SEVERE_DISTRESS
    )


# The widened actor list must not catch sport, cooking or word problems, where
# "<noun> hits me" is ordinary English.
def test_widened_actor_list_stays_silent_on_ordinary_uses():
    for text in (
        "my sister hits the ball in rounders",
        "the batter hits me a home run in the game",
        "teacher marks me down for spelling",
        "dad helped me with this one",
        "mum gave me a snack",
        "i cry laughing at this",
        "i cut the pizza into 4 pieces",
    ):
        _silent(text)
