---
type: Mentar Curriculum Template
title: "Maths Methods — Year 11 (Australia, senior)"
tags: [AU, mathematics, "Year 11", senior]
timestamp: "2026-08-21T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), W2 of
# docs/design/curriculum_depth_program.md: Methods + Specialist complete the
# four-course structure begun by W1 (Essential + General).
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).
# The 'Algebra foundations' strand holds the nodes absorbed verbatim from the
# retired merged year11_maths template — SAME ids, so learner mastery survives.

template_id: au11-maths-methods
country: AU
year_level: "Year 11"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Maths Methods — Year 11 🇦🇺"
icon: "📈"
description: "Functions, trigonometric functions, calculus and probability — the mainstream senior course."
item_source: au11_methods

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au11m_function_value
    label: "Evaluating a function"
    strand: "Functions and graphs"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "For the function f(x) = x² + 2x + 5, find f(4)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_line_gradient
    label: "Gradient between two points"
    strand: "Functions and graphs"
    prereqs: [au11m_function_value]
    grounding: {}
    transfer_seeds:
      - "A straight line passes through (3, 2) and (5, 12). What is its gradient?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_quadratic_vertex
    label: "Vertex of a parabola"
    strand: "Functions and graphs"
    prereqs: [au11m_line_gradient]
    grounding: {}
    transfer_seeds:
      - "The parabola y = x² − 4x + 3 has its vertex at x = ?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_exact_trig
    label: "Exact trig values"
    strand: "Trigonometric functions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is the exact value of cos 90°?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_trig_period
    label: "Period of a sine graph"
    strand: "Trigonometric functions"
    prereqs: [au11m_exact_trig]
    grounding: {}
    transfer_seeds:
      - "What is the period, in degrees, of y = sin(3x°)?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_derivative_power
    label: "Derivative of a power"
    strand: "Differential calculus"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If f(x) = 4x³, find f′(4)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_curve_gradient
    label: "Gradient of a curve"
    strand: "Differential calculus"
    prereqs: [au11m_derivative_power]
    grounding: {}
    transfer_seeds:
      - "Find the gradient of the curve y = x² + 4x at the point where x = 3."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_increasing_decreasing
    label: "Increasing or decreasing"
    strand: "Differential calculus"
    prereqs: [au11m_curve_gradient]
    grounding: {}
    transfer_seeds:
      - "The curve y = x² − 6x has derivative dy/dx = 2x − 6. At x = 6, is the curve increasing or decreasing?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_two_coin_prob
    label: "Probability with two coins"
    strand: "Discrete probability"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Two fair coins are tossed. What is the probability of getting two tails? Give your answer as a decimal."
    verifier:
      answer_type: decimal
      checker: decimal_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11m_expected_value
    label: "Expected value"
    strand: "Discrete probability"
    prereqs: [au11m_two_coin_prob]
    grounding: {}
    transfer_seeds:
      - "A fair spinner shows 1, 2, 3 or 6, each with probability 1/4. What is the expected value?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_binomial_product_area
    label: "Area as an algebraic expression (binomial sides)"  # AC9M11A02 alignment
    strand: \"Algebra foundations\"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A rectangle has width (x + 2) and length (x + 5). Write an expression for its area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_word_to_quadratic_expression
    label: "Writing quadratic expressions from words"       # AC9M11A02 alignment
    strand: \"Algebra foundations\"
    prereqs: [au11_binomial_product_area]
    grounding: {}
    transfer_seeds:
      - "Write an algebraic expression for: the square of a number x, plus 4 times the number, minus 7."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_combine_quadratic_linear
    label: "Combining a quadratic and a linear expression"  # AC9M11A02 alignment
    strand: \"Algebra foundations\"
    prereqs: [au11_word_to_quadratic_expression]
    grounding: {}
    transfer_seeds:
      - "If a = 2x**2 + 3x and b = 4x + 5, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_difference_of_expressions
    label: "Difference of two related expressions"          # AC9M11A02 alignment
    strand: \"Algebra foundations\"
    prereqs: [au11_combine_quadratic_linear]
    grounding: {}
    transfer_seeds:
      - "A number is x. A second number is 3 times x, minus 4. Write an expression for the SECOND number minus the FIRST number."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Maths Methods — Year 11 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_ms_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
