---
type: Mentar Curriculum Template
title: "Science — Class 10 (India, general)"
tags: [IN, science, "Class 10", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 10 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 10.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c10-science
country: IN
year_level: "Class 10"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 10 🇮🇳 (general)"
icon: "🔬"
description: "DNA and genes, evidence for evolution, and types of chemical reaction — general science at roughly Class 10 level."
item_source: in_c10_science

language_register:
  reading_level: "~ages 15-16"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-10
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[10], derived from
# engine/science_items.py's AU Year 10 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: in_c10_genetic_molecules
    label: "DNA, genes and chromosomes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a molecule that carries genetic information? A) DNA  B) an enzyme  C) haemoglobin  D) insulin. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_evolution_evidence
    label: "Evidence for evolution"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is evidence for evolution over time? A) fossils in dated rock layers  B) the phases of the Moon  C) the colour of a painted wall  D) the price of fossil fuels. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_reaction_types
    label: "Types of chemical reaction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a precipitation reaction? A) two solutions mixing to make an insoluble solid  B) methane burning in air  C) a candle burning  D) indigestion tablets reacting with stomach acid. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_bond_kinds
    label: "Kinds of chemical bond"
    strand: "Chemical bonding"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is where METALLIC bonding happens? A) in a metal: a lattice in a sea of free electrons  B) between non-metals, sharing electron pairs  C) between a metal and a non-metal, swapping electrons  D) in table salt, where sodium hands chlorine an electron. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_global_systems
    label: "Global systems"
    strand: "Global systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the ENHANCED greenhouse effect? A) extra fossil-fuel gases trapping extra heat  B) forests absorbing carbon dioxide as they grow  C) the sea soaking up most of the trapped extra heat  D) burning coal returning ancient carbon to the air. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_motion
    label: "Describing motion"
    strand: "Motion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an object DECELERATING? A) a dropped stone falling faster and faster  B) a train braking smoothly into a station  C) a sprinter pulling away from the blocks  D) a car cruising with the speedo needle steady. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_periodic_table
    label: "Reading the periodic table"
    strand: "Periodic table"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of the NOBLE gases? A) across it, elements shift from metal to non-metal  B) lithium, sodium and potassium all sit in it together  C) helium and neon are among them  D) its elements share similar chemical behaviour. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_universe
    label: "The universe"
    strand: "Universe"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of a LIGHT-YEAR? A) faint leftover heat filling the whole sky  B) billions of stars held together by gravity  C) our Sun sits in one called the Milky Way  D) it measures distance — how far light travels in a year. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 10 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 10 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c10_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
