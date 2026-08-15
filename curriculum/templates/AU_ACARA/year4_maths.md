---
type: Mentar Curriculum Template
title: "Maths — Year 4 (AU)"
tags: [AU, mathematics, "Year 4"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 4 Mathematics (Number strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR4_GENERATORS).

template_id: au-year4-maths
country: AU
year_level: "Year 4"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M4 Number)"
schema_version: "0.1"
label: "Maths — Year 4 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Bigger numbers, times tables to 10×10, division and equivalent fractions (Australian Year 4)."
item_source: au_year4

language_register:
  reading_level: "~Year 4 / ages 9-10"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

# 6 nodes: place value root; mult facts -> division facts -> sharing word problems;
# equivalent fractions -> adding fractions.
concepts:

  - id: au4_place_value
    label: "Place value to 9999"             # AC9M4N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 3852, what is the value of the digit 8? A) 8  B) 80  C) 800  D) 8000. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_mult_facts
    label: "Times tables to 10 × 10"          # AC9M4N05
    prereqs: [au4_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 7 × 8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_division_facts
    label: "Division facts from the times tables"  # AC9M4N05
    prereqs: [au4_mult_facts]
    grounding: {}
    transfer_seeds:
      - "What is 56 ÷ 8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_sharing_division
    label: "Sharing and grouping word problems"    # AC9M4N05
    prereqs: [au4_division_facts]
    grounding: {}
    transfer_seeds:
      - "Share 24 stickers equally among 4 children. How many stickers does each get?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_equivalent_fractions
    label: "Equivalent fractions"             # AC9M4N03
    prereqs: [au4_place_value]
    grounding: {}
    transfer_seeds:
      - "Fill in the missing number: 1/2 = ?/4"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_adding_fractions
    label: "Adding fractions (same denominator)"   # AC9M4N04
    prereqs: [au4_equivalent_fractions]
    grounding: {}
    transfer_seeds:
      - "What is 1/5 + 2/5?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 4 Mathematics (Number)

ACARA v9 Number strand, Year 4 — sibling of `year3_maths.md` in the per-country/per-year
pattern (SPEC §6). Parametric generators only (`engine/au_items.py`); the deterministic
verifier scores every answer.

**Alignment note:** AC9M4Nxx codes are references to ACARA v9 content descriptions for
alignment/traceability. Question text, labels and generators are Mentar-authored. ACARA
core curriculum content is CC BY 4.0 (verified 2026-07-10 — `docs/CONTENT_LICENSES.md`);
no ACARA descriptor text is reproduced in this template.
