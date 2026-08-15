---
type: Mentar Curriculum Template
title: "Science — Class 9 (India, general)"
tags: [IN, science, "Class 9", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 9 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 9.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c9-science
country: IN
year_level: "Class 9"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 9 🇮🇳 (general)"
icon: "9️⃣"
description: "Inside the atom, wave types, and the landforms plate boundaries make — general science at roughly Class 9 level."
item_source: in_c9_science

language_register:
  reading_level: "~ages 14-15"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-9
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[9], derived from
# engine/science_items.py's AU Year 9 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: in_c9_atomic_structure
    label: "Inside the atom — protons, neutrons, electrons"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a particle found in the NUCLEUS of an atom? A) an electron  B) a molecule  C) a compound  D) a proton. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_wave_types
    label: "Transverse and longitudinal waves"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a longitudinal wave (the wave moves along the direction of travel)? A) a light wave  B) a wave on a shaken rope  C) a sound wave in air  D) a water ripple. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_plate_boundaries
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

# India — Class 9 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 9 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c9_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
