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
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'a naming word (noun)': 'a noun names a person, place or thing',
            'a doing word (verb)': 'a verb is something you can DO',
            'a describing word (adjective)': 'an adjective tells you what something is LIKE',
        },
        concept_name='WORD CLASSES',
    )


def gen_synonyms_y2(rng: random.Random):
    """AC9E2A alignment: simple synonym pairs."""
    table = {
        "happy": ["glad", "cheerful"],
        "sad": ["unhappy", "upset"],
        "big": ["large", "giant"],
        "small": ["little", "tiny"],
        "cold": ["chilly", "icy"],
    }
    return mc_which_is(
        rng, "Which word means the SAME as '{label}'?", table,
        glosses=dict.fromkeys(table, 'a synonym is a different word with the same meaning'),
        concept_name='SYNONYMS',
    )


def gen_plurals_y2(rng: random.Random):
    """AC9E2A alignment: plural forms, mostly regular with a couple of irregulars."""
    table = {
        "cat": ["cats"], "dog": ["dogs"], "box": ["boxes"],
        "child": ["children"], "mouse": ["mice"], "book": ["books"],
    }
    return mc_which_is(
        rng, "What is the plural of '{label}'?", table,
        glosses=dict.fromkeys(table, 'most words add -s; words ending x/ch/sh/s add -es; a few change completely'),
        concept_name='PLURALS',
    )


def gen_rhyming_y2(rng: random.Random):
    """AC9E2A alignment: rhyming word families."""
    table = {
        "pig": ["big", "dig", "wig"],
        "bell": ["shell", "well", "tell"],
        "king": ["sing", "ring", "wing"],
        "boat": ["coat", "goat", "float"],
    }
    return mc_which_is(
        rng, "Which word rhymes with '{label}'?", table,
        glosses=dict.fromkeys(table, 'rhyming words share their ENDING SOUND -- the spelling can differ'),
        concept_name='RHYMING WORDS',
    )


# ── Year 3 ─────────────────────────────────────────────────────────────────

def gen_antonyms_basic_y3(rng: random.Random):
    """AC9E3A alignment: basic opposite-pairs, a stepping stone to Y5's
    'advanced' antonym vocabulary."""
    table = {
        "hot": ["cold"], "fast": ["slow"], "empty": ["full"],
        "day": ["night"], "open": ["closed"], "wet": ["dry"],
    }
    return mc_which_is(
        rng, "Which word means the OPPOSITE of '{label}'?", table,
        glosses=dict.fromkeys(table, 'an antonym is a word with the opposite meaning'),
        concept_name='ANTONYMS',
    )


def gen_prefixes_y3(rng: random.Random):
    """AC9E3A alignment: common prefixes and the meaning they add."""
    table = {
        "un- (not / opposite)": ["unhappy", "unfair", "unlock", "undo"],
        "re- (again)": ["replay", "rewrite", "return", "rebuild"],
        "dis- (not / opposite)": ["disagree", "dislike", "disappear", "distrust"],
    }
    return mc_which_is(
        rng, "Which of these words begins with the prefix {label}?", table,
        glosses={
            'un- (not / opposite)': 'un- on the front flips the meaning to its opposite',
            're- (again)': 're- on the front means doing it again',
            'dis- (not / opposite)': 'dis- on the front also means not, or the opposite',
        },
        concept_name='PREFIXES',
    )


def gen_homophones_y3(rng: random.Random):
    """AC9E3A alignment: common homophone pairs, matched by meaning."""
    table = {
        # A meaning-label must never contain the word it is asking for: "over
        # there" printed the answer "there" inside the question stem, so the item
        # could be answered without knowing the homophone at all (found by an
        # answer-leak sweep, 2026-08-12).
        "means 'in that place'": ["there"],
        "means 'belonging to them'": ["their"],
        # "a higher number word" describes TWO, which is not in this set and is
        # not what "too" means. "too" = also / more than enough.
        "means 'also' or 'more than enough'": ["too"],
        "means 'in the direction of'": ["to"],
        "means 'in this place'": ["here"],
        "means 'to listen'": ["hear"],
    }
    return mc_which_is(
        rng, "Which word {label}?", table,
        glosses=dict.fromkeys(table, 'homophones sound the same but are spelled differently and mean different things'),
        concept_name='HOMOPHONES',
    )


