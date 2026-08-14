---
type: Mentar Curriculum Template
title: "Biology — Class 11 (India, senior)"
tags: [IN, biology, "Class 11", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 11 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the CBSE/ICSE and state boards,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c11-biology
country: IN
year_level: "Class 11"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Class 11 🇮🇳"
icon: "🧬"
description: "Transport across membranes, enzymes, and photosynthesis and respiration — senior biology at roughly Class 11 level."
item_source: in_c11_biology

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: in_c11_cell_transport
    label: "Diffusion, osmosis and active transport"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is DIFFUSION (particles spread from high to low concentration, no energy needed)? A) the gut absorbing glucose when blood glucose is already higher  B) a raisin swelling in pure water  C) water entering a root hair cell  D) oxygen moving from the alveoli into the blood. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_enzymes
    label: "Enzymes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of enzymes? A) they are proteins  B) they are carbohydrates  C) they work equally well at any pH  D) they are consumed by the reaction. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_photosynthesis_respiration
    label: "Photosynthesis and respiration"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REACTANT of photosynthesis? A) ATP energy  B) oxygen  C) glucose  D) carbon dioxide. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 11 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `in_c11_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
