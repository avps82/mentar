---
type: Mentar Curriculum Template
title: "Maths Methods — Year 12 (Australia, senior)"
tags: [AU, mathematics, "Year 12", senior]
timestamp: "2026-08-21T00:00:00Z"
# SENIOR MATHS IS A SPLIT SUBJECT (maintainer decision 2026-08-20), W2 of
# docs/design/curriculum_depth_program.md: Methods + Specialist complete the
# four-course structure begun by W1 (Essential + General).
# NO claimed alignment: senior courses are set by state certificate authorities
# (VCE/HSC/QCE/SACE); course names/strands follow the common national structure,
# content is 100% Mentar-authored (docs/CONTENT_LICENSES.md §2b posture).
# The 'Algebra foundations' strand holds the nodes absorbed verbatim from the
# retired merged year12_maths template — SAME ids, so learner mastery survives.

template_id: au12-maths-methods
country: AU
year_level: "Year 12"
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Maths Methods — Year 12 🇦🇺"
icon: "📈"
description: "Functions, trigonometric functions, calculus and probability — the mainstream senior course."
item_source: au12_methods

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au12m_chain_rule
    label: "Chain rule"
    strand: "Further differentiation"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "If f(x) = (2x + 1)², find f′(2)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_product_rule
    label: "Product rule for derivatives"
    strand: "Further differentiation"
    prereqs: [au12m_chain_rule]
    grounding: {}
    transfer_seeds:
      - "Using the product rule, find f′(3) for f(x) = x(x + 5)."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_stationary_point
    label: "Stationary point"
    strand: "Further differentiation"
    prereqs: [au12m_product_rule]
    grounding: {}
    transfer_seeds:
      - "Find the x-value of the stationary point of y = x² − 12x + 1."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_integral_2x
    label: "Integral of 2x"
    strand: "Integral calculus"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Evaluate the definite integral of 2x from x = 0 to x = 4."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_integral_x_squared
    label: "Integral of x²"
    strand: "Integral calculus"
    prereqs: [au12m_integral_2x]
    grounding: {}
    transfer_seeds:
      - "Evaluate the definite integral of x² from x = 0 to x = 6."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_area_under_line
    label: "Area under a line"
    strand: "Integral calculus"
    prereqs: [au12m_integral_x_squared]
    grounding: {}
    transfer_seeds:
      - "Find the area between the line y = 1x and the x-axis, from x = 0 to x = 4."
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_binomial_mean
    label: "Mean of a binomial"
    strand: "Random variables"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A binomial random variable has n = 50 trials, each with success probability p = 0.2. What is its mean?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_die_expected
    label: "Expected value of a die"
    strand: "Random variables"
    prereqs: [au12m_binomial_mean]
    grounding: {}
    transfer_seeds:
      - "A fair 11-sided die shows the numbers 1 to 11. What is the expected value of one roll?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_standard_error
    label: "Standard error"
    strand: "Statistical inference"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A population has standard deviation 12. A sample of 9 values is taken. What is the standard error of the sample mean?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12m_ci_concept
    label: "Confidence intervals"
    strand: "Statistical inference"
    prereqs: [au12m_standard_error]
    grounding: {}
    transfer_seeds:
      - "A confidence interval for a population mean is recalculated after the sample size n is decreased, with everything else unchanged. The new interval is…"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.2, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_revenue_expression
    label: "Revenue as a quadratic expression"              # AC9M12A02 alignment
    strand: \"Algebra foundations\"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "A shop sells items for $x each. On a day they sell (3x + 4) items. Write an expression for the total revenue (price times number sold)."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_combine_two_quadratics
    label: "Combining two quadratic expressions"            # AC9M12A02 alignment
    strand: \"Algebra foundations\"
    prereqs: [au12_revenue_expression]
    grounding: {}
    transfer_seeds:
      - "If a = 2x**2 + 3x + 1 and b = 3x**2 + 4x + 2, what is a + b? Give your answer as a simplified expression."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_compound_shape_area
    label: "Compound-shape area as an algebraic expression"  # AC9M12A02 alignment
    strand: \"Algebra foundations\"
    prereqs: [au12_combine_two_quadratics]
    grounding: {}
    transfer_seeds:
      - "A garden is rectangular with width x and length (x + 6), but a square section of side 3 is removed from one corner for a path. Write an expression for the remaining garden area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Maths Methods — Year 12 (Australia)

Senior maths, split by course (see the frontmatter note). Topics are grouped by
`strand:`; items come from `engine/au_senior_maths_ms_items.py` parametric
generators, so the deterministic verifier scores every answer and every topic
carries a formula-first method card.
