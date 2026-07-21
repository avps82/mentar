---
type: Mentar Curriculum Template
title: "Maths — Year 8 (AU)"
tags: [AU, mathematics, "Year 8"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 8 Mathematics (Number + Algebra strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR8_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year8-maths
country: AU
year_level: "Year 8"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M8 Number, Algebra)"
schema_version: "0.1"
label: "Maths — Year 8 🇦🇺"                          # R3.1: web picker catalog fields
icon: "8️⃣"
description: "Two-step equations, squares, negative-number multiplication, percentage change and dividing decimals (Australian Year 8)."
item_source: au_year8

language_register:
  reading_level: "~Year 8 / ages 13-14"
  vocabulary_note: "Clear sentences. Plain number words. One idea per question."

# 5 independent nodes (separate strands, no natural prereq chain at this level):
# two-step equations, squares, negative multiplication, percentage change, dividing decimals.
concepts:

  - id: au8_two_step_equations
    label: "Solving two-step equations"                  # AC9M8A02
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If 2x + 3 = 11, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_squares
    label: "Squaring numbers"                            # AC9M8N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 6 squared (6²)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_negative_multiplication
    label: "Multiplying negative numbers"                # AC9M8N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is -5 × -10?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_percentage_change
    label: "Percentage increase"                         # AC9M8N03
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A price of $100 increases by 10%. What is the new price?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_div_decimal_by_decimal
    label: "Dividing decimals"                           # AC9M8N05
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 16.32 ÷ 3.4?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 8 Mathematics (Number, Algebra)

ACARA v9 Number + Algebra strands, Year 8 — sibling of `year2_maths.md`–`year7_maths.md` in
the per-country/per-year pattern (SPEC §6). Parametric generators only
(`engine/au_items.py`); the deterministic verifier scores every answer.

**Alignment note:** the AC9M8Nxx/AC9M8Axx codes in the node comments are references to ACARA
v9 content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
