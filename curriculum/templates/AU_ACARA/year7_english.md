---
type: Mentar Curriculum Template
title: "English — Year 7 (AU)"
tags: [AU, english, "Year 7"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 7 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR7_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year7-english
country: AU
year_level: "Year 7"
subject: english
curriculum_standard: "ACARA v9 (AC9E7A Language)"
schema_version: "0.1"
label: "English — Year 7"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Idioms, formal/informal register, active/passive voice and personification (Australian Year 7)."
item_source: au_english_year7

language_register:
  reading_level: "~Year 7 / ages 12-13"
  vocabulary_note: "Clear sentences. Secondary-level vocabulary."

# 4 independent nodes — same shape as year2/3/4/5/6_english.md.
concepts:

  - id: aue7_idioms
    label: "Idioms"                                        # AC9E7A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an idiom (doesn't mean what the words literally say)? A) it's raining cats and dogs  B) it's raining heavily outside  C) good luck with the show  D) I feel sick today. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue7_formal_informal
    label: "Formal and informal language"                  # AC9E7A alignment
    strand: "Writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is formal language? A) purchase  B) buy  C) start  D) help. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue7_active_passive
    label: "Active and passive voice"                       # AC9E7A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is passive voice (the subject RECEIVES the action)? A) the dog chased the cat  B) the cat was chased by the dog  C) she wrote the letter  D) they built the house. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue7_personification
    label: "Personification"                                # AC9E7A alignment
    strand: "Literature"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is personification (giving human qualities to something non-human)? A) the old car started slowly  B) the sun shone down on us  C) the sun smiled down on us  D) the wind blew through the trees. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue7_apostrophes
    label: "Apostrophes"
    strand: "Punctuation"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an apostrophe in a CONTRACTION? A) the dog's collar (one dog)  B) its' — never a correct form  C) apple's for sale (just a plural, no apostrophe needed)  D) don't, standing for 'do not'. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 7 English (Language, Literacy)

ACARA v9 English (Language strand), Year 7 — sibling of `year6_english.md`, extending the
per-country/per-year pattern (SPEC §6) into secondary school. Every node reuses
`engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, grade-differentiated,
hand-verified pairwise-disjoint word/phrase table. `aue7_personification` is a new
figurative-language device (distinct from Y4's simile and Y6's simile-vs-metaphor).

**Alignment note:** the AC9E7A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
