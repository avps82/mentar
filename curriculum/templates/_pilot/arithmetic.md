---
type: Mentar Curriculum Template
title: "Pilot — Arithmetic"
tags: [pilot, mathematics]
timestamp: "2026-07-22T00:00:00Z"
# Mentar testing template — whole-number arithmetic (Phase 0 testing variety)
# Subject sibling to the fractions pilot; all items come from parametric generators
# (engine/itemgen.py ARITHMETIC_GENERATORS) so the deterministic verifier scores them.

template_id: pilot-arithmetic
country: null
year_level: pilot
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
label: "Maths: + − × 🔢"                             # R3.1: web picker catalog fields
icon: "🔢"
description: "Adding, subtracting, and multiplying numbers."
item_source: arithmetic

language_register:
  reading_level: "~Year 3-4 / ages 8-9"
  vocabulary_note: "Short sentences. Plain number words. One operation at a time."

# 3 concept nodes (small DAG): addition -> subtraction, addition -> multiplication.
concepts:

  - id: addition
    label: "Adding whole numbers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is 23 + 41?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: subtraction
    label: "Subtracting whole numbers"
    prereqs: [addition]
    grounding: {}
    transfer_seeds:
      - "What is 52 - 18?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: multiplication
    label: "Multiplying whole numbers"
    prereqs: [addition]
    grounding: {}
    transfer_seeds:
      - "What is 6 × 7?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors: { guess: 0.05, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Whole-number arithmetic (testing template)

A small math sibling to the fractions pilot, used to give product testing more than one
topic. Every question is generated parametrically with a computed answer, so the
deterministic verifier stays authoritative (no LLM in the correctness path).
