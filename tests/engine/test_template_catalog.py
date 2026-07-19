"""Tests for R3.1 — template catalog auto-discovery + named item-source registry.

    python3 tests/engine/test_template_catalog.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import (  # noqa: E402
    derive_subject_key,
    load_curriculum,
    load_template_meta,
)
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
    "curriculum/templates/AU_ACARA/year3_maths.md": {
        "key": "au_acara_year3_maths", "label": "Maths — Year 3 🇦🇺", "item_source": "au_year3",
    },
    "curriculum/templates/AU_ACARA/year4_maths.md": {
        "key": "au_acara_year4_maths", "label": "Maths — Year 4 🇦🇺", "item_source": "au_year4",
    },
    "curriculum/templates/AU_ACARA/year2_maths.md": {
        "key": "au_acara_year2_maths", "label": "Maths — Year 2 🇦🇺", "item_source": "au_year2",
    },
    "curriculum/templates/AU_ACARA/year5_maths.md": {
        "key": "au_acara_year5_maths", "label": "Maths — Year 5 🇦🇺", "item_source": "au_year5",
    },
    "curriculum/templates/AU_ACARA/year6_maths.md": {
        "key": "au_acara_year6_maths", "label": "Maths — Year 6 🇦🇺", "item_source": "au_year6",
    },
    "curriculum/templates/AU_ACARA/year2_english.md": {
        "key": "au_acara_year2_english", "label": "English — Year 2 🇦🇺", "item_source": "au_english_year2",
    },
    "curriculum/templates/AU_ACARA/year5_english.md": {
        "key": "au_acara_year5_english", "label": "English — Year 5 🇦🇺", "item_source": "au_english_year5",
    },
    "curriculum/templates/AU_ACARA/year6_english.md": {
        "key": "au_acara_year6_english", "label": "English — Year 6 🇦🇺", "item_source": "au_english_year6",
    },
    "curriculum/templates/practice/maths.md": {
        "key": "practice_maths", "label": "Maths practice ➗", "item_source": "maths_practice",
    },
    "curriculum/templates/practice/english.md": {
        "key": "practice_english", "label": "English practice 📖", "item_source": "english_practice",
    },
    "curriculum/templates/IN_GENERIC/class3_maths.md": {
        "key": "in_generic_class3_maths", "label": "Maths — Class 3 🇮🇳 (general)",
        "item_source": "in_generic_maths",
    },
}


def test_all_shipped_templates_discovered_with_expected_meta():
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
    """derive_subject_key() must reproduce every shipped template's key exactly
    (originally 5, at the R3 migration; more added since), with ZERO manual
    input from any template -- an already-issued session cookie must keep
    resolving to the same subject after this change."""
    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert derive_subject_key(REPO_ROOT / rel, meta) == expected["key"], rel


def test_subject_key_front_matter_still_wins_when_present():
    """The escape hatch itself still works, for the rare genuine collision."""
    meta = {"subject_key": "custom_key"}
    assert derive_subject_key(REPO_ROOT / "curriculum/templates/AU_ACARA/year3_maths.md", meta) == "custom_key"


def test_authority_dir_resolved_past_a_year_subfolder():
    """R-MC: derive_subject_key must resolve the AUTHORITY dir (the one
    directly under templates/), not just the immediate parent -- so a future
    templates/<AUTHORITY>/<year>/*.md shape (MULTI_COUNTRY.md §2b, not built
    yet) can't silently change a template's key. Simulated with a path that
    doesn't need to exist on disk (derive_subject_key does no I/O)."""
    meta = {"subject_key": None}
    flat = derive_subject_key(REPO_ROOT / "curriculum/templates/AU_ACARA/year3_maths.md", meta)
    nested = derive_subject_key(
        REPO_ROOT / "curriculum/templates/AU_ACARA/2027/year3_maths.md", meta
    )
    assert flat == nested == "au_acara_year3_maths"


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


def test_no_skill_id_collides_across_any_shipped_template():
    """R6.2/practice-pack guard: skill_id is NOT auto-namespaced the way the
    subject_key is -- individual node ids inside a template's `concepts:`
    list must be manually kept collision-free (AU's au3_/au4_ prefixes, the
    practice pack's practice_ prefix, the in_generic_ prefix). A collision
    would silently merge two unrelated skills' skill_state mastery rows in
    the DB. As of R10 every pack ships under curriculum/templates/ (India
    moved there from the old downloadable_packs/), so scanning templates/
    covers every shipped pack -- and a new one dropped in later is covered
    automatically, not just the ones in _EXPECTED."""
    owners: dict[str, str] = {}
    paths = sorted(_TPL.glob("**/*.md"))
    for path in paths:
        curriculum = load_curriculum(path)
        for skill_id in curriculum:
            rel = str(path.relative_to(REPO_ROOT))
            assert skill_id not in owners, (
                f"skill_id {skill_id!r} used by both {owners.get(skill_id)!r} and {rel!r}"
            )
            owners[skill_id] = rel


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} template-catalog tests passed.")
