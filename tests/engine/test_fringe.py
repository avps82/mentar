"""Tests for the KST outer-fringe computation.

Spec: docs/SPEC.md §10; tests: docs/TESTS.md T3.2.

All five T3.2 cases:
  (a) empty knowledge state → fringe = roots only
  (b) full state           → fringe = ∅
  (c) mid-state on the pilot fractions graph → expected fringe
  (d) boundary at threshold 0.85 (test 0.849 vs 0.851)
  (e) property test: invariant fringe ⊥ unmastered-prereqs (uses hypothesis if available)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mentar.engine.fringe import (
    DEFAULT_MASTERY_THRESHOLD,
    fringe_from_template,
    graph_from_template,
    is_mastered,
    leaves,
    outer_fringe,
    roots,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PILOT_TEMPLATE = REPO_ROOT / "curriculum" / "templates" / "_pilot" / "fractions.md"


# ─── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def pilot_graph():
    """The 8-node pilot fractions graph loaded from disk."""
    return graph_from_template(str(PILOT_TEMPLATE))


@pytest.fixture
def linear_graph():
    """A simple linear 4-node graph for boundary tests: a → b → c → d."""
    return {
        "a": [],
        "b": ["a"],
        "c": ["b"],
        "d": ["c"],
    }


# ─── (a) empty state ────────────────────────────────────────────────────────


def test_empty_state_fringe_is_roots_only(pilot_graph):
    """T3.2(a): with no mastery yet, the fringe equals the graph's roots."""
    fringe = outer_fringe(pilot_graph, mastery={})
    assert fringe == roots(pilot_graph)
    # Pilot graph has exactly one root.
    assert fringe == {"whole_number_division"}


def test_empty_state_on_linear_graph(linear_graph):
    fringe = outer_fringe(linear_graph, mastery={})
    assert fringe == {"a"}


# ─── (b) full state ─────────────────────────────────────────────────────────


def test_full_state_fringe_is_empty(pilot_graph):
    """T3.2(b): with everything mastered, fringe is empty."""
    mastery = {cid: 1.0 for cid in pilot_graph}
    assert outer_fringe(pilot_graph, mastery) == set()


# ─── (c) mid-state on the pilot graph ───────────────────────────────────────


def test_pilot_midstate_at_equivalent_fractions(pilot_graph):
    """T3.2(c): after mastering through equivalent_fractions, the fringe is
    {comparing_equal_denom, adding_equal_denom} — the two children of
    equivalent_fractions in the pilot graph.

    (The 23 sample graph stops at unit_fractions; this version inserts
    equivalent_fractions as a prereq for comparing/adding/subtracting — see
    curriculum/templates/_pilot/fractions.md prerequisite rationale.)
    """
    mastered = {
        "whole_number_division": 1.0,
        "fraction_as_part_of_whole": 1.0,
        "equal_vs_unequal_parts": 1.0,
        "unit_fractions": 1.0,
        "equivalent_fractions": 1.0,
    }
    assert outer_fringe(pilot_graph, mastered) == {
        "comparing_equal_denom",
        "adding_equal_denom",
    }


def test_pilot_after_adding_unlocks_subtracting(pilot_graph):
    """Mastering through `adding_equal_denom` (with comparing_equal_denom also
    mastered) unlocks subtracting_equal_denom — which is its sole prereq's child."""
    mastered = {
        "whole_number_division": 1.0,
        "fraction_as_part_of_whole": 1.0,
        "equal_vs_unequal_parts": 1.0,
        "unit_fractions": 1.0,
        "equivalent_fractions": 1.0,
        "comparing_equal_denom": 1.0,
        "adding_equal_denom": 1.0,
    }
    assert outer_fringe(pilot_graph, mastered) == {"subtracting_equal_denom"}


# ─── (d) boundary at threshold 0.85 ─────────────────────────────────────────


