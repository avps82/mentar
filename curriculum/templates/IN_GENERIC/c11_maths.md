---
type: Mentar Curriculum Template
title: "Maths — Class 11 (India, general)"
tags: [IN, mathematics, "Class 11", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 11 Maths (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior mathematics at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 11.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c11-maths
country: IN
year_level: "Class 11"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 11 🇮🇳 (general)"
icon: "1️⃣1️⃣"
description: "Binomial products, quadratic expressions and combining terms — general senior maths at roughly Class 11 level."
item_source: in_c11_maths

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c11_binomial_product_area
    label: "Area as an algebraic expression (binomial sides)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle has width (x + 1) and length (x + 7). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_word_to_quadratic_expression
    label: "Writing quadratic expressions from words"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: the square of a number y, plus 6 times the number, minus 2."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_combine_quadratic_linear
    label: "Combining a quadratic and a linear expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If a = 4y**2 + 2y and b = 3y + 7, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_difference_of_expressions
    label: "Difference of two related expressions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A number is x. A second number is 6 times x, minus 9. Write an expression for the SECOND number minus the FIRST number."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 11 Maths (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 11 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
