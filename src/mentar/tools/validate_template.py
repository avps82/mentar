"""validate_template.py — W3.1 curriculum-template validator.

Parses a Markdown file with YAML frontmatter and validates the ``concepts:``
list against the W3.1 schema rules:

  * concepts list must exist and be non-empty.
  * every id must be unique (snake_case string).
  * every prereq id must reference an existing concept id.
  * the prereq graph must be a DAG (no cycles) — uses graphlib.TopologicalSorter.
  * a concept that has no prereqs AND is referenced by no other concept's prereqs
    is "orphan" (stranded singleton); this emits a warning, not an error.

Optional per-node fields (grounding, transfer_seeds, verifier, bkt_priors) are
checked for presence and emit warnings if missing — they do NOT cause errors.

Exit codes (CLI): 0 = pass (warnings go to stderr); 1 = error.

Usage:
    python -m mentar.tools.validate_template <path>

Programmatic:
    from mentar.tools.validate_template import validate
    result = validate("curriculum/templates/_pilot/fractions.md")
"""

from __future__ import annotations

import graphlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Outcome of validating a single template file."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    concept_ids: list[str] = field(default_factory=list)
    roots: list[str] = field(default_factory=list)   # nodes with no prereqs
    leaves: list[str] = field(default_factory=list)  # nodes not referenced as a prereq


