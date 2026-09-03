---
type: Mentar Curriculum Template
title: "Physics — Year 12 (Australia, senior)"
tags: [AU, physics, "Year 12", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Australia, Year 12 Physics.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by state certificate authorities (VCE/HSC/QCE/SACE),
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior physics, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: au12-physics
country: AU
year_level: "Year 12"
subject: physics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Physics — Year 12"
icon: "⚛️"
description: "Series and parallel circuits, the electromagnetic spectrum, and conservation in collisions — senior physics at roughly Year 12 level."
item_source: au12_physics

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: au12_circuits_series_parallel
    label: "Series and parallel circuits"
    strand: "Electrical circuits"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of a SERIES circuit? A) the same current flows through every component  B) each branch gets the full supply voltage  C) one lamp can fail while the others stay lit  D) the total current splits between the branches. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au12_em_spectrum
    label: "The electromagnetic spectrum"
    strand: "Electromagnetism"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these radiations is higher in energy than visible light? A) ultraviolet  B) infrared  C) microwaves  D) radio waves. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au12_conservation_collisions
    label: "What is conserved in a collision"
    strand: "Momentum"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is conserved in every collision (total before = total after)? A) total momentum  B) total kinetic energy  C) the shape of the objects  D) the objects' separate speeds. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_gravity_fields
    label: "Gravity and orbits"
    strand: "Gravity"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of a gravitational FIELD? A) a satellite is continually falling toward Earth while moving sideways fast enough to keep missing it  B) it changes when you move to the Moon; your mass does not  C) it points toward the mass creating it  D) the Moon is held in its path by Earth's gravity alone. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_wave_properties
    label: "Wave properties"
    strand: "Waves"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a property of wave FREQUENCY? A) what determines how loud a sound or bright a light is  B) the distance from one crest to the next  C) measured in hertz  D) measured in metres. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_quantum_ideas
    label: "Quantum ideas"
    strand: "Quantum"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a quantum idea about ATOMS? A) light energy arriving in discrete lumps proportional to frequency  B) light spreading out after passing a narrow gap  C) electrons occupying only fixed energy levels  D) the double-slit experiment producing an interference pattern. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_relativity_ideas
    label: "Special relativity"
    strand: "Special relativity"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a CONSEQUENCE of special relativity? A) GPS satellite clocks needing correction to stay accurate  B) the speed of light in a vacuum is the same for every observer  C) the laws of physics are the same in every non-accelerating frame  D) a fast-moving object is measured shorter along its direction of travel. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 12 Physics (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior physics at roughly this level.

Node ids are prefixed `au12_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
