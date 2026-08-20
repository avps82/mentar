---
type: Mentar Curriculum Template
title: "Science — Class 7 (India, general)"
tags: [IN, science, "Class 7", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 7 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 7.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c7-science
country: IN
year_level: "Class 7"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 7 🇮🇳 (general)"
icon: "🔬"
description: "Body systems, contact and non-contact forces, and mixtures — general science at roughly Class 7 level."
item_source: in_c7_science

language_register:
  reading_level: "~ages 11-13"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-7
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[7], derived from
# engine/science_items.py's AU Year 7 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: in_c7_body_systems
    label: "Digestive and circulatory systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of the circulatory system? A) the liver  B) the oesophagus  C) the stomach  D) the heart. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_forces
    label: "Contact and non-contact forces"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a non-contact force (acts at a distance)? A) pulling a rope  B) friction between shoes and the ground  C) pushing a door  D) magnetism pulling a paperclip. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c7_mixtures
    label: "Pure substances and mixtures"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a mixture (more than one substance mixed together)? A) table salt (sodium chloride)  B) distilled water  C) oxygen gas  D) salt water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c7_vertebrate_groups
    label: "Vertebrate groups"
    strand: "Classification"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a FISH? A) it breathes through gills its whole life  B) it starts life in water and moves onto land as an adult  C) the platypus  D) it has dry scales and lays leathery eggs on land. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c7_sky_patterns
    label: "Patterns in the sky"
    strand: "Earth Moon and Sun"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PHASE of the Moon? A) the stars seeming to wheel across the night sky  B) day turning into night  C) summer changing to winter  D) a thin crescent growing to a full moon over two weeks. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c7_ecosystem_relationships
    label: "Ecosystem relationships"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is COMPETITION between organisms? A) a spider trapping flies in its web  B) a bee feeding while pollinating the flower  C) two magpies squabbling over the same territory  D) a cleaner fish eating parasites off a larger fish. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c7_water_cycle
    label: "Water on the move"
    strand: "Water and resources"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of the WATER CYCLE? A) rain falling from cooling clouds  B) a rainwater tank by a shed  C) a dam across a river valley  D) watering gardens at dusk so less evaporates. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 7 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 7 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c7_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
