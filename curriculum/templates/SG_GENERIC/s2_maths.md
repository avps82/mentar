---
type: Mentar Curriculum Template
title: "Maths — Secondary 2 (Singapore, general)"
tags: [SG, mathematics, "Secondary 2", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 2 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what Singapore teaches in Secondary 2.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: sg-s2-maths
country: SG
year_level: "Secondary 2"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Secondary 2 (general)"
icon: "🔢"
description: "Two-step equations, square numbers, multiplying negative numbers and more — general maths at roughly Secondary 2 level."
item_source: sg_s2_maths

language_register:
  reading_level: "~ages 12-13"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: sg_s2_two_step_equations
    label: "Two-step equations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If 5x + 2 = 12, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s2_squares
    label: "Square numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 5 squared (5²)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s2_negative_multiplication
    label: "Multiplying negative numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 4 × -8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s2_percentage_change
    label: "Percentage increase and decrease"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A price of $130 increases by 20%. What is the new price?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s2_div_decimal_by_decimal
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

# Singapore — Secondary 2 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Secondary 2 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_s2_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
