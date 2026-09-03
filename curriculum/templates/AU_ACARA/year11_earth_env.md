---
type: Mentar Curriculum Template
title: "Earth & Environmental Science — Year 11 (Australia, senior)"
tags: [AU, earth_environmental, "Year 11", senior]
timestamp: "2026-08-22T00:00:00Z"
# W3 of docs/design/curriculum_depth_program.md: the maintainer's reference
# names Earth & Environmental Science as a fourth senior science -- Mentar
# lacked the subject entirely. AU-ONLY until other countries' shapes are
# verified. No claimed alignment (state certificate authorities own senior
# courses); content is universally-taught earth science, 100% Mentar-authored.

template_id: au11-earth-env
country: AU
year_level: "Year 11"
subject: earth_environmental
curriculum_standard: null
schema_version: "0.1"
label: "Earth & Env Science — Year 11"
icon: "🌏"
description: "Earth's systems: rocks, atmosphere, climate, hazards and sustainability."
item_source: au11_earth_env

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: au11_earth_structure
    label: "Earth's layers"
    strand: "Earth structure"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of the CRUST? A) a metal centre — liquid outside, solid inside  B) the layer whose slow currents move the plates above  C) the thick layer of hot rock that slowly flows  D) thinnest under the oceans, thickest under mountains. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_minerals
    label: "Minerals and ores"
    strand: "Minerals"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of an ORE? A) quartz and feldspar are examples  B) how it splits or breaks (cleavage)  C) its hardness on the Mohs scale  D) bauxite mined as the source of aluminium. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_rock_cycle
    label: "The rock cycle"
    strand: "Rock cycle"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a METAMORPHIC rock (changed by heat and pressure)? A) slate  B) sandstone  C) basalt  D) shale. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_atmosphere
    label: "The atmosphere"
    strand: "Atmosphere"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of the STRATOSPHERE? A) home of the ozone layer that absorbs UV  B) certain gases trapping outgoing heat and warming the surface  C) temperature falls as you climb through it  D) without it Earth would average well below freezing. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au11_human_impact
    label: "Human impact"
    strand: "Human impact"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an impact on WATERWAYS? A) burning fossil fuels raising carbon dioxide levels  B) fertiliser runoff causing algal blooms  C) clearing forest for farmland  D) urban sprawl fragmenting habitats. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Earth & Environmental Science — Year 11 (Australia)

Senior earth science (see the frontmatter note). Topics grouped by `strand:`;
items come from `engine/senior_science_depth_items.py` fact tables via the
shared mc_which_is helper, so every node carries an explain-mode card.
