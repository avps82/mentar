---
type: Mentar Curriculum Template
title: "Science — Year 8 (AU)"
tags: [AU, science, "Year 8"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 8 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat
# year2_science.md-year7_science.md already carry for their own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR8_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year8-science
country: AU
year_level: "Year 8"
subject: science
curriculum_standard: "ACARA v9 (AC9S8 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 8"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Plant/animal cell structures, renewable and non-renewable energy, and elements vs. compounds (Australian Year 8 Science)."
item_source: au_science_year8

language_register:
  reading_level: "~Year 8 / ages 13-14"
  vocabulary_note: "Clear sentences. Secondary-level vocabulary. Multiple-choice, answer with a letter."

# 3 nodes: cell structures, energy sources, elements/compounds -- all independent roots,
# same shape as year2_science.md through year7_science.md.
concepts:

  - id: au8_science_cell_structures
    label: "Plant and animal cell structures"                        # AC9S8U01 (provisional)
    strand: "Cells"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is found in a plant cell but not in an animal cell? A) a cell wall  B) a nucleus  C) mitochondria  D) a cell membrane. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_science_energy_sources
    label: "Renewable and non-renewable energy"                      # AC9S8U02 (provisional)
    strand: "Energy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a renewable energy source? A) solar power  B) coal  C) oil  D) natural gas. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au8_science_elements_compounds
    label: "Elements and compounds"                                  # AC9S8U03 (provisional)
    strand: "Elements and compounds"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an element (only one type of atom)? A) oxygen  B) water (H2O)  C) carbon dioxide (CO2)  D) table salt (NaCl). Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au8_science_organ_systems
    label: "Organ systems and their jobs"
    strand: "Body systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the job of the SKELETAL system? A) pulling on bones so the body can move  B) getting oxygen in and carbon dioxide out  C) breaking food down so it can be absorbed  D) holding the body up and protecting organs. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au8_science_reaction_signs
    label: "Signs of chemical reactions"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a SIGN a chemical reaction happened? A) sugar disappearing into tea  B) the mixture getting hot by itself  C) iron slowly rusting  D) ice melting into water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au8_science_rock_types
    label: "How rocks form"
    strand: "Rock cycle"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is how SEDIMENTARY rock forms? A) limestone baked deep underground until it becomes marble  B) lava from an eruption setting solid  C) mud and sand on a sea floor slowly cementing  D) an existing rock changed by heat and pressure underground. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 8 Science

Extends `year2_science.md`–`year7_science.md`'s proven 3-node shape one year further, and
**completes the AU Science Year 2-8 breadth** to match the maths and English packs' own
Y2-8 sequences: plant/animal cell structures (Biological sciences), renewable/non-renewable
energy sources (Physical sciences), and elements vs. compounds (Chemical sciences — builds
on `year7_science.md`'s pure-substance/mixture split: elements and compounds are BOTH pure
substances, a distinction mixtures sit outside of entirely). Every node reuses
`engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, hand-verified pairwise-disjoint
fact table — the LLM never decides correctness (SPEC §14).

**Alignment note:** the AC9S8U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md`–`year7_science.md` already carry for their own codes. Question text,
labels and fact tables are Mentar-authored. ACARA core curriculum content is CC BY 4.0
(verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced
in this template.
