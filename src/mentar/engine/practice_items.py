"""Evergreen "Try-out practice" sampler pack -- times tables, skip counting,
doubles/halves. Generic, country-agnostic drill content (never expires, no
curriculum authority owns it) -- kept separate from any country-curriculum
templates under curriculum/templates/<COUNTRY_AUTHORITY>/.
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is


def _gen_times_tables(rng: random.Random) -> tuple[str, str, str, str]:
    a, b = rng.randint(1, 12), rng.randint(1, 12)
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


def _gen_skip_counting(rng: random.Random) -> tuple[str, str, str, str]:
    step = rng.choice([2, 3, 5, 10])
    start = rng.randint(1, 5) * step
    terms = [start + step * i for i in range(4)]
    answer_val = start + step * 4
    problem = f"What number comes next: {', '.join(map(str, terms))}, __?"
    return ("int", "int_exact", problem, str(answer_val))


def _gen_doubles_halves(rng: random.Random) -> tuple[str, str, str, str]:
    op = rng.choice(["double", "half"])
    if op == "double":
        n = rng.randint(1, 50)
        return ("int", "int_exact", f"What is double {n}?", str(n * 2))
    n = rng.randint(1, 50) * 2
    return ("int", "int_exact", f"What is half of {n}?", str(n // 2))


MATHS_PRACTICE_GENERATORS: dict[str, GenFn] = {
    "practice_times_tables": _gen_times_tables,
    "practice_skip_counting": _gen_skip_counting,
    "practice_doubles_halves": _gen_doubles_halves,
}


# ── English practice: curated fact tables (verified pairwise-disjoint, no
# ── ambiguous cross-category overlap) ───────────────────────────────────────

_SYNONYM_GROUPS = {
    "happy": ["glad", "joyful", "cheerful"],
    "sad": ["unhappy", "gloomy", "sorrowful"],
    "big": ["large", "huge", "giant"],
    "small": ["tiny", "little", "mini"],
    "fast": ["quick", "speedy", "rapid"],
    "smart": ["clever", "bright", "wise"],
}

_ANTONYM_PAIRS = {
    "happy": ["sad"],
    "big": ["small"],
    "fast": ["slow"],
    "hot": ["cold"],
    "up": ["down"],
    "day": ["night"],
    "open": ["closed"],
    "full": ["empty"],
}

_RHYME_GROUPS = {
    "cat": ["hat", "bat", "mat", "rat"],
    "dog": ["log", "fog", "jog", "frog"],
    "sun": ["fun", "run", "bun", "gun"],
    "tree": ["bee", "sea", "key", "pea"],
    "star": ["car", "far", "jar", "bar"],
}

_PLURAL_PAIRS = {
    "child": ["children"],
    "mouse": ["mice"],
    "foot": ["feet"],
    "tooth": ["teeth"],
    "goose": ["geese"],
    "person": ["people"],
    "man": ["men"],
    "woman": ["women"],
}

_ODD_ONE_OUT_CLASSES = {
    "fruit": ["apple", "banana", "grape", "orange", "pear"],
    "vegetable": ["carrot", "potato", "broccoli", "onion", "pea"],
    "animal": ["dog", "cat", "cow", "sheep", "pig"],
    "vehicle": ["car", "bus", "bike", "truck", "van"],
}


def _gen_synonyms_antonyms(rng: random.Random):
    if rng.choice([True, False]):
        return mc_which_is(rng, "Which word means the SAME as '{label}'?", _SYNONYM_GROUPS)
    return mc_which_is(rng, "Which word means the OPPOSITE of '{label}'?", _ANTONYM_PAIRS)


def _gen_rhyming_words(rng: random.Random):
    return mc_which_is(rng, "Which word rhymes with '{label}'?", _RHYME_GROUPS)


def _gen_plural_forms(rng: random.Random):
    return mc_which_is(rng, "What is the plural of '{label}'?", _PLURAL_PAIRS)


def _gen_odd_one_out(rng: random.Random):
    """Custom shape (not mc_which_is): 3 items from one category + 1 from a
    DIFFERENT category; the odd one is the answer. The category itself is
    never named -- working out what the 3 majority items share IS the point
    of this exercise."""
    labels = list(_ODD_ONE_OUT_CLASSES)
    majority_label, minority_label = rng.sample(labels, 2)
    majority_items = rng.sample(_ODD_ONE_OUT_CLASSES[majority_label], 3)
    minority_item = rng.choice(_ODD_ONE_OUT_CLASSES[minority_label])
    options = [*majority_items, minority_item]
    rng.shuffle(options)
    letter = "ABCD"[options.index(minority_item)]
    stem = "Which one does NOT belong with the others?"
    return ("mc4", "mc_choice", stem, letter, options)


ENGLISH_PRACTICE_GENERATORS: dict[str, GenFn] = {
    "practice_synonyms_antonyms": _gen_synonyms_antonyms,
    "practice_rhyming_words": _gen_rhyming_words,
    "practice_odd_one_out": _gen_odd_one_out,
    "practice_plural_forms": _gen_plural_forms,
}
