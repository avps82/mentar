---
type: Mentar Curriculum Template
title: "Science — Year 2 (AU)"
tags: [AU, science, "Year 2"]
timestamp: "2026-08-10T00:00:00Z"
# Mentar curriculum template — Australia, Year 2 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# (2026-08-10): all 3 planned Year 2 Science topics now covered — sound, solar system,
# and changing materials.
# All items come from parametric generators (engine/science_items.py SCIENCE_GENERATORS),
# so the deterministic verifier scores every answer.

template_id: au-year2-science
country: AU
year_level: "Year 2"
subject: science
curriculum_standard: "ACARA v9 (AC9S2 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 2"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "How sound is made, the solar system, and how
   materials change shape (Australian Year 2 Science)."
item_source: au_science_year2

language_register:
  reading_level: "~Year 2 / ages 6-7"
  vocabulary_note: "Very short sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 nodes: sound, solar system, and materials — all independent roots.
concepts:

  - id: au2_science_sound
    label: "How sound is made (vibration)"                          # AC9S2U02
    strand: "Sound"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these makes a sound by vibrating? A) a guitar string  B) a rock  C) a pillow  D) a book. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_science_solar_system
    label: "Earth is a planet in the solar system"                  # AC9S2U01
    strand: "Space"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these IS a planet? A) the Sun  B) Earth  C) the Moon  D) a comet. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au2_science_materials
    label: "Changing a material's shape (bend, twist, stretch)"     # AC9S2U03
    strand: "Materials"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these can be bent, twisted or stretched? A) a rubber band  B) a glass cup  C) a wooden ruler  D) a ceramic plate. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_science_how_things_move
    label: "How things move"
    strand: "Forces and motion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is something that ROLLS? A) a log rolling down a hill  B) a coin skidding across ice  C) a ball dropped straight down onto concrete  D) a basketball dribbled on the spot. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_science_young_animals
    label: "Animals and their young"
    strand: "Life cycles"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the young of a CHICKEN? A) a chick hatching from its egg  B) a caterpillar munching a leaf  C) a tadpole swimming in a pond  D) a joey in its mother's pouch. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au2_science_saving_water
    label: "Caring for water"
    strand: "Resources"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a way to SAVE water? A) hosing the path instead of sweeping it  B) watering the vegetable garden  C) a dripping tap left unfixed  D) a short shower instead of a long one. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 2 Science

Covers all 3 planned Year 2 Science topics: sound, the solar system, and changing materials.

**Alignment note:** the AC9S2U01/AC9S2U02/AC9S2U03 codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and generators are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
AC9S2U01/AC9S2U03 codes and content descriptions were identified via web search (QCAA/ACARA alignment documents), not fetched verbatim from the primary ACARA site (blocked to automated fetch) — treat as provisional pending a direct-source check before wider release, same as every other code cited in this repo's templates is expected to be dated and sourced.
