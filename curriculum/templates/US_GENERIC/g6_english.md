---
type: Mentar Curriculum Template
title: "English — Grade 6 (United States, general)"
tags: [US, english, "Grade 6", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 6 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what United States teaches in Grade 6.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g6-english
country: US
year_level: "Grade 6"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Grade 6 🇺🇸 (general)"
icon: "📖"
description: "Similes and metaphors, nuanced synonyms/antonyms, conjunctions and prepositions — general English at roughly Grade 6 level."
item_source: us_g6_english

language_register:
  reading_level: "~ages 10-12"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year6_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: us_g6_figurative_language
    label: "Similes and metaphors"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a simile (uses 'like' or 'as')? A) as brave as a lion  B) time is money  C) her heart is a stone  D) the world is a stage. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_synonyms_nuanced
    label: "Synonyms (nuanced vocabulary)"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'meticulous'? A) precise  B) hesitant  C) unwilling  D) honest. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_antonyms_nuanced
    label: "Antonyms (nuanced vocabulary)"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'transparent'? A) rigid  B) opaque  C) verbose  D) compulsory. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_conjunctions_prepositions
    label: "Conjunctions and prepositions"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a preposition (shows position or time)? A) between  B) but  C) and  D) although. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 6 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Grade 6 difficulty,
with **no claimed alignment** to any curriculum authority. Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g6_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
