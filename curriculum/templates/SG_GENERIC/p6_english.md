---
type: Mentar Curriculum Template
title: "English — Primary 6 (Singapore, general)"
tags: [SG, english, "Primary 6", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 6 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what Singapore teaches in Primary 6.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-p6-english
country: SG
year_level: "Primary 6"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Primary 6 (general)"
icon: "📖"
description: "Similes and metaphors, nuanced synonyms/antonyms, conjunctions and prepositions — general English at roughly Primary 6 level."
item_source: sg_p6_english

language_register:
  reading_level: "~ages 10-12"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year6_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: sg_p6_figurative_language
    label: "Similes and metaphors"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a simile (uses 'like' or 'as')? A) as brave as a lion  B) time is money  C) her heart is a stone  D) the world is a stage. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_synonyms_nuanced
    label: "Synonyms (nuanced vocabulary)"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'candid'? A) adaptable  B) thorough  C) precise  D) honest. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_antonyms_nuanced
    label: "Antonyms (nuanced vocabulary)"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'concise'? A) opaque  B) rigid  C) verbose  D) compulsory. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_conjunctions_prepositions
    label: "Conjunctions and prepositions"                                       # AC9E6A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a conjunction (joins two ideas)? A) before  B) during  C) under  D) but. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 6 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Primary 6 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p6_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
