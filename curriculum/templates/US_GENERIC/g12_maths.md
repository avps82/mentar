---
type: Mentar Curriculum Template
title: "Maths — Grade 12 (the United States, general)"
tags: [US, mathematics, "Grade 12", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — the United States, Grade 12 Maths (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior mathematics at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what the United States teaches at Grade 12.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: us-g12-maths
country: US
year_level: "Grade 12"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Grade 12 🇺🇸 (general)"
icon: "🔢"
description: "Algebra applied to modelled scenarios: revenue, combined quadratics and compound areas — general senior maths at roughly Grade 12 level."
item_source: us_g12_maths

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: us_g12_revenue_expression
    label: "Revenue as a quadratic expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A shop sells items for $x each. On a day they sell (2x + 9) items. Write an expression for the total revenue (price times number sold)."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g12_combine_two_quadratics
    label: "Combining two quadratic expressions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If a = 4y**2 + 3y + 8 and b = 4y**2 + 2y + 9, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g12_compound_shape_area
    label: "Compound-shape area as an algebraic expression"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A garden is rectangular with width y and length (y + 2), but a square section of side 2 is removed from one corner for a path. Write an expression for the remaining garden area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
---

# the United States — Grade 12 Maths (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Grade 12 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