def test_boundary_above_threshold_counts_as_mastered():
    """T3.2(d): p = 0.851 > 0.85 → mastered."""
    assert is_mastered(0.851)
    assert is_mastered(0.85)  # equal-to threshold IS mastered (>= semantics)


def test_boundary_below_threshold_not_mastered():
    """T3.2(d): p = 0.849 < 0.85 → NOT mastered."""
    assert not is_mastered(0.849)


def test_boundary_in_fringe(linear_graph):
    """A node with p = 0.851 vs 0.849 changes downstream fringe membership."""
    # a JUST below threshold: b should NOT be on the fringe (a not mastered)
    mastery_below = {"a": 0.849}
    assert outer_fringe(linear_graph, mastery_below) == {"a"}

    # a JUST above threshold: b IS on the fringe (a mastered, b not)
    mastery_above = {"a": 0.851}
    assert outer_fringe(linear_graph, mastery_above) == {"b"}


def test_custom_threshold():
    """An override threshold takes effect end-to-end."""
    g = {"a": [], "b": ["a"]}
    # at threshold 0.9, p=0.851 is NOT mastered
    assert outer_fringe(g, {"a": 0.851}, threshold=0.9) == {"a"}
    # at threshold 0.5, p=0.851 IS mastered
    assert outer_fringe(g, {"a": 0.851}, threshold=0.5) == {"b"}


# ─── helpers around roots / leaves on the pilot graph ───────────────────────


def test_pilot_roots_and_leaves(pilot_graph):
    assert roots(pilot_graph) == {"whole_number_division"}
    assert leaves(pilot_graph) == {"comparing_equal_denom", "subtracting_equal_denom"}


def test_fringe_from_template_convenience():
    """fringe_from_template loads + computes in one call."""
    f = fringe_from_template(str(PILOT_TEMPLATE), mastery={})
    assert f == {"whole_number_division"}


# ─── (e) property test ─────────────────────────────────────────────────────


def test_invariant_fringe_excludes_unmastered_prereqs(pilot_graph):
    """For every state, every fringe member has all prereqs mastered."""
    # A few hand-crafted states (cheap property check without hypothesis):
    states = [
        {},
        {"whole_number_division": 1.0},
        {"whole_number_division": 1.0, "fraction_as_part_of_whole": 1.0},
        {cid: 0.851 for cid in pilot_graph},   # all just-above
        {cid: 0.849 for cid in pilot_graph},   # all just-below
    ]
    for mastery in states:
        f = outer_fringe(pilot_graph, mastery)
        for concept in f:
            # Every prereq must be mastered
            for pr in pilot_graph[concept]:
                assert is_mastered(mastery.get(pr, 0.0)), (
                    f"FRINGE INVARIANT VIOLATED: {concept} on fringe but prereq {pr} "
                    f"has mastery {mastery.get(pr, 0.0)} < {DEFAULT_MASTERY_THRESHOLD}"
                )
            # And the fringe member itself must NOT be mastered
            assert not is_mastered(mastery.get(concept, 0.0)), (
                f"FRINGE INVARIANT VIOLATED: {concept} on fringe but already mastered"
            )


# Hypothesis-based property test — runs if hypothesis is installed; skipped otherwise.
try:
    from hypothesis import given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
def test_invariant_property(pilot_graph):
    """Hypothesis-driven property test (T3.2(e) — 1000 examples)."""
    concept_ids = list(pilot_graph.keys())

    @given(
        mastery_values=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            min_size=len(concept_ids),
            max_size=len(concept_ids),
        )
    )
    @settings(max_examples=1000, deadline=None)
    def _check(mastery_values):
        mastery = dict(zip(concept_ids, mastery_values))
        f = outer_fringe(pilot_graph, mastery)
        for concept in f:
            for pr in pilot_graph[concept]:
                assert is_mastered(mastery[pr]), (
                    f"{concept} on fringe but prereq {pr} = {mastery[pr]}"
                )
            assert not is_mastered(mastery[concept]), (
                f"{concept} on fringe but already mastered = {mastery[concept]}"
            )

    _check()
