---
type: Mentar Curriculum Template
title: "Literature — Year 11 (Australia, senior)"
tags: [AU, english, "Year 11", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.

template_id: au11-literature
country: AU
year_level: "Year 11"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "Literature — Year 11"
icon: "📜"
description: "Close study of literary texts: periods, poetry, theory and interpretation."
item_source: au11_literature

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue11l_canonical_literature
    label: "Literary periods"
    strand: "Canonical literature"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these belongs to the VICTORIAN novel? A) Dickens' Great Expectations  B) Wordsworth's daffodils  C) a play written for the Globe's open stage  D) poetry exalting nature and feeling over reason. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11l_poetry_forms
    label: "Poetic forms"
    strand: "Poetry"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these describes a SONNET? A) rhythm built from breath and line-breaks alone  B) three lines of five, seven and five syllables  C) fourteen lines turning on a volta  D) a single season-image, said and left. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11l_genre_over_time
    label: "Genre conventions"
    strand: "Genre over time"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a SCIENCE FICTION element? A) a storm rattling the casements at midnight  B) the least likely suspect proving guilty  C) a technology arriving before the ethics for it  D) a locked room and a missing key. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Literature — Year 11 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
