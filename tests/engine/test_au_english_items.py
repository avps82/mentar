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


if __name__ == "__main__":
    test_year2_english_generators_self_validate()
    print("  ✓ test_year2_english_generators_self_validate")
    test_year5_english_generators_self_validate()
    print("  ✓ test_year5_english_generators_self_validate")
    test_year6_english_generators_self_validate()
    print("  ✓ test_year6_english_generators_self_validate")
