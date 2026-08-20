---
type: Mentar Curriculum Template
title: "English — Year 12 (Australia, senior)"
tags: [AU, english, "Year 12", senior]
timestamp: "2026-08-23T00:00:00Z"
# SENIOR ENGLISH IS A SPLIT SUBJECT (W4 of docs/design/curriculum_depth_program.md),
# mirroring senior maths and senior science: a real senior student enrols in
# Essential English, English, or Literature. NO claimed alignment: senior courses
# are set by state certificate authorities; content is 100% Mentar-authored.
# The 'Language and analysis' strand holds the nodes absorbed verbatim from the
# retired merged year12_english template — SAME ids, so learner mastery survives.

template_id: au12-english-main
country: AU
year_level: "Year 12"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "English — Year 12 🇦🇺"
icon: "📝"
description: "The mainstream senior course: analysis, argument, contexts and craft."
item_source: au12_mainstream_english

language_register:
  reading_level: "~ages 16-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

concepts:
  - id: aue12m_comparative_contexts
    label: "Reading through contexts"
    strand: "Comparative contexts"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a use of HISTORICAL context? A) rereading a childhood book as a parent and finding it changed  B) knowing censorship laws shaped what the novel could say  C) reading a text through the customs of the society that made it  D) a migrant reader connecting a border-crossing scene to their own journey. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12m_media_bias
    label: "How media bias works"
    strand: "Media bias"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these shows bias through SELECTION and omission? A) reporting the protest's one broken window but not its 10,000 marchers  B) a photo angle that makes a small crowd look vast  C) calling the same plan “a reckless gamble” rather than “a bold reform”  D) burying the correction on page 14 after a front-page accusation. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12m_comparative_essays
    label: "Comparative essay structures"
    strand: "Comparative essays"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an effective COMPARATIVE link? A) each paragraph taking one idea across both texts  B) alternating texts within every body paragraph  C) “where Orwell uses fear, Atwood uses ritual”  D) all of Text A's treatment first, then all of Text B's. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12m_persuasive_essays
    label: "Rhetorical appeals"
    strand: "Persuasive essays"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these uses ETHOS (credibility appeal)? A) “as a nurse of twenty years, I have seen what these cuts do”  B) “three independent studies reached the same conclusion”  C) “picture your daughter waiting alone at that unlit bus stop”  D) “if each unit costs $4 and we need fifty, the maths is simple”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12_bias
    label: "Biased and balanced wording"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is BALANCED wording (it reports the same event neutrally)? A) The cost was met from public funds.  B) A mob of protesters swarmed the square.  C) The so-called expert made yet another excuse.  D) Taxpayers were forced to foot the bill again.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12_allusion
    label: "Allusion"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a plain description (no reference)? A) The plan had one serious weakness.  B) He met his Waterloo in the final round.  C) She opened a Pandora's box of paperwork.  D) The plan was his Achilles heel.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12_syntax_for_effect
    label: "Syntax chosen for effect"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a long, accumulating sentence used to build detail? A) Across the valley, past the fence line and the dry creek, the smoke was already rising.  B) It failed.  C) Nobody moved.  D) That was the end.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue12_language_change
    label: "How English changes over time"
    strand: "Language and analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word COINED for new technology? A) bungalow  B) typhoon  C) kindergarten  D) podcast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# English — Year 12 (Australia)

Senior English, split by course (see the frontmatter note). Topics grouped by
`strand:`; items come from `engine/au_senior_english_items.py` fact tables via
the shared mc_which_is helper, so every node carries an explain-mode card.
