"""W4 of the curriculum depth program: senior English SPLIT into the three
courses a real senior student enrols in — Essential English (practical/
vocational), English (mainstream), and Literature — mirroring the senior maths
and senior science splits.

The old merged senior English (au_english_year11/12) retires; its nodes are
absorbed VERBATIM into the mainstream English course (same ids, mastery
survives). Same discipline as every senior module: disjoint fact tables ->
mc_which_is, glosses on every category, no claimed alignment.
"""

from __future__ import annotations

import random

from mentar.engine.au_english_items import (
    AU_ENGLISH_YEAR11_GENERATORS,
    AU_ENGLISH_YEAR12_GENERATORS,
)
from mentar.engine.itemgen import GenFn, mc_which_is

# ── Essential English Year 11 ────────────────────────────────────────────────

_WORKPLACE = {
    "a WORKPLACE text": [
        "a staff roster for the week", "a workplace safety notice",
        "an incident report form",
    ],
    "a PERSONAL text": ["a diary entry", "a birthday card message"],
    "a text for a GENERAL PUBLIC audience": [
        "a council flyer about bin collection", "a supermarket catalogue",
    ],
}
_WORKPLACE_GLOSSES = {
    "a WORKPLACE text": "written to get a job done: clear, dated, often a set form",
    "a PERSONAL text": "private audience, informal register",
    "a text for a GENERAL PUBLIC audience": "broad audience, plain language, no jargon",
}


def gen_workplace_texts(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _WORKPLACE,
                       glosses=_WORKPLACE_GLOSSES, concept_name="WORKPLACE TEXTS")


_AD_TECHNIQUES = {
    "the BANDWAGON technique (everyone's doing it)": [
        "“Join the two million Australians who have already switched”",
    ],
    "an appeal to an EXPERT or authority": [
        "“9 out of 10 dentists recommend this toothpaste”",
        "“developed with leading sports scientists”",
    ],
    "an EMOTIONAL appeal": [
        "“don't let your family go unprotected”",
        "a charity ad showing a shivering puppy",
    ],
}
_AD_TECHNIQUES_GLOSSES = {
    "the BANDWAGON technique (everyone's doing it)": "belonging as the bait — nobody wants to be left out",
    "an appeal to an EXPERT or authority": "borrowed credibility: trust the coat, not the claim",
    "an EMOTIONAL appeal": "feelings first, facts optional",
}


def gen_advertising_media(rng: random.Random):
    return mc_which_is(rng, "Which of these uses {label}?", _AD_TECHNIQUES,
                       glosses=_AD_TECHNIQUES_GLOSSES, concept_name="ADVERTISING TECHNIQUES")


_INSTRUCTIONAL = {
    "a feature of INSTRUCTIONAL texts": [
        "numbered steps in the order you do them",
        "command verbs like “press”, “lift”, “turn”",
    ],
    "a feature of NARRATIVE texts": [
        "characters and a plot with a complication",
        "past-tense storytelling",
    ],
    "a feature of PERSUASIVE texts": [
        "a call to action at the end",
        "rhetorical questions aimed at the reader",
    ],
}
_INSTRUCTIONAL_GLOSSES = {
    "a feature of INSTRUCTIONAL texts": "written to be USED, not read for pleasure: steps, commands, diagrams",
    "a feature of NARRATIVE texts": "written to tell a story",
    "a feature of PERSUASIVE texts": "written to change your mind or your behaviour",
}


def gen_instructional_texts(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _INSTRUCTIONAL,
                       glosses=_INSTRUCTIONAL_GLOSSES, concept_name="INSTRUCTIONAL TEXTS")


# ── Essential English Year 12 ────────────────────────────────────────────────

_NEWS = {
    "a statement of FACT": [
        "“the council voted 7–2 to close the pool”",
        "“the fire began on Tuesday evening”",
    ],
    "a statement of OPINION": [
        "“closing the pool is a disgraceful decision”",
        "“this is the best show of the year”",
    ],
    "a sign of a source's PERSPECTIVE": [
        "a mining story quoting only the company's spokesperson",
        "a headline calling protesters “a mob”",
    ],
}
_NEWS_GLOSSES = {
    "a statement of FACT": "checkable against evidence — it could be proved wrong",
    "a statement of OPINION": "a judgement; no measurement could settle it",
    "a sign of a source's PERSPECTIVE": "who gets quoted and what they're called shapes the story",
}


def gen_news_perspectives(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _NEWS,
                       glosses=_NEWS_GLOSSES, concept_name="NEWS AND PERSPECTIVE")