def gen_adjectives_comparative_y3(rng: random.Random):
    """AC9E3A alignment: comparative/superlative adjective recognition."""
    table = {
        "a comparative adjective (comparing TWO things)": ["bigger", "faster", "taller", "smaller"],
        "a superlative adjective (comparing THREE OR MORE things)": ["biggest", "fastest", "tallest", "smallest"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'a comparative adjective (comparing TWO things)': '-er compares exactly two things',
            'a superlative adjective (comparing THREE OR MORE things)': '-est picks the top one out of three or more',
        },
        concept_name='COMPARING ADJECTIVES',
    )


# ── Year 4 ─────────────────────────────────────────────────────────────────

def gen_suffixes_y4(rng: random.Random):
    """AC9E4A alignment: common suffixes and the meaning they add."""
    table = {
        "-ful (full of)": ["joyful", "careful", "colourful", "helpful"],
        "-less (without)": ["careless", "hopeless", "fearless", "harmless"],
        "-ness (a state of being)": ["happiness", "kindness", "sadness", "darkness"],
    }
    return mc_which_is(
        rng, "Which of these words ends with the suffix {label}?", table,
        glosses={
            '-ful (full of)': '-ful on the end means full of that thing',
            '-less (without)': '-less on the end means without it',
            '-ness (a state of being)': '-ness turns a describing word into the state of being it',
        },
        concept_name='SUFFIXES',
    )


def gen_contractions_y4(rng: random.Random):
    """AC9E4A alignment: matching a contraction to the words it shortens."""
    table = {
        "do not": ["don't"], "cannot": ["can't"], "it is": ["it's"],
        "I am": ["I'm"], "they are": ["they're"], "will not": ["won't"],
    }
    return mc_which_is(
        rng, "Which is the SHORT form (contraction) of '{label}'?", table,
        glosses=dict.fromkeys(table, 'a contraction joins two words and the apostrophe marks the missing letters'),
        concept_name='CONTRACTIONS',
    )


def gen_common_proper_nouns_y4(rng: random.Random):
    """AC9E4A alignment: common vs. proper noun (capitalisation) recognition."""
    table = {
        "a common noun (no capital needed)": ["city", "river", "school", "country"],
        "a proper noun (needs a capital letter)": ["London", "Nile", "Australia", "Monday"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'a common noun (no capital needed)': 'any one of many -- a city, some river',
            'a proper noun (needs a capital letter)': 'the NAME of one particular one, so it takes a capital',
        },
        concept_name='COMMON AND PROPER NOUNS',
    )


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
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            "a simile (uses 'like' or 'as' to compare)": "the words 'like' or 'as' are the giveaway",
            'a plain sentence (no comparison)': 'it states what happened without comparing it to anything',
        },
        concept_name='SIMILES',
    )


# ── Year 7 ─────────────────────────────────────────────────────────────────

def gen_idioms_y7(rng: random.Random):
    """AC9E7A alignment: idiom vs. literal-phrase recognition."""
    table = {
        "an idiom (doesn't mean what the words literally say)": [
            "it's raining cats and dogs", "break a leg", "spill the beans", "under the weather",
        ],
        "a literal phrase (means exactly what it says)": [
            "it's raining heavily outside", "good luck with the show", "I dropped the beans", "I feel sick today",
        ],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            "an idiom (doesn't mean what the words literally say)": 'the phrase has a meaning the words alone would never give you',
            'a literal phrase (means exactly what it says)': 'the words add up to exactly what is meant',
        },
        concept_name='IDIOMS',
    )


def gen_formal_informal_y7(rng: random.Random):
    """AC9E7A alignment: formal vs. informal register."""
    table = {
        "formal language": ["purchase", "commence", "assistance", "residence"],
        "informal language": ["buy", "start", "help", "home"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'formal language': "the word you would use in writing, or with someone you don't know",
            'informal language': 'the everyday word you would use with a friend',
        },
        concept_name='FORMAL AND INFORMAL WORDS',
    )


