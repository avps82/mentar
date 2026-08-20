---
type: Mentar Curriculum Template
title: "Maths — Year 3 (AU)"
tags: [AU, mathematics, "Year 3"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 3 Mathematics (Number strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR3_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year3-maths
country: AU
year_level: "Year 3"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M3 Number)"
schema_version: "0.1"
label: "Maths — Year 3 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Place value, adding, times tables and fractions (Australian Year 3)."
item_source: au_year3

language_register:
  reading_level: "~Year 3 / ages 8-9"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

# 6 nodes: place value is the root; addition -> subtraction; mult facts builds on
# addition; unit fractions -> fraction-of-a-whole.
concepts:

  - id: au3_place_value
    label: "Place value to 999"           # AC9M3N01
    strand: "Number"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 472, what is the value of the digit 7? A) 7  B) 70  C) 700  D) 40. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_addition
    label: "Adding numbers to 1000"       # AC9M3N02
    strand: "Number"
    prereqs: [au3_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 235 + 148?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_subtraction
    label: "Subtracting numbers to 1000"  # AC9M3N02
    strand: "Number"
    prereqs: [au3_addition]
    grounding: {}
    transfer_seeds:
      - "What is 520 − 180?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_mult_facts
    label: "Times tables: 3, 4, 5 and 10"  # AC9M3N03
    strand: "Number"
    prereqs: [au3_addition]
    grounding: {}
    transfer_seeds:
      - "What is 4 × 7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_unit_fractions
    label: "Unit fractions (1/2, 1/3, 1/4, 1/5, 1/10)"  # AC9M3N04
    strand: "Fractions"
    prereqs: [au3_place_value]
    grounding: {}
    transfer_seeds:
      - "A cake is split into 4 equal parts. What fraction is ONE part?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_fraction_of_whole
    label: "Fractions as parts of a whole"  # AC9M3N04
    strand: "Fractions"
    prereqs: [au3_unit_fractions]
    grounding: {}
    transfer_seeds:
      - "A pizza is cut into 5 equal slices and you eat 2. What fraction did you eat?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 3 Mathematics (Number)

First template in the per-country/per-year pattern (SPEC §6): ACARA v9 Number strand,
Year 3. Every question is generated parametrically with a computed ground truth
(`engine/au_items.py`), so the deterministic verifier stays authoritative and the LLM
never decides correctness.

**Alignment note:** the AC9M3Nxx codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