_PERSUASIVE_ARGS = {
    "an argument using STATISTICS": [
        "“road deaths fell 40% after the limit changed”",
    ],
    "an argument using an ANECDOTE": [
        "“my neighbour waited nine hours in that emergency room”",
        "“when my own street flooded, no one came”",
    ],
    "a RHETORICAL QUESTION": [
        "“how many more warnings do we need?”",
        "“is this really the future we want?”",
    ],
}
_PERSUASIVE_ARGS_GLOSSES = {
    "an argument using STATISTICS": "numbers lend weight — check where they came from",
    "an argument using an ANECDOTE": "one vivid story standing in for many cases",
    "a RHETORICAL QUESTION": "a question that expects agreement, not an answer",
}


def gen_persuasive_arguments(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _PERSUASIVE_ARGS,
                       glosses=_PERSUASIVE_ARGS_GLOSSES, concept_name="PERSUASIVE ARGUMENTS")


# Email and letter conventions are ONE category (fixed 2026-08-21): they were
# split, so "Yours sincerely above a full name" sat under "formal LETTER" and
# was a WRONG answer to "which is appropriate in a PROFESSIONAL email?" -- but
# that sign-off is entirely appropriate in a professional email. The third
# category is now habits that WEAKEN a professional message, which overlaps
# neither of the others.
_PROFESSIONAL = {
    "appropriate in a PROFESSIONAL message (email or letter)": [
        "“Dear Ms Chen, I am writing to apply for…”",
        "a clear subject line naming the matter",
        "“Yours sincerely” above a full name",
        "referring to the position title exactly as advertised",
    ],
    "appropriate only in a CASUAL message": [
        "“hey!! can u cover my shift lol”",
        "emojis standing in for the actual request",
        "“hiya — sorted?” as the whole opening line",
    ],
    "a habit that WEAKENS a professional message": [
        "writing the entire message in capital letters",
        "sending it without checking how the reader spells their name",
        "burying the actual request in the very last line",
    ],
}
_PROFESSIONAL_GLOSSES = {
    "appropriate in a PROFESSIONAL message (email or letter)":
        "greeting, purpose, request, sign-off — respect the reader's time",
    "appropriate only in a CASUAL message": "fine for friends; costly in a workplace",
    "a habit that WEAKENS a professional message":
        "the reader has to work harder than they should to find what you want",
}


def gen_professional_communication(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _PROFESSIONAL,
                       glosses=_PROFESSIONAL_GLOSSES, concept_name="PROFESSIONAL COMMUNICATION")


# ── English (mainstream) Year 11 ─────────────────────────────────────────────

_PERSPECTIVES = {
    "a FIRST-PERSON participant's perspective": [
        "“I was on the bridge when it began to sway”",
    ],
    "an EXPERT's perspective": [
        "“as an engineer, I can say the design was sound”",
        "a historian weighing two accounts of the event",
    ],
    "a perspective shaped by SELF-INTEREST": [
        "a developer praising the very project they profit from",
        "a company's own report calling its spill “minor”",
    ],
}
_PERSPECTIVES_GLOSSES = {
    "a FIRST-PERSON participant's perspective": "they were there — vivid, but only one vantage point",
    "an EXPERT's perspective": "trained judgement; still worth asking which school they belong to",
    "a perspective shaped by SELF-INTEREST": "follow the incentive before trusting the account",
}


def gen_perspectives_values(rng: random.Random):
    return mc_which_is(rng, "Which of these shows {label}?", _PERSPECTIVES,
                       glosses=_PERSPECTIVES_GLOSSES, concept_name="PERSPECTIVES AND VALUES")


_TEXT_STRUCTURES = {
    "CAUSE-AND-EFFECT structure": [
        "“because the dam failed, the valley flooded, which forced…”",
    ],
    "COMPARE-AND-CONTRAST structure": [
        "“the city offers X; the country, by contrast, offers Y”",
        "paragraphs alternating between two rival plans",
    ],
    "CHRONOLOGICAL structure": [
        "“first… then… by nightfall… the next morning…”",
        "a biography moving birth to death in order",
    ],
}
_TEXT_STRUCTURES_GLOSSES = {
    "CAUSE-AND-EFFECT structure": "links events by WHY — signal words: because, therefore, as a result",
    "COMPARE-AND-CONTRAST structure": "sets two things side by side — however, whereas, on the other hand",
    "CHRONOLOGICAL structure": "time is the organiser — first, then, finally",
}


