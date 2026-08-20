---
type: Mentar Curriculum Template
title: "Maths — Year 9 (AU)"
tags: [AU, mathematics, "Year 9"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 9 Mathematics (Algebra strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR9_GENERATORS),
# so the deterministic verifier scores every answer.
# FIRST Y9+ template (B0, 2026-08-11): uses answer_type="expression"
# (verify_numeric.py's sympy-backed expression_equiv, simplify(a-b)==0). Every
# node is deliberately phrased so the answer must be DERIVED from a word/shape
# setup, never a transform of an already-algebraic prompt (see au_items.py's
# Year 9 section docstring for why "Expand X"/"Factorise X" style tasks are
# NOT safe for an equivalence checker — a lazy retype of the prompt would pass).

template_id: au-year9-maths
country: AU
year_level: "Year 9"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M9 Algebra)"
schema_version: "0.1"
label: "Maths — Year 9 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Writing and combining algebraic expressions, and expressions for perimeter and area (Australian Year 9)."
item_source: au_year9

language_register:
  reading_level: "~Year 9 / ages 14-15"
  vocabulary_note: "Clear sentences. Answer with an algebraic expression (e.g. 2x + 6)."

# 4 independent nodes (no natural prereq chain at this level): word-to-expression
# translation, combining two given expressions, perimeter/area from algebraic
# side lengths.
concepts:

  - id: au9_word_to_expression
    label: "Writing algebraic expressions from words"     # AC9M9A02 alignment
    strand: "Algebra"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: 3 more than 2 times a number n."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au9_combine_expressions
    label: "Combining algebraic expressions"               # AC9M9A02 alignment
    strand: "Algebra"
    prereqs: [au9_word_to_expression]
    grounding: {}
    transfer_seeds:
      - "If a = 3x + 2 and b = 5x + 1, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au9_rectangle_perimeter_expression
    label: "Perimeter as an algebraic expression"          # AC9M9A02 alignment
    strand: "Measurement"
    prereqs: [au9_combine_expressions]
    grounding: {}
    transfer_seeds:
      - "A rectangle has width x and length (x + 4). Write a simplified expression for its perimeter."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au9_rectangle_area_expression
    label: "Area as an algebraic expression"               # AC9M9A02 alignment
    strand: "Measurement"
    prereqs: [au9_rectangle_perimeter_expression]
    grounding: {}
    transfer_seeds:
      - "A rectangle has width x and length (x + 4). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 9 Mathematics (Algebra)

ACARA v9 Algebra strand, Year 9 — the first template in this repo to use
`answer_type: expression` (B0, 2026-08-11), unblocked the same day sympy was
installed. Every node's answer must be DERIVED from a word description or a
shape's algebraic side lengths, never produced by transforming an
already-algebraic prompt — see `engine/au_items.py`'s Year 9 section docstring
for the reasoning (an equivalence checker cannot distinguish "did the work"
from "retyped the prompt" for a single-expression transform task like
"expand this").

**Alignment note:** the AC9M9A02 code in the node comments is a reference to
ACARA v9 content descriptions for alignment/traceability. Question text,
labels and generators are Mentar-authored. ACARA core curriculum content is
CC BY 4.0 (verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA
descriptor text is reproduced in this template.
