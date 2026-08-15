---
type: Mentar Curriculum Template
title: "English — Primary 4 (Singapore, general)"
tags: [SG, english, "Primary 4", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 4 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what Singapore teaches in Primary 4.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-p4-english
country: SG
year_level: "Primary 4"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Primary 4 🇸🇬 (general)"
icon: "📖"
description: "Suffixes, contractions, proper nouns and similes — general English at roughly Primary 4 level."
item_source: sg_p4_english

language_register:
  reading_level: "~ages 8-10"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year4_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: sg_p4_suffixes
    label: "Word suffixes (-ful, -less, -ness)"                                       # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words ends with the suffix -ness (a state of being)? A) happiness  B) careful  C) careless  D) joyful. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p4_contractions
    label: "Contractions (don't, can't, it's)"                                       # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which is the SHORT form (contraction) of 'do not'? A) don't  B) can't  C) it's  D) won't. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p4_proper_nouns
    label: "Common and proper nouns"                                       # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a proper noun (needs a capital letter)? A) Australia  B) city  C) river  D) school. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p4_similes
    label: "Similes (using 'like' or 'as')"                                       # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a simile (uses 'like' or 'as' to compare)? A) ran like the wind  B) the dog ran fast  C) she sang a song  D) he was very brave. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 4 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Primary 4 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p4_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
