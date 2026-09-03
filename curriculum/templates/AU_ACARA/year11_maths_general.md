---
type: Mentar Curriculum Template
title: "General Maths — Year 11 (Australia, senior)"
tags: [AU, mathematics, "Year 11", senior]
timestamp: "2026-08-20T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), mirroring
# the senior-science split: students enrol in Essential, General, Mathematical
# Methods or Specialist. The old merged "Year 11 Maths" held 4 topics from a
# single strand -- the maintainer's verdict was "quite less and incomplete".
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).
# `strand:` groups topics for display and for tools/audit_curriculum_coverage
# (maintainer 2026-08-20: "split the topics and subtopics") -- the engine still
# works per-concept.

template_id: au11-maths-general
country: AU
year_level: "Year 11"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "General Maths — Year 11"
icon: "📐"
description: "Sequences, matrices, trigonometry, networks and statistics."
item_source: au11_general

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au11g_arithmetic_nth
    label: "Arithmetic sequence — nth term"
    strand: "Sequences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "An arithmetic sequence starts at 7 and goes up by 4 each term. What is term 15?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_geometric_nth
    label: "Geometric sequence — nth term"
    strand: "Sequences"
    prereqs: [au11g_arithmetic_nth]
    grounding: {}
    transfer_seeds:
      - "A geometric sequence starts at 5 and multiplies by 3 each term. What is term 5?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_matrix_addition
    label: "Matrix addition"
    strand: "Matrices"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A = [7 9; 2 7] and B = [4 7; 6 8] (rows separated by ';'). What is the TOP-LEFT entry of A + B?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_matrix_scalar
    label: "Scalar multiple of a matrix"
    strand: "Matrices"
    prereqs: [au11g_matrix_addition]
    grounding: {}
    transfer_seeds:
      - "M = [9 6; 9 9] (rows separated by ';'). What is the bottom-left entry of 2M?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_linear_rule_value
    label: "Value from a linear rule"
    strand: "Linear and non-linear relationships"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A line has the rule y = 5x + 2. What is y when x = 3?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_pythagoras
    label: "Pythagoras' theorem"
    strand: "Trigonometry"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A right-angled triangle has shorter sides 5 m and 12 m. How long is the hypotenuse, in metres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_trig_opposite
    label: "Height from an angle (tan)"
    strand: "Trigonometry"
    prereqs: [au11g_pythagoras]
    grounding: {}
    transfer_seeds:
      - "From 15 m away, the angle up to the top of a pole is 45°. tan 45° = 1. How tall is the pole, in metres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_circle_circumference
    label: "Circumference of a circle"
    strand: "Trigonometry"
    prereqs: [au11g_trig_opposite]
    grounding: {}
    transfer_seeds:
      - "A circular track has radius 15 m. Using π ≈ 3.14, what is its circumference, in metres?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_two_way_table
    label: "Two-way table — the missing cell"
    strand: "Statistics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In this two-way table, how many students play NEITHER sport nor music?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_correlation_direction
    label: "Correlation direction"
    strand: "Statistics"
    prereqs: [au11g_two_way_table]
    grounding: {}
    transfer_seeds:
      - "What correlation does this scatter plot show? A) positive  B) negative  C) no correlation  D) perfect correlation. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_percentage_change
    label: "Percentage increase"
    strand: "Consumer arithmetic"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A gym membership costs $40 a month. The price rises by 10%. How many dollars is the new monthly price?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11g_parabola_value
    label: "A non-linear rule"
    strand: "Linear and non-linear relationships"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "The height of an arch follows the non-linear rule y = x² + 3. What is y when x = 2?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# General Maths — Year 11 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
