---
type: Mentar Curriculum Template
title: "Essential English — Year 11 (Australia, senior)"
tags: [AU, english, "Year 11", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.

template_id: au11-english-essential
country: AU
year_level: "Year 11"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "Essential English — Year 11 🇦🇺"
icon: "🛠️"
description: "Practical English: workplace texts, media and clear communication."
item_source: au11_essential_english

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue11e_workplace_texts
    label: "Workplace texts"
    strand: "Workplace texts"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a text for a GENERAL PUBLIC audience? A) a workplace safety notice  B) an incident report form  C) a supermarket catalogue  D) a staff roster for the week. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11e_advertising_media
    label: "Advertising techniques"
    strand: "Advertising and media"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these uses the BANDWAGON technique (everyone's doing it)? A) “don't let your family go unprotected”  B) “Join the two million Australians who have already switched”  C) “9 out of 10 dentists recommend this toothpaste”  D) “developed with leading sports scientists”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11e_instructional_texts
    label: "Instructional texts"
    strand: "Instructional texts"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a feature of NARRATIVE texts? A) rhetorical questions aimed at the reader  B) numbered steps in the order you do them  C) a call to action at the end  D) characters and a plot with a complication. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Essential English — Year 11 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