def gen_active_passive_y7(rng: random.Random):
    """AC9E7A alignment: active vs. passive voice recognition."""
    table = {
        "active voice (the subject DOES the action)": [
            "the dog chased the cat", "she wrote the letter", "the chef cooked the meal", "they built the house",
        ],
        "passive voice (the subject RECEIVES the action)": [
            "the cat was chased by the dog", "the letter was written by her",
            "the meal was cooked by the chef", "the house was built by them",
        ],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'active voice (the subject DOES the action)': 'the doer comes first: who did what',
            'passive voice (the subject RECEIVES the action)': 'the thing it happened TO comes first, and the doer moves to the end (or vanishes)',
        },
        concept_name='ACTIVE AND PASSIVE VOICE',
    )


def gen_personification_y7(rng: random.Random):
    """AC9E7A alignment: personification vs. a literal statement of the same
    event (distinguishing it from Y4's simile / Y6's simile-vs-metaphor)."""
    table = {
        # Every member must attribute a distinctly HUMAN act -- whispering,
        # smiling, groaning, grumbling. "time flew by" was here and was removed
        # (2026-08-12): flying is not a human trait (birds and planes fly), so it
        # is a metaphor, and a teacher would fairly mark it wrong as an answer to
        # "which of these is personification?".
        "personification (giving human qualities to something non-human)": [
            "the wind whispered through the trees", "the sun smiled down on us",
            "the old car groaned to a start", "the thunder grumbled angrily",
        ],
        "a literal statement": [
            "the wind blew through the trees", "the sun shone down on us",
            "the old car started slowly", "the thunder rumbled loudly",
        ],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'personification (giving human qualities to something non-human)': 'a thing is doing something only a person can do',
            'a literal statement (no human qualities given)': 'it describes the same event with no human traits attached',
        },
        concept_name='PERSONIFICATION',
    )


# ── Year 8 ─────────────────────────────────────────────────────────────────

def gen_connotation_y8(rng: random.Random):
    """AC9E8A alignment: positive vs. negative connotation (word choice that
    colours meaning beyond the dictionary definition)."""
    table = {
        "a word with a POSITIVE connotation": ["slender", "confident", "curious", "frugal"],
        "a word with a NEGATIVE connotation": ["skinny", "arrogant", "nosy", "stingy"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'a word with a POSITIVE connotation': 'same basic meaning, but it makes the thing sound good',
            'a word with a NEGATIVE connotation': 'same basic meaning, but it makes the thing sound bad',
        },
        concept_name='CONNOTATION',
    )


def gen_clauses_y8(rng: random.Random):
    """AC9E8A alignment: main clause (stands alone) vs. subordinate clause
    (cannot)."""
    table = {
        "a main clause (can stand alone as a full sentence)": [
            "she went to the store", "the dog barked loudly", "we finished our homework", "he plays the guitar",
        ],
        "a subordinate clause (cannot stand alone)": [
            "because she was hungry", "although the dog barked", "when we finished", "if he plays well",
        ],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'a main clause (can stand alone as a full sentence)': 'read it on its own and it still makes sense',
            'a subordinate clause (cannot stand alone)': 'it leaves you waiting for the rest of the sentence',
        },
        concept_name='MAIN AND SUBORDINATE CLAUSES',
    )


def gen_adverbial_phrases_y8(rng: random.Random):
    """AC9E8A alignment: adverbial phrase (how/when/where) vs. noun phrase."""
    table = {
        "an adverbial phrase (tells HOW, WHEN or WHERE)": [
            "in the morning", "very quickly", "under the table", "with great care",
        ],
        "a noun phrase (names a person, place or thing)": [
            "the big red car", "my best friend", "a beautiful sunset", "the old oak tree",
        ],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'an adverbial phrase (tells HOW, WHEN or WHERE)': 'it tells you about the action, not about a thing',
            'a noun phrase (names a person, place or thing)': 'it names a thing, with words describing it',
        },
        concept_name='ADVERBIAL AND NOUN PHRASES',
    )


