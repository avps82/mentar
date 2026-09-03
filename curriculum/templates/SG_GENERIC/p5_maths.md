---
type: Mentar Curriculum Template
title: "Maths — Primary 5 (Singapore, general)"
tags: [SG, mathematics, "Primary 5", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 5 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what Singapore teaches in Primary 5.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: sg-p5-maths
country: SG
year_level: "Primary 5"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Primary 5 (general)"
icon: "🔢"
description: "Decimal place value, adding and subtracting decimals, multiplying a fraction by a whole number and more — general maths at roughly Primary 5 level."
item_source: sg_p5_maths

language_register:
  reading_level: "~ages 9-10"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: sg_p5_decimal_place_value
    label: "Decimal place value"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In 8.6, what does the 6 represent? A) 6 tenths  B) 6 ones  C) 6 hundredths  D) 6 tens. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_add_sub_decimals
    label: "Adding and subtracting decimals"
    prereqs: [sg_p5_decimal_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 5.1 - 1.5?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_mult_fraction_whole
    label: "Multiplying a fraction by a whole number"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 3/8 × 5?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_percentage_of_quantity
    label: "Percentage of a quantity"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 50% of 94?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_negative_numbers
    label: "Negative numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "The temperature was 5°C and dropped by 9°C. What is the new temperature?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_division_remainder_fraction
    label: "Division with a remainder (as a fraction)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 55 ÷ 4?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p5_division_remainder_decimal
    label: "Division with a remainder (as a decimal)"
    prereqs: [sg_p5_division_remainder_fraction]
    grounding: {}
    transfer_seeds:
      - "What is 311 ÷ 20?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 5 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Primary 5 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p5_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
