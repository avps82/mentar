---
type: Mentar Curriculum Template
title: "Essential Maths — Year 12 (Australia, senior)"
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

template_id: au12-maths-essential
country: AU
year_level: "Year 12"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Essential Maths — Year 12 🇦🇺"
icon: "🧮"
description: "Everyday money, measurement and data — the practical senior course."
item_source: au12_essential

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au12e_compound_growth
    label: "Compound growth (two steps)"
    strand: "Financial mathematics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "$2000 grows by 10% each year, compounding. How many dollars is it worth after 2 years?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_loan_total_cost
    label: "True cost of a loan"
    strand: "Financial mathematics"
    prereqs: [au12e_compound_growth]
    grounding: {}
    transfer_seeds:
      - "A $10000 loan is repaid at $300 per month for 48 months. How many dollars MORE than the loan amount is repaid in total?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_income_tax
    label: "Income tax (two brackets)"
    strand: "Financial mathematics"
    prereqs: [au12e_loan_total_cost]
    grounding: {}
    transfer_seeds:
      - "Tax is 0% on the first $18000 earned and 25% on the rest. How many dollars of tax are paid on an income of $58000?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_gst_price
    label: "Adding gst"
    strand: "Financial mathematics"
    prereqs: [au12e_income_tax]
    grounding: {}
    transfer_seeds:
      - "A service costs $250 before GST. GST adds 10%. What is the final price, in dollars?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_scale_drawing
    label: "Scale drawing"
    strand: "Measurement and plans"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A plan uses a scale of 1:200. A wall measures 4 cm on the plan. How long is the real wall, in metres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_network_edges
    label: "Edges in a complete network"
    strand: "Networks"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In a network, 6 towns are ALL connected directly to each other. How many roads (edges) is that?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_shortest_path
    label: "Shortest path"
    strand: "Networks"
    prereqs: [au12e_network_edges]
    grounding: {}
    transfer_seeds:
      - "Route 1 from home to school: two roads of 6 km and 9 km. Route 2: three roads of 3 km, 3 km and 5 km. How long is the SHORTER route, in km?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_relative_frequency
    label: "Relative frequency"
    strand: "Univariate data"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A spinner landed on red 18 times out of 90 spins. What is the relative frequency of red, as a fraction?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_energy_cost
    label: "Energy cost"
    strand: "Measurement and plans"
    prereqs: [au12e_scale_drawing]
    grounding: {}
    transfer_seeds:
      - "A heater uses 3 kWh every hour and runs for 10 hours. Electricity costs 40 cents per kWh. What is the total cost, in dollars?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12e_speed_distance_time
    label: "Distance from speed and time"
    strand: "Measurement and plans"
    prereqs: [au12e_energy_cost]
    grounding: {}
    transfer_seeds:
      - "A car travels at 100 km/h for 3.5 hours. How far does it go, in km?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Essential Maths — Year 12 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
