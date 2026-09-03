---
type: Mentar Curriculum Template
title: "English — Primary 3 (Singapore, general)"
tags: [SG, english, "Primary 3", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 3 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what Singapore teaches in Primary 3.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-p3-english
country: SG
year_level: "Primary 3"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Primary 3 (general)"
icon: "📖"
description: "Antonyms, prefixes, homophones and comparative adjectives — general English at roughly Primary 3 level."
item_source: sg_p3_english

language_register:
  reading_level: "~ages 7-9"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year3_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: sg_p3_antonyms
    label: "Antonyms (opposite words)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'fast'? A) night  B) slow  C) full  D) dry. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_prefixes
    label: "Word prefixes (un-, re-, dis-)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words begins with the prefix un- (not / opposite)? A) unhappy  B) replay  C) dislike  D) return. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_homophones
    label: "Homophones (their/there, to/too)"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means 'in this place'? A) here  B) hear  C) there  D) too. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_adjectives_comparative
    label: "Comparative and superlative adjectives"                                       # AC9E3A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a superlative adjective (comparing THREE OR MORE things)? A) fastest  B) smaller  C) faster  D) bigger. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 3 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Primary 3 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p3_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
