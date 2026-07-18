"""Tests for select_next — the micro-learning NODE_SELECT policy (R11):
interleaving, spaced-review injection, determinism.
"""

from __future__ import annotations

import random

from mentar.engine.fringe import REVIEW_EVERY_N, select_next


def test_interleave_switches_away_from_current():
    """Ensure the selector picks a different node from the fringe if others are available."""
    graph = {"a": [], "b": [], "c": []}
    mastery = {}
    rng = random.Random(42)
    result = select_next(
        graph, mastery, stale_mastered=set(), current="a",
        items_completed=1, rng=rng
    )
    assert result in {"b", "c"}
    assert result != "a"


def test_sticks_when_current_is_only_fringe_node():
    """Ensure it returns the current node if it is the only one available."""
    graph = {"a": []}
    mastery = {}
    rng = random.Random(42)
    result = select_next(
        graph, mastery, stale_mastered=set(), current="a",
        items_completed=1, rng=rng
    )
    assert result == "a"


def test_review_fires_on_multiple_of_review_every_n():
    """Ensure spaced review is injected when items_completed is a multiple of REVIEW_EVERY_N."""
    graph = {"a": [], "b": [], "c": []}
    mastery = {}
    stale = {"z"}
    rng1 = random.Random(42)
    res1 = select_next(
        graph, mastery, stale_mastered=stale, current=None,
        items_completed=REVIEW_EVERY_N, rng=rng1
    )
    assert res1 == "z"

    rng2 = random.Random(43)
    res2 = select_next(
        graph, mastery, stale_mastered=stale, current=None,
        items_completed=2 * REVIEW_EVERY_N, rng=rng2
    )
    assert res2 == "z"


def test_review_does_not_fire_at_zero_or_off_cycle():
    """Ensure review is only injected on the specific cycle."""
    graph = {"a": [], "b": [], "c": []}
    mastery = {}
    stale = {"z"}
    rng1 = random.Random(42)
    res1 = select_next(
        graph, mastery, stale_mastered=stale, current=None,
        items_completed=0, rng=rng1
    )
    assert res1 in {"a", "b", "c"}
    assert res1 != "z"

    rng2 = random.Random(43)
    res2 = select_next(
        graph, mastery, stale_mastered=stale, current=None,
        items_completed=REVIEW_EVERY_N - 1, rng=rng2
    )
    assert res2 in {"a", "b", "c"}
    assert res2 != "z"


def test_empty_fringe_falls_back_to_stale_review():
    """Ensure stale review is picked if no new items are available."""
    graph = {"a": []}
    mastery = {"a": 0.9}
    stale = {"a"}
    rng = random.Random(42)
    result = select_next(
        graph, mastery, stale_mastered=stale, current="a",
        items_completed=1, rng=rng
    )
    assert result == "a"


def test_all_done_returns_none():
    """Ensure None is returned when both fringe and stale are empty."""
    graph = {"a": []}
    mastery = {"a": 0.9}
    stale = set()
    rng = random.Random(42)
    result = select_next(
        graph, mastery, stale_mastered=stale, current="a",
        items_completed=1, rng=rng
    )
    assert result is None


def test_same_seed_same_sequence():
    """Ensure deterministic behavior with the same seed."""
    graph = {"a": [], "b": [], "c": []}
    mastery = {}
    stale = set()

    rng1 = random.Random(42)
    seq1 = []
    for i in range(1, 11):
        res = select_next(graph, mastery, stale_mastered=stale, current=None, items_completed=i, rng=rng1)
        seq1.append(res)

    rng2 = random.Random(42)
    seq2 = []
    for i in range(1, 11):
        res = select_next(graph, mastery, stale_mastered=stale, current=None, items_completed=i, rng=rng2)
        seq2.append(res)

    assert seq1 == seq2
