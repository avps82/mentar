---
type: Mentar Curriculum Template
title: "English — Grade 8 (United States, general)"
tags: [US, english, "Grade 8", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 8 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what United States teaches in Grade 8.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g8-english
country: US
year_level: "Grade 8"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Grade 8 🇺🇸 (general)"
icon: "8️⃣"
description: "Connotation, clauses, adverbial phrases and onomatopoeia — general English at roughly Grade 8 level."
item_source: us_g8_english

language_register:
  reading_level: "~ages 12-14"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year8_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: us_g8_connotation
    label: "Word connotation (positive/negative)"                                       # AC9E8A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word with a NEGATIVE connotation? A) skinny  B) slender  C) confident  D) curious. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_clauses
    label: "Main and subordinate clauses"                                       # AC9E8A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a subordinate clause (cannot stand alone)? A) she went to the store  B) because she was hungry  C) the dog barked loudly  D) he plays the guitar. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_adverbial_phrases
    label: "Adverbial phrases"                                       # AC9E8A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an adverbial phrase (tells HOW, WHEN or WHERE)? A) in the morning  B) my best friend  C) a beautiful sunset  D) the old oak tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_onomatopoeia
    label: "Onomatopoeia"                                       # AC9E8A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is onomatopoeia (a word that sounds like what it means)? A) buzz  B) loud  C) sudden  D) fast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 8 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Grade 8 difficulty,
with **no claimed alignment** to any curriculum authority. Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g8_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