def gen_onomatopoeia_y8(rng: random.Random):
    """AC9E8A alignment: onomatopoeia (sound-word) recognition."""
    table = {
        "onomatopoeia (a word that sounds like what it means)": ["buzz", "crash", "sizzle", "whoosh"],
        "a regular descriptive word": ["loud", "sudden", "hot", "fast"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'onomatopoeia (a word that sounds like what it means)': 'say it aloud -- the sound of the word IS the sound it describes',
            'a regular descriptive word': 'it describes the thing without sounding like it',
        },
        concept_name='ONOMATOPOEIA',
    )


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
    return mc_which_is(
        rng, "Which word means the SAME as '{label}'?", table,
        glosses=dict.fromkeys(table, 'a synonym is a different word with the same meaning'),
        concept_name='SYNONYMS',
    )


def gen_antonyms_advanced_y5(rng: random.Random):
    """AC9E5A alignment: richer vocabulary antonym pairs."""
    table = {
        "generous": ["stingy"],
        "ancient": ["modern"],
        "cautious": ["reckless"],
        "genuine": ["fake"],
        "abundant": ["scarce"],
    }
    return mc_which_is(
        rng, "Which word means the OPPOSITE of '{label}'?", table,
        glosses=dict.fromkeys(table, 'an antonym is a word with the opposite meaning'),
        concept_name='ANTONYMS',
    )


def gen_word_classes_advanced_y5(rng: random.Random):
    """AC9E5A alignment: adverb/pronoun/verb classification (harder than Y2's
    noun/verb/adjective)."""
    table = {
        "an adverb (describes HOW something is done)": ["quickly", "quietly", "carefully", "loudly"],
        "a pronoun (stands in for a noun)": ["she", "they", "it", "we"],
        "a verb": ["walk", "think", "build", "carry"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            'an adverb (describes HOW something is done)': 'adverbs describe the verb, and often end -ly',
            'a pronoun (stands in for a noun)': 'it replaces a name you already know',
            'a verb': 'a verb is the action itself',
        },
        concept_name='WORD CLASSES',
    )


def gen_compound_words_y5(rng: random.Random):
    """AC9E5A alignment: recognising real compound words vs. invented ones."""
    table = {
        "a real compound word": ["sunflower", "toothbrush", "basketball", "butterfly", "football"],
        "not a real word": ["moonbrush", "chairwater", "tablesong", "doorsinger"],
    }
    return mc_which_is(
        rng, "Which of these IS {label}?", table,
        glosses={
            'a real compound word': 'two real words joined into one word people actually use',
            'not a real word': 'two real words stuck together, but not a word anyone uses',
        },
        concept_name='COMPOUND WORDS',
    )


# ── Year 6 ─────────────────────────────────────────────────────────────────

def gen_figurative_language_y6(rng: random.Random):
    """AC9E6A alignment: distinguishing similes from metaphors."""
    table = {
        "a simile (uses 'like' or 'as')": ["as brave as a lion", "ran like the wind", "as quiet as a mouse", "as busy as a bee"],
        "a metaphor (says one thing IS another)": ["time is money", "the classroom was a zoo", "her heart is a stone", "the world is a stage"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            "a simile (uses 'like' or 'as')": 'it says one thing is LIKE another',
            'a metaphor (says one thing IS another)': "it says one thing IS the other, with no 'like' or 'as'",
        },
        concept_name='SIMILE AND METAPHOR',
    )


def gen_synonyms_nuanced_y6(rng: random.Random):
    """AC9E6A alignment: nuanced/contextual synonym pairs."""
    table = {
        "reluctant": ["hesitant", "unwilling"],
        "meticulous": ["thorough", "precise"],
        "candid": ["honest", "frank"],
        "resilient": ["tough", "adaptable"],
    }
    return mc_which_is(
        rng, "Which word means the SAME as '{label}'?", table,
        glosses=dict.fromkeys(table, 'a synonym is a different word with the same meaning -- the shade of meaning can differ'),
        concept_name='SYNONYMS',
    )


