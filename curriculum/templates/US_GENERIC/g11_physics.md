---
type: Mentar Curriculum Template
title: "Physics — Grade 11 (the United States, senior)"
tags: [US, physics, "Grade 11", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — the United States, Grade 11 Physics.
# SENIOR SCIENCE IS A SPLIT SUBJECT, and in the US it is also SEQUENCED. Junior
# grades ship one combined "Science" pack because that is what a student studies.
# High school does not: the common US pattern is a whole year on Biology (Grade
# 9), then Chemistry (Grade 10), then Physics (Grade 11) -- one subject at a
# time, rather than the three in parallel that Australia, India and Singapore
# run. So this pack is a FULL YEAR of physics: both senior stages of it,
# six nodes, where a parallel-country senior pack carries three.
# Grade 12 is deliberately not shipped -- it is electives (AP, anatomy,
# environmental science, or none), which has no single shape to model.
# NO claimed alignment: senior science is set by state boards and district frameworks,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior physics, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g11-physics
country: US
year_level: "Grade 11"
subject: physics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Physics — Grade 11 🇺🇸"
icon: "⚛️"
description: "Scalars and vectors, energy and Newton's laws, then circuits, the electromagnetic spectrum and conservation — senior physics at roughly Grade 11 level."
item_source: us_g11_physics

language_register:
  reading_level: "~ages 14-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 6 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: us_g11_scalars_vectors
    label: "Scalars and vectors"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a VECTOR quantity (it has a direction as well as a size)? A) velocity  B) mass  C) energy  D) distance. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g11_energy_forms
    label: "Forms of energy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these stores mainly gravitational potential energy? A) a book held above a desk  B) a moving car  C) a stretched rubber band  D) a compressed spring. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g11_newton_laws
    label: "Newton's laws of motion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of Newton's FIRST law (an object keeps doing what it is doing unless a force acts)? A) a swimmer pushing water back and moving forward  B) a harder kick giving the ball a greater acceleration  C) the same push accelerating a light trolley more than a heavy one  D) a puck sliding on frictionless ice at constant speed. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g11_circuits_series_parallel
    label: "Series and parallel circuits"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of a SERIES circuit? A) the same current flows through every component  B) each branch gets the full supply voltage  C) one lamp can fail while the others stay lit  D) the total current splits between the branches. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g11_em_spectrum
    label: "The electromagnetic spectrum"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these radiations is higher in energy than visible light? A) ultraviolet  B) infrared  C) microwaves  D) radio waves. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g11_conservation_collisions
    label: "What is conserved in a collision"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is conserved in every collision (total before = total after)? A) total momentum  B) total kinetic energy  C) the shape of the objects  D) the objects' separate speeds. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# the United States — Grade 11 Physics (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior physics at roughly this level.

Node ids are prefixed `us_g11_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
