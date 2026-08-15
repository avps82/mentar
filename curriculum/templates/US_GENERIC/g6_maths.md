---
type: Mentar Curriculum Template
title: "Maths — Grade 6 (United States, general)"
tags: [US, mathematics, "Grade 6", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 6 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what United States teaches in Grade 6.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: us-g6-maths
country: US
year_level: "Grade 6"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Grade 6 🇺🇸 (general)"
icon: "🔢"
description: "Order of operations, multiplying decimals, dividing decimals and more — general maths at roughly Grade 6 level."
item_source: us_g6_maths

language_register:
  reading_level: "~ages 10-11"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: us_g6_order_of_operations
    label: "Order of operations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 51 + 3 × 7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_mult_decimals
    label: "Multiplying decimals"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3.1 × 7?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_div_decimals
    label: "Dividing decimals"
    prereqs: [us_g6_mult_decimals]
    grounding: {}
    transfer_seeds:
      - "What is 43.2 ÷ 9?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_area_perimeter
    label: "Area and perimeter"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle is 12cm by 9cm. What is its area, in square centimetres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g6_fraction_decimal_equiv
    label: "Fractions as decimals"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write 1/4 as a decimal."
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 6 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Grade 6 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g6_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
