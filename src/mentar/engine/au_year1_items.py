"""W5/W6 of the curriculum depth program: YEAR 1 — the year that did not exist.

The maintainer's reference lists Year 1 for maths (Number, Algebra,
Measurement, Space, Statistics), English (Phonics, Reading, Writing,
Handwriting, Speaking) and Science (Living things, Environments, Materials,
Earth and sky, Forces); the auditor read every one of them ABSENT. This module
gives each strand one age-6 topic: numeric items are exact-by-construction
ints, knowledge items are disjoint fact tables via mc_which_is.

Language register: very short sentences, everyday words, numbers within 20.
"""

from __future__ import annotations

import random

from mentar.engine.au_senior_maths_items import _card
from mentar.engine.itemgen import GenFn, mc_which_is
from mentar.engine.visuals import number_line

# ── Maths ────────────────────────────────────────────────────────────────────

def gen_count_objects(rng: random.Random):
    n = rng.choice([3, 4, 5, 6, 7, 8, 9])
    p = f"Count the stars: {'★' * n}. How many stars are there?"
    card = _card("COUNTING", p, n,
                 "  Touch each star once as you count",
                 f"  1. {' '.join(str(i) for i in range(1, n + 1))}.",
                 f"  2. The last number you say is how many: {n}.")
    return ("int", "int_exact", p, str(n), None, card,
            "(Count each one once; the last number is the answer)")


def gen_add_within_10(rng: random.Random):
    a = rng.choice([1, 2, 3, 4, 5])
    b = rng.choice([1, 2, 3, 4])
    p = f"You have {a} apples. You get {b} more. How many apples now?"
    card = _card("ADDING SMALL NUMBERS", p, a + b,
                 "  Start at the first number and count on",
                 f"  1. Start at {a}.",
                 f"  2. Count on {b} more: {' '.join(str(a + i) for i in range(1, b + 1))}.",
                 f"  3. You land on {a + b}.")
    return ("int", "int_exact", p, str(a + b), None, card,
            "(Start at the first number, count on the second)")


def gen_skip_count_2s(rng: random.Random):
    """Shows the number line with a `?` where the next number goes (visual-first,
    2026-08-21): skip counting is a picture of equal hops before it is a sequence
    of digits, and the hop the child has to make needs to be visible."""
    start = rng.choice([2, 4, 6, 8, 10])
    p = f"Counting by 2s: {start}, {start + 2}, {start + 4}, ... What number comes next?"
    card = _card("COUNTING BY 2s", p, start + 6,
                 "  Each number is 2 more than the one before",
                 f"  1. {start + 4} + 2 = {start + 6}.")
    return ("int", "int_exact", p, str(start + 6), None, card,
            "(Add 2 each time)",
            number_line(start, start + 4, 2, unknown_next=True))


def gen_shape_sides(rng: random.Random):
    shape, n = rng.choice([("triangle", 3), ("square", 4), ("rectangle", 4),
                           ("pentagon", 5), ("hexagon", 6)])
    p = f"How many sides does a {shape} have?"
    card = _card("SHAPE SIDES", p, n,
                 "  Trace the edge with your finger and count each straight side",
                 f"  1. A {shape} has {n} straight sides.")
    return ("int", "int_exact", p, str(n), None, card,
            "(Count each straight side once)")


# LENGTH and WEIGHT are separate tables ON PURPOSE (bug found 2026-08-21 by
# reading real draws). One combined table asked "which is the HEAVIER one?" and
# offered "a bus (next to a pencil)" as a distractor because it was filed under
# LONGER -- but a bus IS heavier than a pencil, so a child reasoning correctly
# was marked wrong. The categories were disjoint as LABELS and overlapping in
# MEANING; test_fact_table_disjointness matches substrings and cannot see that.
# Drawing from one dimension at a time makes every distractor wrong on the same
# axis the question asks about.
_Y1_LENGTH = {
    "the LONGER one": ["a bus (next to a pencil)", "a river (next to a puddle)",
                       "a broom (next to a spoon)"],
    "the SHORTER one": ["a pencil (next to a bus)", "an ant (next to a dog)",
                        "a spoon (next to a broom)"],
}
_Y1_WEIGHT = {
    "the HEAVIER one": ["an elephant (next to a cat)", "a brick (next to a feather)",
                        "a rock (next to a leaf)"],
    "the LIGHTER one": ["a feather (next to a brick)", "a leaf (next to a rock)",
                        "a cat (next to an elephant)"],
}
_Y1_COMPARE_GLOSSES = {
    "the LONGER one": "longer means it reaches further from end to end",
    "the SHORTER one": "shorter means it reaches less far",
    "the HEAVIER one": "heavier means it pulls down harder in your hands",
    "the LIGHTER one": "lighter means it is easier to lift",
}


