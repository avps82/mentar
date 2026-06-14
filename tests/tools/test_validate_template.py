"""Tests for T3.1 — curriculum-template validator (W3.1 schema).

Six test cases required by TESTS.md T3.1:
  (a) valid pilot template passes
  (b) cycle injected → fails with cycle path in error message
  (c) prereq referencing unknown id → fails naming the unknown id
  (d) duplicate id → fails mentioning "duplicate" and the id
  (e) empty concepts list → fails mentioning "empty"
  (f) node unreachable (orphan / stranded singleton) → warning, not error
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mentar.tools.validate_template import validate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_template(tmp_path: Path, concepts_yaml: str, *, extra_fields: str = "") -> Path:
    """Write a minimal valid-structure template with the given concepts YAML block."""
    content = f"""---
template_id: test-template
country: null
year_level: test
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
{extra_fields}
concepts:
{concepts_yaml}
---

# Test template body (ignored by validator).
"""
    p = tmp_path / "template.md"
    p.write_text(content, encoding="utf-8")
    return p


def _write_minimal_concept(
    cid: str,
    label: str,
    prereqs: list[str],
    *,
    include_recommended: bool = True,
) -> str:
    """Return YAML lines for one concept entry (indented for list item)."""
    prereqs_str = "[" + ", ".join(prereqs) + "]"
    lines = [
        f"  - id: {cid}",
        f"    label: {label!r}",
        f"    prereqs: {prereqs_str}",
    ]
    if include_recommended:
        lines += [
            "    grounding:",
            "      source: wikipedia_simple",
            "      anchor: 'https://simple.wikipedia.org/wiki/Test'",
            "      passage_hint: 'Test passage'",
            "    transfer_seeds:",
            "      - 'Transfer seed 1'",
            "      - 'Transfer seed 2'",
            "    verifier:",
            "      answer_type: mc4",
            "      checker: mc_choice",
            "    bkt_priors:",
            "      guess: 0.2",
            "      slip: 0.1",
            "      learns: 0.2",
            "      forgets: 0",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# T3.1 (a) — valid pilot fractions template passes
# ---------------------------------------------------------------------------

def test_pilot_fractions_passes():
    """Acceptance test: the 8-node pilot fractions template must pass with no errors
    and no warnings.  This is the hard acceptance criterion for W3.1."""
    fractions_path = Path(__file__).parents[2] / "curriculum" / "templates" / "_pilot" / "fractions.md"
    assert fractions_path.exists(), f"Pilot template not found at {fractions_path}"

    result = validate(str(fractions_path))

    assert result.ok is True, (
        f"Pilot fractions template failed validation.\nErrors: {result.errors}"
    )
    assert result.warnings == [], (
        f"Pilot fractions template produced unexpected warnings: {result.warnings}"
    )
    # Sanity: 8 concepts, 1 root, 2 leaves per template comments
    assert len(result.concept_ids) == 8
    assert result.roots == ["whole_number_division"]
    assert set(result.leaves) == {"comparing_equal_denom", "subtracting_equal_denom"}


# ---------------------------------------------------------------------------
# T3.1 (b) — cycle detected → fails, error mentions "cycle" and involved ids
# ---------------------------------------------------------------------------

def test_cycle_detected(tmp_path):
    """A → B → A cycle must fail with a message containing 'cycle' and both ids."""
    concepts_yaml = "\n".join([
        _write_minimal_concept("concept_a", "Concept A", ["concept_b"]),
        _write_minimal_concept("concept_b", "Concept B", ["concept_a"]),
    ])
    path = _write_template(tmp_path, concepts_yaml)

    result = validate(str(path))

    assert result.ok is False, "Expected failure for cycle A→B→A"
    assert any("cycle" in e.lower() for e in result.errors), (
        f"Expected 'cycle' in error messages; got: {result.errors}"
    )
    # Both ids involved in the cycle must appear in at least one error message
    all_errors = " ".join(result.errors)
    assert "concept_a" in all_errors, f"Expected concept_a in errors; got: {result.errors}"
    assert "concept_b" in all_errors, f"Expected concept_b in errors; got: {result.errors}"


# ---------------------------------------------------------------------------
# T3.1 (c) — prereq referencing unknown id → error names the unknown id
# ---------------------------------------------------------------------------

def test_unknown_prereq_id(tmp_path):
    """A concept that prereqs a non-existent id must fail, naming the missing id."""
    concepts_yaml = _write_minimal_concept("concept_b", "Concept B", ["missing_id"])
    path = _write_template(tmp_path, concepts_yaml)

    result = validate(str(path))

    assert result.ok is False, "Expected failure for unknown prereq id"
    all_errors = " ".join(result.errors)
    assert "missing_id" in all_errors, (
        f"Expected 'missing_id' named in error; got: {result.errors}"
    )


# ---------------------------------------------------------------------------
# T3.1 (d) — duplicate id → fails, error mentions "duplicate" and the id
# ---------------------------------------------------------------------------

def test_duplicate_id(tmp_path):
    """Two concepts sharing id 'concept_a' must fail with 'duplicate' + id in error."""
    concepts_yaml = "\n".join([
        _write_minimal_concept("concept_a", "Concept A first", []),
        _write_minimal_concept("concept_a", "Concept A second", []),
    ])
    path = _write_template(tmp_path, concepts_yaml)

    result = validate(str(path))

    assert result.ok is False, "Expected failure for duplicate id"
    all_errors = " ".join(result.errors)
    assert "duplicate" in all_errors.lower(), (
        f"Expected 'duplicate' in errors; got: {result.errors}"
    )
    assert "concept_a" in all_errors, (
        f"Expected the duplicate id 'concept_a' named in errors; got: {result.errors}"
    )


# ---------------------------------------------------------------------------
# T3.1 (e) — empty concepts list → fails with mention of "empty"
# ---------------------------------------------------------------------------

def test_empty_concepts_list(tmp_path):
    """An explicit empty concepts list must fail with an 'empty' message."""
    # Write a template where concepts: is an explicit empty list []
    content = """\
