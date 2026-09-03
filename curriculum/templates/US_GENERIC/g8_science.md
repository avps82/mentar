---
type: Mentar Curriculum Template
title: "Science — Grade 8 (the United States, general)"
tags: [US, science, "Grade 8", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — the United States, Grade 8 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what the United States teaches at Grade 8.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g8-science
country: US
year_level: "Grade 8"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Grade 8 (general)"
icon: "🔬"
description: "Plant and animal cells, renewable energy, and elements and compounds — general science at roughly Grade 8 level."
item_source: us_g8_science

language_register:
  reading_level: "~ages 12-14"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-8
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[8], derived from
# engine/science_items.py's AU Year 8 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: us_g8_cell_structures
    label: "Plant and animal cell structures"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is found in both plant and animal cells? A) a cell membrane  B) a cell wall  C) a chloroplast  D) a large permanent vacuole. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_energy_sources
    label: "Renewable and non-renewable energy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a non-renewable energy source? A) biomass  B) hydroelectric power  C) solar power  D) coal. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g8_elements_compounds
    label: "Elements and compounds"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a compound (two or more elements chemically joined)? A) carbon  B) gold  C) oxygen  D) water (H2O). Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g8_organ_systems
    label: "Organ systems and their jobs"
    strand: "Body systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the job of the DIGESTIVE system? A) holding the body up and protecting organs  B) breaking food down so it can be absorbed  C) pulling on bones so the body can move  D) getting oxygen in and carbon dioxide out. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g8_reaction_signs
    label: "Signs of chemical reactions"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an everyday CHEMICAL reaction? A) the mixture getting hot by itself  B) a cake rising as it bakes  C) gas bubbles forming in the mixture  D) sugar disappearing into tea. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g8_rock_types
    label: "How rocks form"
    strand: "Rock cycle"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is how SEDIMENTARY rock forms? A) molten rock cooling and hardening  B) lava from an eruption setting solid  C) mud and sand on a sea floor slowly cementing  D) limestone baked deep underground until it becomes marble. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# The United States — Grade 8 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Grade 8 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy.

Node ids are prefixed `us_g8_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
