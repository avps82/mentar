---
type: Mentar Curriculum Template
title: "Maths — Class 8 (India, general)"
tags: [IN, mathematics, "Class 8", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — India, Class 8 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what India teaches in Class 8.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: in-c8-maths
country: IN
year_level: "Class 8"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 8 🇮🇳 (general)"
icon: "8️⃣"
description: "Two-step equations, square numbers, multiplying negative numbers and more — general maths at roughly Class 8 level."
item_source: in_c8_maths

language_register:
  reading_level: "~ages 12-13"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: in_c8_two_step_equations
    label: "Two-step equations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If 5x + 2 = 12, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_squares
    label: "Square numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 5 squared (5²)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_negative_multiplication
    label: "Multiplying negative numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 4 × -8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_percentage_change
    label: "Percentage increase and decrease"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A price of $130 increases by 20%. What is the new price?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_div_decimal_by_decimal
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

# India — Class 8 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Class 8 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c8_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
