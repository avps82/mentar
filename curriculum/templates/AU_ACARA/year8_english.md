---
type: Mentar Curriculum Template
title: "English — Year 8 (AU)"
tags: [AU, english, "Year 8"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 8 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR8_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year8-english
country: AU
year_level: "Year 8"
subject: english
curriculum_standard: "ACARA v9 (AC9E8A Language)"
schema_version: "0.1"
label: "English — Year 8 🇦🇺"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Connotation, clauses, adverbial phrases and onomatopoeia (Australian Year 8)."
item_source: au_english_year8

language_register:
  reading_level: "~Year 8 / ages 13-14"
  vocabulary_note: "Clear sentences. Secondary-level vocabulary."

# 4 independent nodes — same shape as year2/3/4/5/6/7_english.md.
concepts:

  - id: aue8_connotation
    label: "Word connotation (positive/negative)"           # AC9E8A alignment
    strand: "Text analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word with a NEGATIVE connotation? A) skinny  B) slender  C) confident  D) curious. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue8_clauses
    label: "Main and subordinate clauses"                   # AC9E8A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a subordinate clause (cannot stand alone)? A) she went to the store  B) because she was hungry  C) the dog barked loudly  D) he plays the guitar. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue8_adverbial_phrases
    label: "Adverbial phrases"                              # AC9E8A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an adverbial phrase (tells HOW, WHEN or WHERE)? A) in the morning  B) my best friend  C) a beautiful sunset  D) the old oak tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue8_onomatopoeia
    label: "Onomatopoeia"                                   # AC9E8A alignment
    strand: "Creative writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is onomatopoeia (a word that sounds like what it means)? A) buzz  B) loud  C) sudden  D) fast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue8_digital_literacy
    label: "Judging online sources"
    strand: "Digital literacy"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a sign to be SUSPICIOUS? A) opening a second source to compare the claim  B) a well-known institution stands behind it  C) it names its author and cites its sources  D) no author, no date, no sources anywhere. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue8_persuasive_structure
    label: "Shape of a persuasive text"
    strand: "Persuasive writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a strong persuasive MIDDLE? A) a hook that makes the reader care in the first line  B) a bold statement of position with the stakes made plain  C) leaving the reader with one line they will remember  D) answering the other side's best objection head-on. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue8_speech_delivery
    label: "Delivering a speech"
    strand: "Speaking"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is strong speech DELIVERY? A) the rule of three: 'cheaper, cleaner, fairer'  B) a rhetorical question that pulls listeners in  C) reading every word off the page in a monotone  D) making eye contact around the whole room. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 8 English (Language, Literacy)

ACARA v9 English (Language strand), Year 8 — sibling of `year7_english.md`, completing
the AU English sequence at Y2-8 to match the maths pack's own Y2-8 breadth. Every node
reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, grade-differentiated,
hand-verified pairwise-disjoint word/phrase table.

**Alignment note:** the AC9E8A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
