---
type: Mentar Curriculum Template
title: "Science — Class 8 (India, general)"
tags: [IN, science, "Class 8", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 8 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 8.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c8-science
country: IN
year_level: "Class 8"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 8 🇮🇳 (general)"
icon: "🔬"
description: "Plant and animal cells, renewable energy, and elements and compounds — general science at roughly Class 8 level."
item_source: in_c8_science

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

  - id: in_c8_cell_structures
    label: "Plant and animal cell structures"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is found in both plant and animal cells? A) a cell membrane  B) a cell wall  C) a chloroplast  D) a large permanent vacuole. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_energy_sources
    label: "Renewable and non-renewable energy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a non-renewable energy source? A) biomass  B) hydroelectric power  C) solar power  D) coal. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c8_elements_compounds
    label: "Elements and compounds"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a compound (two or more elements chemically joined)? A) carbon  B) gold  C) oxygen  D) water (H2O). Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c8_organ_systems
    label: "Organ systems and their jobs"
    strand: "Body systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the job of the SKELETAL system? A) getting oxygen in and carbon dioxide out  B) pulling on bones so the body can move  C) holding the body up and protecting organs  D) breaking food down so it can be absorbed. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c8_reaction_signs
    label: "Signs of chemical reactions"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PHYSICAL change, not a reaction? A) a cake rising as it bakes  B) an unexpected colour change  C) iron slowly rusting  D) ice melting into water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c8_rock_types
    label: "How rocks form"
    strand: "Rock cycle"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is how SEDIMENTARY rock forms? A) an existing rock changed by heat and pressure underground  B) limestone baked deep underground until it becomes marble  C) mud and sand on a sea floor slowly cementing  D) lava from an eruption setting solid. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 8 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 8 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c8_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
