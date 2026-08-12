"""Tests for the new subject content generators (maths arithmetic + science MC).

Safety contract (same as itemgen): the generator's own ground truth must PASS the
deterministic verifier, and science MC ground truth comes from the curated fact
table (never the LLM).

    python3 tests/engine/test_science_items.py
"""

from __future__ import annotations

import pathlib
import random
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.itemgen import (  # noqa: E402
    ARITHMETIC_GENERATORS,
    ItemGenerator,
    compose_mc_problem,
    mc_which_is,
)
from mentar.engine.science_items import SCIENCE_GENERATORS  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def test_arithmetic_generators_self_validate():
    g = ItemGenerator(generators=ARITHMETIC_GENERATORS, rng=random.Random(7))
    for node in ARITHMETIC_GENERATORS:
        for _ in range(100):
            it = g.sample(node)
            assert it is not None and it.answer.lstrip("-").isdigit()
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer)


def test_science_generators_self_validate():
    g = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(3))
    for node in SCIENCE_GENERATORS:
        for _ in range(100):
            it = g.sample(node)
            assert it.answer in ("A", "B", "C", "D"), it.problem
            assert "Answer with the letter" in it.problem
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS


def test_mc_answer_letter_points_to_a_real_member():
    """The computed answer letter must map to a real fact-table member (guards the
    option-index logic). Three classes so any target leaves >=3 distractors."""
    classes = {"alpha": ["a1", "a2"], "beta": ["b1", "b2"], "gamma": ["c1", "c2"]}
    members = {m for ms in classes.values() for m in ms}
    rng = random.Random(0)
    letters = "ABCD"
    for _ in range(100):
        _, _, stem, letter, choices, _ = mc_which_is(rng, "Which is {label}?", classes)
        # R2.1: the 3rd element is the STEM only -- no inline "A) ..." options
        # (the web view shows stem + radios; CLI/transcript gets the composed
        # inline form via itemgen.compose_mc_problem, tested separately).
        assert not re.search(r"[A-D]\)\s", stem)
        assert choices[letters.index(letter)] in members


def test_science_mc_has_four_distinct_options():
    g = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(11))
    it = g.sample("classify_animals")
    opts = re.findall(r"[A-D]\)\s*([^A-D]+?)(?=\s+[A-D]\)|\.\s*Answer)", it.problem)
    opts = [o.strip() for o in opts]
    assert len(opts) == 4 and len(set(opts)) == 4, it.problem
    # Structured choices carried on the Item, in the same A/B/C/D order as the text.
    assert it.choices is not None and len(it.choices) == 4
    assert list(it.choices) == opts
    # R2.1: stem carries no inline options; problem = compose_mc_problem(stem, choices).
    assert it.stem is not None and "A)" not in it.stem
    assert it.problem == compose_mc_problem(it.stem, it.choices)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} passed.")
