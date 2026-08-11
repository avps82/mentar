---
type: Mentar Curriculum Template
title: "English — Grade 7 (United States, general)"
tags: [US, english, "Grade 7", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 7 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what United States teaches in Grade 7.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g7-english
country: US
year_level: "Grade 7"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Grade 7 🇺🇸 (general)"
icon: "7️⃣"
description: "Idioms, formal/informal register, active/passive voice and personification — general English at roughly Grade 7 level."
item_source: us_g7_english

language_register:
  reading_level: "~ages 11-13"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year7_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: us_g7_idioms
    label: "Idioms"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an idiom (doesn't mean what the words literally say)? A) it's raining cats and dogs  B) it's raining heavily outside  C) good luck with the show  D) I feel sick today. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g7_formal_informal
    label: "Formal and informal language"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is formal language? A) purchase  B) buy  C) start  D) help. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g7_active_passive
    label: "Active and passive voice"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is passive voice (the subject RECEIVES the action)? A) the dog chased the cat  B) the cat was chased by the dog  C) she wrote the letter  D) they built the house. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g7_personification
    label: "Personification"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is personification (giving human qualities to something non-human)? A) the wind whispered through the trees  B) the wind blew through the trees  C) the sun shone down on us  D) time passed by quickly. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 7 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Grade 7 difficulty,
with **no claimed alignment** to any curriculum authority. Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g7_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
