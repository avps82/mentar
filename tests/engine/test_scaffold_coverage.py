"""Brute-force scaffold coverage — every concept node in every shipped
curriculum template must have a matching visual scaffold.

If this test fails, add keywords to an existing scaffold or create a new
scaffold file in curriculum/visual_scaffolds/<subject>/.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.visual_scaffold import _scan_scaffold_dir, load_visual_scaffold

TEMPLATES = REPO / "curriculum" / "templates"
SCAFFOLD_ROOT = REPO / "curriculum" / "visual_scaffolds"


def test_every_concept_node_has_a_scaffold():
    _scan_scaffold_dir.cache_clear()
    missing = []
    for tmpl in sorted(TEMPLATES.glob("**/*.md")):
        if tmpl.name in ("index.md", "log.md"):
            continue
        text = tmpl.read_text(encoding="utf-8")
        parts = text.split("\n---\n", 1)
        raw = yaml.safe_load(parts[0].removeprefix("---\n")) or {}
        subject = raw.get("subject", "")
        tid = raw.get("template_id", tmpl.stem)
        for node in raw.get("concepts", []):
            label = node.get("label", "")
            if not load_visual_scaffold(SCAFFOLD_ROOT, subject, label):
                missing.append(f"[{tid}] {label!r} ({subject})")
    assert not missing, (
        "These concept nodes have no matching visual scaffold "
        "(add keywords or a new file under curriculum/visual_scaffolds/):\n"
        + "\n".join(f"  {m}" for m in missing)
    )


def test_scaffold_routing_prefers_most_specific_match():
    """E1 Findings 1+2 regression (2026-08-11): most-keywords-matched wins.

    Finding 2: 'Adding fractions...' labels matched addition_subtraction.md
    first (alphabetical first-match) instead of fractions.md. Finding 1:
    whole-number place-value labels matched decimals.md via its bare
    'place value' keyword (now narrowed to 'decimal place value'; whole
    numbers route to the new place_value.md)."""
    _scan_scaffold_dir.cache_clear()
    cases = [
        # (label, unique marker of the CORRECT scaffold's body)
        ("Place value to 99", "Hundreds | Tens | Ones"),          # place_value.md
        ("Decimal place value (tenths and hundredths)", "place-value chart"),  # decimals.md
        ("Adding fractions with the same denominator", "1/2 shaded"),          # fractions.md
        ("Adding and subtracting fractions with unlike denominators", "1/2 shaded"),
        ("Adding numbers to 100", "number line"),                  # addition_subtraction.md
    ]
    for label, marker in cases:
        body = load_visual_scaffold(SCAFFOLD_ROOT, "mathematics", label)
        assert body and marker.lower() in body.lower(), (
            f"label {label!r} routed to the wrong scaffold "
            f"(wanted body containing {marker!r}; got: {body[:120]!r})"
        )
