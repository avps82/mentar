---
type: Mentar Curriculum Template
title: "Specialist Maths — Year 11 (Australia, senior)"
tags: [AU, mathematics, "Year 11", senior]
timestamp: "2026-08-21T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), W2 of
# docs/design/curriculum_depth_program.md: Methods + Specialist complete the
# four-course structure begun by W1 (Essential + General).
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).

template_id: au11-maths-specialist
country: AU
year_level: "Year 11"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Specialist Maths — Year 11 🇦🇺"
icon: "🧭"
description: "Combinatorics, vectors, complex numbers, proof and mechanics — the advanced senior course."
item_source: au11_specialist

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au11s_permutations
    label: "Permutations"
    strand: "Combinatorics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "How many ways can 3 different prizes be given to 3 of 4 people (one prize each, order matters)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_combinations
    label: "Combinations"
    strand: "Combinatorics"
    prereqs: [au11s_permutations]
    grounding: {}
    transfer_seeds:
      - "How many different teams of 2 can be chosen from 7 people (order does not matter)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_vector_add
    label: "Adding vectors"
    strand: "Vectors"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "For the vectors a = (3, 2) and b = (5, 2), what is the x-component of a + b?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_vector_magnitude
    label: "Magnitude of a vector"
    strand: "Vectors"
    prereqs: [au11s_vector_add]
    grounding: {}
    transfer_seeds:
      - "Find the magnitude of the vector (5, 12)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_complex_add
    label: "Adding complex numbers"
    strand: "Complex numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "For the complex numbers (5 + 2i) and (1 + 3i), what is the imaginary part of their sum?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_complex_multiply
    label: "Multiplying complex numbers"
    strand: "Complex numbers"
    prereqs: [au11s_complex_add]
    grounding: {}
    transfer_seeds:
      - "What is the real part of (4 + 2i)(3 + 1i)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_circle_angle
    label: "Angle at the centre"
    strand: "Circle geometry"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "An arc of a circle subtends an angle of 40° at the circumference. What angle, in degrees, does the same arc subtend at the centre?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_circle_radius
    label: "Radius from a circle equation"
    strand: "Circle geometry"
    prereqs: [au11s_circle_angle]
    grounding: {}
    transfer_seeds:
      - "The circle x² + y² = 81 has what radius?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_parity_proof
    label: "Parity proof"
    strand: "Proof"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "In a proof about parity, the sum of two odd numbers is…"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11s_counterexample
    label: "Finding a counterexample"
    strand: "Proof"
    prereqs: [au11s_parity_proof]
    grounding: {}
    transfer_seeds:
      - "To DISPROVE the claim “every multiple of 5 ends in the digit 5”, which number is a counterexample?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Specialist Maths — Year 11 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_ms_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
