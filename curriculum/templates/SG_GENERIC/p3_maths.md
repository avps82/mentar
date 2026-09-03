---
type: Mentar Curriculum Template
title: "Maths — Primary 3 (Singapore, general)"
tags: [SG, mathematics, "Primary 3", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 3 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what Singapore teaches in Primary 3.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: sg-p3-maths
country: SG
year_level: "Primary 3"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Primary 3 (general)"
icon: "🔢"
description: "Place value, adding numbers, subtracting numbers and more — general maths at roughly Primary 3 level."
item_source: sg_p3_maths

language_register:
  reading_level: "~ages 7-8"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: sg_p3_place_value
    label: "Place value"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 124, what is the value of the digit 2? A) 2  B) 20  C) 200  D) 100. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_addition
    label: "Adding numbers"
    prereqs: [sg_p3_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 664 + 158?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_subtraction
    label: "Subtracting numbers"
    prereqs: [sg_p3_addition]
    grounding: {}
    transfer_seeds:
      - "What is 260 − 194?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_mult_facts
    label: "Times tables"
    prereqs: [sg_p3_addition]
    grounding: {}
    transfer_seeds:
      - "What is 3 × 5?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_unit_fractions
    label: "Unit fractions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A pie 🥧 is split into 3 equal parts. What fraction is ONE part?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p3_fraction_of_whole
    label: "Fractions of a whole"
    prereqs: [sg_p3_unit_fractions]
    grounding: {}
    transfer_seeds:
      - "A pizza is cut into 9 equal slices and you take 1. What fraction did you take?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 3 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Primary 3 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p3_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
