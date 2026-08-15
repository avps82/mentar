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
    card = (
        "SKIP COUNTING",
        f"{problem} → {answer_val}",
        f"  1. Find the jump between terms: {terms[1]} - {terms[0]} = {step}.",
        f"  2. Check it holds: {terms[2]} - {terms[1]} = {step}, {terms[3]} - {terms[2]} = {step}.",
        f"  3. Add one more jump: {terms[3]} + {step} = {answer_val}.",
        f"  Answer: {answer_val}",
    )
    return ("int", "int_exact", problem, str(answer_val), None, card)


def _gen_doubles_halves(rng: random.Random) -> tuple[str, str, str, str]:
    op = rng.choice(["double", "half"])
    if op == "double":
        n = rng.randint(1, 50)
        problem = f"What is double {n}?"
        card = (
            "DOUBLING",
            f"{problem} → {n * 2}",
            f"  1. Double means two of them: {n} + {n}.",
            f"  2. {n} + {n} = {n * 2}  (same as {n} × 2).",
            f"  Answer: {n * 2}",
        )
        return ("int", "int_exact", problem, str(n * 2), None, card)
    n = rng.randint(1, 50) * 2
    problem = f"What is half of {n}?"
    card = (
        "HALVING",
        f"{problem} → {n // 2}",
        f"  1. Half means split into two equal parts: {n} ÷ 2.",
        f"  2. {n // 2} + {n // 2} = {n}, so half of {n} is {n // 2}.",
        "  Halving undoes doubling — they are opposites.",
        f"  Answer: {n // 2}",
    )
    return ("int", "int_exact", problem, str(n // 2), None, card)


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
        return mc_which_is(
            rng, "Which word means the SAME as '{label}'?", _SYNONYM_GROUPS,
            glosses=dict.fromkeys(
                _SYNONYM_GROUPS, "a synonym is a different word with the same meaning"),
            concept_name="SYNONYMS",
        )
    return mc_which_is(
        rng, "Which word means the OPPOSITE of '{label}'?", _ANTONYM_PAIRS,
        glosses=dict.fromkeys(_ANTONYM_PAIRS, "an antonym is a word with the opposite meaning"),
        concept_name="ANTONYMS",
    )


def _gen_rhyming_words(rng: random.Random):
    return mc_which_is(
        rng, "Which word rhymes with '{label}'?", _RHYME_GROUPS,
        glosses=dict.fromkeys(
            _RHYME_GROUPS, "rhyming words share their ENDING SOUND -- the spelling can differ"),
        concept_name="RHYMING WORDS",
    )


def _gen_plural_forms(rng: random.Random):
    return mc_which_is(
        rng, "What is the plural of '{label}'?", _PLURAL_PAIRS,
        glosses=dict.fromkeys(
            _PLURAL_PAIRS,
            "most words add -s; words ending x/ch/sh/s add -es; a few change completely"),
        concept_name="PLURALS",
    )


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
    # The card NAMES the category the question deliberately withholds. That is
    # safe and is the whole teaching point: explain-mode only runs after the
    # child has answered or asked for help, so nothing is given away early.
    card = (
        "ODD ONE OUT",
        f"{stem} -> {minority_item}",
        f"  {', '.join(majority_items)} are all in one group: {majority_label}.",
        f"  {minority_item} is a {minority_label}, so it is the odd one out.",
        "  Look for what MOST of them share -- the odd one is the one left over.",
    )
    return ("mc4", "mc_choice", stem, letter, options, card)


ENGLISH_PRACTICE_GENERATORS: dict[str, GenFn] = {
    "practice_synonyms_antonyms": _gen_synonyms_antonyms,
    "practice_rhyming_words": _gen_rhyming_words,
    "practice_odd_one_out": _gen_odd_one_out,
    "practice_plural_forms": _gen_plural_forms,
}
