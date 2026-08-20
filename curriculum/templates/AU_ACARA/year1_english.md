---
type: Mentar Curriculum Template
title: "English — Year 1 (Australia)"
tags: [AU, english, "Year 1"]
timestamp: "2026-08-24T00:00:00Z"
# W5/W6 of docs/design/curriculum_depth_program.md: Year 1 was ABSENT in every
# subject — the loudest row in the coverage audit. Age-6 register: very short
# sentences, numbers within 20, mc4 knowledge items from disjoint fact tables.

template_id: au-year1-english
country: AU
year_level: "Year 1"
subject: english
curriculum_standard: "AC v9 (CC BY 4.0) — year level only; codes not cited"
schema_version: "0.1"
label: "English — Year 1 🇦🇺"
icon: "🔤"
description: "First sounds, rhymes, sentences and letters."
item_source: au1_english

language_register:
  reading_level: "~Year 1 / ages 5-7"
  vocabulary_note: "Very short sentences. Everyday words. Numbers within 20."

concepts:
  - id: aue1_first_sounds
    label: "First sounds"
    strand: "Phonics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word that starts like 'dog'? A) mat  B) mouse  C) sock  D) door. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aue1_rhymes
    label: "Rhyming words"
    strand: "Reading"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word that rhymes with 'dog'? A) mat  B) bat  C) far  D) log. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aue1_sentence_basics
    label: "Writing a sentence"
    strand: "Writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is missing its CAPITAL letter? A) my hat is red.  B) The bird can fly  C) I see the moon  D) I like my school.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aue1_letter_case
    label: "Big and small letters"
    strand: "Handwriting"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is the lowercase partner of B? A) b  B) r  C) g  D) d. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }
  - id: aue1_speaking_listening
    label: "Speaking and listening"
    strand: "Speaking"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is GOOD speaking? A) waiting for your turn to speak  B) looking at the person who is talking  C) using a clear voice others can hear  D) talking while someone else is talking. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.3, slip: 0.15, learns: 0.25, forgets: 0 }

---

# English — Year 1 (Australia)

The first year of each subject (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_year1_items.py`.