def gen_text_structures(rng: random.Random):
    return mc_which_is(rng, "Which of these uses {label}?", _TEXT_STRUCTURES,
                       glosses=_TEXT_STRUCTURES_GLOSSES, concept_name="TEXT STRUCTURES")


_ANALYTICAL = {
    "a THESIS statement": [
        "“Shakespeare presents ambition as a corrosive force”",
    ],
    "textual EVIDENCE": [
        "a quotation from the scene being discussed",
        "“the stage direction reads: 'he drops the crown'”",
    ],
    "ANALYSIS of evidence": [
        "“the metaphor of poison suggests the corruption spreads unseen”",
        "explaining what the word choice makes the audience feel",
    ],
}
_ANALYTICAL_GLOSSES = {
    "a THESIS statement": "the essay's one-sentence claim — everything else serves it",
    "textual EVIDENCE": "the text's own words, quoted exactly",
    "ANALYSIS of evidence": "the WHY between quote and claim — where marks live",
}


def gen_analytical_essays(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ANALYTICAL,
                       glosses=_ANALYTICAL_GLOSSES, concept_name="ANALYTICAL ESSAYS")


_IMAGINATIVE = {
    "FORESHADOWING": [
        "a storm gathering in chapter one before the tragedy",
        "the gun mentioned casually on the mantel early on",
    ],
    "a FLASHBACK": [
        "the narrator suddenly recalling the summer it all began",
    ],
    "sensory IMAGERY": [
        "“the air tasted of salt and diesel”",
        "“frost crunched like glass beneath their boots”",
    ],
}
_IMAGINATIVE_GLOSSES = {
    "FORESHADOWING": "a planted hint the ending will collect",
    "a FLASHBACK": "the timeline steps backwards to show how we got here",
    "sensory IMAGERY": "the five senses doing the describing",
}


def gen_imaginative_texts(rng: random.Random):
    return mc_which_is(rng, "Which of these is an example of {label}?", _IMAGINATIVE,
                       glosses=_IMAGINATIVE_GLOSSES, concept_name="IMAGINATIVE TECHNIQUES")


# ── English (mainstream) Year 12 ─────────────────────────────────────────────

_CONTEXTS = {
    "HISTORICAL context": [
        "reading a war poem against the battle its poet survived",
        "knowing censorship laws shaped what the novel could say",
    ],
    "CULTURAL context": [
        "reading a text through the customs of the society that made it",
    ],
    "the reader's PERSONAL context": [
        "a migrant reader connecting a border-crossing scene to their own journey",
        "rereading a childhood book as a parent and finding it changed",
    ],
}
_CONTEXTS_GLOSSES = {
    "HISTORICAL context": "when it was written changes what it means",
    "CULTURAL context": "whose beliefs and customs the text breathes",
    "the reader's PERSONAL context": "what YOU bring shapes what you find",
}


def gen_comparative_contexts(rng: random.Random):
    return mc_which_is(rng, "Which of these is a use of {label}?", _CONTEXTS,
                       glosses=_CONTEXTS_GLOSSES, concept_name="CONTEXTS")


_MEDIA_BIAS = {
    "bias through LOADED language": [
        "calling the same plan “a reckless gamble” rather than “a bold reform”",
    ],
    "bias through SELECTION and omission": [
        "reporting the protest's one broken window but not its 10,000 marchers",
        "quoting only critics of the policy",
    ],
    "bias through FRAMING and placement": [
        "burying the correction on page 14 after a front-page accusation",
        "a photo angle that makes a small crowd look vast",
    ],
}
_MEDIA_BIAS_GLOSSES = {
    "bias through LOADED language": "the adjective does the arguing",
    "bias through SELECTION and omission": "what's left OUT tilts the story",
    "bias through FRAMING and placement": "position and picture steer the eye before the words start",
}


def gen_media_bias(rng: random.Random):
    return mc_which_is(rng, "Which of these shows {label}?", _MEDIA_BIAS,
                       glosses=_MEDIA_BIAS_GLOSSES, concept_name="MEDIA BIAS")


_COMPARATIVE_ESSAYS = {
    "BLOCK structure (one text, then the other)": [
        "all of Text A's treatment first, then all of Text B's",
    ],
    "POINT-BY-POINT structure": [
        "each paragraph taking one idea across both texts",
        "alternating texts within every body paragraph",
    ],
    "an effective COMPARATIVE link": [
        "“where Orwell uses fear, Atwood uses ritual”",
        "“both texts arrive at obedience, but by opposite roads”",
    ],
}
_COMPARATIVE_ESSAYS_GLOSSES = {
    "BLOCK structure (one text, then the other)": "simple to write, weak at linking — the comparison waits till the end",
    "POINT-BY-POINT structure": "the comparison happens in every paragraph",
    "an effective COMPARATIVE link": "one sentence holding both texts at once",
}


