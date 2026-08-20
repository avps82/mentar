---
type: Mentar Curriculum Template
title: "Biology — Secondary 3 (Singapore, senior)"
tags: [SG, biology, "Secondary 3", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 3 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the Singapore-Cambridge examination syllabuses,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-s3-biology
country: SG
year_level: "Secondary 3"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Secondary 3 🇸🇬"
icon: "🧬"
description: "Transport across membranes, enzymes, and photosynthesis and respiration — senior biology at roughly Secondary 3 level."
item_source: sg_s3_biology

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: sg_s3_cell_transport
    label: "Diffusion, osmosis and active transport"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is DIFFUSION (particles spread from high to low concentration, no energy needed)? A) the gut absorbing glucose when blood glucose is already higher  B) a raisin swelling in pure water  C) water entering a root hair cell  D) oxygen moving from the alveoli into the blood. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s3_enzymes
    label: "Enzymes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of enzymes? A) they are proteins  B) they are carbohydrates  C) they work equally well at any pH  D) they are consumed by the reaction. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s3_photosynthesis_respiration
    label: "Photosynthesis and respiration"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REACTANT of photosynthesis? A) ATP energy  B) oxygen  C) glucose  D) carbon dioxide. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_ecosystem_roles
    label: "Roles in an ecosystem"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a DECOMPOSER? A) a kangaroo grazing  B) grass on a plain  C) a gum tree  D) soil bacteria recycling dead leaves. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_adaptation_types
    label: "Types of adaptation"
    strand: "Adaptations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PHYSIOLOGICAL adaptation (an internal process)? A) kidneys concentrating urine in desert mammals  B) desert animals feeding only at night  C) a cactus storing water in a thick stem  D) a polar bear's layer of blubber. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_transport_systems
    label: "Transport systems"
    strand: "Transport systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of a PLANT's transport system? A) capillaries exchanging materials with tissues  B) arteries carrying blood away from the heart  C) oxygen diffusing across the alveoli into the blood  D) xylem carrying water up from the roots. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Secondary 3 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `sg_s3_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
