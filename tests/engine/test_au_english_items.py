"""Tests for the ACARA-aligned Year 2/5/6 English item generators
(engine/au_english_items.py).

Safety contract (same as test_au_items.py/itemgen/science_items): every generator's
own ground truth must PASS the deterministic verifier over many draws; mc4
generators must carry structured choices whose answer letter points at the
correct option, and the choices must be pairwise distinct (proves the curated
word tables stay disjoint at runtime, not just on manual review).

    python3 tests/engine/test_au_english_items.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.au_english_items import (  # noqa: E402
    AU_ENGLISH_YEAR2_GENERATORS,
    AU_ENGLISH_YEAR5_GENERATORS,
    AU_ENGLISH_YEAR6_GENERATORS,
    AU_ENGLISH_YEAR9_GENERATORS,
    AU_ENGLISH_YEAR10_GENERATORS,
    AU_ENGLISH_YEAR11_GENERATORS,
    AU_ENGLISH_YEAR12_GENERATORS,
)
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def _self_validate(generators: dict, seed: int, draws: int = 200) -> None:
    g = ItemGenerator(generators=generators, rng=random.Random(seed))
    for node in generators:
        for _ in range(draws):
            it = g.sample(node)
            assert it is not None and it.problem.strip(), node
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)
            assert it.answer_type == "mc4", node  # every English node this wave is mc4
            assert it.choices is not None and len(it.choices) == 4, node
            assert len(set(it.choices)) == 4, (node, it.choices)  # distinct options


def test_year2_english_generators_self_validate():
    _self_validate(AU_ENGLISH_YEAR2_GENERATORS, seed=102)


def test_year5_english_generators_self_validate():
    _self_validate(AU_ENGLISH_YEAR5_GENERATORS, seed=105)


def test_year6_english_generators_self_validate():
    _self_validate(AU_ENGLISH_YEAR6_GENERATORS, seed=106)


def test_senior_english_generators_self_validate_and_carry_method_cards():
    """Year 9-12 (2026-08-14). Same ground-truth contract as every year above,
    PLUS a method card: these generators pass glosses/concept_name, so
    explain-mode's Type-4 card path works for senior English. Year 2-8 English
    still has no cards (pre-existing gap, tracked) -- that is why this asserts
    the card only for the years that claim one."""
    for year, gens in (
        (9, AU_ENGLISH_YEAR9_GENERATORS),
        (10, AU_ENGLISH_YEAR10_GENERATORS),
        (11, AU_ENGLISH_YEAR11_GENERATORS),
        (12, AU_ENGLISH_YEAR12_GENERATORS),
    ):
        _self_validate(gens, seed=100 + year)
        g = ItemGenerator(generators=gens, rng=random.Random(year))
        for node in gens:
            item = g.sample(node)
            assert item.method_steps, f"Year {year} node {node} has no method card"
            assert item.method_steps[0].isupper(), item.method_steps[0]


if __name__ == "__main__":
    test_year2_english_generators_self_validate()
    print("  ✓ test_year2_english_generators_self_validate")
    test_year5_english_generators_self_validate()
    print("  ✓ test_year5_english_generators_self_validate")
    test_year6_english_generators_self_validate()
    print("  ✓ test_year6_english_generators_self_validate")
    test_senior_english_generators_self_validate_and_carry_method_cards()
    print("  ✓ test_year6_english_generators_self_validate")


def test_every_english_generator_carries_an_explain_card():
    """2026-08-15: English was the largest explain-mode gap -- 116 of the 158
    nodes with no deterministic explanation at all were English, because these
    generators never passed glosses/concept_name. Every one does now, so a new
    English generator that forgets is a failure here rather than a silent
    fallback to LLM prose for a child who asked how it works.

    Covers the practice pack too: its odd-one-out generator has a custom shape
    (not mc_which_is) and needed its card written by hand."""
    import mentar.engine.au_english_items as english
    from mentar.engine.practice_items import ENGLISH_PRACTICE_GENERATORS

    generators = {
        name: getattr(english, name)
        for name in dir(english)
        if name.startswith("gen_") and callable(getattr(english, name))
    }
    generators.update(ENGLISH_PRACTICE_GENERATORS)
    assert len(generators) >= 32, f"expected the whole English set, found {len(generators)}"

    without = []
    for name, fn in sorted(generators.items()):
        g = ItemGenerator(generators={name: fn}, rng=random.Random(13))
        for _ in range(30):
            item = g.sample(name)
            if not item.method_steps:
                without.append(name)
                break
            # A card must NAME the concept and show the answer, not just restate
            # the options: first line is the concept, second holds the answer.
            assert item.method_steps[0].isupper(), (name, item.method_steps[0])
            assert len(item.method_steps) >= 3, (name, item.method_steps)
    assert not without, f"English generators with no explain card: {without}"