def gen_comparative_essays(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _COMPARATIVE_ESSAYS,
                       glosses=_COMPARATIVE_ESSAYS_GLOSSES, concept_name="COMPARATIVE ESSAYS")


_RHETORIC = {
    "ETHOS (credibility appeal)": [
        "“as a nurse of twenty years, I have seen what these cuts do”",
    ],
    "PATHOS (emotional appeal)": [
        "“picture your daughter waiting alone at that unlit bus stop”",
        "“no child should go to school hungry”",
    ],
    "LOGOS (logical appeal)": [
        "“if each unit costs $4 and we need fifty, the maths is simple”",
        "“three independent studies reached the same conclusion”",
    ],
}
_RHETORIC_GLOSSES = {
    "ETHOS (credibility appeal)": "trust me — look who is speaking",
    "PATHOS (emotional appeal)": "feel this — the heart votes first",
    "LOGOS (logical appeal)": "follow this — premises marching to a conclusion",
}


def gen_persuasive_essays(rng: random.Random):
    return mc_which_is(rng, "Which of these uses {label}?", _RHETORIC,
                       glosses=_RHETORIC_GLOSSES, concept_name="RHETORICAL APPEALS")


# ── Literature Year 11 ───────────────────────────────────────────────────────

_CANON = {
    "ELIZABETHAN drama": [
        "Shakespeare's Macbeth", "a play written for the Globe's open stage",
    ],
    "the VICTORIAN novel": [
        "Dickens' Great Expectations", "a serialised novel of industrial London",
    ],
    "ROMANTIC poetry": [
        "Wordsworth's daffodils", "poetry exalting nature and feeling over reason",
    ],
}
_CANON_GLOSSES = {
    "ELIZABETHAN drama": "verse drama for a public playhouse, c. 1600",
    "the VICTORIAN novel": "sprawling social novels of the industrial age",
    "ROMANTIC poetry": "nature, emotion and the individual, against the machine age",
}


def gen_canonical_literature(rng: random.Random):
    return mc_which_is(rng, "Which of these belongs to {label}?", _CANON,
                       glosses=_CANON_GLOSSES, concept_name="LITERARY PERIODS")


_POETRY = {
    "a SONNET": [
        "fourteen lines turning on a volta",
        "Shakespeare's “Shall I compare thee…”",
    ],
    "a HAIKU": [
        "three lines of five, seven and five syllables",
        "a single season-image, said and left",
    ],
    "FREE VERSE": [
        "lines with no set rhyme or meter",
        "rhythm built from breath and line-breaks alone",
    ],
}
_POETRY_GLOSSES = {
    "a SONNET": "14 lines; the volta is where the poem changes its mind",
    "a HAIKU": "5-7-5; the smallest room a poem can live in",
    "FREE VERSE": "form follows voice — the poet keeps the ruler in the drawer",
}


def gen_poetry_forms(rng: random.Random):
    return mc_which_is(rng, "Which of these describes {label}?", _POETRY,
                       glosses=_POETRY_GLOSSES, concept_name="POETIC FORMS")


_GENRE = {
    "a GOTHIC element": [
        "a decaying mansion hiding a family secret",
        "a storm rattling the casements at midnight",
    ],
    "a SCIENCE FICTION element": [
        "a colony ship waking its frozen crew",
        "a technology arriving before the ethics for it",
    ],
    "a DETECTIVE fiction element": [
        "a locked room and a missing key",
        "the least likely suspect proving guilty",
    ],
}
_GENRE_GLOSSES = {
    "a GOTHIC element": "dread in old houses: the past refusing to stay buried",
    "a SCIENCE FICTION element": "the future used as a mirror",
    "a DETECTIVE fiction element": "a puzzle wearing a plot",
}


def gen_genre_over_time(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _GENRE,
                       glosses=_GENRE_GLOSSES, concept_name="GENRE CONVENTIONS")


# ── Literature Year 12 ───────────────────────────────────────────────────────

_THEORIES = {
    "a FEMINIST reading": [
        "asking why the novel's women speak only about its men",
        "tracing who does the housework of the plot",
    ],
    "a MARXIST reading": [
        "reading the manor and the mill as class in conflict",
        "asking who owns what, and what that ownership silences",
    ],
    "a POSTCOLONIAL reading": [
        "hearing the colony answer back to the empire's narrator",
        "asking whose land the adventure story treats as empty",
    ],
}
_THEORIES_GLOSSES = {
    "a FEMINIST reading": "gender and power: who speaks, who is spoken for",
    "a MARXIST reading": "class and capital: the economics under the romance",
    "a POSTCOLONIAL reading": "empire and identity: the map drawn by the winners",
}


