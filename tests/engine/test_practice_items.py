"""Tests for the evergreen Try-out practice sampler (engine/practice_items.py) --
times tables/skip counting/doubles-halves (maths) + synonyms-antonyms/rhyming/
odd-one-out/plurals (English).

Safety contract (same as itemgen/science_items): the generator's own ground
truth must PASS the deterministic verifier -- the LLM never decides
correctness for these drills either.

    python3 tests/engine/test_practice_items.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.engine.practice_items import (  # noqa: E402
    _ANTONYM_PAIRS,
    _ODD_ONE_OUT_CLASSES,
    _PLURAL_PAIRS,
    _RHYME_GROUPS,
    _SYNONYM_GROUPS,
    ENGLISH_PRACTICE_GENERATORS,
    MATHS_PRACTICE_GENERATORS,
)
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def test_maths_practice_generators_self_validate():
    g = ItemGenerator(generators=MATHS_PRACTICE_GENERATORS, rng=random.Random(11))
    for node in MATHS_PRACTICE_GENERATORS:
        for _ in range(200):
            it = g.sample(node)
            assert it is not None and it.answer.lstrip("-").isdigit(), (node, it.problem, it.answer)
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)


def test_times_tables_stays_within_1_to_12():
    g = ItemGenerator(generators=MATHS_PRACTICE_GENERATORS, rng=random.Random(1))
    for _ in range(200):
        it = g.sample("practice_times_tables")
        # "What is A × B?" -- both factors must be in [1, 12].
        a_str, b_str = it.problem.replace("What is ", "").rstrip("?").split(" × ")
        assert 1 <= int(a_str) <= 12
        assert 1 <= int(b_str) <= 12


def test_skip_counting_sequence_is_consistent():
    g = ItemGenerator(generators=MATHS_PRACTICE_GENERATORS, rng=random.Random(2))
    for _ in range(200):
        it = g.sample("practice_skip_counting")
        nums = [int(x) for x in it.problem.replace(
            "What number comes next: ", "").rstrip("?").replace("__", "").split(", ") if x]
        # 4 given terms + the answer must form one constant-step arithmetic sequence.
        full = [*nums, int(it.answer)]
        steps = {full[i + 1] - full[i] for i in range(len(full) - 1)}
        assert len(steps) == 1, (it.problem, it.answer)
        assert next(iter(steps)) in (2, 3, 5, 10)


def test_doubles_halves_math_is_correct():
    g = ItemGenerator(generators=MATHS_PRACTICE_GENERATORS, rng=random.Random(3))
    for _ in range(200):
        it = g.sample("practice_doubles_halves")
        if "double" in it.problem:
            n = int(it.problem.replace("What is double ", "").rstrip("?"))
            assert int(it.answer) == n * 2
        else:
            n = int(it.problem.replace("What is half of ", "").rstrip("?"))
            assert n % 2 == 0, "half-of target must always be evenly halvable"
            assert int(it.answer) == n // 2


def test_english_practice_generators_self_validate():
    g = ItemGenerator(generators=ENGLISH_PRACTICE_GENERATORS, rng=random.Random(13))
    for node in ENGLISH_PRACTICE_GENERATORS:
        for _ in range(200):
            it = g.sample(node)
            assert it.answer in ("A", "B", "C", "D"), (node, it.problem, it.answer)
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)


def _assert_pairwise_disjoint(table: dict[str, list[str]], name: str) -> None:
    """R6.2-style content-quality guard: every fact table's members must be
    pairwise disjoint across labels -- a member appearing under two different
    labels would make a distractor for one label accidentally also correct
    for another (ambiguous question)."""
    seen: dict[str, str] = {}
    for label, members in table.items():
        for m in members:
            assert m not in seen, (
                f"{name}: {m!r} appears under both {seen.get(m)!r} and {label!r} -- ambiguous"
            )
            seen[m] = label


def test_english_fact_tables_are_pairwise_disjoint():
    """Guards against a future edit accidentally introducing an ambiguous
    distractor (e.g. a word added to two rhyme groups)."""
    _assert_pairwise_disjoint(_SYNONYM_GROUPS, "_SYNONYM_GROUPS")
    _assert_pairwise_disjoint(_ANTONYM_PAIRS, "_ANTONYM_PAIRS")
    _assert_pairwise_disjoint(_RHYME_GROUPS, "_RHYME_GROUPS")
    _assert_pairwise_disjoint(_PLURAL_PAIRS, "_PLURAL_PAIRS")
    _assert_pairwise_disjoint(_ODD_ONE_OUT_CLASSES, "_ODD_ONE_OUT_CLASSES")


def test_odd_one_out_never_names_the_category_in_the_stem():
    """The point of this exercise is inferring the shared category from the 3
    majority items -- the stem must never leak the category name."""
    g = ItemGenerator(generators=ENGLISH_PRACTICE_GENERATORS, rng=random.Random(5))
    for _ in range(100):
        it = g.sample("practice_odd_one_out")
        for label in _ODD_ONE_OUT_CLASSES:
            assert label not in it.problem.lower()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} practice-items tests passed.")
