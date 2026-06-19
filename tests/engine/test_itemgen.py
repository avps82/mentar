"""Tests for mentar.engine.itemgen — parametric item generator (Option B).

Contract checks:
    - Every generator, over MANY random draws, produces an item whose own answer PASSes the
      deterministic verifier (the generator's ground truth must be self-consistent).
    - Answers stay in the verifier's grammar (no decimals -> no SAFE_REJECT).
    - sample() yields variety (not a constant) and fresh ids.
    - CompositeItemSource routes to the generator where it has the node, else the bank.
    - A generated item scores PASS + persists through the controller.

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner (python3-runnable without pytest):
    python3 tests/engine/test_itemgen.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.itembank import Item, ItemBank  # noqa: E402
from mentar.engine.itemgen import (  # noqa: E402
    DEFAULT_GENERATORS,
    CompositeItemSource,
    ItemGenerator,
    default_item_generator,
)
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402


def test_every_generator_self_validates_many_draws():
    gen = ItemGenerator(rng=random.Random(12345))
    for node in DEFAULT_GENERATORS:
        for _ in range(200):
            it = gen.sample(node)
            assert it is not None and it.node == node
            oc = check(answer_type=it.answer_type, checker=it.checker,
                       llm_output=it.answer, ground_truth=it.answer)
            assert oc.result is CheckResult.PASS, (node, it.problem, it.answer, oc.result)


def test_child_correct_answer_passes():
    # Simulate the child typing exactly the ground-truth answer (with words around it).
    gen = ItemGenerator(rng=random.Random(7))
    for node in DEFAULT_GENERATORS:
        it = gen.sample(node)
        child = f"I think it is {it.answer}."
        oc = check(answer_type=it.answer_type, checker=it.checker,
                   llm_output=child, ground_truth=it.answer)
        assert oc.result is CheckResult.PASS, (node, child, it.answer, oc.result)


def test_variety_and_unique_ids():
    gen = ItemGenerator(rng=random.Random(1))
    probs = {gen.sample("adding_equal_denom").problem for _ in range(20)}
    ids = {gen.sample("unit_fractions").id for _ in range(20)}
    assert len(probs) > 1          # not a constant template instance
    assert len(ids) == 20          # ids are unique


def test_unsupported_node_returns_none():
    gen = ItemGenerator(rng=random.Random(1))
    assert not gen.has("equal_vs_unequal_parts")
    assert gen.sample("equal_vs_unequal_parts") is None


def test_composite_routes_generator_then_bank():
    gen = ItemGenerator(rng=random.Random(1))
    bank = ItemBank([Item("b1", "equal_vs_unequal_parts", "Is this split fair?", "A", "mc4", "mc_choice")])
    comp = CompositeItemSource(gen, bank)
    # generator owns this node -> id from the generator
    assert comp.sample("adding_equal_denom").id.startswith("gen-")
    # generator lacks this node -> falls back to the authored bank
    assert comp.sample("equal_vs_unequal_parts").id == "b1"
    assert comp.has("unit_fractions") and comp.has("equal_vs_unequal_parts")
    assert not comp.has("nonexistent_node")


def test_controller_scores_generated_item():
    from mentar.dialogue.controller import SessionController

    class _MemStore:
        def __init__(self): self.skills = {}
        def get_skill_state(self, l, n): return {"p_mastery": self.skills[n]} if n in self.skills else None
        def update_skill_state(self, l, n, p, **k): self.skills[n] = p

    curriculum = {"adding_equal_denom": {
        "concept": "Adding fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "", "grounding": {}, "prerequisites": []}}
    gen = default_item_generator(rng=random.Random(3))
    ctrl = SessionController(
        llm_call=lambda m: "(unused)", prompt_dir=REPO_ROOT / "prompts",
        grounding_cfg={}, curriculum=curriculum, db_store=_MemStore(),
        learner_id="t", item_bank=gen,
    )
    ctrl.step(None)                       # presents a generated item
    truth = ctrl._ctx.current_item.answer
    ctrl.step(truth)                      # correct -> PASS -> persists
    assert ctrl._store.skills.get("adding_equal_denom") is not None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} itemgen tests passed.")
