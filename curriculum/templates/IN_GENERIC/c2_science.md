---
type: Mentar Curriculum Template
title: "Science — Class 2 (India, general)"
tags: [IN, science, "Class 2", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 2 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 2.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c2-science
country: IN
year_level: "Class 2"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 2 🇮🇳 (general)"
icon: "2️⃣"
description: "Sound and vibration, Earth in the solar system, and changing a material's shape — general science at roughly Class 2 level."
item_source: in_c2_science

language_register:
  reading_level: "~ages 6-8"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-2
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[2], derived from
# engine/science_items.py's AU Year 2 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: in_c2_sound
    label: "How sound is made (vibration)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these makes a sound by vibrating? A) a chair  B) a pillow  C) a bell  D) a rock. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_solar_system
    label: "Earth is a planet in the solar system"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a planet? A) a star  B) a comet  C) Jupiter  D) the Sun. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c2_materials
    label: "Changing a material's shape (bend, twist, stretch)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these stays the same shape unless broken? A) a piece of string  B) playdough  C) a rubber band  D) a glass cup. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 2 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 2 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c2_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
