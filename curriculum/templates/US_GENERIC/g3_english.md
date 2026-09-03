---
type: Mentar Curriculum Template
title: "English — Grade 3 (United States, general)"
tags: [US, english, "Grade 3", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 3 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what United States teaches in Grade 3.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g3-english
country: US
year_level: "Grade 3"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Grade 3 (general)"
icon: "📖"
description: "Antonyms, prefixes, homophones and comparative adjectives — general English at roughly Grade 3 level."
item_source: us_g3_english

language_register:
  reading_level: "~ages 7-9"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year3_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: us_g3_antonyms
    label: "Antonyms (opposite words)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'day'? A) slow  B) dry  C) night  D) closed. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g3_prefixes
    label: "Word prefixes (un-, re-, dis-)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words begins with the prefix un- (not / opposite)? A) unhappy  B) replay  C) dislike  D) return. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g3_homophones
    label: "Homophones (their/there, to/too)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means 'in this place'? A) here  B) hear  C) there  D) too. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g3_adjectives_comparative
    label: "Comparative and superlative adjectives"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a superlative adjective (comparing THREE OR MORE things)? A) bigger  B) faster  C) taller  D) smallest. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 3 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Grade 3 difficulty,
with **no claimed alignment** to any curriculum authority. Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g3_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
