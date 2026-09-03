---
type: Mentar Curriculum Template
title: "Essential English — Year 12 (Australia, senior)"
tags: [AU, english, "Year 12", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.

template_id: au12-english-essential
country: AU
year_level: "Year 12"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "Essential English — Year 12"
icon: "🛠️"
description: "Practical English: workplace texts, media and clear communication."
item_source: au12_essential_english

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue12e_news_perspectives
    label: "Fact, opinion and perspective in the news"
    strand: "News media perspectives"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a statement of FACT? A) a mining story quoting only the company's spokesperson  B) “closing the pool is a disgraceful decision”  C) “the council voted 7–2 to close the pool”  D) a headline calling protesters “a mob”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12e_persuasive_arguments
    label: "Persuasive arguments"
    strand: "Persuasive arguments"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an argument using STATISTICS? A) “when my own street flooded, no one came”  B) “is this really the future we want?”  C) “road deaths fell 40% after the limit changed”  D) “how many more warnings do we need?”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12e_professional_communication
    label: "Professional communication"
    strand: "Professional communication"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is appropriate only in a CASUAL message? A) emojis standing in for the actual request  B) referring to the position title exactly as advertised  C) “Dear Ms Chen, I am writing to apply for…”  D) sending it without checking how the reader spells their name. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Essential English — Year 12 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
