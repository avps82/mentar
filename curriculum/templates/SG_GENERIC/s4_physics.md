---
type: Mentar Curriculum Template
title: "Physics — Secondary 4 (Singapore, senior)"
tags: [SG, physics, "Secondary 4", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 4 Physics.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the Singapore-Cambridge examination syllabuses,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior physics, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-s4-physics
country: SG
year_level: "Secondary 4"
subject: physics
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Physics — Secondary 4 🇸🇬"
icon: "⚛️"
description: "Series and parallel circuits, the electromagnetic spectrum, and conservation in collisions — senior physics at roughly Secondary 4 level."
item_source: sg_s4_physics

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: sg_s4_circuits_series_parallel
    label: "Series and parallel circuits"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of a SERIES circuit? A) the same current flows through every component  B) each branch gets the full supply voltage  C) one lamp can fail while the others stay lit  D) the total current splits between the branches. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s4_em_spectrum
    label: "The electromagnetic spectrum"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these radiations is higher in energy than visible light? A) ultraviolet  B) infrared  C) microwaves  D) radio waves. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s4_conservation_collisions
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

# Singapore — Secondary 4 Physics (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior physics at roughly this level.

Node ids are prefixed `sg_s4_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
