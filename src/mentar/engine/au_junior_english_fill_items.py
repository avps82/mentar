"""W6 (English half): the Y2-10 English strand fill — one disjoint fact table
per reference strand the auditor named MISSING after W7 tagging."""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is


def _mc(stem, table, glosses, concept):
    def gen(rng: random.Random):
        return mc_which_is(rng, stem, table, glosses=glosses, concept_name=concept)
    return gen


# ── Year 2 ───────────────────────────────────────────────────────────────────

gen_end_marks = _mc("Which of these should end with {label}?", {
    "a FULL STOP": ["The dog is asleep", "We walked to school"],
    "a QUESTION MARK": ["Where is my hat", "What time is lunch"],
    "an EXCLAMATION MARK": ["Watch out for that car", "What an amazing goal"],
}, {
    "a FULL STOP": "a telling sentence ends with a full stop",
    "a QUESTION MARK": "an asking sentence ends with a question mark",
    "an EXCLAMATION MARK": "a strong-feeling sentence ends with an exclamation mark",
}, "ENDING A SENTENCE")

gen_sentence_order = _mc("Which of these is {label}?", {
    "a sentence in the RIGHT order": ["The cat sat on the mat", "My dad cooked dinner tonight"],
    "a MUDDLED sentence": ["mat the sat cat the on", "dinner my cooked tonight dad"],
    "NOT a full sentence": ["the big red", "under the"],
}, {
    "a sentence in the RIGHT order": "the words follow who-did-what order",
    "a MUDDLED sentence": "the same words, wrong order — the meaning is lost",
    "NOT a full sentence": "a piece of a sentence with no action or actor",
}, "BUILDING A SENTENCE")

# ── Year 3 ───────────────────────────────────────────────────────────────────

gen_comprehension_clue = _mc("Which of these is {label}?", {
    "a fact stated RIGHT THERE in the text": ["the story says 'Sam's bike is blue', so the bike is blue", "the report gives the date of the flood in its first line"],
    "something you work out from CLUES": ["Sam shivered and pulled on a coat, so it must be cold", "the empty bowl and happy dog suggest who ate the dinner"],
    "your own OPINION, not the text's": ["thinking the story would be better with a dragon in it", "feeling that the ending was too sad"],
}, {
    "a fact stated RIGHT THERE in the text": "point at the line — it says it",
    "something you work out from CLUES": "the text hints; the reader adds it up",
    "your own OPINION, not the text's": "fine to have — but it is not evidence",
}, "READING FOR MEANING")

gen_speech_marks = _mc("Which of these is {label}?", {
    "speech marks used CORRECTLY": ["“Wait for me,” called Ben.", "Mia said, “It's my turn now.”"],
    "MISSING its speech marks": ["Wait for me, called Ben.", "Mia said, it's my turn now."],
    "a sentence with NO speech in it": ["Ben ran to catch the bus."],
}, {
    "speech marks used CORRECTLY": "the spoken words sit inside the quotation marks",
    "MISSING its speech marks": "spoken words need their marks",
    "a sentence with NO speech in it": "nobody speaks, so no marks are needed",
}, "SPEECH MARKS")

gen_reading_fluency = _mc("Which of these is {label}?", {
    "reading with GOOD fluency": ["reading smoothly, in phrases, with expression",
                                  "pausing at the commas and stopping at the full stops"],
    "reading WITHOUT fluency": ["reading word... by... word... in a flat voice",
                                "rushing past every full stop without a break"],
    "a way to IMPROVE fluency": ["re-reading a favourite page until it flows"],
}, {
    "reading with GOOD fluency": "sounds like talking — smooth and expressive",
    "reading WITHOUT fluency": "choppy or flat reading makes meaning hard to hold",
    "a way to IMPROVE fluency": "practice on familiar text builds the flow",
}, "READING FLUENCY")