# ---------------------------------------------------------------------------
# Parser: split frontmatter from body
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body_text).

    Expects the file to start with ``---`` on line 1 (possibly after blank lines),
    with the closing ``---`` on its own line. Raises ValueError on parse failure.
    """
    lines = text.splitlines(keepends=True)

    # Skip blank lines at top
    start = 0
    while start < len(lines) and lines[start].strip() == "":
        start += 1

    if start >= len(lines) or not lines[start].startswith("---"):
        raise ValueError("No YAML frontmatter found (file must begin with '---').")

    # Find closing ---
    close = start + 1
    while close < len(lines):
        stripped = lines[close].rstrip("\n\r")
        if stripped == "---" or stripped == "---\r":
            break
        close += 1

    if close >= len(lines):
        raise ValueError("Frontmatter opening '---' has no matching closing '---'.")

    fm_text = "".join(lines[start + 1 : close])
    body = "".join(lines[close + 1 :])

    data = yaml.safe_load(fm_text)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter parsed to {type(data).__name__}, expected a mapping.")

    return data, body


# ---------------------------------------------------------------------------
# Validator core
# ---------------------------------------------------------------------------

_RECOMMENDED_FIELDS = ("grounding", "transfer_seeds", "verifier", "bkt_priors")
_BKT_PRIOR_KEYS = frozenset({"guess", "slip", "learns", "forgets"})


def validate(path: str) -> ValidationResult:
    """Validate the curriculum template at *path* and return a ValidationResult."""
    errors: list[str] = []
    warnings: list[str] = []

    # ---- read file ---------------------------------------------------------
    filepath = Path(path)
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        return ValidationResult(ok=False, errors=[f"Cannot read file: {exc}"])

    # ---- parse frontmatter -------------------------------------------------
    try:
        data, _body = _parse_frontmatter(text)
    except ValueError as exc:
        return ValidationResult(ok=False, errors=[str(exc)])

    # ---- concepts presence + non-empty ------------------------------------
    raw_concepts = data.get("concepts")
    if not raw_concepts:
        # None, missing, empty list, empty string all count as missing/empty
        errors.append("concepts list is empty or missing")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    if not isinstance(raw_concepts, list):
        errors.append(f"'concepts' must be a YAML list, got {type(raw_concepts).__name__}")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    # ---- per-entry validation: id, label, prereqs -------------------------
    seen_ids: dict[str, int] = {}   # id → first-seen index (1-based)
    concept_ids: list[str] = []
    parsed_concepts: list[dict[str, Any]] = []

    for idx, entry in enumerate(raw_concepts, start=1):
        if not isinstance(entry, dict):
            errors.append(f"concepts[{idx}]: expected a mapping, got {type(entry).__name__}")
            continue

        cid = entry.get("id")
        if not cid or not isinstance(cid, str):
            errors.append(f"concepts[{idx}]: missing or non-string 'id'")
            cid = f"__unnamed_{idx}__"
        else:
            if cid in seen_ids:
                errors.append(f"duplicate concept id: {cid!r} (first at position {seen_ids[cid]})")
            else:
                seen_ids[cid] = idx
                concept_ids.append(cid)

        label = entry.get("label")
        if not label or not isinstance(label, str):
            errors.append(f"concept '{cid}': missing or non-string 'label'")

        prereqs = entry.get("prereqs")
        if prereqs is None:
            errors.append(f"concept '{cid}': missing 'prereqs' key (use [] for roots)")
            prereqs = []
        elif not isinstance(prereqs, list):
            errors.append(f"concept '{cid}': 'prereqs' must be a list, got {type(prereqs).__name__}")
            prereqs = []

        # Recommended optional fields
        for field_name in _RECOMMENDED_FIELDS:
            if field_name not in entry:
                warnings.append(
                    f"concept '{cid}': missing recommended field '{field_name}'"
                )

        # bkt_priors, when present, must be sane: engine.bkt.params_for applies
        # them unchecked, a value outside [0,1] yields a posterior outside [0,1],
        # the schema CHECK then rejects the persist and the child carries corrupt
        # in-memory mastery for the session. Presence stays a warning; a bad
        # value is an ERROR (2026-09-02, W3.3 §6 B2).
        priors = entry.get("bkt_priors")
        if priors is not None:
            if not isinstance(priors, dict):
                errors.append(f"concept '{cid}': bkt_priors must be a mapping, got {type(priors).__name__}")
            else:
                for key, val in priors.items():
                    if key not in _BKT_PRIOR_KEYS:
                        errors.append(f"concept '{cid}': bkt_priors.{key} is not a BKT parameter (expected one of {sorted(_BKT_PRIOR_KEYS)})")
                    elif isinstance(val, bool) or not isinstance(val, (int, float)):
                        errors.append(f"concept '{cid}': bkt_priors.{key} must be a number in [0, 1], got {val!r}")
                    elif not 0.0 <= float(val) <= 1.0:
                        errors.append(f"concept '{cid}': bkt_priors.{key} = {val} is outside [0, 1]")

        parsed_concepts.append({"id": cid, "prereqs": prereqs})

    # If we found duplicate-id errors, abort before graph checks
    if errors:
        return ValidationResult(
            ok=False,
            errors=errors,
            warnings=warnings,
            concept_ids=concept_ids,
        )

    # ---- build id set for cross-ref checks --------------------------------
    id_set = set(concept_ids)

    # ---- unknown prereq check ---------------------------------------------
    for concept in parsed_concepts:
        cid = concept["id"]
        for prid in concept["prereqs"]:
            if not isinstance(prid, str):
                errors.append(
                    f"concept '{cid}': prereq entry {prid!r} is not a string"
                )
            elif prid not in id_set:
                errors.append(
                    f"concept '{cid}' references unknown prereq id {prid!r}"
                )

    if errors:
        return ValidationResult(
            ok=False,
            errors=errors,
            warnings=warnings,
            concept_ids=concept_ids,
        )

    # ---- DAG / cycle check using graphlib.TopologicalSorter ---------------
    graph: dict[str, set[str]] = {c["id"]: set(c["prereqs"]) for c in parsed_concepts}
    ts = graphlib.TopologicalSorter(graph)
    try:
        ts.prepare()  # raises CycleError if a cycle exists
        # drain the sorter to confirm full ordering
        order = []
        while ts.is_active():
            ready = list(ts.get_ready())
            order.extend(ready)
            for node in ready:
                ts.done(node)
    except graphlib.CycleError as exc:
        # exc.args[1] is a list of nodes involved in the cycle
        cycle_nodes = exc.args[1] if len(exc.args) > 1 else []
        if cycle_nodes:
            path_str = " → ".join(str(n) for n in cycle_nodes)
            errors.append(f"cycle in prereq graph: {path_str}")
        else:
            errors.append("cycle in prereq graph (details unavailable)")
        return ValidationResult(
            ok=False,
            errors=errors,
            warnings=warnings,
            concept_ids=concept_ids,
        )

    # ---- compute roots and leaves -----------------------------------------
    # roots: nodes with no prereqs
    roots = [c["id"] for c in parsed_concepts if not c["prereqs"]]

    # leaves: nodes not referenced as a prereq by any other node
    referenced_as_prereq: set[str] = set()
    for c in parsed_concepts:
        referenced_as_prereq.update(c["prereqs"])
    leaves = [cid for cid in concept_ids if cid not in referenced_as_prereq]

    # ---- orphan check -------------------------------------------------------
    # An "orphan" is a node that is BOTH a root (no prereqs) AND a leaf
    # (no other node depends on it) — i.e., a stranded singleton disconnected
    # from all other concepts.  This fires a warning, not an error.
    #
    # Rationale: in a proper DAG every node is reachable from some root by
    # definition, so "unreachable from any root" only makes sense as "the node
    # is a root but has no successors and no predecessors" — a disconnected
    # singleton.  A single-node template with one concept is therefore always
    # an orphan; that is intentional for very small templates.
    root_set = set(roots)
    leaf_set = set(leaves)
    orphan_ids = [cid for cid in concept_ids if cid in root_set and cid in leaf_set]

    # Only warn if there are OTHER non-orphan nodes (a completely isolated
    # one-node template is degenerate but still valid for testing purposes).
    if len(concept_ids) > 1:
        for oid in orphan_ids:
            warnings.append(
                f"concept '{oid}' is orphan (no path from a root to other nodes; "
                "it has no prereqs and no other concept lists it as a prereq)"
            )

    return ValidationResult(
        ok=True,
        errors=[],
        warnings=warnings,
        concept_ids=concept_ids,
        roots=roots,
        leaves=leaves,
    )


def validate_or_raise(path: str | Path) -> ValidationResult:
    """Validate *path* and raise RuntimeError naming the template + every error
    if invalid (A16 — loud-fail at startup instead of a silently-broken fringe
    producing a false "you've mastered everything!" completion). Warnings do
    not raise. Returns the ValidationResult on success."""
    result = validate(str(path))
    if not result.ok:
        detail = "; ".join(result.errors)
        raise RuntimeError(f"Invalid curriculum template {path}: {detail}")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def report(result: ValidationResult, path: str) -> int:
    """Print a ValidationResult (warnings/errors to stderr, summary to stdout).

    Returns the process exit code: 0 on pass, 1 on error.  Shared by this
    module's CLI and the unified ``mentar validate-template`` subcommand so the
    output format lives in exactly one place.
    """
    for w in result.warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    for e in result.errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if result.ok:
        n = len(result.concept_ids)
        print(
            f"OK: {path} — {n} concept(s); "
            f"roots={result.roots}; leaves={result.leaves}",
            file=sys.stdout,
        )
        if result.warnings:
            print(f"  {len(result.warnings)} warning(s) — see stderr.", file=sys.stdout)
        return 0
    print(f"FAIL: {path} — {len(result.errors)} error(s).", file=sys.stdout)
    return 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.  Returns 0 on pass, 1 on error."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="mentar-validate-template",
        description="Validate a Mentar curriculum template (W3.1 schema).",
    )
    parser.add_argument("path", help="Path to curriculum template Markdown file.")
    args = parser.parse_args(argv)

    return report(validate(args.path), args.path)


if __name__ == "__main__":
    raise SystemExit(main())