def gen_antonyms_nuanced_y6(rng: random.Random):
    """AC9E6A alignment: nuanced antonym pairs."""
    table = {
        "transparent": ["opaque"],
        "concise": ["verbose"],
        "voluntary": ["compulsory"],
        "flexible": ["rigid"],
    }
    return mc_which_is(
        rng, "Which word means the OPPOSITE of '{label}'?", table,
        glosses=dict.fromkeys(table, 'an antonym is a word with the opposite meaning'),
        concept_name='ANTONYMS',
    )


def gen_word_classes_conj_prep_y6(rng: random.Random):
    """AC9E6A alignment: conjunction/preposition classification."""
    table = {
        "a conjunction (joins two ideas)": ["and", "but", "because", "although"],
        "a preposition (shows position or time)": ["under", "before", "between", "during"],
    }
    return mc_which_is(
        rng, "Which of these is {label}?", table,
        glosses={
            "a conjunction (joins two ideas)": "it sits BETWEEN two ideas and links them",
            "a preposition (shows position or time)": "it tells you where or when something is, in relation to something else",
        },
        concept_name="CONJUNCTIONS AND PREPOSITIONS",
    )


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

AU_ENGLISH_YEAR7_GENERATORS: dict[str, GenFn] = {
    "aue7_idioms": gen_idioms_y7,
    "aue7_formal_informal": gen_formal_informal_y7,
    "aue7_active_passive": gen_active_passive_y7,
    "aue7_personification": gen_personification_y7,
}