gen_text_purpose = _mc("Which of these is {label}?", {
    "how a STORY usually begins": ["introducing a character and a place — 'Once, in a small town...'", "setting the scene before any trouble starts"],
    "how a RECIPE is organised": ["a list of what you need, then numbered steps", "ingredients first, method second, always in doing order"],
    "how a REPORT is organised": ["facts sorted under headings", "an opening definition, then grouped information"],
}, {
    "how a STORY usually begins": "orientation first: who, where, when",
    "how a RECIPE is organised": "ingredients, then method — always that order",
    "how a REPORT is organised": "information grouped by topic, not by time",
}, "HOW TEXTS ARE BUILT")

# ── Year 4 ───────────────────────────────────────────────────────────────────

gen_main_idea = _mc("Which of these is {label}?", {
    "the MAIN IDEA of a paragraph": ["the one big point the whole paragraph keeps coming back to", "what you would keep if you could keep only one sentence"],
    "a SUPPORTING detail": ["one example or fact that backs the big point up", "a statistic that proves the paragraph's point"],
    "an OFF-TOPIC sentence": ["a line about lunch in a paragraph about volcanoes", "a joke about the weekend inside instructions for a science experiment"],
}, {
    "the MAIN IDEA of a paragraph": "cover the paragraph and say it in one sentence",
    "a SUPPORTING detail": "evidence in service of the main idea",
    "an OFF-TOPIC sentence": "it belongs in a different paragraph",
}, "MAIN IDEA AND DETAILS")

gen_presenting = _mc("Which of these is {label}?", {
    "GOOD presenting to the class": ["facing the audience and speaking up",
                                     "using pauses so listeners can keep up"],
    "GOOD listening in the audience": ["watching the speaker and saving questions for the end"],
    "a presenting HABIT to avoid": ["mumbling at the floor", "reading in a flat rush to finish"],
}, {
    "GOOD presenting to the class": "eyes up, voice out, pace steady",
    "GOOD listening in the audience": "attention is the audience's half of the job",
    "a presenting HABIT to avoid": "the audience loses what it cannot hear",
}, "PRESENTING AND LISTENING")

gen_visual_literacy = _mc("Which of these is {label}?", {
    "what a PHOTOGRAPH adds to a report": ["showing exactly what the subject looks like", "proof that the event really happened"],
    "what a DIAGRAM with labels adds": ["naming each part and where it belongs", "showing the inside of something a camera cannot see"],
    "what a MAP adds": ["showing where places sit compared to each other", "the route from one place to another at a glance"],
}, {
    "what a PHOTOGRAPH adds to a report": "true-to-life detail words can't match",
    "what a DIAGRAM with labels adds": "the parts and their names, at a glance",
    "what a MAP adds": "position and distance, drawn to be read",
}, "PICTURES THAT CARRY MEANING")

gen_paragraphs = _mc("Which of these is {label}?", {
    "when to START a new paragraph": ["when the topic changes", "when a new person starts speaking"],
    "a good TOPIC sentence": ["a first sentence that tells what the paragraph is about", "an opening line that promises what the paragraph will show"],
    "a paragraph problem": ["one giant paragraph holding five different topics", "a new speaker's words buried mid-paragraph"],
}, {
    "when to START a new paragraph": "new idea, new paragraph",
    "a good TOPIC sentence": "the paragraph's promise, up front",
    "a paragraph problem": "readers need the breaks to follow the turns",
}, "PARAGRAPHS")

# ── Year 5 ───────────────────────────────────────────────────────────────────

gen_persuasive_starters = _mc("Which of these is {label}?", {
    "a PERSUASIVE opening": ["“Every student deserves a safe ride to school — here is why.”", "“Imagine arriving to find the library gone. That is the plan on the table.”"],
    "a PERSUASIVE connective": ["“furthermore”, linking one argument to the next",
                                "“on the other hand”, admitting the other side before answering it"],
    "an INFORMATIVE (not persuasive) line": ["“The school has 400 students and 12 classrooms.”", "“The canteen opens at half past ten.”"],
}, {
    "a PERSUASIVE opening": "states the position and promises reasons",
    "a PERSUASIVE connective": "the glue that marches arguments forward",
    "an INFORMATIVE (not persuasive) line": "facts alone push no one — persuasion adds the 'should'",
}, "PERSUASIVE WRITING MOVES")

