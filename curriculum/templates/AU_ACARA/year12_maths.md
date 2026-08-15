---
type: Mentar Curriculum Template
title: "Maths — Year 12 (AU)"
tags: [AU, mathematics, "Year 12"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 12 Mathematics (Algebra strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_items.py AU_YEAR12_GENERATORS),
# so the deterministic verifier scores every answer. Same derive-not-transform discipline
# as year9-11_maths.md — algebra APPLIED to a modelled scenario is the Year 12 step up.

template_id: au-year12-maths
country: AU
year_level: "Year 12"
subject: mathematics
curriculum_standard: "ACARA v9 (AC9M12 Algebra)"
schema_version: "0.1"
label: "Maths — Year 12 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔢"
description: "Revenue modelling, combining two quadratic expressions, and compound-shape area with a removed section (Australian Year 12)."
item_source: au_year12

language_register:
  reading_level: "~Year 12 / ages 17-18"
  vocabulary_note: "Clear sentences. Answer with an algebraic expression (e.g. 2x**2 + 8x)."

# 3 independent nodes (no natural prereq chain at this level). Algebra applied to modelled
# scenarios (revenue, compound shapes) is the Year 12-appropriate step up from Year 11's
# pure binomial/quadratic manipulation.
concepts:

  - id: au12_revenue_expression
    label: "Revenue as a quadratic expression"              # AC9M12A02 alignment
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
    prereqs: [au12_combine_two_quadratics]
    grounding: {}
    transfer_seeds:
      - "A garden is rectangular with width x and length (x + 6), but a square section of side 3 is removed from one corner for a path. Write an expression for the remaining garden area."
    verifier:
      answer_type: expression
      checker: expression_equiv
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 12 Mathematics (Algebra)

ACARA v9 Algebra strand, Year 12 — algebra APPLIED to a modelled scenario (a revenue
model, a compound shape with a removed section) rather than pure symbol manipulation,
the Year 12-appropriate step up from Year 11. Same derive-not-transform safety discipline
as every earlier expression-type template — see `engine/au_items.py`'s Year 9 section
docstring.

**Alignment note:** the AC9M12A02 code in the node comments is a reference to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
