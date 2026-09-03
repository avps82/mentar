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
label: "Biology — Grade 9"
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
      - "Which of these is ACTIVE TRANSPORT (moves against the gradient and needs energy)? A) water entering a root hair cell  B) a root absorbing minerals from dilute soil water  C) oxygen moving from the alveoli into the blood  D) a raisin swelling in pure water. Answer with the letter."
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
      - "Which of these is an INPUT photosynthesis needs? A) carbon dioxide breathed out  B) ATP energy the cell can use  C) light energy from the Sun  D) glucose stored as the plant's food. Answer with the letter."
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
      - "Which of these is an example of NEGATIVE feedback (the response reverses the change)? A) sweating when body temperature rises  B) growing taller over years  C) learning a new skill  D) hair turning gray with age. Answer with the letter."
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
  - id: us_g9_ecosystem_roles
    label: "Roles in an ecosystem"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCER? A) a shark hunting fish  B) a kangaroo grazing  C) soil bacteria recycling dead leaves  D) a gum tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_adaptation_types
    label: "Types of adaptation"
    strand: "Adaptations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a BEHAVIOURAL adaptation (something the organism does)? A) kidneys concentrating urine in desert mammals  B) desert animals feeding only at night  C) a snake producing venom  D) a cactus storing water in a thick stem. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_transport_systems
    label: "Transport systems"
    strand: "Transport systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of a PLANT's transport system? A) carbon dioxide leaving the blood to be breathed out  B) xylem carrying water up from the roots  C) oxygen diffusing across the alveoli into the blood  D) arteries carrying blood away from the heart. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_dna_protein
    label: "DNA and protein synthesis"
    strand: "DNA and protein synthesis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of PROTEIN synthesis? A) it uses U (uracil) where DNA uses T  B) ribosomes read the message three bases at a time  C) a single-stranded copy of a gene that travels to the ribosome  D) a double helix of paired bases (A-T, G-C). Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_evolution_evidence
    label: "Evidence for evolution"
    strand: "Evolution"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is evidence from DNA? A) older rock layers holding simpler life forms  B) transitional forms like feathered dinosaurs  C) closely related species sharing more of their genetic code  D) the same bone layout in a whale flipper, bat wing and human arm. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_disease_types
    label: "Disease and defense"
    strand: "Diseases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an INFECTIOUS disease (caused by a pathogen)? A) white blood cells engulfing invaders  B) scurvy from a lack of vitamin C  C) tuberculosis caused by bacteria  D) type 2 diabetes. Answer with the letter."
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