AU_ENGLISH_YEAR8_GENERATORS: dict[str, GenFn] = {
    "aue8_connotation": gen_connotation_y8,
    "aue8_clauses": gen_clauses_y8,
    "aue8_adverbial_phrases": gen_adverbial_phrases_y8,
    "aue8_onomatopoeia": gen_onomatopoeia_y8,
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


# ── Year 9-12 (senior secondary, 2026-08-14) ─────────────────────────────────
# The AU packs stopped at Year 8 for English while maths ran to Year 12 -- a
# breadth asymmetry nobody had ratified (docs/PHASE0_STATUS.md's "what's missing"
# audit flagged it). Same fact-table shape as every generator above: disjoint
# categories, four options, one correct, deterministic verifier.
#
# ACARA codes are alignment REFERENCES only, and PROVISIONAL for these years --
# the same caveat the Year 3-8 science packs carry.

def gen_modality_y9(rng: random.Random):
    """AC9E9A alignment: high vs. low modality (how certain or forceful a word
    makes a claim) -- the core lever in persuasive writing."""
    table = {
        "HIGH modality (very certain or forceful)": ["must", "definitely", "always", "never", "certainly"],
        "LOW modality (tentative or hedged)": ["might", "possibly", "sometimes", "could", "perhaps"],
    }
    return mc_which_is(rng, "Which of these words shows {label}?", table,
        glosses={
            'HIGH modality (very certain or forceful)': 'leaves the reader no room to doubt the claim',
            'LOW modality (tentative or hedged)': 'leaves room for the claim to be wrong',
        },
        concept_name='MODALITY')


def gen_nominalisation_y9(rng: random.Random):
    """AC9E9A alignment: nominalisation -- turning a verb or adjective into a
    noun, which makes writing denser and more formal."""
    table = {
        "a nominalisation (a noun made from a verb or adjective)": [
            "decision", "arrival", "failure", "happiness", "assessment",
        ],
        "a plain verb or adjective (not nominalised)": [
            "decide", "arrive", "fail", "happy", "assess",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a nominalisation (a noun made from a verb or adjective)': 'the action or quality has become a THING you can discuss -- often ending -tion, -ment, -ness, -al, -ure',
            'a plain verb or adjective (not nominalised)': 'still names an action or a quality, not a thing',
        },
        concept_name='NOMINALISATION')


def gen_rhetorical_devices_y9(rng: random.Random):
    """AC9E9A alignment: naming the persuasive device in a short example."""
    table = {
        "a rhetorical question (asked for effect, not for an answer)": [
            "Who wouldn't want cleaner air?", "Isn't it time we acted?", "How much longer must we wait?",
        ],
        "a direct address to the reader": [
            "You can change this today.", "Think about your own street.", "Your voice matters here.",
        ],
        "a repetition for emphasis": [
            "We tried, we failed, we tried again.", "Faster, cleaner, cheaper.", "Never again, never again.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a rhetorical question (asked for effect, not for an answer)': 'the answer is assumed, so the reader agrees without being told to',
            'a direct address to the reader': "speaking to 'you' makes the issue personal",
            'a repetition for emphasis': 'the repeated words drum the idea in',
        },
        concept_name='RHETORICAL DEVICES')


def gen_sentence_types_y9(rng: random.Random):
    """AC9E9A alignment: simple / compound / complex sentence structure."""
    table = {
        "a simple sentence (one main clause)": [
            "The train left early.", "She writes poetry.", "The lights went out.",
        ],
        "a compound sentence (two main clauses joined by and/but/so)": [
            "The train left early, but we caught it.",
            "She writes poetry and she paints.",
            "The lights went out, so we lit a candle.",
        ],
        "a complex sentence (a main clause plus a subordinate clause)": [
            "Although the train left early, we caught it.",
            "She writes poetry because it calms her.",
            "When the lights went out, we lit a candle.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a simple sentence (one main clause)': 'one complete idea, standing alone',
            'a compound sentence (two main clauses joined by and/but/so)': 'two ideas of equal weight -- either half could stand alone',
            'a complex sentence (a main clause plus a subordinate clause)': 'one idea depends on the other, so it cannot stand alone',
        },
        concept_name='SENTENCE TYPES')


def gen_tone_y10(rng: random.Random):
    """AC9E10A alignment: identifying the tone a short line takes."""
    table = {
        "a CRITICAL tone": [
            "The plan was careless and poorly argued.",
            "Once again, the council has ignored the evidence.",
            "This is a shallow response to a serious problem.",
        ],
        "an OPTIMISTIC tone": [
            "With small changes, this street could thrive.",
            "There is every reason to expect a better year.",
            "The early results are genuinely encouraging.",
        ],
        "a NEUTRAL, factual tone": [
            "The council met on Tuesday to review the plan.",
            "Rainfall was 12 mm below the monthly average.",
            "The report was published in March.",
        ],
    }
    return mc_which_is(rng, "Which of these takes {label}?", table,
        glosses={
            'a CRITICAL tone': 'the word choices find fault',
            'an OPTIMISTIC tone': 'the word choices expect a good outcome',
            'a NEUTRAL, factual tone': 'it reports without judging',
        },
        concept_name='TONE')


def gen_irony_satire_y10(rng: random.Random):
    """AC9E10A alignment: irony vs. satire vs. a literal statement."""
    table = {
        "irony (saying the opposite of what is meant)": [
            "What a perfect day for a picnic, he said in the pouring rain.",
            "Brilliant timing, she muttered as the bus pulled away.",
        ],
        "satire (mocking something to criticise it)": [
            "A cartoon showing the minister asleep at a fire drill.",
            "A mock award for the town's least useful new law.",
        ],
        "a literal statement (means exactly what it says)": [
            "It rained for most of the afternoon.",
            "The bus arrived four minutes late.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'irony (saying the opposite of what is meant)': 'the gap between the words and the situation IS the irony',
            'satire (mocking something to criticise it)': 'it mocks a target in order to criticise it',
            'a literal statement (means exactly what it says)': 'no gap and no target -- it just reports',
        },
        concept_name='IRONY AND SATIRE')


def gen_evaluative_language_y10(rng: random.Random):
    """AC9E10A alignment: evaluative (judging) vs. neutral (reporting) wording --
    the distinction that separates an argument from a report."""
    table = {
        "EVALUATIVE language (it judges)": [
            "a disgraceful decision", "an outstanding performance",
            "a reckless proposal", "a masterful reply",
        ],
        "NEUTRAL language (it reports)": [
            "a unanimous decision", "a two-hour performance",
            "a written proposal", "a same-day reply",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'EVALUATIVE language (it judges)': 'the wording passes judgement on the thing',
            'NEUTRAL language (it reports)': 'the wording describes without judging',
        },
        concept_name='EVALUATIVE LANGUAGE')


def gen_cohesion_y10(rng: random.Random):
    """AC9E10A alignment: the cohesive device holding two sentences together."""
    table = {
        "a contrast connective": ["however", "nevertheless", "on the other hand", "whereas"],
        "a cause-and-effect connective": ["therefore", "consequently", "as a result", "because of this"],
        "a sequencing connective": ["firstly", "meanwhile", "subsequently", "finally"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a contrast connective': 'signals that what follows cuts against what came before',
            'a cause-and-effect connective': 'signals that what follows results from what came before',
            'a sequencing connective': 'signals where this step sits in an order',
        },
        concept_name='COHESIVE DEVICES')


def gen_textual_analysis_y11(rng: random.Random):
    """Senior English: naming the technique at work in a short quotation. Codes
    are provisional -- senior English is state-certificate territory, so this is
    universally-taught technique naming, not a claimed unit alignment."""
    table = {
        "a metaphor (says one thing IS another)": [
            "Her voice was a warm blanket.", "The city is a furnace in January.",
            "His memory is a locked room.",
        ],
        "a simile (compares using like or as)": [
            "Her voice was like a warm blanket.", "The city felt as hot as a furnace.",
            "His memory is like a locked room.",
        ],
        "personification (gives human traits to a thing)": [
            "The wind argued with the shutters.", "The old house sighed in the heat.",
            "The clock scolded us from the wall.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a metaphor (says one thing IS another)': "no 'like' or 'as' -- the comparison is stated as fact",
            'a simile (compares using like or as)': "the comparison is signalled by 'like' or 'as'",
            'personification (gives human traits to a thing)': 'a non-human thing is given a human action or feeling',
        },
        concept_name='LITERARY TECHNIQUES')


def gen_argument_structure_y11(rng: random.Random):
    """Senior English: the part an argument sentence is doing (claim / evidence /
    rebuttal) -- the shape every senior essay is marked on."""
    table = {
        "a CLAIM (the position being argued)": [
            "Public transport should be free at peak times.",
            "School should start an hour later.",
            "Local libraries deserve more funding.",
        ],
        "EVIDENCE (a fact or example supporting a claim)": [
            "Ridership rose 14% in the year fares were cut.",
            "Sleep studies show teenagers need nine hours.",
            "Library visits doubled after the late-opening trial.",
        ],
        "a REBUTTAL (answering the opposing view)": [
            "Critics say it costs too much, but road repairs cost more.",
            "Some argue standards would slip; the trial found the opposite.",
            "Opponents call it a luxury, yet the demand is measurable.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a CLAIM (the position being argued)': 'it states what the writer wants you to accept',
            'EVIDENCE (a fact or example supporting a claim)': 'it offers something checkable in support',
            'a REBUTTAL (answering the opposing view)': 'it names the opposing view, then answers it',
        },
        concept_name='ARGUMENT STRUCTURE')


def gen_register_shift_y11(rng: random.Random):
    """Senior English: matching wording to audience and purpose."""
    table = {
        "FORMAL register (suited to an academic essay)": [
            "The evidence suggests a modest improvement.",
            "This paper examines three competing explanations.",
            "The results were inconsistent with the hypothesis.",
        ],
        "INFORMAL register (suited to a message to a friend)": [
            "Looks like it got a bit better.",
            "So there are three ways people explain it.",
            "Yeah, that didn't go how we thought.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'FORMAL register (suited to an academic essay)': 'no contractions, precise verbs, distance from the reader',
            'INFORMAL register (suited to a message to a friend)': 'contractions and everyday words, close to the reader',
        },
        concept_name='REGISTER')


def gen_bias_y12(rng: random.Random):
    """Senior English: loaded vs. balanced reporting of the same event -- media
    literacy, and the closest thing to a life skill in this pack."""
    table = {
        "BIASED wording (it slants the reader)": [
            "A mob of protesters swarmed the square.",
            "The so-called expert made yet another excuse.",
            "Taxpayers were forced to foot the bill again.",
        ],
        "BALANCED wording (it reports the same event neutrally)": [
            "A crowd of protesters gathered in the square.",
            "The researcher gave a further explanation.",
            "The cost was met from public funds.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'BIASED wording (it slants the reader)': 'the loaded words push a judgement the facts do not carry',
            'BALANCED wording (it reports the same event neutrally)': 'same event, no loaded words',
        },
        concept_name='BIAS IN REPORTING')


def gen_allusion_y12(rng: random.Random):
    """Senior English: allusion (a reference to a known text or event) vs. a
    plain description."""
    table = {
        "an allusion (a reference to another text or event)": [
            "He met his Waterloo in the final round.",
            "She opened a Pandora's box of paperwork.",
            "The plan was his Achilles heel.",
        ],
        "a plain description (no reference)": [
            "He lost badly in the final round.",
            "She started a great deal of paperwork.",
            "The plan had one serious weakness.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'an allusion (a reference to another text or event)': 'understanding the line depends on knowing the thing referred to',
            'a plain description (no reference)': 'it says the same idea without borrowing from anywhere',
        },
        concept_name='ALLUSION')


def gen_syntax_for_effect_y12(rng: random.Random):
    """Senior English: a deliberate syntactic choice and the effect it creates."""
    table = {
        "a short sentence used for impact": ["It failed.", "Nobody moved.", "That was the end."],
        "a long, accumulating sentence used to build detail": [
            "The room, still smelling of rain and old paper, filled slowly with people who had "
            "waited outside for hours.",
            "She read the letter twice, folded it, put it in her pocket, and said nothing at all.",
            "Across the valley, past the fence line and the dry creek, the smoke was already rising.",
        ],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a short sentence used for impact': 'the abruptness lands the point',
            'a long, accumulating sentence used to build detail': 'the piling-up slows the reader and builds the picture',
        },
        concept_name='SYNTAX FOR EFFECT')


