---
type: Mentar Curriculum Template
title: "Science — Year 9 (AU)"
tags: [AU, science, "Year 9"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 9 Science.
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes are
# alignment REFERENCES and PROVISIONAL for this year level; all labels and
# questions are Mentar-authored — see docs/CONTENT_LICENSES.md; ACARA core
# content is CC BY 4.0).
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR9_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while science stopped at Year 8, a gap nobody had ratified.

template_id: au-year9-science
country: AU
year_level: "Year 9"
subject: science
curriculum_standard: "ACARA v9 (AC9S9U, provisional)"
schema_version: "0.1"
label: "Science — Year 9 🇦🇺"
icon: "🔬"
description: "Inside the atom, wave types, and the landforms plate boundaries make (Australian Year 9)."
item_source: au_science_year9

language_register:
  reading_level: "~Year 9 / ages 14-15"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 3 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU science template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: au9_science_atomic_structure
    label: "Inside the atom — protons, neutrons, electrons"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a particle found in the NUCLEUS of an atom? A) an electron  B) a molecule  C) a compound  D) a proton. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au9_science_wave_types
    label: "Transverse and longitudinal waves"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a longitudinal wave (the wave moves along the direction of travel)? A) a light wave  B) a wave on a shaken rope  C) a sound wave in air  D) a water ripple. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au9_science_plate_boundaries
    label: "Plate boundaries and the landforms they make"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these landforms is caused by plates sliding PAST each other? A) a transform fault  B) a mid-ocean ridge  C) a rift valley  D) a volcanic island arc. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 9 Science

Aligned to ACARA v9 content descriptions as REFERENCES only — every label and
question is Mentar-authored, and the codes are **provisional** for Year 9.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
