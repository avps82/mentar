---
# Mentar curriculum template — Australia, Year 5 Mathematics (Number strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR5_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year5-maths
country: AU
year_level: "Year 5"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M5 Number)"
schema_version: "0.1"
label: "Maths — Year 5 🇦🇺"                          # R3.1: web picker catalog fields
icon: "5️⃣"
description: "Decimal place value, adding and subtracting decimals, multiplying fractions, percentages and negative numbers (Australian Year 5)."
item_source: au_year5

language_register:
  reading_level: "~Year 5 / ages 10-11"
  vocabulary_note: "Clear sentences. Plain number words. One idea per question."

# 5 nodes: decimal place value, fraction-times-whole, percentages and negative numbers
# are independent strands (no natural prereq chain between them at this level);
# add/subtract decimals is the one true prereq (needs place value first). This is the
# pilot's FIRST use of the "decimal" answer type (R13, 2026-07-19).
concepts:

  - id: au5_decimal_place_value
    label: "Decimal place value (tenths)"                # AC9M5N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In 4.7, what does the 7 represent? A) 7 ones  B) 7 tenths  C) 7 hundredths  D) 7 tens. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_add_sub_decimals
    label: "Adding and subtracting decimals"             # AC9M5N02
    prereqs: [au5_decimal_place_value]
    grounding: {}
    transfer_seeds:
      - "What is 3.4 + 2.6?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_mult_fraction_whole
    label: "Multiplying a fraction by a whole number"    # AC9M5N06
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 2/5 × 3?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_percentage_of_quantity
    label: "Percentages of a quantity (10%, 25%, 50%, 75%)"  # AC9M5N02
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 25% of 80?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_negative_numbers
    label: "Negative numbers (temperature contexts)"     # AC9M5N01
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "The temperature was 3°C and dropped by 8°C. What is the new temperature?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 5 Mathematics (Number)

ACARA v9 Number strand, Year 5 — sibling of `year2_maths.md`/`year3_maths.md`/`year4_maths.md`
in the per-country/per-year pattern (SPEC §6). Parametric generators only
(`engine/au_items.py`); the deterministic verifier scores every answer. This template is the
pilot's first use of the "decimal" answer type (R13, 2026-07-19) — decimal-flavoured content
(tenths place value, adding/subtracting decimals) sits alongside the existing int/fraction/mc4
grammar.

**Alignment note:** the AC9M5Nxx codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
