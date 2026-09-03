---
type: Mentar Curriculum Template
title: "English — Class 3 (India, general)"
tags: [IN, english, "Class 3", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 3 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what India teaches in Class 3.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.
#
# 2026-08-14: this file closes a HOLE, not a new level. Every other India level
# (Class 2, 4-8) shipped both maths and English in the 2026-08-11 wave; Class 3
# had maths only, because its maths pack predates the shared stage table and
# lives on the legacy `in_generic_maths` item source (class3_maths.md), so no
# in_c3 level existed in PACK_LEVELS for English to hang off.

template_id: in-c3-english
country: IN
year_level: "Class 3"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 3 (general)"
icon: "📖"
description: "Antonyms, prefixes, homophones and comparative adjectives — general English at roughly Class 3 level."
item_source: in_c3_english

language_register:
  reading_level: "~ages 7-9"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# stage-3 generator set every other generic pack's Stage 3 level uses
# (engine/generic_english_items.py::STAGE_CONCEPTS[3]), so behaviour and word
# tables are already tested/verified there.
concepts:

  - id: in_c3_antonyms
    label: "Antonyms (opposite words)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'day'? A) full  B) slow  C) dry  D) night. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c3_prefixes
    label: "Word prefixes (un-, re-, dis-)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words begins with the prefix un- (not / opposite)? A) unhappy  B) replay  C) dislike  D) return. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c3_homophones
    label: "Homophones (their/there, to/too)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means 'in this place'? A) here  B) hear  C) there  D) too. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c3_adjectives_comparative
    label: "Comparative and superlative adjectives"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a comparative adjective (comparing TWO things)? A) biggest  B) bigger  C) smallest  D) tallest. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 3 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Class 3 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c3_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
