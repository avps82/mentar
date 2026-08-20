---
type: Mentar Curriculum Template
title: "Science — Year 10 (AU)"
tags: [AU, science, "Year 10"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 10 Science.
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes are
# alignment REFERENCES and PROVISIONAL for this year level; all labels and
# questions are Mentar-authored — see docs/CONTENT_LICENSES.md; ACARA core
# content is CC BY 4.0).
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR10_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while science stopped at Year 8, a gap nobody had ratified.

template_id: au-year10-science
country: AU
year_level: "Year 10"
subject: science
curriculum_standard: "ACARA v9 (AC9S10U, provisional)"
schema_version: "0.1"
label: "Science — Year 10 🇦🇺"
icon: "🔬"
description: "DNA and genes, evidence for evolution, and types of chemical reaction (Australian Year 10)."
item_source: au_science_year10

language_register:
  reading_level: "~Year 10 / ages 15-16"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 3 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU science template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: au10_science_genetic_molecules
    label: "DNA, genes and chromosomes"
    strand: "Genetics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a molecule that carries genetic information? A) DNA  B) an enzyme  C) haemoglobin  D) insulin. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au10_science_evolution_evidence
    label: "Evidence for evolution"
    strand: "Evolution"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is evidence for evolution over time? A) fossils in dated rock layers  B) the phases of the Moon  C) the colour of a painted wall  D) the price of fossil fuels. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au10_science_reaction_types
    label: "Types of chemical reaction"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a precipitation reaction? A) two solutions mixing to make an insoluble solid  B) methane burning in air  C) a candle burning  D) indigestion tablets reacting with stomach acid. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 10 Science

Aligned to ACARA v9 content descriptions as REFERENCES only — every label and
question is Mentar-authored, and the codes are **provisional** for Year 10.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