def gen_longer_shorter(rng: random.Random):
    table = rng.choice([_Y1_LENGTH, _Y1_WEIGHT])
    return mc_which_is(rng, "Which of these is {label}?", table,
                       glosses=_Y1_COMPARE_GLOSSES, concept_name="COMPARING THINGS")


def gen_simple_tally(rng: random.Random):
    red = rng.choice([4, 5, 6, 7])
    blue = rng.choice([1, 2, 3])
    p = (f"The class voted for a colour. Red got {red} votes. Blue got {blue} votes. "
         "How many MORE votes did red get than blue?")
    card = _card("COMPARING VOTES", p, red - blue,
                 "  'How many more' means take the smaller from the bigger",
                 f"  1. {red} − {blue} = {red - blue}.")
    return ("int", "int_exact", p, str(red - blue), None, card,
            "(How many more = bigger number − smaller number)")


AU_YEAR1_MATHS_GENERATORS: dict[str, GenFn] = {
    "au1_count_objects": gen_count_objects,       # Number
    "au1_add_within_10": gen_add_within_10,       # Number
    "au1_skip_count_2s": gen_skip_count_2s,       # Algebra
    "au1_longer_shorter": gen_longer_shorter,     # Measurement
    "au1_shape_sides": gen_shape_sides,           # Space
    "au1_simple_tally": gen_simple_tally,         # Statistics
}

# ── English ──────────────────────────────────────────────────────────────────

_FIRST_SOUNDS = {
    "a word that starts like 'sun'": ["sock", "sand", "seven"],
    "a word that starts like 'dog'": ["door", "duck", "dish"],
    "a word that starts like 'moon'": ["milk", "mat", "mouse"],
}
_FIRST_SOUNDS_GLOSSES = {
    "a word that starts like 'sun'": "say them out loud: sss... the first sound matches",
    "a word that starts like 'dog'": "d-d-dog: listen for the very first sound",
    "a word that starts like 'moon'": "mmm... the lips press together to start",
}


def gen_first_sounds(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _FIRST_SOUNDS,
                       glosses=_FIRST_SOUNDS_GLOSSES, concept_name="FIRST SOUNDS")


_RHYMES = {
    "a word that rhymes with 'cat'": ["hat", "mat", "bat"],
    "a word that rhymes with 'dog'": ["log", "frog", "fog"],
    "a word that rhymes with 'star'": ["car", "far", "jar"],
}
_RHYMES_GLOSSES = {
    "a word that rhymes with 'cat'": "rhymes share their ending sound: -at",
    "a word that rhymes with 'dog'": "listen to the ending: -og",
    "a word that rhymes with 'star'": "the ending -ar makes the rhyme",
}


def gen_rhymes(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _RHYMES,
                       glosses=_RHYMES_GLOSSES, concept_name="RHYMING WORDS")


_SENTENCES = {
    "a sentence written CORRECTLY": [
        "The dog runs fast.", "I like my school.", "We went to the park.",
    ],
    "missing its CAPITAL letter": [
        "the cat is asleep.", "my hat is red.",
    ],
    "missing its FULL STOP": [
        "The bird can fly", "I see the moon",
    ],
}
_SENTENCES_GLOSSES = {
    "a sentence written CORRECTLY": "a capital at the start AND a full stop at the end",
    "missing its CAPITAL letter": "sentences begin with a capital letter",
    "missing its FULL STOP": "sentences end with a full stop",
}


def gen_sentence_basics(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _SENTENCES,
                       glosses=_SENTENCES_GLOSSES, concept_name="WRITING A SENTENCE")


_LETTER_CASE = {
    "the lowercase partner of B": ["b"],
    "the lowercase partner of D": ["d"],
    "the lowercase partner of G": ["g"],
    "the lowercase partner of R": ["r"],
}
_LETTER_CASE_GLOSSES = {
    "the lowercase partner of B": "big B, little b — same letter, two sizes",
    "the lowercase partner of D": "big D, little d",
    "the lowercase partner of G": "big G, little g",
    "the lowercase partner of R": "big R, little r",
}


def gen_letter_case(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LETTER_CASE,
                       glosses=_LETTER_CASE_GLOSSES, concept_name="BIG AND SMALL LETTERS")


_LISTENING = {
    "GOOD listening": [
        "looking at the person who is talking",
        "waiting for your turn to speak",
    ],
    "GOOD speaking": [
        "using a clear voice others can hear",
        "staying on the topic the class is talking about",
    ],
    "NOT good listening or speaking": [
        "talking while someone else is talking",
        "walking away in the middle of a question",
    ],
}
_LISTENING_GLOSSES = {
    "GOOD listening": "eyes on the speaker, ears open, mouth resting",
    "GOOD speaking": "clear, kind, and on topic",
    "NOT good listening or speaking": "it makes it hard for everyone to share",
}


def gen_speaking_listening(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LISTENING,
                       glosses=_LISTENING_GLOSSES, concept_name="SPEAKING AND LISTENING")


