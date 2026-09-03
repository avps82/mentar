---
type: Mentar Curriculum Template
title: "Earth & Environmental Science — Year 12 (Australia, senior)"
tags: [AU, earth_environmental, "Year 12", senior]
timestamp: "2026-08-22T00:00:00Z"
# W3 of docs/design/curriculum_depth_program.md: the maintainer's reference
# names Earth & Environmental Science as a fourth senior science -- Mentar
# lacked the subject entirely. AU-ONLY until other countries' shapes are
# verified. No claimed alignment (state certificate authorities own senior
# courses); content is universally-taught earth science, 100% Mentar-authored.

template_id: au12-earth-env
country: AU
year_level: "Year 12"
subject: earth_environmental
curriculum_standard: null
schema_version: "0.1"
label: "Earth & Env Science — Year 12"
icon: "🌏"
description: "Earth's systems: rocks, atmosphere, climate, hazards and sustainability."
item_source: au12_earth_env

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au12_hazards
    label: "Natural hazards"
    strand: "Hazards"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of VOLCANOES? A) most occur along plate boundaries  B) they spin around a calm central eye  C) their size is compared on the logarithmic magnitude scale  D) they form where magma reaches the surface. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_climate_systems
    label: "Climate systems"
    strand: "Climate systems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a driver of the OCEAN's role in climate? A) forests taking in carbon dioxide as they grow  B) tree rings recording good and bad growing years  C) currents carrying warmth from the equator toward the poles  D) air bubbles trapped in ancient ice cores. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_resource_management
    label: "Managing resources"
    strand: "Resource management"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a way to manage resources SUSTAINABLY? A) timber from managed forests  B) recycling metals instead of mining more  C) coal  D) natural gas. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_sustainability
    label: "Sustainability"
    strand: "Sustainability"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of REDUCING demand? A) composting food scraps into garden soil  B) refilling water bottles instead of buying new ones  C) insulating homes so they need less heating  D) returning wetlands to filter water naturally. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Earth & Environmental Science — Year 12 (Australia)

Senior earth science (see the frontmatter note). Topics grouped by `strand:`;
items come from `engine/senior_science_depth_items.py` fact tables via the
shared mc_which_is helper, so every node carries an explain-mode card.