def gen_literary_theories(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _THEORIES,
                       glosses=_THEORIES_GLOSSES, concept_name="CRITICAL LENSES")


_DRAMA_TECH = {
    "a SOLILOQUY": [
        "Hamlet alone on stage, thinking aloud to the audience",
    ],
    "DRAMATIC IRONY": [
        "the audience knowing the letter is forged while the hero trusts it",
        "we see the murderer behind the door; the victim does not",
    ],
    "an ASIDE": [
        "a character's quick remark to the audience, unheard on stage",
        "one line dropped sideways to us mid-scene",
    ],
}
_DRAMA_TECH_GLOSSES = {
    "a SOLILOQUY": "a mind opened on stage — no listeners but us",
    "DRAMATIC IRONY": "we know more than they do, and it hurts",
    "an ASIDE": "a stage whisper the plot can't hear",
}


def gen_complex_plays(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _DRAMA_TECH,
                       glosses=_DRAMA_TECH_GLOSSES, concept_name="DRAMATIC TECHNIQUES")


_INTERPRETATION = {
    "an interpretation SUPPORTED by the text": [
        "a claim followed by the quotation that grounds it",
        "“the repeated 'again' shows the cycle continuing — as the final line confirms”",
    ],
    "an UNSUPPORTED assertion": [
        "“this is obviously the best poem ever written”",
        "a sweeping claim with no line of the text behind it",
    ],
    "the BIOGRAPHICAL fallacy": [
        "assuming the narrator's opinions must be the author's own",
        "reading every first-person poem as confession",
    ],
}
_INTERPRETATION_GLOSSES = {
    "an interpretation SUPPORTED by the text": "claim + quotation + reasoning: the full chain",
    "an UNSUPPORTED assertion": "volume is not evidence",
    "the BIOGRAPHICAL fallacy": "the speaker is a made thing — not the maker",
}


def gen_critical_interpretation(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _INTERPRETATION,
                       glosses=_INTERPRETATION_GLOSSES, concept_name="CRITICAL INTERPRETATION")


# ── registries ───────────────────────────────────────────────────────────────

AU_ESSENTIAL_ENGLISH_Y11_GENERATORS: dict[str, GenFn] = {
    "aue11e_workplace_texts": gen_workplace_texts,
    "aue11e_advertising_media": gen_advertising_media,
    "aue11e_instructional_texts": gen_instructional_texts,
}
AU_ESSENTIAL_ENGLISH_Y12_GENERATORS: dict[str, GenFn] = {
    "aue12e_news_perspectives": gen_news_perspectives,
    "aue12e_persuasive_arguments": gen_persuasive_arguments,
    "aue12e_professional_communication": gen_professional_communication,
}
AU_MAINSTREAM_ENGLISH_Y11_GENERATORS: dict[str, GenFn] = {
    "aue11m_perspectives_values": gen_perspectives_values,
    "aue11m_text_structures": gen_text_structures,
    "aue11m_analytical_essays": gen_analytical_essays,
    "aue11m_imaginative_texts": gen_imaginative_texts,
    # absorbed from the retired merged year11_english (ids kept: mastery survives)
    **AU_ENGLISH_YEAR11_GENERATORS,
}
AU_MAINSTREAM_ENGLISH_Y12_GENERATORS: dict[str, GenFn] = {
    "aue12m_comparative_contexts": gen_comparative_contexts,
    "aue12m_media_bias": gen_media_bias,
    "aue12m_comparative_essays": gen_comparative_essays,
    "aue12m_persuasive_essays": gen_persuasive_essays,
    # absorbed from the retired merged year12_english (ids kept: mastery survives)
    **AU_ENGLISH_YEAR12_GENERATORS,
}
AU_LITERATURE_Y11_GENERATORS: dict[str, GenFn] = {
    "aue11l_canonical_literature": gen_canonical_literature,
    "aue11l_poetry_forms": gen_poetry_forms,
    "aue11l_genre_over_time": gen_genre_over_time,
}
AU_LITERATURE_Y12_GENERATORS: dict[str, GenFn] = {
    "aue12l_literary_theories": gen_literary_theories,
    "aue12l_complex_plays": gen_complex_plays,
    "aue12l_critical_interpretation": gen_critical_interpretation,
}
