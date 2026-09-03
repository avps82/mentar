---
type: Mentar Curriculum Template
title: "Maths — Year 10 (AU)"
tags: [AU, mathematics, "Year 10"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 10 Mathematics (Algebra strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR10_GENERATORS),
# so the deterministic verifier scores every answer. Same answer_type: expression /
# derive-not-transform discipline as year9_maths.md — see au_items.py's Year 9 section
# docstring for why "expand X"/"simplify X" phrasings are unsafe for this checker.

template_id: au-year10-maths
country: AU
year_level: "Year 10"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M10 Algebra)"
schema_version: "0.1"
label: "Maths — Year 10"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Distributive-law expressions, combining three expressions, squared expressions, and combined-perimeter expressions (Australian Year 10)."
item_source: au_year10

language_register:
  reading_level: "~Year 10 / ages 15-16"
  vocabulary_note: "Clear sentences. Answer with an algebraic expression (e.g. 4x + 8)."

# 4 independent nodes (no natural prereq chain at this level).
concepts:

  - id: au10_distributive_word_to_expression
    label: "Distributive-law expressions from words"       # AC9M10A02 alignment
    strand: "Algebra"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: the sum of x and 5, all multiplied by 3."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au10_combine_three_expressions
    label: "Combining three algebraic expressions"         # AC9M10A02 alignment
    strand: "Algebra"
    prereqs: [au10_distributive_word_to_expression]
    grounding: {}
    transfer_seeds:
      - "If a = 4x + 3, b = 2x + 1 and c = 3x + 2, what is a + b - c? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au10_square_expression
    label: "Squared expressions (area of a square)"        # AC9M10A02 alignment
    strand: "Algebra"
    prereqs: [au10_combine_three_expressions]
    grounding: {}
    transfer_seeds:
      - "A square has side length (x + 4). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au10_combined_rectangles_perimeter
    label: "Combined perimeter as an algebraic expression"  # AC9M10A02 alignment
    strand: "Measurement and space"
    prereqs: [au10_square_expression]
    grounding: {}
    transfer_seeds:
      - "Two identical rectangles each have width x and length (x + 3). Write a simplified expression for their COMBINED perimeter (both rectangles together)."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au10_compound_two_years
    label: "Compound interest — two years"
    strand: "Number and finance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "$400 is invested at 20% compound interest per year. What is the balance, in dollars, after two years?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au10_two_stage_probability
    label: "Two-stage probability"
    strand: "Probability"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A fair coin is tossed twice. What is the probability of two heads from two coin tosses? Give a decimal."
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au10_compare_means
    label: "Comparing two data sets"
    strand: "Statistics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Class A scored 7, 12, 17. Class B scored 12, 17, 22. How much higher is Class B's mean than Class A's?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 10 Mathematics (Algebra)

ACARA v9 Algebra strand, Year 10 — sibling of `year9_maths.md`, one step harder: the
distributive law read from words, subtraction-combining three expressions (not just
addition), a squared expression setting up Year 11's binomial-product content, and a
"combined shapes" perimeter task. Same derive-not-transform safety discipline as Year 9.

**Alignment note:** the AC9M10A02 code in the node comments is a reference to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
