"""Tests for R3.1 — template catalog auto-discovery + named item-source registry.

    python3 tests/engine/test_template_catalog.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import derive_subject_key, load_template_meta  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402

_TPL = REPO_ROOT / "curriculum" / "templates"

# The exact catalog the hardcoded SUBJECTS dict carried before R3.1 -- the scan
# must reproduce these keys/labels/item_sources exactly (session-cookie
# stability). Keys are now derived FULLY AUTOMATICALLY from directory
# structure (derive_subject_key) -- no template needs a subject_key: override,
# proven by its absence below.
_EXPECTED = {
    "curriculum/templates/_pilot/fractions.md": {
        "key": "fractions", "label": "Fractions 🍕", "item_source": "pilot_fractions",
    },
    "curriculum/templates/_pilot/arithmetic.md": {
        "key": "arithmetic", "label": "Maths: + − × 🔢", "item_source": "arithmetic",
    },
    "curriculum/templates/_pilot/science.md": {
        "key": "science", "label": "Science 🔬", "item_source": "science",
    },
    "curriculum/templates/AU/year3_maths.md": {
        "key": "au_year3_maths", "label": "Maths — Year 3 🇦🇺", "item_source": "au_year3",
    },
    "curriculum/templates/AU/year4_maths.md": {
        "key": "au_year4_maths", "label": "Maths — Year 4 🇦🇺", "item_source": "au_year4",
    },
}


def test_all_five_templates_discovered_with_expected_meta():
    found = sorted(str(p.relative_to(REPO_ROOT)) for p in _TPL.glob("**/*.md"))
    assert found == sorted(_EXPECTED), found

    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert meta["label"] == expected["label"], rel
        assert meta["item_source"] == expected["item_source"], rel


def test_no_shipped_template_needs_the_subject_key_escape_hatch():
    """The automatic directory-based rule must be sufficient on its own -- if
    a future template needed subject_key: to avoid a collision, that would be
    a signal something's off with the automatic rule, not routine authoring."""
    for rel in _EXPECTED:
        meta = load_template_meta(REPO_ROOT / rel)
        assert meta["subject_key"] is None, f"{rel} shouldn't need the escape hatch"


def test_derived_keys_match_the_pre_r3_hardcoded_dict():
    """derive_subject_key() must reproduce today's 5 literal keys exactly, with
    ZERO manual input from any template -- an already-issued session cookie
    must keep resolving to the same subject after this change."""
    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert derive_subject_key(REPO_ROOT / rel, meta) == expected["key"], rel


def test_subject_key_front_matter_still_wins_when_present():
    """The escape hatch itself still works, for the rare genuine collision."""
    meta = {"subject_key": "custom_key"}
    assert derive_subject_key(REPO_ROOT / "curriculum/templates/AU/year3_maths.md", meta) == "custom_key"


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
