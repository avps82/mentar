---
type: Mentar Curriculum Template
title: "Maths — Year 7 (AU)"
tags: [AU, mathematics, "Year 7"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 7 Mathematics (Number + Algebra strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR7_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year7-maths
country: AU
year_level: "Year 7"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M7 Number, Algebra)"
schema_version: "0.1"
label: "Maths — Year 7 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Integers, order of operations, unlike-denominator fractions, one-step equations and multiplying decimals (Australian Year 7)."
item_source: au_year7

language_register:
  reading_level: "~Year 7 / ages 12-13"
  vocabulary_note: "Clear sentences. Plain number words. One idea per question."

# 5 independent nodes (separate strands, no natural prereq chain at this level):
# integers, order of operations, unlike-denominator fractions, one-step equations,
# multiplying decimals. R15's first use of negative-integer content + the pilot's
# first "solve for x" node (still verifier-native: the answer is just an int).
concepts:

  - id: au7_integers_add_sub
    label: "Adding and subtracting integers"             # AC9M7N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is -8 - 3?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_order_of_ops_negatives
    label: "Order of operations with negative numbers"   # AC9M7N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is -6 + 16 ÷ 8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_unlike_denom_fractions
    label: "Adding fractions with different denominators"  # AC9M7N04
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 1/3 + 1/4?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_one_step_equations
    label: "Solving one-step equations"                  # AC9M7A02
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If x + 5 = 12, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_mult_decimal_by_decimal
    label: "Multiplying decimals"                        # AC9M7N06
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 4.1 × 2.3?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 7 Mathematics (Number, Algebra)

ACARA v9 Number + Algebra strands, Year 7 — sibling of `year2_maths.md`–`year6_maths.md` in
the per-country/per-year pattern (SPEC §6). Parametric generators only
(`engine/au_items.py`); the deterministic verifier scores every answer. First use of
negative-integer content and the pilot's first "solve for x" node — still verifier-native,
the answer is just an integer.

**Alignment note:** the AC9M7Nxx/AC9M7Axx codes in the node comments are references to ACARA
v9 content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