def gen_language_change_y12(rng: random.Random):
    """Senior English: how English changes -- borrowed words vs. words coined for
    new technology."""
    table = {
        "a word BORROWED from another language": ["kindergarten", "safari", "typhoon", "bungalow"],
        "a word COINED for new technology": ["podcast", "smartphone", "software", "livestream"],
    }
    return mc_which_is(rng, "Which of these is {label}?", table,
        glosses={
            'a word BORROWED from another language': 'English took the word from another language',
            'a word COINED for new technology': 'the word was built for something that did not exist before',
        },
        concept_name='HOW ENGLISH CHANGES')


AU_ENGLISH_YEAR9_GENERATORS: dict[str, GenFn] = {
    "aue9_modality": gen_modality_y9,
    "aue9_nominalisation": gen_nominalisation_y9,
    "aue9_rhetorical_devices": gen_rhetorical_devices_y9,
    "aue9_sentence_types": gen_sentence_types_y9,
}

AU_ENGLISH_YEAR10_GENERATORS: dict[str, GenFn] = {
    "aue10_tone": gen_tone_y10,
    "aue10_irony_satire": gen_irony_satire_y10,
    "aue10_evaluative_language": gen_evaluative_language_y10,
    "aue10_cohesion": gen_cohesion_y10,
}

AU_ENGLISH_YEAR11_GENERATORS: dict[str, GenFn] = {
    "aue11_textual_analysis": gen_textual_analysis_y11,
    "aue11_argument_structure": gen_argument_structure_y11,
    "aue11_register_shift": gen_register_shift_y11,
}

AU_ENGLISH_YEAR12_GENERATORS: dict[str, GenFn] = {
    "aue12_bias": gen_bias_y12,
    "aue12_allusion": gen_allusion_y12,
    "aue12_syntax_for_effect": gen_syntax_for_effect_y12,
    "aue12_language_change": gen_language_change_y12,
}
