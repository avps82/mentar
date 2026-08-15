---
type: Mentar Curriculum Template
title: "Biology — Grade 9 (the United States, senior)"
tags: [US, biology, "Grade 9", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — the United States, Grade 9 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT, and in the US it is also SEQUENCED. Junior
# grades ship one combined "Science" pack because that is what a student studies.
# High school does not: the common US pattern is a whole year on Biology (Grade
# 9), then Chemistry (Grade 10), then Physics (Grade 11) -- one subject at a
# time, rather than the three in parallel that Australia, India and Singapore
# run. So this pack is a FULL YEAR of biology: both senior stages of it,
# six nodes, where a parallel-country senior pack carries three.
# Grade 12 is deliberately not shipped -- it is electives (AP, anatomy,
# environmental science, or none), which has no single shape to model.
# NO claimed alignment: senior science is set by state boards and district frameworks,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g9-biology
country: US
year_level: "Grade 9"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Grade 9 🇺🇸"
icon: "🧬"
description: "Transport across membranes, enzymes, photosynthesis and respiration, genotype and phenotype, homeostasis and trophic levels — senior biology at roughly Grade 9 level."
item_source: us_g9_biology

language_register:
  reading_level: "~ages 14-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 6 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: us_g9_cell_transport
    label: "Diffusion, osmosis and active transport"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is DIFFUSION (particles spread from high to low concentration, no energy needed)? A) the gut absorbing glucose when blood glucose is already higher  B) a raisin swelling in pure water  C) water entering a root hair cell  D) oxygen moving from the alveoli into the blood. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_enzymes
    label: "Enzymes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of enzymes? A) they are proteins  B) they are carbohydrates  C) they work equally well at any pH  D) they are consumed by the reaction. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_photosynthesis_respiration
    label: "Photosynthesis and respiration"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REACTANT of photosynthesis? A) ATP energy  B) oxygen  C) glucose  D) carbon dioxide. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_inheritance
    label: "Genotype and phenotype"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a GENOTYPE (the alleles an organism carries)? A) Bb  B) tall stem  C) recessive  D) the b in Bb. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_homeostasis
    label: "Homeostasis and negative feedback"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of NEGATIVE feedback (the response reverses the change)? A) sweating when body temperature rises  B) growing taller over years  C) learning a new skill  D) hair turning grey with age. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_trophic_levels
    label: "Trophic levels in a food chain"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCER (makes its own food from light)? A) soil bacteria  B) a caterpillar eating leaves  C) a rabbit eating grass  D) grass. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# the United States — Grade 9 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `us_g9_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
