---
type: Mentar Curriculum Template
title: "Maths — Year 6 (AU)"
tags: [AU, mathematics, "Year 6"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 6 Mathematics (Number + Measurement strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR6_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year6-maths
country: AU
year_level: "Year 6"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M6 Number, Measurement)"
schema_version: "0.1"
label: "Maths — Year 6 🇦🇺"                          # R3.1: web picker catalog fields
icon: "6️⃣"
description: "Order of operations, multiplying and dividing decimals, rectangle area and perimeter, and fraction-to-decimal conversion (Australian Year 6)."
item_source: au_year6

language_register:
  reading_level: "~Year 6 / ages 11-12"
  vocabulary_note: "Clear sentences. Plain number words. One idea per question."

# 5 nodes: order of operations is the root; multiplying decimals -> dividing decimals
# is the one true prereq chain; area/perimeter and fraction-to-decimal conversion are
# independent strands.
concepts:

  - id: au6_order_of_operations
    label: "Order of operations"                         # AC9M6N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3 + 4 × 2?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_mult_decimals
    label: "Multiplying decimals"                        # AC9M6N02
    prereqs: [au6_order_of_operations]
    grounding: {}
    transfer_seeds:
      - "What is 1.5 × 4?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_div_decimals
    label: "Dividing decimals"                           # AC9M6N02
    prereqs: [au6_mult_decimals]
    grounding: {}
    transfer_seeds:
      - "What is 7.2 ÷ 4?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_area_perimeter
    label: "Area and perimeter of a rectangle"           # AC9M6M01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle is 6cm by 4cm. What is its area, in square centimetres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_fraction_decimal_equiv
    label: "Fraction-to-decimal conversion"              # AC9M6N03
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write 3/4 as a decimal."
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 6 Mathematics (Number, Measurement)

ACARA v9 Number + Measurement strands, Year 6 — sibling of `year2_maths.md`/`year3_maths.md`/
`year4_maths.md`/`year5_maths.md` in the per-country/per-year pattern (SPEC §6). Parametric
generators only (`engine/au_items.py`); the deterministic verifier scores every answer.

**Alignment note:** the AC9M6Nxx/AC9M6Mxx codes in the node comments are references to
ACARA v9 content descriptions for alignment/traceability. Question text, labels and generators
are Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
