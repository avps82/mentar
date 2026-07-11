---
# Mentar curriculum template — evergreen maths practice sampler.
# Country-agnostic drill content (never expires, no curriculum authority owns it) --
# always available under the picker's "Try-out topics" group, separate from any
# country-curriculum templates. All items come from parametric generators
# (engine/practice_items.py MATHS_PRACTICE_GENERATORS), deterministic verifier.

template_id: practice-maths
country: null
year_level: pilot
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Maths practice ➗"                            # R3.1: web picker catalog fields
icon: "➗"
description: "Times tables, skip counting, and doubles/halves -- quick drills that never get old."
item_source: maths_practice

language_register:
  reading_level: "~Year 3-5 / ages 8-10"
  vocabulary_note: "Short sentences. Plain number words."

# 3 independent drill nodes -- no prerequisites, each a standalone practice skill.
concepts:

  - id: practice_times_tables
    label: "Times tables (1-12)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 7 × 8?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: practice_skip_counting
    label: "Skip counting and number patterns"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What number comes next: 2, 4, 6, 8, __?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: practice_doubles_halves
    label: "Doubles and halves"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is double 6?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Maths practice (evergreen sampler)

A permanent "Try-out topics" fixture, separate from country-curriculum content --
quick, repeatable maths fluency drills (times tables, skip counting, doubles/halves)
that stay relevant regardless of which country's curriculum a family is following.
Every item is parametrically generated and scored by the deterministic verifier;
the LLM never decides correctness.
