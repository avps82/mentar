"""Science item generators — multiple-choice questions built from small CURATED
fact tables.

Why this shape: science facts can't be *computed* like maths, and an LLM that
invents the "correct" option could teach a child a wrong fact. So the fact tables
below are the authoritative ground truth (authored once, small), and questions are
generated automatically with random distractors. The deterministic verifier
(`mc_choice`) scores the child's letter against that ground truth — the LLM never
decides correctness (same safety rule as the maths path; see SPEC §14).

Each generator returns the GenFn tuple `(answer_type, checker, problem, answer)`
so it drops into `ItemGenerator(generators=SCIENCE_GENERATORS)`.
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is

# ── Curated fact tables (the ground truth) — Year-4 friendly, disjoint classes ──

_ANIMAL_CLASSES = {
    "mammal": ["dog", "cat", "whale", "bat", "horse", "elephant"],
    "bird": ["eagle", "owl", "penguin", "robin", "duck"],
    "fish": ["shark", "salmon", "tuna", "goldfish"],
    "insect": ["ant", "bee", "butterfly", "beetle"],
}

_MATTER_CLASSES = {
    "solid": ["a rock", "ice", "a book", "a coin"],
    "liquid": ["water", "milk", "juice", "oil"],
    "gas": ["air", "steam", "oxygen", "helium"],
}

_LIVING_CLASSES = {
    "living thing": ["a tree", "a dog", "a flower", "a child", "a fish"],
    "non-living thing": ["a rock", "a car", "a spoon", "a cloud", "a chair"],
}


def _gen_classify_animals(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _ANIMAL_CLASSES)


def _gen_states_of_matter(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _MATTER_CLASSES)


def _gen_living_nonliving(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _LIVING_CLASSES)


# Registry — node_id -> generator (matches the science curriculum template node ids).
SCIENCE_GENERATORS: dict[str, GenFn] = {
    "classify_animals": _gen_classify_animals,
    "states_of_matter": _gen_states_of_matter,
    "living_nonliving": _gen_living_nonliving,
}
