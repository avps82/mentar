---
type: Mentar Curriculum Template
title: "Specialist Maths — Year 12 (Australia, senior)"
tags: [AU, mathematics, "Year 12", senior]
timestamp: "2026-08-21T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), W2 of
# docs/design/curriculum_depth_program.md: Methods + Specialist complete the
# four-course structure begun by W1 (Essential + General).
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).

template_id: au12-maths-specialist
country: AU
year_level: "Year 12"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Specialist Maths — Year 12 🇦🇺"
icon: "🧭"
description: "Combinatorics, vectors, complex numbers, proof and mechanics — the advanced senior course."
item_source: au12_specialist

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au12s_vector3_magnitude
    label: "Magnitude of a 3d vector"
    strand: "Vectors in 3D"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Find the magnitude of the 3D vector (1, 2, 2)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_dot_product
    label: "Dot product"
    strand: "Vectors in 3D"
    prereqs: [au12s_vector3_magnitude]
    grounding: {}
    transfer_seeds:
      - "Find the dot product of a = (2, 4, 3) and b = (3, 3, 2)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_complex_modulus
    label: "Modulus of a complex number"
    strand: "Complex numbers polar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Find the modulus of the complex number 5 + 12i."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_polar_argument
    label: "Argument of a complex number"
    strand: "Complex numbers polar"
    prereqs: [au12s_complex_modulus]
    grounding: {}
    transfer_seeds:
      - "On an Argand diagram, what is the argument of the complex number 1 + i?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_second_derivative
    label: "Second derivative"
    strand: "Advanced calculus"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If f(x) = 1x³, find the second derivative f″(5)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_integral_3x_squared
    label: "Integral of 3x²"
    strand: "Advanced calculus"
    prereqs: [au12s_second_derivative]
    grounding: {}
    transfer_seeds:
      - "Evaluate the definite integral of 3x² from x = 0 to x = 5."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_force_ma
    label: "Force from mass and acceleration"
    strand: "Mechanics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A 5 kg mass accelerates at 4 m/s². What net force, in newtons (N), acts on it?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_momentum
    label: "Momentum"
    strand: "Mechanics"
    prereqs: [au12s_force_ma]
    grounding: {}
    transfer_seeds:
      - "A 3 kg object moves at 8 m/s. What is its momentum, in kg·m/s?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_sampling_mean
    label: "Mean of the sampling distribution"
    strand: "Sampling distributions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A population has mean 60. Samples of size 16 are repeatedly drawn. What is the mean of the sampling distribution of the sample mean?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12s_se_sampling
    label: "Spread of the sampling distribution"
    strand: "Sampling distributions"
    prereqs: [au12s_sampling_mean]
    grounding: {}
    transfer_seeds:
      - "A population has standard deviation 20. For samples of size 16, what is the standard deviation of the sampling distribution (the standard error)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Specialist Maths — Year 12 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_ms_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
