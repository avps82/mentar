"""Tests for the R8 India generic Class 3 maths pack (engine/in_generic_items.py
+ curriculum/templates/IN_GENERIC/class3_maths.md).

Safety contract (same as itemgen/practice_items): reused generators must still
self-validate under their NEW node ids/registry entry, and the template itself
must pass the same validator every other shipped template does.

    python3 tests/engine/test_in_generic_items.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import load_curriculum, load_template_meta  # noqa: E402
from mentar.engine.in_generic_items import IN_GENERIC_MATHS_GENERATORS  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402
from mentar.tools.validate_template import validate  # noqa: E402

_PACK_PATH = REPO_ROOT / "curriculum" / "templates" / "IN_GENERIC" / "class3_maths.md"


def test_in_generic_generators_self_validate():
    g = ItemGenerator(generators=IN_GENERIC_MATHS_GENERATORS, rng=random.Random(21))
    for node in IN_GENERIC_MATHS_GENERATORS:
        for _ in range(200):
            it = g.sample(node)
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)


def test_in_generic_template_passes_validation():
    result = validate(str(_PACK_PATH))
    assert result.ok is True, f"IN_GENERIC template failed validation: {result.errors}"
    assert set(result.concept_ids) == {
        "in_generic_addition", "in_generic_subtraction",
        "in_generic_times_tables", "in_generic_unit_fractions",
    }


def test_in_generic_template_has_no_ncert_branding_or_alignment():
    """The whole point of this pack: no NCERT/CBSE branding, codes, or claimed
    curriculum alignment in anything a parent/child/code actually sees or
    uses (label, description, curriculum_standard, node labels) --
    docs/CONTENT_LICENSES.md §2b. Explanatory comments ABOUT that licensing
    decision (which legitimately name NCERT) are out of scope for this
    check; only surfaced/consumed content matters."""
    meta = load_template_meta(_PACK_PATH)
    curriculum = load_curriculum(_PACK_PATH)
    surfaced = " ".join([
        meta["label"] or "", meta["description"] or "",
        *[node["label"] for node in curriculum.values()],
    ]).lower()
    for banned in ("ncert", "cbse", "icse"):
        assert banned not in surfaced, f"{banned!r} must not appear in surfaced content"


def test_in_generic_node_ids_match_registry():
    """The template's node ids must exactly match the generator registry's
    keys -- a mismatch would mean a node has no generator (loud-fail at
    startup, A9) or a generator nobody's template references."""
    curriculum = load_curriculum(_PACK_PATH)
    assert set(curriculum) == set(IN_GENERIC_MATHS_GENERATORS)


def test_item_source_registry_has_in_generic_maths():
    registry = build_registry(REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    assert "in_generic_maths" in registry
    entry = registry["in_generic_maths"]
    assert entry["generators"] is IN_GENERIC_MATHS_GENERATORS
    assert entry["itembank"] is None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} IN_GENERIC tests passed.")
