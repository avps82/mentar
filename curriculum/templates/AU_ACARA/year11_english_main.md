---
type: Mentar Curriculum Template
title: "English — Year 11 (Australia, senior)"
tags: [AU, english, "Year 11", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.
# The 'Language and analysis' strand holds the nodes absorbed verbatim from the
# retired merged year11_english template — SAME ids, so learner mastery survives.

template_id: au11-english-main
country: AU
year_level: "Year 11"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "English — Year 11 🇦🇺"
icon: "📝"
description: "The mainstream senior course: analysis, argument, contexts and craft."
item_source: au11_mainstream_english

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue11m_perspectives_values
    label: "Perspectives and values"
    strand: "Perspectives and values"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these shows an EXPERT's perspective? A) “I was on the bridge when it began to sway”  B) a historian weighing two accounts of the event  C) a developer praising the very project they profit from  D) a company's own report calling its spill “minor”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11m_text_structures
    label: "Text structures"
    strand: "Text structures"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these uses CAUSE-AND-EFFECT structure? A) a biography moving birth to death in order  B) “the city offers X; the country, by contrast, offers Y”  C) “first… then… by nightfall… the next morning…”  D) “because the dam failed, the valley flooded, which forced…”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11m_analytical_essays
    label: "Parts of an analytical essay"
    strand: "Analytical essays"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is ANALYSIS of evidence? A) “Shakespeare presents ambition as a corrosive force”  B) a quotation from the scene being discussed  C) “the stage direction reads: 'he drops the crown'”  D) explaining what the word choice makes the audience feel. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11m_imaginative_texts
    label: "Imaginative techniques"
    strand: "Imaginative texts"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of FORESHADOWING? A) “frost crunched like glass beneath their boots”  B) “the air tasted of salt and diesel”  C) the narrator suddenly recalling the summer it all began  D) a storm gathering in chapter one before the tragedy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11_textual_analysis
    label: "Naming the technique in a quotation"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is personification (gives human traits to a thing)? A) His memory is like a locked room.  B) The city felt as hot as a furnace.  C) The old house sighed in the heat.  D) Her voice was a warm blanket.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11_argument_structure
    label: "Claim, evidence and rebuttal"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REBUTTAL (answering the opposing view)? A) Library visits doubled after the late-opening trial.  B) Sleep studies show teenagers need nine hours.  C) Some argue standards would slip; the trial found the opposite.  D) Public transport should be free at peak times.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue11_register_shift
    label: "Matching register to audience"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is INFORMAL register (suited to a message to a friend)? A) Yeah, that didn't go how we thought.  B) The evidence suggests a modest improvement.  C) This paper examines three competing explanations.  D) The results were inconsistent with the hypothesis.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# English — Year 11 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