---
template_id: test-empty
country: null
year_level: test
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
concepts: []
---

# Body
"""
    path = tmp_path / "empty.md"
    path.write_text(content, encoding="utf-8")

    result = validate(str(path))

    assert result.ok is False, "Expected failure for empty concepts list"
    all_errors = " ".join(result.errors)
    assert "empty" in all_errors.lower(), (
        f"Expected 'empty' in errors; got: {result.errors}"
    )


# ---------------------------------------------------------------------------
# T3.1 (f) — orphan / stranded singleton → warning (not error)
# ---------------------------------------------------------------------------

def test_orphan_warning(tmp_path):
    """A stranded singleton node (no prereqs, not referenced by any other node)
    alongside a connected chain must produce an orphan warning but not an error.

    Orphan definition (W3.1): a node with prereqs=[] AND no other concept lists
    it as a prereq — i.e., completely disconnected from the rest of the graph.

    The chain A → B → C is well-connected.  Node Z has no prereqs and is not
    referenced by A, B, or C.  Z is an orphan / stranded singleton.
    """
    concepts_yaml = "\n".join([
        _write_minimal_concept("node_a", "Node A (root of chain)", []),
        _write_minimal_concept("node_b", "Node B", ["node_a"]),
        _write_minimal_concept("node_c", "Node C (leaf of chain)", ["node_b"]),
        _write_minimal_concept("node_z", "Node Z (stranded singleton)", []),
    ])
    path = _write_template(tmp_path, concepts_yaml)

    result = validate(str(path))

    assert result.ok is True, (
        f"Orphan check must produce a warning, not an error; got errors: {result.errors}"
    )
    all_warnings = " ".join(result.warnings)
    assert "node_z" in all_warnings, (
        f"Expected orphan warning mentioning 'node_z'; got warnings: {result.warnings}"
    )
    assert any("orphan" in w.lower() for w in result.warnings), (
        f"Expected at least one warning containing 'orphan'; got: {result.warnings}"
    )

    # node_a is a root but IS referenced (by node_b) so must NOT be flagged as orphan
    orphan_warnings = [w for w in result.warnings if "orphan" in w.lower()]
    assert not any("node_a" in w for w in orphan_warnings), (
        f"node_a should not be flagged as orphan (it has dependents); warnings: {result.warnings}"
    )


# ---------------------------------------------------------------------------
# Additional edge cases (robustness)
# ---------------------------------------------------------------------------

def test_single_root_no_warns(tmp_path):
    """A single root concept (no prereqs, no dependents) in a single-node template
    must pass without orphan warnings (degenerate but valid)."""
    concepts_yaml = _write_minimal_concept("solo", "Solo concept", [])
    path = _write_template(tmp_path, concepts_yaml)

    result = validate(str(path))

    assert result.ok is True
    # Single-node templates are not warned — there's nothing else in the graph
    orphan_warnings = [w for w in result.warnings if "orphan" in w.lower()]
    assert orphan_warnings == [], (
        f"Single-node template should not produce orphan warnings; got: {result.warnings}"
    )


def test_missing_concepts_key(tmp_path):
    """A template with no 'concepts' key at all must fail with 'empty or missing'."""
    content = """\
---
template_id: test-no-concepts
schema_version: "0.1"
---

# Body
"""
    path = tmp_path / "no_concepts.md"
    path.write_text(content, encoding="utf-8")

    result = validate(str(path))

    assert result.ok is False
    all_errors = " ".join(result.errors)
    assert "empty" in all_errors.lower() or "missing" in all_errors.lower()
