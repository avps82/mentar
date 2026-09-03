---
type: Mentar Curriculum Template
title: "Maths — Grade 8 (United States, general)"
tags: [US, mathematics, "Grade 8", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 8 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what United States teaches in Grade 8.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: us-g8-maths
country: US
year_level: "Grade 8"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Grade 8 (general)"
icon: "🔢"
description: "Two-step equations, square numbers, multiplying negative numbers and more — general maths at roughly Grade 8 level."
item_source: us_g8_maths

language_register:
  reading_level: "~ages 12-13"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: us_g8_two_step_equations
    label: "Two-step equations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If 5x + 2 = 12, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_squares
    label: "Square numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 5 squared (5²)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_negative_multiplication
    label: "Multiplying negative numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 4 × -8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_percentage_change
    label: "Percentage increase and decrease"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A price of $130 increases by 20%. What is the new price?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_div_decimal_by_decimal
    label: "Dividing a decimal by a decimal"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3.0 ÷ 2.0?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 8 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Grade 8 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g8_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
