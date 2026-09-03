---
type: Mentar Curriculum Template
title: "Science — Grade 3 (the United States, general)"
tags: [US, science, "Grade 3", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — the United States, Grade 3 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what the United States teaches at Grade 3.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g3-science
country: US
year_level: "Grade 3"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Grade 3 (general)"
icon: "🔬"
description: "Life cycles, sources of heat, and where living things live — general science at roughly Grade 3 level."
item_source: us_g3_science

language_register:
  reading_level: "~ages 7-9"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-3
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[3], derived from
# engine/science_items.py's AU Year 3 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: us_g3_life_cycle
    label: "Life cycle stages"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a stage in a living thing's life cycle? A) a spoon  B) a chair  C) a tadpole  D) a rock. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g3_heat_sources
    label: "Sources of heat"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a source of heat? A) a window  B) a mirror  C) a stove  D) an ice cube. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g3_habitats
    label: "Where living things live (habitats)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these lives mainly on land? A) an octopus  B) a crab  C) a fish  D) a lion. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g3_landforms
    label: "Landforms"
    strand: "Earth's surface"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a BEACH? A) a sandy shore where waves wash in  B) a high rocky peak with steep sides  C) land with water all the way around it  D) fresh water flowing along a channel to the sea. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g3_animal_groups
    label: "Grouping animals"
    strand: "Grouping living things"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an INSECT (six legs)? A) a dog  B) a beetle  C) an emu  D) a magpie. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g3_material_groups
    label: "Grouping materials"
    strand: "Grouping materials"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is something sorted for RECYCLING? A) wood from trees  B) paper in the recycling bin  C) plastic made in a factory  D) wool from sheep. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# The United States — Grade 3 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Grade 3 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy.

Node ids are prefixed `us_g3_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
