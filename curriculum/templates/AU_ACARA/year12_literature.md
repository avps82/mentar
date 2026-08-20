---
type: Mentar Curriculum Template
title: "Literature — Year 12 (Australia, senior)"
tags: [AU, english, "Year 12", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.

template_id: au12-literature
country: AU
year_level: "Year 12"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "Literature — Year 12 🇦🇺"
icon: "📜"
description: "Close study of literary texts: periods, poetry, theory and interpretation."
item_source: au12_literature

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue12l_literary_theories
    label: "Critical lenses"
    strand: "Literary theories"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a POSTCOLONIAL reading? A) asking who owns what, and what that ownership silences  B) hearing the colony answer back to the empire's narrator  C) tracing who does the housework of the plot  D) asking why the novel's women speak only about its men. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12l_complex_plays
    label: "Dramatic techniques"
    strand: "Complex novels and plays"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is DRAMATIC IRONY? A) one line dropped sideways to us mid-scene  B) Hamlet alone on stage, thinking aloud to the audience  C) a character's quick remark to the audience, unheard on stage  D) the audience knowing the letter is forged while the hero trusts it. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12l_critical_interpretation
    label: "Interpretation and evidence"
    strand: "Critical interpretation"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an interpretation SUPPORTED by the text? A) “this is obviously the best poem ever written”  B) a sweeping claim with no line of the text behind it  C) a claim followed by the quotation that grounds it  D) reading every first-person poem as confession. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Literature — Year 12 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
