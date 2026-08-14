---
type: Mentar Curriculum Template
title: "Science — Grade 4 (the United States, general)"
tags: [US, science, "Grade 4", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — the United States, Grade 4 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what the United States teaches at Grade 4.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g4-science
country: US
year_level: "Grade 4"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Grade 4 🇺🇸 (general)"
icon: "4️⃣"
description: "Producers and consumers, magnetic materials, and changes of state — general science at roughly Grade 4 level."
item_source: us_g4_science

language_register:
  reading_level: "~ages 8-10"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-4
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[4], derived from
# engine/science_items.py's AU Year 4 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: us_g4_food_chain_roles
    label: "Producers and consumers"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a consumer (eats other living things for food)? A) seaweed  B) a sunflower  C) a tree  D) a lion. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_magnetic_materials
    label: "Materials attracted to a magnet"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is attracted to a magnet? A) a glass marble  B) a rubber band  C) a steel spoon  D) a wooden pencil. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g4_state_change_heat
    label: "Changes of state — adding or removing heat"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is caused by REMOVING heat? A) water boiling into steam  B) chocolate melting in your hand  C) ice melting into water  D) water freezing into ice. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# The United States — Grade 4 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Grade 4 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy.

Node ids are prefixed `us_g4_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
