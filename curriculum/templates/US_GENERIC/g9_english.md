---
type: Mentar Curriculum Template
title: "English — Grade 9 (the United States, general)"
tags: [US, english, "Grade 9", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — the United States, Grade 9 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior english at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what the United States teaches at Grade 9.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: us-g9-english
country: US
year_level: "Grade 9"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Grade 9 (general)"
icon: "📖"
description: "Modality, nominalisation, rhetorical devices and sentence types — general senior english at roughly Grade 9 level."
item_source: us_g9_english

language_register:
  reading_level: "~ages 14-15"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: us_g9_modality
    label: "High and low modality"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words shows HIGH modality (very certain or forceful)? A) must  B) possibly  C) could  D) perhaps. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_nominalisation
    label: "Nominalisation (verb or adjective to noun)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a nominalisation (a noun made from a verb or adjective)? A) assessment  B) decide  C) assess  D) happy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_rhetorical_devices
    label: "Rhetorical devices in persuasive writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a repetition for emphasis? A) You can change this today.  B) Who wouldn't want cleaner air?  C) We tried, we failed, we tried again.  D) Think about your own street.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g9_sentence_types
    label: "Simple, compound and complex sentences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a complex sentence (a main clause plus a subordinate clause)? A) When the lights went out, we lit a candle.  B) The lights went out.  C) She writes poetry.  D) The train left early.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_comparing_texts
    label: "Comparing texts"
    strand: "Comparative reading"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a CONTRAST between two texts? A) “where the film ends in rescue, the novel refuses one”  B) “the novel's narrator hides the truth until the last page”  C) observing that the play opens with a storm  D) “both poems treat the war as a betrayal of the young”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g9_shakespeare_poetry
    label: "Shakespeare and poetry"
    strand: "Poetry and Shakespeare"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of Shakespeare's THEATER? A) ten syllables to a line: da-DUM da-DUM da-DUM da-DUM da-DUM  B) plays staged in daylight at the open-roofed Globe  C) an unstressed beat then a stressed one, five times a line  D) fourteen lines ending in a rhyming couplet. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# the United States — Grade 9 English (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Grade 9 difficulty,
with **no claimed alignment** to any curriculum authority. US Common Core carries a purpose clause and trademark terms that a claimed-alignment pack cannot satisfy.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
