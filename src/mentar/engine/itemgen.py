"""Parametric item generator (Option B) — infinite, non-repeating checkable items.

Where the authored item bank (Option A, engine/itembank.py) is a finite list, this generates
fresh (problem, answer) items on demand with constrained random numbers and a computed
ground truth. The verifier stays authoritative; the LLM stays out of the correctness path.

Each generator returns an `Item` identical in shape to the bank's, so an `ItemGenerator`
duck-types `ItemBank` (`has` / `sample` / `example`) and is a drop-in for
`SessionController(item_bank=...)`.  `CompositeItemSource` chains a generator with the authored
bank so conceptual nodes the generator can't parametrise (e.g. equal-vs-unequal parts) still
get authored items.

Year-4 pilot scope: answers stay within the deterministic verifier's grammar (int / proper
fraction); fraction answers are intentionally left UNREDUCED — `fraction_equiv` accepts any
equivalent form, so the child may reduce or not.
"""

from __future__ import annotations

import random
from typing import Callable

from mentar.engine.itembank import Item

# A generator: rng -> (answer_type, checker, problem, answer)
GenFn = Callable[[random.Random], "tuple[str, str, str, str]"]

_THINGS = ["stickers", "crayons", "grapes", "marbles", "sweets", "pencils", "apples", "cookies"]
_GROUPS = ["children", "friends", "baskets", "boxes", "bags", "plates", "pots"]
_WHOLES = ["a cake", "a pizza", "a chocolate bar", "a ribbon", "a pie"]


def _gen_whole_number_division(rng: random.Random):
    b = rng.randint(2, 6)          # groups
    q = rng.randint(2, 9)          # each gets
    a = b * q                      # total (divisible -> clean int answer)
    thing, who = rng.choice(_THINGS), rng.choice(_GROUPS)
    return ("int", "int_exact",
            f"Share {a} {thing} equally among {b} {who}. How many {thing} does each get?",
            str(q))


def _gen_unit_fractions(rng: random.Random):
    d = rng.randint(2, 10)
    whole = rng.choice(_WHOLES)
    return ("fraction", "fraction_equiv",
            f"{whole.capitalize()} is split into {d} equal parts. What fraction is ONE part?",
            f"1/{d}")


def _gen_fraction_as_part_of_whole(rng: random.Random):
    d = rng.randint(3, 10)
    n = rng.randint(1, d - 1)
    whole = rng.choice(_WHOLES)
    return ("fraction", "fraction_equiv",
            f"{whole.capitalize()} is cut into {d} equal slices and you take {n}. "
            f"What fraction did you take?",
            f"{n}/{d}")


def _gen_equivalent_fractions(rng: random.Random):
    d = rng.randint(2, 6)
    n = rng.randint(1, d - 1)
    k = rng.randint(2, 4)
    return ("fraction", "fraction_equiv",
            f"Write a fraction equal to {n}/{d} but with denominator {d * k}.",
            f"{n * k}/{d * k}")


def _gen_adding_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a = rng.randint(1, d - 1)
    b = rng.randint(1, d - a)      # a + b <= d  -> proper (<= 1 whole)
    return ("fraction", "fraction_equiv",
            f"What is {a}/{d} + {b}/{d}?",
            f"{a + b}/{d}")


def _gen_subtracting_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a = rng.randint(2, d - 1)
    b = rng.randint(1, a - 1)      # a > b -> positive result
    return ("fraction", "fraction_equiv",
            f"What is {a}/{d} - {b}/{d}?",
            f"{a - b}/{d}")


def _gen_comparing_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a, b = rng.sample(range(1, d), 2)   # distinct numerators
    hi = max(a, b)
    return ("fraction", "fraction_equiv",
            f"Which is bigger: {a}/{d} or {b}/{d}? Give the bigger fraction.",
            f"{hi}/{d}")


# Registry — node_id -> generator. Conceptual/visual nodes (equal_vs_unequal_parts) are
# intentionally absent; CompositeItemSource falls back to the authored bank for those.
DEFAULT_GENERATORS: dict[str, GenFn] = {
    "whole_number_division": _gen_whole_number_division,
    "unit_fractions": _gen_unit_fractions,
    "fraction_as_part_of_whole": _gen_fraction_as_part_of_whole,
    "equivalent_fractions": _gen_equivalent_fractions,
    "adding_equal_denom": _gen_adding_equal_denom,
    "subtracting_equal_denom": _gen_subtracting_equal_denom,
    "comparing_equal_denom": _gen_comparing_equal_denom,
}


class ItemGenerator:
    """Generates fresh checkable items per node. Duck-types ItemBank (has/sample/example)."""

    def __init__(self, generators: dict[str, GenFn] | None = None,
                 rng: random.Random | None = None) -> None:
        self._gens = generators if generators is not None else DEFAULT_GENERATORS
        self._rng = rng or random.Random()

    def has(self, node_id: str) -> bool:
        return node_id in self._gens

    def _make(self, node_id: str) -> Item | None:
        gen = self._gens.get(node_id)
        if gen is None:
            return None
        answer_type, checker, problem, answer = gen(self._rng)
        return Item(
            id=f"gen-{node_id}-{self._rng.randrange(10 ** 9)}",
            node=node_id, problem=problem, answer=answer,
            answer_type=answer_type, checker=checker,
        )

    def sample(self, node_id: str) -> Item | None:
        return self._make(node_id)

    def example(self, node_id: str, exclude_id: str | None = None) -> Item | None:
        # Generated items are effectively unique; exclude_id is irrelevant.
        return self._make(node_id)


class CompositeItemSource:
    """Chain item sources: first source that `has` a node serves it.

    Typical use: CompositeItemSource(generator, authored_bank) — generator for parametrisable
    nodes, authored bank for conceptual ones.
    """

    def __init__(self, *sources) -> None:
        self._sources = [s for s in sources if s is not None]

    def _for(self, node_id: str):
        for s in self._sources:
            if s.has(node_id):
                return s
        return None

    def has(self, node_id: str) -> bool:
        return self._for(node_id) is not None

    def sample(self, node_id: str):
        s = self._for(node_id)
        return s.sample(node_id) if s else None

    def example(self, node_id: str, exclude_id: str | None = None):
        s = self._for(node_id)
        return s.example(node_id, exclude_id=exclude_id) if s else None


def default_item_generator(rng: random.Random | None = None) -> ItemGenerator:
    return ItemGenerator(rng=rng)


def build_item_source(mode: str, bank=None, rng: random.Random | None = None):
    """Build the checkable-item source for the controller from a config `item_source`.

    mode:
      "composite" (default) — generator for parametrisable nodes, authored bank for the rest.
      "generator"           — parametric only (conceptual nodes fall through to the LLM path).
      "bank"                — authored bank only (Option A).
    Returns an object with has/sample/example, or None when nothing is available.
    """
    mode = (mode or "composite").lower()
    if mode == "bank":
        return bank
    gen = default_item_generator(rng=rng)
    if mode == "generator":
        return gen
    # composite (default): generator first, authored bank as fallback
    return CompositeItemSource(gen, bank) if bank is not None else gen
