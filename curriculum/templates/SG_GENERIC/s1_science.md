---
type: Mentar Curriculum Template
title: "Science — Secondary 1 (Singapore, general)"
tags: [SG, science, "Secondary 1", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 1 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what Singapore teaches at Secondary 1.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-s1-science
country: SG
year_level: "Secondary 1"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Secondary 1 (general)"
icon: "🔬"
description: "Body systems, contact and non-contact forces, and mixtures — general science at roughly Secondary 1 level."
item_source: sg_s1_science

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

  - id: sg_s1_body_systems
    label: "Digestive and circulatory systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of the circulatory system? A) the liver  B) the oesophagus  C) the stomach  D) the heart. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_forces
    label: "Contact and non-contact forces"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a non-contact force (acts at a distance)? A) pulling a rope  B) friction between shoes and the ground  C) pushing a door  D) magnetism pulling a paperclip. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s1_mixtures
    label: "Pure substances and mixtures"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a mixture (more than one substance mixed together)? A) table salt (sodium chloride)  B) distilled water  C) oxygen gas  D) salt water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s1_vertebrate_groups
    label: "Vertebrate groups"
    strand: "Classification"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REPTILE? A) it has dry scales and lays leathery eggs on land  B) it starts life in water and moves onto land as an adult  C) the platypus  D) it breathes through gills its whole life. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s1_sky_patterns
    label: "Patterns in the sky"
    strand: "Earth Moon and Sun"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PHASE of the Moon? A) day turning into night  B) a half-lit Moon a week after new moon  C) the stars seeming to wheel across the night sky  D) summer changing to winter. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s1_ecosystem_relationships
    label: "Ecosystem relationships"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PREDATOR-and-prey relationship? A) a spider trapping flies in its web  B) two seedlings racing each other for light  C) a cleaner fish eating parasites off a larger fish  D) a bee feeding while pollinating the flower. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s1_water_cycle
    label: "Water on the move"
    strand: "Water and resources"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a way to use water WISELY? A) watering gardens at dusk so less evaporates  B) a rainwater tank by a shed  C) rain falling from cooling clouds  D) water evaporating from the sea. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Secondary 1 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Secondary 1 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_s1_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
