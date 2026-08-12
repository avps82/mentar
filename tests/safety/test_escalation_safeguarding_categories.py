"""safety/escalation.py — coverage of established safeguarding categories.

Written after a 2026-08-12 category-coverage review that probed the classifier
against recognised child-safeguarding taxonomies (physical/sexual/emotional
abuse, neglect, domestic abuse, peer violence, online harms). Whole categories
that SAFETY.md §3.2 already lists as in-scope had ZERO patterns:

  Category A (§3.2, "dangerous location or situation", "physical abuse by
    another person") — no peer violence, no witnessing domestic violence, no
    neglect/running-away indicators.
  Category B (§3.2, "being emotionally or psychologically abused") — the bank
    only covered the child's OWN despair, nothing for abuse BY someone.
  Category C (§3.2, exploitation) — no sextortion / online-coercion patterns.

This is the interim v0.1 list failing to cover its own stated scope, so these
are additions to a fix, not new scope.

**NOT the W2.2 professional safeguarding review.** These patterns are
adult-authored and engineering-reviewed, not clinically validated. That review is
sought pro-bono (SAFETY.md §3.5.1 — an unfunded OSS project cannot commission it)
and gates UNSUPERVISED mode, not the supervised pilot. A green suite here is
coverage, not clinical sign-off. Fixtures are synthetic, adult-authored, child-voiced (register
only), per TESTS.md's standing constraint.

    python3 tests/safety/test_escalation_safeguarding_categories.py
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.safety.escalation import Severity, classify  # noqa: E402


def _fires(text: str):
    m = classify(text)
    assert m is not None, f"a safeguarding disclosure was MISSED: {text!r}"
    return m


def _silent(text: str):
    m = classify(text)
    assert m is None, f"false positive on {text!r} -> {m.trigger_class} span={m.matched_span!r}"


# ── peer violence / bullying with a physical element ─────────────────────────

def test_physical_violence_by_peers_fires():
    for text in (
        "kids at school hit me every day and i'm scared to go",
        "a boy at school keeps hurting me at lunch",
        "they said they'll beat me up tomorrow",
        "i'm scared to go to school",
    ):
        assert _fires(text).severity is Severity.CRITICAL, text


def test_ordinary_school_friction_stays_silent():
    for text in (
        "I'm a bit sad today, my friend was mean to me at school",
        "The teacher was mean about my handwriting",
        "I don't want to go to school because it's boring",
        "My brother and I fight over the TV sometimes",
    ):
        _silent(text)


# ── witnessing domestic violence ─────────────────────────────────────────────

def test_witnessing_domestic_violence_fires():
    for text in (
        "dad hits mum when he's angry",
        "he pushed my mum down the stairs",
        "my parents fight and throw things every night",
        "i hide in my room when daddy shouts at mummy",
    ):
        _fires(text)


# ── neglect / unsafe home / running away ─────────────────────────────────────

def test_neglect_and_unsafe_situation_fires():
    for text in (
        "there's no food in the house again",
        "i haven't eaten since yesterday",
        "nobody has been home for two days",
        "i have to look after my baby brother all the time and i'm scared",
        "my mum drinks until she falls asleep and i can't wake her",
        "there are needles in the house",
    ):
        _fires(text)


def test_running_away_and_sleeping_rough_fires():
    for text in (
        "i'm going to run away tonight",
        "i slept outside last night because i couldn't go home",
    ):
        _fires(text)


def test_ordinary_home_life_stays_silent():
    for text in (
        "We had no food left so we went shopping",
        "I have to look after my little brother after school",
        "I haven't eaten breakfast yet today",
        "I'm going to run to the shop",
        "We slept outside in a tent camping",
        "I slept outside under the stars for fun",
        "I locked myself out of my room",
    ):
        _silent(text)


# ── emotional / psychological abuse ──────────────────────────────────────────

def test_emotional_abuse_by_a_person_fires():
    for text in (
        "my dad says i'm worthless and stupid every day",
        "mum says she wishes i was never born",
        "they lock me in my room for hours",
        "i get called names at home all the time",
    ):
        _fires(text)


def test_a_one_off_harsh_remark_stays_silent():
    for text in ("Mum said the film was worthless",
                 "My mum said I'm being silly"):
        _silent(text)


# ── eating-related self-harm ─────────────────────────────────────────────────

def test_deliberate_eating_self_harm_fires():
    for text in ("i make myself sick after eating",
                 "i haven't eaten for three days on purpose"):
        assert _fires(text).severity is Severity.CRITICAL, text


def test_ordinary_illness_and_appetite_stay_silent():
    for text in ("I was sick yesterday and stayed home",
                 "I haven't eaten breakfast yet today",
                 "I don't like broccoli"):
        _silent(text)


# ── sextortion / online coercion ─────────────────────────────────────────────

def test_online_coercion_fires():
    for text in (
        "someone online said they'll share my photos if i don't do what they say",
        "a stranger online knows my school and where i live",
        "someone keeps messaging me even though i asked them to stop",
    ):
        _fires(text)


def test_benign_online_talk_stays_silent():
    for text in ("My friend keeps messaging me funny memes",
                 "someone online said maths is fun"):
        _silent(text)


# ── despair-pattern fix (pre-existing over-match surfaced by this review) ─────

def test_never_feel_better_is_despair_but_always_feel_better_is_not():
    """A pre-2026-08-12 pattern matched (always|never) feel better -- so it
    fired on 'I always feel better after a nap', a positive statement. Despair
    is 'never feel better' / 'always feel worse', not 'always feel better'."""
    for despair in ("i never feel better", "i'll never be happy",
                    "i always feel worse", "i always feel sad"):
        _fires(despair)
    for positive in ("I always feel better after a nap",
                     "I always feel good when I finish my homework",
                     "I never feel bored in art class"):
        _silent(positive)


# ── the whole original fixture set is unaffected ─────────────────────────────

def test_no_syntax_corruption_in_the_patterns():
    """A splice through a shell heredoc once turned \\b into a literal backspace.
    Guard against any control character sneaking into a compiled pattern."""
    import mentar.safety.escalation as esc
    banks = (esc._HARM_TO_SELF_PATTERNS, esc._PHYSICAL_DANGER_PATTERNS,
             esc._SEVERE_DISTRESS_PATTERNS, esc._ABUSE_DISCLOSURE_PATTERNS,
             esc._SECRECY_REQUEST_PATTERNS)
    ctrl = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
    for bank in banks:
        for p in bank:
            assert not ctrl.search(p.pattern), f"control char in pattern: {p.pattern!r}"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
