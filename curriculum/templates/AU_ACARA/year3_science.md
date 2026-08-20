---
type: Mentar Curriculum Template
title: "Science — Year 3 (AU)"
tags: [AU, science, "Year 3"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 3 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat year2_science.md
# already carries for its own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR3_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year3-science
country: AU
year_level: "Year 3"
subject: science
curriculum_standard: "ACARA v9 (AC9S3 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 3 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Life cycles, heat sources, and habitats (Australian Year 3 Science)."
item_source: au_science_year3

language_register:
  reading_level: "~Year 3 / ages 8-9"
  vocabulary_note: "Short sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 nodes: life cycles, heat sources, habitats -- all independent roots, same shape as
# year2_science.md's 3-node pattern.
concepts:

  - id: au3_science_life_cycle
    label: "Life cycle stages"                                       # AC9S3U01 (provisional)
    strand: "Life cycles"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a stage in a living thing's life cycle? A) an egg  B) a rock  C) a car  D) a chair. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_science_heat_sources
    label: "Sources of heat"                                         # AC9S3U02 (provisional)
    strand: "Heat"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a source of heat? A) the Sun  B) an ice cube  C) a fan  D) a mirror. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au3_science_habitats
    label: "Where living things live (habitats)"                     # AC9S3U03 (provisional)
    strand: "Habitats"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these lives mainly in water? A) a fish  B) a lion  C) a spider  D) a rabbit. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au3_science_landforms
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
  - id: au3_science_animal_groups
    label: "Grouping animals"
    strand: "Grouping living things"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an INSECT (six legs)? A) a magpie  B) a kangaroo  C) a dragonfly  D) an emu. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au3_science_material_groups
    label: "Grouping materials"
    strand: "Grouping materials"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a MANUFACTURED material? A) wood from trees  B) plastic made in a factory  C) empty cans collected for melting down  D) wool from sheep. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 3 Science

Extends `year2_science.md`'s proven 3-node shape one year further: life cycles and
habitats (Biological sciences) and heat sources (Physical sciences). Every node reuses
`engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, hand-verified pairwise-disjoint
fact table — the LLM never decides correctness (SPEC §14); a curated fact table is the
ground truth and `mc_choice` scores the letter against it.

**Alignment note:** the AC9S3U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md` already carries for its own codes. Question text, labels and fact tables
are Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
