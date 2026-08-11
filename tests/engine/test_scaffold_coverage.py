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
        # Finding 6 (full-corpus re-audit, 2026-08-11): the *_order_of_ops_negatives
        # nodes generate "What is -13 + 6 x 6?" -- the skill under test is PRECEDENCE,
        # but the label matched negative_numbers.md 3-2 (it had explicitly claimed the
        # keyword "order of operations with negative") and a child was shown a
        # thermometer/number-line where they needed a priority ladder. Fixing this
        # needed BOTH sides: dropping the keyword alone still lost the resulting 2-2
        # tie on the alphabetical tie-break ("negative_numbers" < "order_of_operations").
        ("Order of operations with negative numbers", "priority ladder"),
        ("Order of operations with negatives", "priority ladder"),
        # ...and the plain negatives nodes must NOT be dragged along with them.
        ("Negative numbers (temperature contexts)", "thermometer"),
    ]
    for label, marker in cases:
        body = load_visual_scaffold(SCAFFOLD_ROOT, "mathematics", label)
        assert body and marker.lower() in body.lower(), (
            f"label {label!r} routed to the wrong scaffold "
            f"(wanted body containing {marker!r}; got: {body[:120]!r})"
        )


def test_no_mc4_question_leaks_its_own_answer():
    """A meaning-label must never contain the word it is asking for.

    Found 2026-08-12: the homophone item asked "Which word means 'over there'
    or 'in that place'?" with the correct answer "there" -- printed inside its
    own stem, so a child could score it without knowing the homophone at all.
    Swept across every mc4 generator in the registry rather than one node,
    because the generic SG/US/IN packs reuse the same generator functions and
    replicated the same defect three times.
    """
    import random as _random

    from mentar.engine.item_sources import build_registry

    registry = build_registry(REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    leaks, seen = [], set()
    for src in registry.values():
        for node, fn in src["generators"].items():
            if node in seen:
                continue
            seen.add(node)
            rng = _random.Random(11)
            for _ in range(40):
                res = fn(rng)
                if res[0] != "mc4" or len(res) < 5:
                    break
                idx = "ABCD".find(str(res[3]).strip().upper())
                if idx < 0 or idx >= len(res[4]):
                    continue
                correct = str(res[4][idx]).lower()
                stem = res[2].split("A)")[0].lower()
                if len(correct) > 3 and correct in stem:
                    others = [str(c).lower() for i, c in enumerate(res[4]) if i != idx]
                    # if the stem quotes every option it is a legitimate "which of
                    # these" framing; only a lone correct answer in the stem leaks
                    if not any(o in stem for o in others if len(o) > 3):
                        leaks.append((node, res[2][:120], correct))
                        break
    assert leaks == [], f"mc4 questions containing their own answer: {leaks}"
