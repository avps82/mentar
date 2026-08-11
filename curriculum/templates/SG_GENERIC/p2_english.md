---
type: Mentar Curriculum Template
title: "English — Primary 2 (Singapore, general)"
tags: [SG, english, "Primary 2", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 2 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught English at roughly
# this difficulty, 100% Mentar-authored/reused-generic (engine/au_english_items.py's
# generator functions, already tested and shipped as AU content — same word-table
# generator shape, no new item logic); the level name is a display label, not a
# claim about what Singapore teaches in Primary 2.
# Items come from shared parametric generators (engine/generic_english_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-p2-english
country: SG
year_level: "Primary 2"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Primary 2 🇸🇬 (general)"
icon: "2️⃣"
description: "Word classes, synonyms, plurals and rhyming words — general English at roughly Primary 2 level."
item_source: sg_p2_english

language_register:
  reading_level: "~ages 6-8"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper, reusing the exact
# generator functions AU_ACARA/year2_english.md ships (engine/au_english_items.py),
# so behaviour and word tables are already tested/verified there.
concepts:

  - id: sg_p2_word_classes
    label: "Naming, doing and describing words"                                       # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a naming word (noun)? A) run  B) dog  C) happy  D) jump. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p2_synonyms
    label: "Simple synonyms"                                       # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'happy'? A) glad  B) run  C) box  D) tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p2_plurals
    label: "Plural forms"                                       # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is the plural of 'child'? A) childs  B) children  C) childes  D) child. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p2_rhyming
    label: "Rhyming words"                                       # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word rhymes with 'pig'? A) big  B) cat  C) run  D) sun. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 2 English (generic)

A board-agnostic English pack: universally-taught topics at roughly Primary 2 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p2_` and the item generators are shared across every
generic pack (`engine/generic_english_items.py` — one concept-progression table, reused
`engine/au_english_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
