---
type: Mentar Curriculum Template
title: "Maths — Grade 4 (United States, general)"
tags: [US, mathematics, "Grade 4", generic]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — United States, Grade 4 Mathematics (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught maths at roughly
# this difficulty, 100% Mentar-authored/reused-generic; the level name is a display
# label, not a claim about what United States teaches in Grade 4.
# Items come from shared parametric generators (engine/generic_items.py, which
# reuses already-tested generator functions), so the deterministic verifier scores
# every answer.

template_id: us-g4-maths
country: US
year_level: "Grade 4"
subject: mathematics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Maths — Grade 4 (general)"
icon: "🔢"
description: "Place value, times tables, division facts and more — general maths at roughly Grade 4 level."
item_source: us_g4_maths

language_register:
  reading_level: "~ages 8-9"
  vocabulary_note: "Short sentences. Plain number words. One idea per question."

concepts:

  - id: us_g4_place_value
    label: "Place value"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In the number 1384, what is the value of the digit 1? A) 1  B) 100  C) 1000  D) 10. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_mult_facts
    label: "Times tables"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 7 × 8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_division_facts
    label: "Division facts"
    prereqs: [us_g4_mult_facts]
    grounding: {}
    transfer_seeds:
      - "What is 15 ÷ 3?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_sharing_division
    label: "Sharing equally (word problems)"
    prereqs: [us_g4_division_facts]
    grounding: {}
    transfer_seeds:
      - "Share 12 crayons equally among 4 bags. How many crayons does each get?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_equivalent_fractions
    label: "Equivalent fractions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Write a fraction equal to 1/2 but with denominator 6."
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_adding_fractions
    label: "Adding fractions (same denominator)"
    prereqs: [us_g4_equivalent_fractions]
    grounding: {}
    transfer_seeds:
      - "What is 6/9 + 2/9?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.1, slip: 0.1, learns: 0.2, forgets: 0 }

---

# United States — Grade 4 Mathematics (generic)

A board-agnostic maths pack: universally-taught topics at roughly Grade 4 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core's public licence carries a purpose clause and trademark this pack deliberately stays clear of.

Node ids are prefixed `us_g4_` and the item generators are shared across every
generic pack (`engine/generic_items.py` — one concept-progression table, reused
generator functions, zero new item logic). The deterministic verifier scores every
answer; the model never decides correctness (SPEC §14).
