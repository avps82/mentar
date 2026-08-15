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

# Levels where science is taught as SEPARATE subjects. NOT a stage cutoff: the
# split happens at a different point in each country -- India keeps a combined
# Science through Class 10, Singapore splits at Secondary 3, the US sequences from
# Grade 9. A stage cutoff shipped India Class 9-10 with no science at all, which
# the coverage matrix caught, so this keys off the split itself.
def _split_prefixes():
    """Prefixes with no COMBINED science pack: the split levels, plus the levels
    that ship no science at all (US Grade 12 is electives)."""
    from mentar.engine.senior_science_items import (
        NO_SCIENCE_LEVELS,
        SENIOR_LEVELS,
        US_SEQUENCE,
    )
    return ({p for levels in SENIOR_LEVELS.values() for p, _n, _s in levels}
            | {p for p, _n, _s in US_SEQUENCE} | NO_SCIENCE_LEVELS)


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


def _labels(path: pathlib.Path) -> dict[str, str]:
    """{concept id (or AU slug): label} from a template's front matter."""
    import re

    import yaml

    front = path.read_text(encoding="utf-8").split("---", 2)[1]
    out = {}
    for c in yaml.safe_load(front)["concepts"]:
        out[re.sub(r"^au\d+_science_", "", c["id"])] = c["label"]
    return out


def _seed_questions(path: pathlib.Path) -> dict[str, str]:
    """{concept id: the question part of its first transfer seed} -- everything
    before the "A)" option list, which is what a generator emits as the stem."""
    import yaml

    front = path.read_text(encoding="utf-8").split("---", 2)[1]
    return {
        c["id"]: c["transfer_seeds"][0].split("A)")[0].strip()
        for c in yaml.safe_load(front)["concepts"]
    }


def test_every_generic_level_ships_every_subject_it_has_a_stage_table_for():
    """The hole check. A level in PACK_LEVELS is a promise that the picker offers
    that country/level -- so each subject with a shared stage table must have a
    template there, or the cell is silently missing."""
    shipped = {
        (meta["country"], meta["year_level"], meta["subject"])
        for meta, _path in _shipped()
    }
    missing = []
    wrong_science = []
    for authority, levels in PACK_LEVELS.items():
        country = authority.split("_")[0]
        for _prefix, level_name, _stage in levels:
            senior = _prefix in _split_prefixes()
            for subject in ("mathematics", "english", "science"):
                if subject == "mathematics" and (country, level_name) in _LEGACY_MATHS:
                    continue
                if subject == "science" and senior:
                    # A combined science pack here would contradict the split.
                    if (country, level_name, subject) in shipped:
                        wrong_science.append(f"{country} {level_name}")
                    continue
                if (country, level_name, subject) not in shipped:
                    missing.append(f"{country} {level_name} {subject}")
    assert not missing, "generic packs missing a subject at a shipped level: " + ", ".join(missing)
    assert not wrong_science, (
        "senior levels must ship split science (physics/chemistry/biology), not a "
        "combined 'science' pack: " + ", ".join(wrong_science)
    )


def test_every_senior_level_ships_its_split_science():
    """The other half: a senior level exists because a student studies the three
    sciences separately there, so each of AU/IN/SG's senior levels must carry all
    three, and each US high-school grade its one sequenced subject."""
    from mentar.engine.senior_science_items import SENIOR_LEVELS, US_SEQUENCE

    shipped = {
        (meta["country"], meta["year_level"], meta["subject"]) for meta, _p in _shipped()
    }
    missing = []
    for authority, levels in SENIOR_LEVELS.items():
        country = authority.split("_")[0]
        for _prefix, level_name, _stage in levels:
            for subject in ("physics", "chemistry", "biology"):
                if (country, level_name, subject) not in shipped:
                    missing.append(f"{country} {level_name} {subject}")
    for _prefix, level_name, subject in US_SEQUENCE:
        if ("US", level_name, subject) not in shipped:
            missing.append(f"US {level_name} {subject}")
    assert not missing, "senior science missing: " + ", ".join(missing)


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


def test_generic_science_matches_the_au_template_of_the_same_stage():
    """The stage table for science is DERIVED from engine/science_items.py's AU
    year dicts, so a code-only test would be tautological. Compare the shipped
    TEMPLATES instead: a generic level must carry exactly the labels its AU
    counterpart carries at that stage. Catches a mis-mapped stage (Stage 3
    quietly serving Stage 5 content) in the one place it would actually show.
    """
    from mentar.engine.generic_science_items import STAGE_CONCEPTS

    au_labels = {}
    # 2-10: AU ships combined Science to Year 10, and India's combined Science
    # now runs to Class 10 (stage 10) against those same year templates.
    for year in range(2, 11):
        path = _TPL / "AU_ACARA" / f"year{year}_science.md"
        au_labels[year] = _labels(path)

    seen = 0
    for authority, levels in PACK_LEVELS.items():
        country = authority.split("_")[0]
        for prefix, level_name, stage in levels:
            if prefix in _split_prefixes():
                continue  # science is split here, so there is no combined template
            path = next(
                p for meta, p in _shipped()
                if meta["country"] == country and meta["year_level"] == level_name
                and meta["subject"] == "science"
            )
            got = _labels(path)
            want = {
                slug: au_labels[stage][slug] for slug in STAGE_CONCEPTS[stage]
            }
            assert {k.replace(prefix + "_", ""): v for k, v in got.items()} == want, (
                f"{path.relative_to(REPO_ROOT)}: stage {stage} labels drifted from AU Year {stage}"
            )
            seen += 1
    from mentar.engine.generic_science_items import GENERIC_SCIENCE_ITEM_SOURCES
    assert seen == len(GENERIC_SCIENCE_ITEM_SOURCES), (
        f"expected {len(GENERIC_SCIENCE_ITEM_SOURCES)} combined-science levels, saw {seen}"
    )


def test_generic_science_nodes_serve_their_own_concept():
    """The routing check, and the one that matters most for a DERIVED stage table:
    key sets matching proves nothing about which FUNCTION each id points at, so a
    mis-derivation could wire sg_p3_life_cycle to the heat-sources generator with
    every other test still green. Each node's own seed question must therefore turn
    up among the stems it actually draws (the generators use a small fixed set of
    positive/negative phrasings per concept, so this is exact, not fuzzy).
    """
    registry = build_registry(_BANK)
    checked = 0
    for meta, path in _shipped():
        if meta["subject"] != "science" or not meta["item_source"].endswith("_science"):
            continue
        if meta["country"] not in ("SG", "US", "IN"):
            continue  # generic packs only -- AU's own science packs are tested separately
        gens = registry[meta["item_source"]]["generators"]
        g = ItemGenerator(generators=gens, rng=random.Random(11))
        for node, seed in _seed_questions(path).items():
            stems = {g.sample(node).stem.casefold() for _ in range(20)}
            # casefold: some authored seeds SHOUT a word for emphasis ("Which of
            # these IS a planet?") where the generator's stem does not.
            assert seed.casefold() in stems, (
                f"{path.relative_to(REPO_ROOT)}: {node} never asks its own seed question\n"
                f"  seed:  {seed!r}\n  drew:  {sorted(stems)!r}"
            )
            checked += 1
    from mentar.engine.generic_science_items import GENERIC_SCIENCE_ITEM_SOURCES
    expected = sum(len(g) for g in GENERIC_SCIENCE_ITEM_SOURCES.values())
    assert checked == expected, f"expected {expected} combined-science nodes, checked {checked}"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} generic-pack coverage tests passed.")
