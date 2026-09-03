---
type: Mentar Curriculum Template
title: "Biology — Year 11 (Australia, senior)"
tags: [AU, biology, "Year 11", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Australia, Year 11 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by state certificate authorities (VCE/HSC/QCE/SACE),
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: au11-biology
country: AU
year_level: "Year 11"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Year 11"
icon: "🧬"
description: "Transport across membranes, enzymes, and photosynthesis and respiration — senior biology at roughly Year 11 level."
item_source: au11_biology

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: au11_cell_transport
    label: "Diffusion, osmosis and active transport"
    strand: "Cells"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is OSMOSIS (water moving across a partially permeable membrane)? A) water entering a root hair cell  B) oxygen moving from the alveoli into the blood  C) a scent spreading across a room  D) a root absorbing minerals from dilute soil water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au11_enzymes
    label: "Enzymes"
    strand: "Cells"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of enzymes? A) they are proteins  B) they are carbohydrates  C) they work equally well at any pH  D) they are consumed by the reaction. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au11_photosynthesis_respiration
    label: "Photosynthesis and respiration"
    strand: "Cells"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCT of aerobic respiration? A) water drawn up from the roots  B) light energy from the Sun  C) water given off as the cell releases energy  D) carbon dioxide taken in by the leaf. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_ecosystem_roles
    label: "Roles in an ecosystem"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCER? A) grass on a plain  B) soil bacteria recycling dead leaves  C) fungi breaking down a fallen log  D) a shark hunting fish. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_adaptation_types
    label: "Types of adaptation"
    strand: "Adaptations"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PHYSIOLOGICAL adaptation (an internal process)? A) kidneys concentrating urine in desert mammals  B) birds migrating before winter  C) a polar bear's layer of blubber  D) desert animals feeding only at night. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_transport_systems
    label: "Transport systems"
    strand: "Transport systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of the CIRCULATORY system? A) oxygen diffusing across the alveoli into the blood  B) xylem carrying water up from the roots  C) carbon dioxide leaving the blood to be breathed out  D) arteries carrying blood away from the heart. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 11 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `au11_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
