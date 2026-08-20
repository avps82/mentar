---
type: Mentar Curriculum Template
title: "Maths — Year 1 (Australia)"
tags: [AU, mathematics, "Year 1"]
timestamp: "2026-08-24T00:00:00Z"
# W5/W6 of docs/design/curriculum_depth_program.md: Year 1 was ABSENT in every
# subject — the loudest row in the coverage audit. Age-6 register: very short
# sentences, numbers within 20, mc4 knowledge items from disjoint fact tables.

template_id: au-year1-maths
country: AU
year_level: "Year 1"
subject: mathematics
curriculum_standard: "AC v9 (CC BY 4.0) — year level only; codes not cited"
schema_version: "0.1"
label: "Maths — Year 1 🇦🇺"
icon: "🔢"
description: "First steps: counting, adding, shapes and patterns."
item_source: au1_maths

language_register:
  reading_level: "~Year 1 / ages 5-7"
  vocabulary_note: "Very short sentences. Everyday words. Numbers within 20."

concepts:
  - id: au1_count_objects
    label: "Counting objects"
    strand: "Number"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Count the stars: ★★★★★★. How many stars are there?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: au1_add_within_10
    label: "Adding small numbers"
    strand: "Number"
    prereqs: [au1_count_objects]
    grounding: {}
    transfer_seeds:
      - "You have 1 apples. You get 4 more. How many apples now?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: au1_skip_count_2s
    label: "Counting by 2s"
    strand: "Algebra"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Counting by 2s: 8, 10, 12, ... What number comes next?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: au1_longer_shorter
    label: "Longer, shorter, heavier, lighter"
    strand: "Measurement"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the LIGHTER one? A) an elephant (next to a cat)  B) a feather (next to a brick)  C) a broom (next to a spoon)  D) a pencil (next to a bus). Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: au1_shape_sides
    label: "Sides of a shape"
    strand: "Space"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "How many sides does a pentagon have?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: au1_simple_tally
    label: "Comparing votes"
    strand: "Statistics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "The class voted for a colour. Red got 5 votes. Blue got 3 votes. How many MORE votes did red get than blue?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.1, slip: 0.15, learns: 0.25, forgets: 0 }

---

# Maths — Year 1 (Australia)

The first year of each subject (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_year1_items.py`.
