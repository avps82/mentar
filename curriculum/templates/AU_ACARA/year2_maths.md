---
type: Mentar Curriculum Template
title: "Maths — Year 2 (AU)"
tags: [AU, mathematics, "Year 2"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 2 Mathematics (Number strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR2_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year2-maths
country: AU
year_level: "Year 2"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M2 Number)"
schema_version: "0.1"
label: "Maths — Year 2 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Place value to 100, adding, subtracting, times tables for 2/5/10, and halves
  and quarters (Australian Year 2)."
item_source: au_year2

language_register:
  reading_level: "~Year 2 / ages 6-7"
  vocabulary_note: "Very short sentences. Plain number words. One idea per question."

# 5 nodes: place value is the root; addition -> subtraction;
# mult facts builds on addition; halves/quarters is a separate strand off place value.
concepts:

  - id: au2_place_value
    label: "Place value to 99"                          # AC9M2N01
    strand: "Number"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 47, what is the value of the digit 4? A) 4  B) 40  C) 7  D) 70. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_addition
    label: "Adding numbers to 100"                     # AC9M2N02
    strand: "Number"
    prereqs: [au2_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 34 + 25?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_subtraction
    label: "Subtracting numbers to 100"                # AC9M2N02
    strand: "Number"
    prereqs: [au2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 68 − 23?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_mult_facts_2_5_10
    label: "Times tables: 2, 5 and 10"                 # AC9M2N03
    strand: "Number"
    prereqs: [au2_addition]
    grounding: {}
    transfer_seeds:
      - "What is 5 × 3?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_halves_quarters
    label: "Halves and quarters"                       # AC9M2N04
    strand: "Fractions"
    prereqs: [au2_place_value]
    grounding: {}
    transfer_seeds:
      - "A pizza is cut into 4 equal slices. What fraction is ONE slice?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_length_compare
    label: "Comparing lengths"
    strand: "Measurement"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A pencil is 18 cm long. A crayon is 4 cm long. How many centimetres longer is the pencil?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_money_coins
    label: "Counting money"
    strand: "Money and time"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "You have these coins: $2 and $2 and $1. How many dollars altogether?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_time_oclock
    label: "Reading o'clock time"
    strand: "Money and time"
    prereqs: [au2_money_coins]
    grounding: {}
    transfer_seeds:
      - "On the clock, the little hand points at 5 and the big hand points straight up at 12. What o'clock is it?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_position_words
    label: "Position words"
    strand: "Space and location"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these shows something BETWEEN another thing? A) the tree hiding the cat so you cannot see it  B) the bed with slippers below it  C) the cheese in the middle of two slices of bread  D) the box that the ball rolled out of sight of. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 2 Mathematics (Number)

ACARA v9 Number strand, Year 2 — sibling of `year3_maths.md`/`year4_maths.md` in the
per-country/per-year pattern (SPEC §6). Parametric generators only (`engine/au_items.py`);
the deterministic verifier scores every answer.

**Alignment note:** the AC9M2Nxx codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
