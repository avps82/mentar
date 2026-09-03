---
type: Mentar Curriculum Template
title: "Maths — Class 3 (IN generic)"
tags: [IN, mathematics, "Class 3"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — India, generic (board-agnostic) Class 3 Maths.
# NOT tied to NCERT, CBSE, ICSE, or any specific state board -- NCERT's e-content
# licence was found to prohibit adaptation/derivation (docs/CONTENT_LICENSES.md §2b),
# so this pack deliberately claims NO curriculum alignment. Universally-taught topics
# only, reusing existing generic generators (engine/in_generic_items.py) -- see that
# module's docstring for exactly which functions are reused, unmodified.

template_id: in-generic-class3-maths
country: IN
year_level: "Class 3"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Maths — Class 3 (general)"                # R3.1: web picker catalog fields
icon: "🔢"
description: "Place value, adding, times tables and fractions -- general topics, not tied to any specific board."
item_source: in_generic_maths

language_register:
  reading_level: "~Class 3 / ages 8-9"
  vocabulary_note: "Short sentences. Plain number words."

# 4 independent drill nodes -- no prerequisites, each a standalone practice skill.
concepts:

  - id: in_generic_addition
    label: "Addition (2-digit numbers)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 47 + 36?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_generic_subtraction
    label: "Subtraction (2-digit numbers)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 82 − 45?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_generic_times_tables
    label: "Times tables (1-12)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 6 × 7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_generic_unit_fractions
    label: "Unit fractions (1/n)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A chocolate bar 🍫 is split into 8 equal parts. What fraction is ONE part?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — General Class 3 Maths (evergreen, board-agnostic)

A generic Class 3 maths pack for families in India whose child's school follows any
board -- deliberately NOT aligned to NCERT, CBSE, ICSE, or a specific state board (see
`docs/CONTENT_LICENSES.md` §2b for why). Every item is parametrically generated and
scored by the deterministic verifier; the LLM never decides correctness. Ships in-repo
like every other pack; a family turns it on/off from Settings (R10) rather than
downloading it.