gen_commas = _mc("Which of these is {label}?", {
    "a comma used CORRECTLY in a list": ["We packed hats, snacks, water and a map.", "The stall sold apples, pears, plums and grapes."],
    "a comma used CORRECTLY after an opener": ["After the storm, the street was covered in leaves.", "Before the bell, everyone lined up outside."],
    "a sentence MISSING a needed comma": ["We packed hats snacks water and a map.", "After the storm the street was a mess of branches leaves and mud."],
}, {
    "a comma used CORRECTLY in a list": "commas keep list items apart",
    "a comma used CORRECTLY after an opener": "a comma marks the pause after a starter phrase",
    "a sentence MISSING a needed comma": "read it aloud — the pile-up shows where the comma goes",
}, "COMMAS")

gen_skimming_scanning = _mc("Which of these is {label}?", {
    "SKIMMING a text": ["running your eyes over headings to get the gist", "flipping through a chapter to see what it covers"],
    "SCANNING a text": ["hunting for one date or name without reading everything", "running a finger down a timetable for the 3 o'clock bus"],
    "CLOSE reading": ["reading every sentence carefully to study the meaning", "re-reading a stanza to weigh each word choice"],
}, {
    "SKIMMING a text": "fast overview: what is this about?",
    "SCANNING a text": "fast search: where is that one detail?",
    "CLOSE reading": "slow and careful: how does this work?",
}, "WAYS OF READING")

# ── Year 6 ───────────────────────────────────────────────────────────────────

gen_editing = _mc("Which of these is {label}?", {
    "an EDITING fix (meaning and flow)": ["cutting a sentence that repeats the one before it",
                                          "swapping a tired word for a sharper one"],
    "a PROOFREADING fix (surface errors)": ["correcting a spelling mistake",
                                            "adding the missing capital to a name"],
    "a REDRAFTING move (big changes)": ["reordering paragraphs so the argument builds"],
}, {
    "an EDITING fix (meaning and flow)": "making it clearer and tighter",
    "a PROOFREADING fix (surface errors)": "the final polish pass",
    "a REDRAFTING move (big changes)": "structure first, sentences second, spelling last",
}, "EDITING YOUR WRITING")

gen_media_literacy_y6 = _mc("Which of these is {label}?", {
    "an ADVERTISEMENT'S job": ["to make you want to buy or do something", "to make its product look like the obvious choice"],
    "a NEWS report's job": ["to tell you what happened, when and where", "to answer who, what, when, where and why"],
    "a sign an ad is at WORK on you": ["a toy filmed to look far bigger than it is",
                                       "“hurry — offer ends today!” pressure"],
}, {
    "an ADVERTISEMENT'S job": "someone pays for it to change your behaviour",
    "a NEWS report's job": "information first; check it still for fairness",
    "a sign an ad is at WORK on you": "spot the trick and the spell weakens",
}, "READING THE MEDIA")

gen_discussion_skills = _mc("Which of these is {label}?", {
    "BUILDING on another's idea": ["“Adding to what Priya said, we could also...”", "“That connects with the point about the ending, because...”"],
    "DISAGREEING respectfully": ["“I see it differently, because...”", "“That's a fair point, but the text also says...”"],
    "DERAILING a discussion": ["talking over the speaker to change the subject", "bringing up the weekend in a discussion about the novel"],
}, {
    "BUILDING on another's idea": "discussion grows by addition",
    "DISAGREEING respectfully": "attack the idea, never the person",
    "DERAILING a discussion": "it costs the group the thread of thought",
}, "CLASS DISCUSSION SKILLS")

gen_writing_style = _mc("Which of these is {label}?", {
    "a SHOW-don't-tell sentence": ["“Her hands trembled as she reached for the letter.”", "“He checked the clock for the third time in a minute.”"],
    "a TELLING sentence": ["“She was nervous.”", "“He was impatient.”"],
    "a way to VARY sentences": ["following a long flowing sentence with a short sharp one", "opening one sentence with a verb and the next with a place"],
}, {
    "a SHOW-don't-tell sentence": "the reader feels it without being told",
    "a TELLING sentence": "quick and plain — fine sometimes, flat always",
    "a way to VARY sentences": "rhythm keeps readers awake",
}, "WRITING STYLE")

