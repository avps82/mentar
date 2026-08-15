---
type: Mentar Curriculum Template
title: "Maths — Primary 6 (Singapore, general)"
tags: [SG, mathematics, "Primary 6", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 6 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what Singapore teaches in Primary 6.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: sg-p6-maths
country: SG
year_level: "Primary 6"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Primary 6 🇸🇬 (general)"
icon: "🔢"
description: "Order of operations, multiplying decimals, dividing decimals and more — general maths at roughly Primary 6 level."
item_source: sg_p6_maths

language_register:
  reading_level: "~ages 10-11"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: sg_p6_order_of_operations
    label: "Order of operations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 51 + 3 × 7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_mult_decimals
    label: "Multiplying decimals"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3.1 × 7?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_div_decimals
    label: "Dividing decimals"
    prereqs: [sg_p6_mult_decimals]
    grounding: {}
    transfer_seeds:
      - "What is 43.2 ÷ 9?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_area_perimeter
    label: "Area and perimeter"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle is 12cm by 9cm. What is its area, in square centimetres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_fraction_decimal_equiv
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

# Singapore — Primary 6 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Primary 6 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p6_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