AU_YEAR1_ENGLISH_GENERATORS: dict[str, GenFn] = {
    "aue1_first_sounds": gen_first_sounds,             # Phonics
    "aue1_rhymes": gen_rhymes,                         # Reading
    "aue1_sentence_basics": gen_sentence_basics,       # Writing
    "aue1_letter_case": gen_letter_case,               # Handwriting
    "aue1_speaking_listening": gen_speaking_listening, # Speaking
}

# ── Science ──────────────────────────────────────────────────────────────────

_LIVING = {
    "a LIVING thing": ["a tree", "a bird", "a spider", "grass"],
    "a thing that has NEVER been alive": ["a rock", "a bicycle", "a glass of water"],
    "a thing that WAS once alive": ["a fallen leaf", "a wooden chair", "a seashell"],
}
_LIVING_GLOSSES = {
    "a LIVING thing": "it grows, needs food and water, and can make more of itself",
    "a thing that has NEVER been alive": "it never grew and never needed food",
    "a thing that WAS once alive": "it came from something that grew, but it is not alive now",
}


def gen_living_things(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LIVING,
                       glosses=_LIVING_GLOSSES, concept_name="LIVING AND NON-LIVING")


_HABITATS = {
    "an animal that lives in WATER": ["a fish", "a crab", "a dolphin"],
    "an animal that lives in TREES": ["a koala", "a possum", "a parrot"],
    "an animal that lives UNDERGROUND": ["a wombat", "an earthworm", "a rabbit in its burrow"],
}
_HABITATS_GLOSSES = {
    "an animal that lives in WATER": "its home, food and safety are all in the water",
    "an animal that lives in TREES": "branches hold its food and keep it safe",
    "an animal that lives UNDERGROUND": "a burrow keeps it cool and hidden",
}


def gen_habitats(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _HABITATS,
                       glosses=_HABITATS_GLOSSES, concept_name="WHERE ANIMALS LIVE")


_MATERIALS_Y1 = {
    "usually made of WOOD": ["a pencil", "a door", "a chopping board"],
    "usually made of METAL": ["a saucepan", "a coin", "a key"],
    "usually made of GLASS": ["a window", "a drinking cup you can see through"],
}
_MATERIALS_Y1_GLOSSES = {
    "usually made of WOOD": "wood comes from trees; it feels warm and can be carved",
    "usually made of METAL": "metal is hard, shiny and cold to touch",
    "usually made of GLASS": "glass is smooth and you can see through it",
}


def gen_materials_y1(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MATERIALS_Y1,
                       glosses=_MATERIALS_Y1_GLOSSES, concept_name="WHAT THINGS ARE MADE OF")


_SKY = {
    "seen in the DAY sky": ["the Sun", "white clouds", "a rainbow"],
    "seen in the NIGHT sky": ["the stars", "the Moon shining brightly"],
    # A DAILY PATTERN, described without naming a day-sky object (fixed
    # 2026-08-21): the old wording "a change that happens EVERY DAY" listed
    # "the Sun seeming to rise and set", which is also plainly something
    # "seen in the DAY sky" — so that option was a defensible answer to the
    # day-sky question and marked wrong.
    "a DAILY pattern (it happens again and again)": [
        "day turning into night",
        "getting light in the morning and dark again at bedtime",
    ],
}
_SKY_GLOSSES = {
    "seen in the DAY sky": "the Sun's light fills the day sky",
    "seen in the NIGHT sky": "when our side of Earth faces away from the Sun",
    "a DAILY pattern (it happens again and again)": "Earth keeps spinning, so the pattern repeats",
}


def gen_day_night_sky(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _SKY,
                       glosses=_SKY_GLOSSES, concept_name="THE DAY AND NIGHT SKY")


_PUSH_PULL = {
    "a PUSH": ["kicking a ball", "pressing a doorbell", "shutting a drawer with your hip"],
    "a PULL": ["opening a fridge door", "dragging a wagon", "tugging a rope"],
    "a TWIST": ["turning a tap on", "winding up a toy"],
}
_PUSH_PULL_GLOSSES = {
    "a PUSH": "a force moving something AWAY from you",
    "a PULL": "a force moving something TOWARD you",
    "a TWIST": "a turning force",
}


def gen_push_pull(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _PUSH_PULL,
                       glosses=_PUSH_PULL_GLOSSES, concept_name="PUSHES AND PULLS")


AU_YEAR1_SCIENCE_GENERATORS: dict[str, GenFn] = {
    "aus1_living_things": gen_living_things,   # Living things
    "aus1_habitats": gen_habitats,             # Environments
    "aus1_materials": gen_materials_y1,        # Materials
    "aus1_day_night_sky": gen_day_night_sky,   # Earth and sky
    "aus1_push_pull": gen_push_pull,           # Forces
}
