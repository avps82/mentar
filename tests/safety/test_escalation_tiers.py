"""The CONCERN tier (2026-08-18, maintainer-authorised) — corpus-driven.

Third-probe findings (SAFEGUARDING_REVIEW_PACKET.md Part 4): five disclosure
shapes fired NOTHING, and one boredom idiom froze a lesson at CRITICAL. The
CONCERN tier logs + surfaces to the parent WITHOUT freezing; the idiom is
neutralised by rewriting the idiom itself, never by weakening a harm pattern.

This file is the measurement corpus: every phrasing carries its expected tier,
so any future pattern change is measured here rather than argued. Extend the
lists, never shrink them.

    python3 -m pytest tests/safety/test_escalation_tiers.py
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.safety.escalation import Severity, TriggerClass, classify

# ── The corpus: (phrasing, expected severity value or None) ──────────────────

# CRITICAL regression sample — the tier work must not weaken ANY of these.
CRITICAL = [
    "i want to kill myself",
    "i want to die",
    "i dont want to be alive anymore",
    "my uncle touches me",
    "my dad hits me when he's angry",
    "i cut myself on purpose",
    "there's a fire in my house",
    "someone is breaking in",
    "i cant breathe",
    "a man is following me",
    # The idiom neutralisation must NOT swallow a real second clause.
    "im bored to death of this and i want to die",
]

# CONCERN — the five probe misses, plus phrase variants the patterns generalise to.
CONCERN = [
    "my mums boyfriend comes into my room at night",
    "my mum's boyfriend came into my room at night",
    "he sneaks into my bedroom at night",
    "i cut myself",
    "i've been cutting myself",
    "i cut myself on the scissors",       # innocent use costs a parent note, not a freeze
    "my brother makes me do things i dont like",
    "he makes me do things i don't want",
    "i'm scared to go home",
    "im afraid to go home",
    "i havent eaten in two days",
    "i haven't eaten for 3 days",
]

# None — must fire NOTHING. Includes the boredom idiom (previously a false
# CRITICAL freeze) and every near-miss neighbour of the CONCERN patterns.
NONE = [
    "i want to die of boredom doing fractions",
    "this is so boring i could die of boredom",
    "i nearly died of laughter",
    "i cut the cake into 4 pieces",
    "the knife cuts 8 slices",
    "my coach makes me do things like pushups",
    "my teacher makes me do things",          # no discomfort clause
    "i havent eaten breakfast",
    "i haven't eaten yet today",
    "my cat comes into my room at night",     # accepted CONCERN? no — see note below
    "i'm scared of the dark",
    "i'm scared i'll get it wrong",
    "the fire burned 3 logs, how many left",
    "subtract 3 from 10",
    "my uncle has 12 apples",
    "999 divided by 3",
    "my brother is 7 years old",
    "i went home after school",
]


# HIGH regression sample — the other freeze tier, equally not-weakened.
HIGH = [
    "he told me not to tell anyone",      # secrecy_request has always been HIGH
]


@pytest.mark.parametrize("text", HIGH)
def test_high_still_fires_high(text):
    m = classify(text)
    assert m is not None and m.severity is Severity.HIGH


@pytest.mark.parametrize("text", CRITICAL)
def test_critical_still_fires_critical(text):
    m = classify(text)
    assert m is not None and m.severity is Severity.CRITICAL, (
        f"{text!r} -> {m and m.severity} — the tier work must never weaken CRITICAL"
    )


@pytest.mark.parametrize("text", CONCERN)
def test_concern_fires_concern_not_a_freeze_tier(text):
    m = classify(text)
    assert m is not None, f"{text!r} fired nothing — the exact gap this tier closes"
    assert m.severity is Severity.CONCERN, f"{text!r} -> {m.severity}, expected CONCERN"
    assert m.trigger_class is TriggerClass.WELFARE_CONCERN


@pytest.mark.parametrize("text", [t for t in NONE if "cat" not in t])
def test_innocent_and_idiom_phrasings_fire_nothing(text):
    m = classify(text)
    assert m is None, f"{text!r} -> {m.trigger_class}/{m.severity} — expected silence"


def test_the_cat_case_is_a_known_concern_false_positive():
    """"my cat comes into my room at night" DOES fire CONCERN — the pattern
    cannot tell a cat from a person without understanding subjects. Recorded as
    a KNOWN, ACCEPTED false positive: the cost is one parent note, not a frozen
    lesson, which is the trade the tier exists to make. If this test starts
    failing because the pattern got smarter, delete it happily."""
    m = classify("my cat comes into my room at night")
    assert m is not None and m.severity is Severity.CONCERN


def test_a_qualified_cut_still_outranks_the_bare_concern_pattern():
    """"i cut myself on purpose" matches BOTH the CRITICAL qualified pattern and
    the CONCERN bare pattern — precedence must keep it CRITICAL."""
    m = classify("i cut myself on purpose to feel something")
    assert m is not None and m.severity is Severity.CRITICAL
