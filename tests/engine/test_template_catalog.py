"""Tests for R3.1 — template catalog auto-discovery + named item-source registry.

    python3 tests/engine/test_template_catalog.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import load_template_meta  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402

_TPL = REPO_ROOT / "curriculum" / "templates"

# The exact catalog the hardcoded SUBJECTS dict carried before R3.1 -- the scan
# must reproduce these keys/labels/item_sources exactly (session-cookie
# stability for the 3 pilot templates via their subject_key: override).
_EXPECTED = {
    "curriculum/templates/_pilot/fractions.md": {
        "subject_key": "fractions", "label": "Fractions 🍕", "item_source": "pilot_fractions",
    },
    "curriculum/templates/_pilot/arithmetic.md": {
        "subject_key": "arithmetic", "label": "Maths: + − × 🔢", "item_source": "arithmetic",
    },
    "curriculum/templates/_pilot/science.md": {
        "subject_key": "science", "label": "Science 🔬", "item_source": "science",
    },
    "curriculum/templates/AU/year3_maths.md": {
        "subject_key": None, "label": "Maths — Year 3 🇦🇺", "item_source": "au_year3",
    },
    "curriculum/templates/AU/year4_maths.md": {
        "subject_key": None, "label": "Maths — Year 4 🇦🇺", "item_source": "au_year4",
    },
}


def test_all_five_templates_discovered_with_expected_meta():
    found = sorted(str(p.relative_to(REPO_ROOT)) for p in _TPL.glob("**/*.md"))
    assert found == sorted(_EXPECTED), found

    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert meta["subject_key"] == expected["subject_key"], rel
        assert meta["label"] == expected["label"], rel
        assert meta["item_source"] == expected["item_source"], rel


def test_derived_keys_match_the_pre_r3_hardcoded_dict():
    """template_id-with-dashes-to-underscores, or the subject_key override when
    present, must reproduce today's 5 literal keys exactly -- an already-issued
    session cookie must keep resolving to the same subject after this change."""
    expected_keys = {"fractions", "arithmetic", "science", "au_year3_maths", "au_year4_maths"}
    derived = set()
    for rel in _EXPECTED:
        meta = load_template_meta(REPO_ROOT / rel)
        key = meta["subject_key"] or meta["template_id"].replace("-", "_")
        derived.add(key)
    assert derived == expected_keys


def test_item_source_registry_has_every_referenced_name():
    registry = build_registry(REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    for rel, expected in _EXPECTED.items():
        assert expected["item_source"] in registry, (rel, expected["item_source"])
        entry = registry[expected["item_source"]]
        assert "generators" in entry and "itembank" in entry


def test_unregistered_item_source_is_detectable():
    """The exact check web/app.py performs at startup (name not in the
    registry) — proven here at the unit level since a full app-module reload
    against a swapped-in bad template would need env-overriding a hardcoded
    templates directory, which is out of scope for this fix."""
    registry = build_registry(REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    assert "not_a_real_item_source" not in registry
    assert None not in registry  # a template with no item_source: field at all


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} template-catalog tests passed.")
