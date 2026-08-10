---
type: Mentar Curriculum Template
title: "Maths — Year 11 (AU)"
tags: [AU, mathematics, "Year 11"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 11 Mathematics (Algebra strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR11_GENERATORS),
# so the deterministic verifier scores every answer. Same derive-not-transform discipline
# as year9_maths.md/year10_maths.md.

template_id: au-year11-maths
country: AU
year_level: "Year 11"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M11 Algebra)"
schema_version: "0.1"
label: "Maths — Year 11 🇦🇺"                          # R3.1: web picker catalog fields
icon: "1️⃣1️⃣"
description: "Binomial-product areas, quadratic expressions from words, combining quadratic and linear expressions, and difference-of-expressions word problems (Australian Year 11)."
item_source: au_year11

language_register:
  reading_level: "~Year 11 / ages 16-17"
  vocabulary_note: "Clear sentences. Answer with an algebraic expression (e.g. x**2 + 5x + 6)."

# 4 independent nodes (no natural prereq chain at this level). First genuinely quadratic
# content in the AU pack (binomial products, "square of a number" translation).
concepts:

  - id: au11_binomial_product_area
    label: "Area as an algebraic expression (binomial sides)"  # AC9M11A02 alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle has width (x + 2) and length (x + 5). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au11_word_to_quadratic_expression
    label: "Writing quadratic expressions from words"       # AC9M11A02 alignment
    prereqs: [au11_binomial_product_area]
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: the square of a number x, plus 4 times the number, minus 7."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au11_combine_quadratic_linear
    label: "Combining a quadratic and a linear expression"  # AC9M11A02 alignment
    prereqs: [au11_word_to_quadratic_expression]
    grounding: {}
    transfer_seeds:
      - "If a = 2x**2 + 3x and b = 4x + 5, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au11_difference_of_expressions
    label: "Difference of two related expressions"          # AC9M11A02 alignment
    prereqs: [au11_combine_quadratic_linear]
    grounding: {}
    transfer_seeds:
      - "A number is x. A second number is 3 times x, minus 4. Write an expression for the SECOND number minus the FIRST number."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 11 Mathematics (Algebra)

ACARA v9 Algebra strand, Year 11 — the first genuinely quadratic content in the AU pack
(binomial products, "square of a number" translation, combining terms of different
degree). Same derive-not-transform safety discipline as Year 9/10 — see
`engine/au_items.py`'s Year 9 section docstring.

**Alignment note:** the AC9M11A02 code in the node comments is a reference to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
