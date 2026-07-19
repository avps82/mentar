"""Tests for the ACARA-aligned Year 3 / Year 4 item generators (engine/au_items.py).

Safety contract (same as itemgen/science_items): every generator's own ground truth
must PASS the deterministic verifier over many draws; mc4 generators must carry
structured choices whose answer letter points at the correct option.

    python3 tests/engine/test_au_items.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.au_items import (  # noqa: E402
    AU_YEAR2_GENERATORS,
    AU_YEAR3_GENERATORS,
    AU_YEAR4_GENERATORS,
    AU_YEAR5_GENERATORS,
    AU_YEAR6_GENERATORS,
    AU_YEAR7_GENERATORS,
    AU_YEAR8_GENERATORS,
    gen_place_value_3digit,
    gen_place_value_4digit,
)
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

_LETTERS = "ABCD"


def _self_validate(generators: dict, seed: int, draws: int = 200) -> None:
    g = ItemGenerator(generators=generators, rng=random.Random(seed))
    for node in generators:
        for _ in range(draws):
            it = g.sample(node)
            assert it is not None and it.problem.strip(), node
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)
            if it.answer_type == "mc4":
                assert it.choices is not None and len(it.choices) == 4, node
                assert len(set(it.choices)) == 4, (node, it.choices)  # distinct options


def test_year3_generators_self_validate():
    _self_validate(AU_YEAR3_GENERATORS, seed=3)


def test_year4_generators_self_validate():
    _self_validate(AU_YEAR4_GENERATORS, seed=4)


def test_year2_generators_self_validate():
    _self_validate(AU_YEAR2_GENERATORS, seed=2)


def test_year5_generators_self_validate():
    """R14a/R13: also the first self-validate coverage of decimal-type generators
    -- exercises _check_decimal_exact end-to-end, not just int/fraction/mc4."""
    _self_validate(AU_YEAR5_GENERATORS, seed=5)


def test_year6_generators_self_validate():
    _self_validate(AU_YEAR6_GENERATORS, seed=6)


def test_year7_generators_self_validate():
    """R15: first coverage of negative-integer content + a 'solve for x' node."""
    _self_validate(AU_YEAR7_GENERATORS, seed=7)


def test_year8_generators_self_validate():
    _self_validate(AU_YEAR8_GENERATORS, seed=8)


def test_place_value_answer_letter_is_the_digit_value():
    """The mc answer letter must point at digit × 10^place — guards the
    option-index logic against shuffle mistakes."""
    rng = random.Random(0)
    for gen, n_digits in ((gen_place_value_3digit, 3), (gen_place_value_4digit, 4)):
        for _ in range(300):
            _, _, problem, letter, choices = gen(rng)
            # Parse "the number N" and "digit D" back out of the stem.
            words = problem.split()
            number = int(words[words.index("number") + 1].rstrip(","))
            digit = int(words[words.index("digit") + 1].rstrip("?"))
            digits = [int(ch) for ch in str(number)]
            pos = digits.index(digit)
            expected = digit * (10 ** (n_digits - 1 - pos))
            assert choices[_LETTERS.index(letter)] == str(expected), problem


def test_au_registries_do_not_collide_with_pilot_node_ids():
    """AU node ids are namespaced (au3_/au4_) so a learner's skill_state rows can
    never collide with the pilot fractions/arithmetic/science nodes."""
    for node in list(AU_YEAR3_GENERATORS) + list(AU_YEAR4_GENERATORS):
        assert node.startswith(("au3_", "au4_")), node


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} au-items tests passed.")
