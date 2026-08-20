---
type: Mentar Curriculum Template
title: "Maths — Class 9 (India, general)"
tags: [IN, mathematics, "Class 9", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 9 Maths (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior mathematics at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 9.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c9-maths
country: IN
year_level: "Class 9"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 9 🇮🇳 (general)"
icon: "🔢"
description: "Expanding brackets, index laws, surds and linear equations — general senior maths at roughly Class 9 level."
item_source: in_c9_maths

language_register:
  reading_level: "~ages 14-15"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c9_word_to_expression
    label: "Writing algebraic expressions from words"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: 2 times a number y, minus 1."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_combine_expressions
    label: "Combining algebraic expressions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If a = 5x + 5 and b = 6x + 1, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_rectangle_perimeter_expression
    label: "Perimeter as an algebraic expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle has width x and length (x + 9). Write a simplified expression for its perimeter."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_rectangle_area_expression
    label: "Area as an algebraic expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle has width x and length (x + 7). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c9_simple_interest
    label: "Simple interest"
    strand: "Number and finance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "$500 is invested at 5% simple interest per year for 3 years. How many dollars of interest does it earn?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c9_scale_factor
    label: "Similar shapes and scale factor"
    strand: "Space"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Two triangles are similar with scale factor 4. A side of the small triangle is 3 cm. How long is the matching side of the large one?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c9_scatter_trend
    label: "Reading a scatterplot trend"
    strand: "Statistics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A scatterplot shows that older cars tended to sell for less. What association is this? A) positive  B) negative  C) no association  D) it cannot be told. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 9 Maths (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 9 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
