---
type: Mentar Curriculum Template
title: "Maths — Grade 2 (United States, general)"
tags: [US, mathematics, "Grade 2", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 2 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what United States teaches in Grade 2.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: us-g2-maths
country: US
year_level: "Grade 2"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Grade 2 (general)"
icon: "🔢"
description: "Place value, adding numbers, subtracting numbers and more — general maths at roughly Grade 2 level."
item_source: us_g2_maths

language_register:
  reading_level: "~ages 6-7"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: us_g2_place_value
    label: "Place value"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 63, what is the value of the digit 6? A) 6  B) 60  C) 3  D) 30. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g2_addition
    label: "Adding numbers"
    prereqs: [us_g2_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 14 + 44?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g2_subtraction
    label: "Subtracting numbers"
    prereqs: [us_g2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 32 − 12?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g2_mult_facts
    label: "Times tables"
    prereqs: [us_g2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 10 × 2?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g2_halves_quarters
    label: "Halves and quarters"
    prereqs: [us_g2_place_value]
    grounding: {}
    transfer_seeds:
      - "A pizza is cut into 2 equal slices. What fraction is ONE slice?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 2 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Grade 2 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g2_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
