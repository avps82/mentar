---
type: Mentar Curriculum Template
title: "General Maths — Year 12 (Australia, senior)"
tags: [AU, mathematics, "Year 12", senior]
timestamp: "2026-08-20T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), mirroring
# the senior-science split: students enrol in Essential, General, Mathematical
# Methods or Specialist. The old merged "Year 12 Maths" held 4 topics from a
# single strand -- the maintainer's verdict was "quite less and incomplete".
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).
# `strand:` groups topics for display and for tools/audit_curriculum_coverage
# (maintainer 2026-08-20: "split the topics and subtopics") -- the engine still
# works per-concept.

template_id: au12-maths-general
country: AU
year_level: "Year 12"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "General Maths — Year 12 🇦🇺"
icon: "📐"
description: "Sequences, matrices, trigonometry, networks and statistics."
item_source: au12_general

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au12g_arithmetic_series_sum
    label: "Sum of an arithmetic series"
    strand: "Sequences and growth"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "An arithmetic sequence starts at 2, goes up by 2, and has 20 terms. What is the sum of all the terms?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_growth_application
    label: "Repeated growth"
    strand: "Sequences and growth"
    prereqs: [au12g_arithmetic_series_sum]
    grounding: {}
    transfer_seeds:
      - "A bacteria colony of 500 cells triples every hour. How many cells after 4 hours?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_matrix_product_entry
    label: "Row × column"
    strand: "Matrices"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Row [4 5] multiplies column [9; 2]. What single number does this row-times-column give?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_determinant
    label: "Determinant of a 2×2 matrix"
    strand: "Matrices"
    prereqs: [au12g_matrix_product_entry]
    grounding: {}
    transfer_seeds:
      - "M = [4 7; 6 8] (rows separated by ';'). What is the determinant of M?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_spanning_tree_edges
    label: "Edges in a spanning tree"
    strand: "Networks and decision"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A network has 5 towns. A spanning tree connects all of them with no loops. How many edges does the spanning tree have?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_eulerian_trail
    label: "Eulerian trails"
    strand: "Networks and decision"
    prereqs: [au12g_spanning_tree_edges]
    grounding: {}
    transfer_seeds:
      - "A network's vertices have 4 vertices of ODD degree. Can you walk every edge exactly once (an Eulerian trail)?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_best_fit_prediction
    label: "Predicting with a line of best fit"
    strand: "Bivariate data"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A line of best fit is: cost = 3 × hours + 20. Predict the cost for 4 hours."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_residual
    label: "Residual"
    strand: "Bivariate data"
    prereqs: [au12g_best_fit_prediction]
    grounding: {}
    transfer_seeds:
      - "A model predicted 60, the actual value was 66. What is the residual (actual − predicted)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_reducing_balance
    label: "Reducing-balance loan (one month)"
    strand: "Loans and annuities"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A loan balance is $4000. This month 2% interest is added, then a $250 payment is made. What is the new balance, in dollars?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_inflation_price
    label: "Inflation-adjusted price"
    strand: "Financial mathematics"
    prereqs: [au12g_reducing_balance]
    grounding: {}
    transfer_seeds:
      - "Inflation is 10% this year. Something costing $100 now will cost how many dollars after one year of that inflation?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_moving_average
    label: "Moving average"
    strand: "Time series"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Monthly sales for three months are 20, 30 and 40. What is the 3-point moving average for these months?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12g_max_area
    label: "Design for maximum area"
    strand: "Design problems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A farmer has 20 m of fencing for a rectangular pen. What is the LARGEST area, in square metres, the pen can enclose?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# General Maths — Year 12 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