# ── Year 7 ───────────────────────────────────────────────────────────────────

gen_apostrophes = _mc("Which of these is {label}?", {
    "an apostrophe of POSSESSION used correctly": ["the dog's collar (one dog)",
                                                   "the players' rooms (many players)"],
    "an apostrophe in a CONTRACTION": ["don't, standing for 'do not'", "it's, standing for 'it is'"],
    "an apostrophe ERROR": ["apple's for sale (just a plural, no apostrophe needed)",
                            "its' — never a correct form"],
}, {
    "an apostrophe of POSSESSION used correctly": "owner + apostrophe: singular 's, plural s'",
    "an apostrophe in a CONTRACTION": "the apostrophe marks the missing letters",
    "an apostrophe ERROR": "plurals never take an apostrophe",
}, "APOSTROPHES")

# ── Year 8 ───────────────────────────────────────────────────────────────────

gen_digital_literacy = _mc("Which of these is {label}?", {
    "a sign a website is TRUSTWORTHY": ["it names its author and cites its sources",
                                        "a well-known institution stands behind it"],
    "a sign to be SUSPICIOUS": ["no author, no date, no sources anywhere",
                                "a headline engineered to make you furious"],
    "a smart CHECKING habit": ["opening a second source to compare the claim"],
}, {
    "a sign a website is TRUSTWORTHY": "accountability: someone owns the words",
    "a sign to be SUSPICIOUS": "anonymity plus outrage is a red flag",
    "a smart CHECKING habit": "lateral reading beats staring harder at one page",
}, "JUDGING ONLINE SOURCES")

gen_persuasive_structure = _mc("Which of these is {label}?", {
    "a strong persuasive OPENING": ["a bold statement of position with the stakes made plain", "a hook that makes the reader care in the first line"],
    "a strong persuasive MIDDLE": ["one argument per paragraph, each backed with evidence", "answering the other side's best objection head-on"],
    "a strong persuasive ENDING": ["restating the position and calling for action", "leaving the reader with one line they will remember"],
}, {
    "a strong persuasive OPENING": "position first: the reader should never wonder where you stand",
    "a strong persuasive MIDDLE": "argument + evidence, repeated in disciplined paragraphs",
    "a strong persuasive ENDING": "close the loop and say what should happen next",
}, "SHAPE OF A PERSUASIVE TEXT")

gen_speech_delivery = _mc("Which of these is {label}?", {
    "strong speech DELIVERY": ["pausing after the key line so it lands",
                               "making eye contact around the whole room"],
    "strong speech LANGUAGE": ["the rule of three: 'cheaper, cleaner, fairer'",
                               "a rhetorical question that pulls listeners in"],
    "a delivery HABIT that weakens a speech": ["reading every word off the page in a monotone"],
}, {
    "strong speech DELIVERY": "voice and body carry half the argument",
    "strong speech LANGUAGE": "patterns of words built for the ear",
    "a delivery HABIT that weakens a speech": "an audience follows energy",
}, "DELIVERING A SPEECH")

# ── Year 9 ───────────────────────────────────────────────────────────────────

gen_comparing_texts = _mc("Which of these is {label}?", {
    "a COMPARISON of two texts": ["“both poems treat the war as a betrayal of the young”", "noting that both speeches lean on the same appeal to fear"],
    "a CONTRAST between two texts": ["“where the film ends in rescue, the novel refuses one”", "showing one poem celebrates what the other mourns"],
    "a claim about ONE text only": ["“the novel's narrator hides the truth until the last page”", "observing that the play opens with a storm"],
}, {
    "a COMPARISON of two texts": "a likeness held across both texts at once",
    "a CONTRAST between two texts": "a difference made meaningful",
    "a claim about ONE text only": "true perhaps — but it compares nothing",
}, "COMPARING TEXTS")

