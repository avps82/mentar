---
type: Mentar Curriculum Template
title: "Maths — Class 2 (India, general)"
tags: [IN, mathematics, "Class 2", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — India, Class 2 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what India teaches in Class 2.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: in-c2-maths
country: IN
year_level: "Class 2"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Class 2 (general)"
icon: "🔢"
description: "Place value, adding numbers, subtracting numbers and more — general maths at roughly Class 2 level."
item_source: in_c2_maths

language_register:
  reading_level: "~ages 6-7"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: in_c2_place_value
    label: "Place value"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 63, what is the value of the digit 6? A) 6  B) 60  C) 3  D) 30. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_addition
    label: "Adding numbers"
    prereqs: [in_c2_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 14 + 44?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_subtraction
    label: "Subtracting numbers"
    prereqs: [in_c2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 32 − 12?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_mult_facts
    label: "Times tables"
    prereqs: [in_c2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 10 × 2?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_halves_quarters
    label: "Halves and quarters"
    prereqs: [in_c2_place_value]
    grounding: {}
    transfer_seeds:
      - "A pizza is cut into 2 equal slices. What fraction is ONE slice?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 2 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Class 2 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c2_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
