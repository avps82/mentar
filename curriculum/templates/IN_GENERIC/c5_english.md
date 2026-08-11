---
type: Mentar Curriculum Template
title: "English — Class 5 (India, general)"
tags: [IN, english, "Class 5", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — India, Class 5 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what India teaches in Class 5.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c5-english
country: IN
year_level: "Class 5"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 5 🇮🇳 (general)"
icon: "5️⃣"
description: "Richer synonyms/antonyms, adverbs/pronouns and compound words — general English at roughly Class 5 level."
item_source: in_c5_english

language_register:
  reading_level: "~ages 9-11"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year5_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: in_c5_synonyms_advanced
    label: "Synonyms (richer vocabulary)"                                       # AC9E5A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'enormous'? A) huge  B) tiny  C) quiet  D) fast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c5_antonyms_advanced
    label: "Antonyms (richer vocabulary)"                                       # AC9E5A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'generous'? A) stingy  B) kind  C) rich  D) happy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c5_word_classes_advanced
    label: "Adverbs, pronouns and verbs"                                       # AC9E5A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an adverb (describes HOW something is done)? A) quickly  B) she  C) walk  D) happy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c5_compound_words
    label: "Compound words"                                       # AC9E5A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these IS a real compound word? A) sunflower  B) moonbrush  C) chairwater  D) tablesong. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 5 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Class 5 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c5_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
