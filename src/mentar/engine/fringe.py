"""KST outer-fringe computation.

Spec: docs/SPEC.md §10 (concept graph, KST); PHASE0 W5.3 (mastery threshold 0.85).
Tests: docs/TESTS.md T3.2.

The OUTER FRINGE is the set of concepts that are not yet mastered AND whose
prerequisites are ALL mastered — i.e. what the learner is ready to learn now.
It is the core adaptive next-step signal driving NODE_SELECT in the session FSM
(see docs/SESSION_FSM.md state S1).

This module is stdlib-only and side-effect-free. The dialogue controller calls
`outer_fringe(graph, mastery)` once per tutoring turn after the BKT update.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

DEFAULT_MASTERY_THRESHOLD = 0.85   # PHASE0 W5.3 pilot default


# A graph is a Mapping from concept_id to its list of prereq concept_ids.
Graph = Mapping[str, list[str]]
# A mastery state is a Mapping from concept_id to its current BKT p_mastery in [0, 1].
Mastery = Mapping[str, float]


def is_mastered(p: float, threshold: float = DEFAULT_MASTERY_THRESHOLD) -> bool:
    """Return True iff the BKT mastery estimate clears the threshold (inclusive).

    Boundary semantics: p == threshold IS mastered. Test T3.2(d) exercises 0.849 / 0.851.
    """
    return p >= threshold


def outer_fringe(
    graph: Graph,
    mastery: Mastery,
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> set[str]:
    """Return the set of concept ids ready to learn now.

    A concept is on the outer fringe iff:
      1. it is not yet mastered (or has no mastery entry yet — treated as p = 0), AND
      2. every prereq id IS mastered (or the concept has no prereqs — then it's a root).

    Roots (concepts with no prereqs) are always on the fringe until mastered.

    Concept ids referenced in mastery but missing from the graph are ignored.
    Mastery entries are interpreted as 0 if absent for a graph concept.
    """
    fringe: set[str] = set()
    for concept_id, prereqs in graph.items():
        p_self = mastery.get(concept_id, 0.0)
        if is_mastered(p_self, threshold):
            continue
        if all(is_mastered(mastery.get(pr, 0.0), threshold) for pr in prereqs):
            fringe.add(concept_id)
    return fringe


def roots(graph: Graph) -> set[str]:
    """Concepts with no prereqs — the graph's entry points."""
    return {cid for cid, prereqs in graph.items() if not prereqs}


def leaves(graph: Graph) -> set[str]:
    """Concepts that no other concept depends on — the graph's terminal points."""
    referenced: set[str] = set()
    for prereqs in graph.values():
        referenced.update(prereqs)
    return {cid for cid in graph if cid not in referenced}


def graph_from_template(template_path: str) -> Graph:
    """Load a curriculum template (W3.1 schema) and return its concept_id → prereqs map.

    Uses the validator's frontmatter parser to avoid duplicating YAML handling.
    Does NOT run full validation here — callers should run `validate()` separately
    if they need to enforce DAG rules before serving content. This function trusts
    that the template was validated at load time.
    """
    from pathlib import Path

    from mentar.tools.validate_template import _parse_frontmatter

    text = Path(template_path).read_text(encoding="utf-8")
    data, _body = _parse_frontmatter(text)
    concepts = data.get("concepts") or []
    return {c["id"]: list(c.get("prereqs") or []) for c in concepts if isinstance(c, dict) and "id" in c}


def fringe_from_template(
    template_path: str,
    mastery: Optional[Mastery] = None,
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> set[str]:
    """Convenience: load a template + compute fringe in one call.

    Empty `mastery` means "fresh learner" — fringe will be exactly the graph roots.
    """
    g = graph_from_template(template_path)
    return outer_fringe(g, mastery or {}, threshold)
