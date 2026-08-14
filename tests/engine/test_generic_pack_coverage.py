"""Coverage + wiring guards for the GENERIC (board-agnostic) country packs.

The generic packs are built from one shared stage table per subject
(engine/generic_items.py PACK_LEVELS x STAGE_CONCEPTS, mirrored for English in
generic_english_items.py), so the failure modes are structural, not per-item:

  1. A HOLE -- a level that ships one subject but not another. Found for real on
     2026-08-14: every India level had maths AND English except Class 3, which had
     maths only, because its legacy maths pack predates the stage table and so no
     in_c3 level existed for English to hang off. Nothing failed; the cell was
     just quietly absent from the picker.
  2. A WIRING drift -- a template's concept ids not matching the generator keys
     its item_source resolves to. Every id that doesn't match is a node that can
     never draw an item (or draws another concept's items).

Per-item correctness is covered elsewhere (test_au_english_items.py /
test_au_items.py self-validate every generator's ground truth against the
verifier); this file only checks that the packs are complete and wired.

    python3 tests/engine/test_generic_pack_coverage.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import load_template_meta  # noqa: E402
from mentar.engine.generic_items import PACK_LEVELS  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

_TPL = REPO_ROOT / "curriculum" / "templates"
_BANK = REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl"

# Class 3 maths ships from the legacy in_generic_maths source (class3_maths.md),
# which predates the shared stage table -- see PACK_LEVELS' own comment.
_LEGACY_MATHS = {("IN", "Class 3")}


def _shipped() -> list[tuple[dict, pathlib.Path]]:
    out = []
    for path in sorted(_TPL.glob("**/*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        out.append((load_template_meta(path), path))
    return out


def _concept_ids(path: pathlib.Path) -> list[str]:
    """Concept ids straight out of the front matter, without importing the app."""
    import yaml

    text = path.read_text(encoding="utf-8")
    front = text.split("---", 2)[1]
    return [c["id"] for c in yaml.safe_load(front)["concepts"]]


def test_every_generic_level_ships_every_subject_it_has_a_stage_table_for():
    """The hole check. A level in PACK_LEVELS is a promise that the picker offers
    that country/level -- so each subject with a shared stage table must have a
    template there, or the cell is silently missing."""
    shipped = {
        (meta["country"], meta["year_level"], meta["subject"])
        for meta, _path in _shipped()
    }
    missing = []
    for authority, levels in PACK_LEVELS.items():
        country = authority.split("_")[0]
        for _prefix, level_name, _stage in levels:
            for subject in ("mathematics", "english"):
                if subject == "mathematics" and (country, level_name) in _LEGACY_MATHS:
                    continue
                if (country, level_name, subject) not in shipped:
                    missing.append(f"{country} {level_name} {subject}")
    assert not missing, "generic packs missing a subject at a shipped level: " + ", ".join(missing)


def test_every_generic_template_concept_id_resolves_to_a_generator():
    """The wiring check, both directions: an id with no generator can never draw
    an item, and a generator with no id is content nobody can reach."""
    registry = build_registry(_BANK)
    prefixes = {p for levels in PACK_LEVELS.values() for p, _n, _s in levels}
    checked = 0
    for meta, path in _shipped():
        source = meta["item_source"]
        if not any(source.startswith(p + "_") for p in prefixes):
            continue  # AU/pilot/practice packs carry their own hand-written dicts
        gens = set(registry[source]["generators"])
        ids = set(_concept_ids(path))
        assert ids == gens, (
            f"{path.relative_to(REPO_ROOT)} ({source}): "
            f"ids-without-generators={sorted(ids - gens)}, "
            f"generators-without-ids={sorted(gens - ids)}"
        )
        checked += 1
    assert checked >= 20, f"expected the generic packs to be scanned, only saw {checked}"


def test_the_class3_english_generators_self_validate():
    """The 2026-08-14 addition specifically: its stage-3 generators are shared
    with every other Stage 3 level, but prove the ground truth still passes the
    verifier through THIS pack's node ids (the same contract every other
    generator file's self-validate test holds)."""
    registry = build_registry(_BANK)
    gens = registry["in_c3_english"]["generators"]
    assert len(gens) == 4, sorted(gens)
    g = ItemGenerator(generators=gens, rng=random.Random(3))
    for node in gens:
        for _ in range(60):
            item = g.sample(node)
            assert item is not None and item.problem.strip(), node
            outcome = check(answer_type=item.answer_type, checker=item.checker,
                            llm_output=item.answer, ground_truth=item.answer)
            assert outcome.result is CheckResult.PASS, (node, item.problem, item.answer)
            assert item.choices is not None and len(set(item.choices)) == 4, node


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} generic-pack coverage tests passed.")
