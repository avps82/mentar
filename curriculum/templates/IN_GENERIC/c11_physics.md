---
type: Mentar Curriculum Template
title: "Physics — Class 11 (India, senior)"
tags: [IN, physics, "Class 11", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 11 Physics.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the CBSE/ICSE and state boards,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior physics, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c11-physics
country: IN
year_level: "Class 11"
subject: physics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Physics — Class 11"
icon: "⚛️"
description: "Scalars and vectors, forms of energy, and Newton's laws — senior physics at roughly Class 11 level."
item_source: in_c11_physics

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: in_c11_scalars_vectors
    label: "Scalars and vectors"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a VECTOR quantity (it has a direction as well as a size)? A) velocity  B) mass  C) energy  D) distance. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_energy_forms
    label: "Forms of energy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these stores mainly gravitational potential energy? A) a book held above a desk  B) a moving car  C) a stretched rubber band  D) a compressed spring. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_newton_laws
    label: "Newton's laws of motion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of Newton's FIRST law (an object keeps doing what it is doing unless a force acts)? A) a swimmer pushing water back and moving forward  B) a harder kick giving the ball a greater acceleration  C) the same push accelerating a light trolley more than a heavy one  D) a puck sliding on frictionless ice at constant speed. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_heating_processes
    label: "Heat transfer processes"
    strand: "Heating processes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of heat transfer by RADIATION (no matter needed at all)? A) feeling a campfire's warmth from metres away  B) water circulating as it boils in a pot  C) a metal spoon handle warming in hot soup  D) warm air rising above a heater. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_nuclear_radiation
    label: "Types of nuclear radiation"
    strand: "Nuclear physics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these describes ALPHA radiation (helium nuclei — heavy, stopped by paper)? A) the radiation stopped by a few millimetres of aluminium  B) an electromagnetic wave from the nucleus, not a particle  C) fast electrons ejected from a decaying nucleus  D) the most ionising but least penetrating type. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_circuit_quantities
    label: "Voltage, current and resistance"
    strand: "Electrical circuits"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these describes RESISTANCE (the opposition, measured in ohms)? A) the energy given to each coulomb of charge by the battery  B) what an ammeter placed in the loop reads  C) what makes a narrow wire harder for charge to pass through  D) what a voltmeter placed across a component reads. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 11 Physics (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior physics at roughly this level.

Node ids are prefixed `in_c11_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
