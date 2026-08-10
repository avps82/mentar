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


# ── Year 3 ─────────────────────────────────────────────────────────────────

def gen_antonyms_basic_y3(rng: random.Random):
    """AC9E3A alignment: basic opposite-pairs, a stepping stone to Y5's
    'advanced' antonym vocabulary."""
    table = {
        "hot": ["cold"], "fast": ["slow"], "empty": ["full"],
        "day": ["night"], "open": ["closed"], "wet": ["dry"],
    }
    return mc_which_is(rng, "Which word means the OPPOSITE of '{label}'?", table)


def gen_prefixes_y3(rng: random.Random):
    """AC9E3A alignment: common prefixes and the meaning they add."""
    table = {
        "un- (not / opposite)": ["unhappy", "unfair", "unlock", "undo"],
        "re- (again)": ["replay", "rewrite", "return", "rebuild"],
        "dis- (not / opposite)": ["disagree", "dislike", "disappear", "distrust"],
    }
    return mc_which_is(rng, "Which of these words begins with the prefix {label}?", table)


def gen_homophones_y3(rng: random.Random):
    """AC9E3A alignment: common homophone pairs, matched by meaning."""
    table = {
        "means 'over there' or 'in that place'": ["there"],
        "means 'belonging to them'": ["their"],
        "means 'also' or a higher number word": ["too"],
        "means 'in the direction of'": ["to"],
        "means 'in this place'": ["here"],
        "means 'to listen'": ["hear"],
    }
    return mc_which_is(rng, "Which word {label}?", table)


def gen_adjectives_comparative_y3(rng: random.Random):
    """AC9E3A alignment: comparative/superlative adjective recognition."""
    table = {
        "a comparative adjective (comparing TWO things)": ["bigger", "faster", "taller", "smaller"],
        "a superlative adjective (comparing THREE OR MORE things)": ["biggest", "fastest", "tallest", "smallest"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


# ── Year 4 ─────────────────────────────────────────────────────────────────

def gen_suffixes_y4(rng: random.Random):
    """AC9E4A alignment: common suffixes and the meaning they add."""
    table = {
        "-ful (full of)": ["joyful", "careful", "colourful", "helpful"],
        "-less (without)": ["careless", "hopeless", "fearless", "harmless"],
        "-ness (a state of being)": ["happiness", "kindness", "sadness", "darkness"],
    }
    return mc_which_is(rng, "Which of these words ends with the suffix {label}?", table)


def gen_contractions_y4(rng: random.Random):
    """AC9E4A alignment: matching a contraction to the words it shortens."""
    table = {
        "do not": ["don't"], "cannot": ["can't"], "it is": ["it's"],
        "I am": ["I'm"], "they are": ["they're"], "will not": ["won't"],
    }
    return mc_which_is(rng, "Which is the SHORT form (contraction) of '{label}'?", table)


def gen_common_proper_nouns_y4(rng: random.Random):
    """AC9E4A alignment: common vs. proper noun (capitalisation) recognition."""
    table = {
        "a common noun (no capital needed)": ["city", "river", "school", "country"],
        "a proper noun (needs a capital letter)": ["London", "Nile", "Australia", "Monday"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


def gen_similes_basic_y4(rng: random.Random):
    """AC9E4A alignment: recognising a simile (introduces figurative language
    before Y6 asks the child to distinguish it from a metaphor)."""
    table = {
        "a simile (uses 'like' or 'as' to compare)": [
            "as brave as a lion", "ran like the wind", "as light as a feather", "sang like an angel",
        ],
        "a plain sentence (no comparison)": [
            "the dog ran fast", "she sang a song", "the feather was light", "he was very brave",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table)


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

AU_ENGLISH_YEAR3_GENERATORS: dict[str, GenFn] = {
    "aue3_antonyms": gen_antonyms_basic_y3,
    "aue3_prefixes": gen_prefixes_y3,
    "aue3_homophones": gen_homophones_y3,
    "aue3_adjectives_comparative": gen_adjectives_comparative_y3,
}

AU_ENGLISH_YEAR4_GENERATORS: dict[str, GenFn] = {
    "aue4_suffixes": gen_suffixes_y4,
    "aue4_contractions": gen_contractions_y4,
    "aue4_common_proper_nouns": gen_common_proper_nouns_y4,
    "aue4_similes": gen_similes_basic_y4,
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
