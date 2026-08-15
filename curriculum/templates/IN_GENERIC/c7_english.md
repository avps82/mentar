---
type: Mentar Curriculum Template
title: "English — Class 7 (India, general)"
tags: [IN, english, "Class 7", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — India, Class 7 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what India teaches in Class 7.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c7-english
country: IN
year_level: "Class 7"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 7 🇮🇳 (general)"
icon: "📖"
description: "Idioms, formal/informal register, active/passive voice and personification — general English at roughly Class 7 level."
item_source: in_c7_english

language_register:
  reading_level: "~ages 11-13"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year7_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: in_c7_idioms
    label: "Idioms"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an idiom (doesn't mean what the words literally say)? A) it's raining cats and dogs  B) it's raining heavily outside  C) good luck with the show  D) I feel sick today. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_formal_informal
    label: "Formal and informal language"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is formal language? A) purchase  B) buy  C) start  D) help. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_active_passive
    label: "Active and passive voice"                                       # AC9E7A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is passive voice (the subject RECEIVES the action)? A) the dog chased the cat  B) the cat was chased by the dog  C) she wrote the letter  D) they built the house. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_personification
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

# India — Class 7 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Class 7 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c7_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
