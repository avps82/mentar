---
type: Mentar Curriculum Template
title: "Maths — Class 7 (India, general)"
tags: [IN, mathematics, "Class 7", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — India, Class 7 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what India teaches in Class 7.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: in-c7-maths
country: IN
year_level: "Class 7"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 7 (general)"
icon: "🔢"
description: "Adding and subtracting integers, order of operations with negatives, adding fractions (different denominators) and more — general maths at roughly Class 7 level."
item_source: in_c7_maths

language_register:
  reading_level: "~ages 11-12"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: in_c7_integers_add_sub
    label: "Adding and subtracting integers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 15 + -7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_order_of_ops_negatives
    label: "Order of operations with negatives"
    prereqs: [in_c7_integers_add_sub]
    grounding: {}
    transfer_seeds:
      - "What is -17 + 54 ÷ 6?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_unlike_denom_fractions
    label: "Adding fractions (different denominators)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3/5 + 3/2?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_one_step_equations
    label: "One-step equations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If x + 15 = 27, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_mult_decimal_by_decimal
    label: "Multiplying a decimal by a decimal"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 2.5 × 4.9?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 7 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Class 7 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c7_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
