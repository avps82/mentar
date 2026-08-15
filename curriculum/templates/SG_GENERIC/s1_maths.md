---
type: Mentar Curriculum Template
title: "Maths — Secondary 1 (Singapore, general)"
tags: [SG, mathematics, "Secondary 1", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 1 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what Singapore teaches in Secondary 1.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: sg-s1-maths
country: SG
year_level: "Secondary 1"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Secondary 1 🇸🇬 (general)"
icon: "🔢"
description: "Adding and subtracting integers, order of operations with negatives, adding fractions (different denominators) and more — general maths at roughly Secondary 1 level."
item_source: sg_s1_maths

language_register:
  reading_level: "~ages 11-12"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: sg_s1_integers_add_sub
    label: "Adding and subtracting integers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 15 + -7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_order_of_ops_negatives
    label: "Order of operations with negatives"
    prereqs: [sg_s1_integers_add_sub]
    grounding: {}
    transfer_seeds:
      - "What is -17 + 54 ÷ 6?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_unlike_denom_fractions
    label: "Adding fractions (different denominators)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3/5 + 3/2?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_one_step_equations
    label: "One-step equations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If x + 15 = 27, what is x?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_mult_decimal_by_decimal
    label: "Multiplying a decimal by a decimal"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 2.5 × 4.9?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Secondary 1 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Secondary 1 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_s1_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
