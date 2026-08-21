---
type: Mentar Curriculum Template
title: "Science — Year 1 (Australia)"
tags: [AU, science, "Year 1"]
timestamp: "2026-08-24T00:00:00Z"
# W5/W6 of docs/design/curriculum_depth_program.md: Year 1 was ABSENT in every
# subject — the loudest row in the coverage audit. Age-6 register: very short
# sentences, numbers within 20, mc4 knowledge items from disjoint fact tables.

template_id: au-year1-science
country: AU
year_level: "Year 1"
subject: science
curriculum_standard: "AC v9 (CC BY 4.0) — year level only; codes not cited"
schema_version: "0.1"
label: "Science — Year 1 🇦🇺"
icon: "🔬"
description: "Living things, materials, the sky, pushes and pulls."
item_source: au1_science

language_register:
  reading_level: "~Year 1 / ages 5-7"
  vocabulary_note: "Very short sentences. Everyday words. Numbers within 20."

concepts:
  - id: aus1_living_things
    label: "Living and non-living"
    strand: "Living things"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a thing that has NEVER been alive? A) a bird  B) a fallen leaf  C) grass  D) a bicycle. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aus1_habitats
    label: "Where animals live"
    strand: "Environments"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an animal that lives UNDERGROUND? A) a rabbit in its burrow  B) a possum  C) a koala  D) a crab. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aus1_materials
    label: "What things are made of"
    strand: "Materials"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is usually made of WOOD? A) a saucepan  B) a drinking cup you can see through  C) a door  D) a coin. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aus1_day_night_sky
    label: "The day and night sky"
    strand: "Earth and sky"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a DAILY pattern (it happens again and again)? A) day turning into night  B) white clouds  C) the stars  D) the Moon shining brightly. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aus1_push_pull
    label: "Pushes and pulls"
    strand: "Forces"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PUSH? A) turning a tap on  B) kicking a ball  C) opening a fridge door  D) winding up a toy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }

---

# Science — Year 1 (Australia)

The first year of each subject (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_year1_items.py`.
