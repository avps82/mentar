---
type: Mentar Curriculum Template
title: "Maths — Class 10 (India, general)"
tags: [IN, mathematics, "Class 10", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 10 Maths (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior mathematics at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 10.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c10-maths
country: IN
year_level: "Class 10"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 10 (general)"
icon: "🔢"
description: "Squared expressions, combined perimeters and distributive-law algebra — general senior maths at roughly Class 10 level."
item_source: in_c10_maths

language_register:
  reading_level: "~ages 15-16"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c10_distributive_word_to_expression
    label: "Distributive-law expressions from words"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: the sum of x and 2, all multiplied by 6."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_combine_three_expressions
    label: "Combining three algebraic expressions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If a = 6y + 2, b = 9y + 5 and c = 2y + 9, what is a + b - c? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_square_expression
    label: "Squared expressions (area of a square)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A square has side length (y + 1). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_combined_rectangles_perimeter
    label: "Combined perimeter as an algebraic expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Two identical rectangles each have width x and length (x + 7). Write a simplified expression for their COMBINED perimeter (both rectangles together)."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_compound_two_years
    label: "Compound interest — two years"
    strand: "Number and finance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "$200 is invested at 20% compound interest per year. What is the balance, in dollars, after two years?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_two_stage_probability
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
  - id: in_c10_compare_means
    label: "Comparing two data sets"
    strand: "Statistics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Class A scored 15, 20, 25. Class B scored 20, 25, 30. How much higher is Class B's mean than Class A's?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 10 Maths (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 10 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
