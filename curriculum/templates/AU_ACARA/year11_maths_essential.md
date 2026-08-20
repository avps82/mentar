---
type: Mentar Curriculum Template
title: "Essential Maths — Year 11 (Australia, senior)"
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

template_id: au11-maths-essential
country: AU
year_level: "Year 11"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Essential Maths — Year 11 🇦🇺"
icon: "🧮"
description: "Everyday money, measurement and data — the practical senior course."
item_source: au11_essential

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au11e_percentage_of_money
    label: "Percentage of an amount"
    strand: "Consumer arithmetic"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A jacket costs $200. It is discounted by 50%. How many dollars do you save?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_best_buy
    label: "Best buy (unit price)"
    strand: "Consumer arithmetic"
    prereqs: [au11e_percentage_of_money]
    grounding: {}
    transfer_seeds:
      - "Pack A: 6 bars for $18. Pack B: 3 bars for $15. Which is the better buy (cheaper per bar)?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_wages_overtime
    label: "Wages with overtime"
    strand: "Consumer arithmetic"
    prereqs: [au11e_best_buy]
    grounding: {}
    transfer_seeds:
      - "Sam earns $26 per hour for a 8-hour shift, then time-and-a-half for 3 extra hours. How many dollars does Sam earn in total?"
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_simple_interest
    label: "Simple interest"
    strand: "Consumer arithmetic"
    prereqs: [au11e_wages_overtime]
    grounding: {}
    transfer_seeds:
      - "$5000 is invested at 3% simple interest per year for 3 years. How many dollars of interest does it earn?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_budget_balance
    label: "Budget leftover"
    strand: "Consumer arithmetic"
    prereqs: [au11e_simple_interest]
    grounding: {}
    transfer_seeds:
      - "Weekly income is $800. Rent is $260, food $150 and travel $80. How many dollars are left over each week?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_composite_area
    label: "Composite area (subtract the cut-out)"
    strand: "Measurement"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "An L-shaped floor is a 9 m by 7 m rectangle with a 2 m by 2 m corner removed. What is its area, in square metres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_volume_box
    label: "Volume of a box"
    strand: "Measurement"
    prereqs: [au11e_composite_area]
    grounding: {}
    transfer_seeds:
      - "A storage box is 4 m long, 4 m wide and 3 m high. What is its volume, in cubic metres?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_fuel_consumption
    label: "Fuel for a trip"
    strand: "Measurement"
    prereqs: [au11e_volume_box]
    grounding: {}
    transfer_seeds:
      - "A car uses 9 L of fuel per 100 km. How many litres does it use on a 500 km trip?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_time_duration
    label: "Finishing time"
    strand: "Measurement"
    prereqs: [au11e_fuel_consumption]
    grounding: {}
    transfer_seeds:
      - "A class starts at 10:30 and runs for 135 minutes. How many minutes past the hour does it finish? (Give just the minutes part of the finishing time.)"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11e_mean_of_data
    label: "Mean (average)"
    strand: "Univariate data"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Scores: 6, 11, 7, 10, 6. What is the mean score?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Essential Maths — Year 11 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