gen_shakespeare_poetry = _mc("Which of these is {label}?", {
    "true of a Shakespearean SONNET": ["fourteen lines ending in a rhyming couplet", "three quatrains that build to a final two-line turn"],
    "true of IAMBIC rhythm": ["ten syllables to a line: da-DUM da-DUM da-DUM da-DUM da-DUM", "an unstressed beat then a stressed one, five times a line"],
    "true of Shakespeare's THEATRE": ["plays staged in daylight at the open-roofed Globe", "audiences standing in the yard around the stage"],
}, {
    "true of a Shakespearean SONNET": "three quatrains build; the couplet turns the key",
    "true of IAMBIC rhythm": "the heartbeat metre of English verse",
    "true of Shakespeare's THEATRE": "no lighting rig, no scenery — the words did the work",
}, "SHAKESPEARE AND POETRY")

# ── Year 10 ──────────────────────────────────────────────────────────────────

gen_reviewing_refining = _mc("Which of these is {label}?", {
    "a REVISION that sharpens an argument": ["moving the strongest point from the middle to the front", "cutting a paragraph that repeats an earlier one"],
    "a REFINEMENT at sentence level": ["cutting 'in my opinion I think that' down to one claim", "replacing a vague 'very good' with a precise word"],
    "useful FEEDBACK to act on": ["“your evidence is strong but I lost your thread in paragraph three”"],
}, {
    "a REVISION that sharpens an argument": "revision reorders thinking, not just words",
    "a REFINEMENT at sentence level": "every needless word costs attention",
    "useful FEEDBACK to act on": "specific, kind, actionable — the only kind worth giving",
}, "REVIEWING AND REFINING")


AU_JUNIOR_ENGLISH_FILL: dict[int, dict[str, tuple[GenFn, str, str]]] = {
    2: {
        "aue2_end_marks": (gen_end_marks, "Punctuation", "Ending a sentence"),
        "aue2_sentence_order": (gen_sentence_order, "Writing", "Building a sentence"),
    },
    3: {
        "aue3_comprehension_clue": (gen_comprehension_clue, "Comprehension", "Reading for meaning"),
        "aue3_speech_marks": (gen_speech_marks, "Punctuation", "Speech marks"),
        "aue3_reading_fluency": (gen_reading_fluency, "Reading fluency", "Reading fluency"),
        "aue3_text_purpose": (gen_text_purpose, "Text structure", "How texts are built"),
    },
    4: {
        "aue4_main_idea": (gen_main_idea, "Comprehension", "Main idea and details"),
        "aue4_presenting": (gen_presenting, "Speaking and listening", "Presenting and listening"),
        "aue4_visual_literacy": (gen_visual_literacy, "Visual literacy", "Pictures that carry meaning"),
        "aue4_paragraphs": (gen_paragraphs, "Writing", "Paragraphs"),
    },
    5: {
        "aue5_persuasive_starters": (gen_persuasive_starters, "Persuasive writing", "Persuasive writing moves"),
        "aue5_commas": (gen_commas, "Punctuation", "Commas"),
        "aue5_skimming_scanning": (gen_skimming_scanning, "Reading", "Ways of reading"),
    },
    6: {
        "aue6_editing": (gen_editing, "Editing", "Editing your writing"),
        "aue6_media_literacy": (gen_media_literacy_y6, "Media literacy", "Reading the media"),
        "aue6_discussion_skills": (gen_discussion_skills, "Speaking and listening", "Class discussion skills"),
        "aue6_writing_style": (gen_writing_style, "Writing style", "Writing style"),
    },
    7: {
        "aue7_apostrophes": (gen_apostrophes, "Punctuation", "Apostrophes"),
    },
    8: {
        "aue8_digital_literacy": (gen_digital_literacy, "Digital literacy", "Judging online sources"),
        "aue8_persuasive_structure": (gen_persuasive_structure, "Persuasive writing", "Shape of a persuasive text"),
        "aue8_speech_delivery": (gen_speech_delivery, "Speaking", "Delivering a speech"),
    },
    9: {
        "aue9_comparing_texts": (gen_comparing_texts, "Comparative reading", "Comparing texts"),
        "aue9_shakespeare_poetry": (gen_shakespeare_poetry, "Poetry and Shakespeare", "Shakespeare and poetry"),
    },
    10: {
        "aue10_reviewing_refining": (gen_reviewing_refining, "Reviewing and refining", "Reviewing and refining"),
    },
}
