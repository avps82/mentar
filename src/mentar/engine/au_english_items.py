"""Australian-curriculum English item generators — Year 2, 5 and 6
(Language/Literacy strands).

Every node reuses `mc_which_is` (from `engine.itemgen`, the same shared helper
`practice_items.py`/`science_items.py` use) over a curated, hand-verified
pairwise-disjoint word table — no new generator SHAPE, only new content.

ACARA v9 content-description codes in the dict-building comments are
alignment REFERENCES only; all word choices are Mentar-authored
(docs/CONTENT_LICENSES.md, ACARA CC BY 4.0).
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is

# ── Year 2 ─────────────────────────────────────────────────────────────────

def gen_word_classes_y2(rng: random.Random):
    """AC9E2A alignment: identify a word's class (noun/verb/adjective)."""
    table = {
        "a naming word (noun)": ["dog", "cat", "ball", "school", "teacher", "apple", "book", "chair"],
        "a doing word (verb)": ["run", "jump", "sing", "eat", "sleep", "play", "swim", "read"],
        "a describing word (adjective)": ["happy", "big", "red", "fast", "small", "soft", "loud", "cold"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


def gen_synonyms_y2(rng: random.Random):
    """AC9E2A alignment: simple synonym pairs."""
    table = {
        "happy": ["glad", "cheerful"],
        "sad": ["unhappy", "upset"],
        "big": ["large", "giant"],
        "small": ["little", "tiny"],
        "cold": ["chilly", "icy"],
    }
    return mc_which_is(rng, "Which word means the SAME as '{label}'?", table)


def gen_plurals_y2(rng: random.Random):
    """AC9E2A alignment: plural forms, mostly regular with a couple of irregulars."""
    table = {
        "cat": ["cats"], "dog": ["dogs"], "box": ["boxes"],
        "child": ["children"], "mouse": ["mice"], "book": ["books"],
    }
    return mc_which_is(rng, "What is the plural of '{label}'?", table)


def gen_rhyming_y2(rng: random.Random):
    """AC9E2A alignment: rhyming word families."""
    table = {
        "pig": ["big", "dig", "wig"],
        "bell": ["shell", "well", "tell"],
        "king": ["sing", "ring", "wing"],
        "boat": ["coat", "goat", "float"],
    }
    return mc_which_is(rng, "Which word rhymes with '{label}'?", table)


# ── Year 5 ─────────────────────────────────────────────────────────────────

def gen_synonyms_advanced_y5(rng: random.Random):
    """AC9E5A alignment: richer vocabulary synonym pairs."""
    table = {
        "enormous": ["huge", "gigantic"],
        "delighted": ["thrilled", "overjoyed"],
        "exhausted": ["tired", "weary"],
        "furious": ["angry", "enraged"],
        "peculiar": ["strange", "odd"],
    }
    return mc_which_is(rng, "Which word means the SAME as '{label}'?", table)


def gen_antonyms_advanced_y5(rng: random.Random):
    """AC9E5A alignment: richer vocabulary antonym pairs."""
    table = {
        "generous": ["stingy"],
        "ancient": ["modern"],
        "cautious": ["reckless"],
        "genuine": ["fake"],
        "abundant": ["scarce"],
    }
    return mc_which_is(rng, "Which word means the OPPOSITE of '{label}'?", table)


def gen_word_classes_advanced_y5(rng: random.Random):
    """AC9E5A alignment: adverb/pronoun/verb classification (harder than Y2's
    noun/verb/adjective)."""
    table = {
        "an adverb (describes HOW something is done)": ["quickly", "quietly", "carefully", "loudly"],
        "a pronoun (stands in for a noun)": ["she", "they", "it", "we"],
        "a verb": ["walk", "think", "build", "carry"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


def gen_compound_words_y5(rng: random.Random):
    """AC9E5A alignment: recognising real compound words vs. invented ones."""
    table = {
        "a real compound word": ["sunflower", "toothbrush", "basketball", "butterfly", "football"],
        "not a real word": ["moonbrush", "chairwater", "tablesong", "doorsinger"],
    }
    return mc_which_is(rng, "Which of these IS {label}?", table)


# ── Year 6 ─────────────────────────────────────────────────────────────────

def gen_figurative_language_y6(rng: random.Random):
    """AC9E6A alignment: distinguishing similes from metaphors."""
    table = {
        "a simile (uses 'like' or 'as')": ["as brave as a lion", "ran like the wind", "as quiet as a mouse", "as busy as a bee"],
        "a metaphor (says one thing IS another)": ["time is money", "the classroom was a zoo", "her heart is a stone", "the world is a stage"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


def gen_synonyms_nuanced_y6(rng: random.Random):
    """AC9E6A alignment: nuanced/contextual synonym pairs."""
    table = {
        "reluctant": ["hesitant", "unwilling"],
        "meticulous": ["thorough", "precise"],
        "candid": ["honest", "frank"],
        "resilient": ["tough", "adaptable"],
    }
    return mc_which_is(rng, "Which word means the SAME as '{label}'?", table)


def gen_antonyms_nuanced_y6(rng: random.Random):
    """AC9E6A alignment: nuanced antonym pairs."""
    table = {
        "transparent": ["opaque"],
        "concise": ["verbose"],
        "voluntary": ["compulsory"],
        "flexible": ["rigid"],
    }
    return mc_which_is(rng, "Which word means the OPPOSITE of '{label}'?", table)


def gen_word_classes_conj_prep_y6(rng: random.Random):
    """AC9E6A alignment: conjunction/preposition classification."""
    table = {
        "a conjunction (joins two ideas)": ["and", "but", "because", "although"],
        "a preposition (shows position or time)": ["under", "before", "between", "during"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


# ── Registries (node_id -> generator) ─────────────────────────────────────────

AU_ENGLISH_YEAR2_GENERATORS: dict[str, GenFn] = {
    "aue2_word_classes": gen_word_classes_y2,
    "aue2_synonyms": gen_synonyms_y2,
    "aue2_plurals": gen_plurals_y2,
    "aue2_rhyming": gen_rhyming_y2,
}

AU_ENGLISH_YEAR5_GENERATORS: dict[str, GenFn] = {
    "aue5_synonyms_advanced": gen_synonyms_advanced_y5,
    "aue5_antonyms_advanced": gen_antonyms_advanced_y5,
    "aue5_word_classes_advanced": gen_word_classes_advanced_y5,
    "aue5_compound_words": gen_compound_words_y5,
}

AU_ENGLISH_YEAR6_GENERATORS: dict[str, GenFn] = {
    "aue6_figurative_language": gen_figurative_language_y6,
    "aue6_synonyms_nuanced": gen_synonyms_nuanced_y6,
    "aue6_antonyms_nuanced": gen_antonyms_nuanced_y6,
    "aue6_word_classes_conjunctions_prepositions": gen_word_classes_conj_prep_y6,
}
