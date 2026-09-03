---
type: Mentar Curriculum Template
title: "English — Class 12 (India, general)"
tags: [IN, english, "Class 12", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 12 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior english at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 12.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c12-english
country: IN
year_level: "Class 12"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 12 (general)"
icon: "📖"
description: "Bias, allusion, syntax for effect and language change — general senior english at roughly Class 12 level."
item_source: in_c12_english

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c12_bias
    label: "Biased and balanced wording"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is BIASED wording (it slants the reader)? A) A mob of protesters swarmed the square.  B) A crowd of protesters gathered in the square.  C) The researcher gave a further explanation.  D) The cost was met from public funds.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c12_allusion
    label: "Allusion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an allusion (a reference to another text or event)? A) He lost badly in the final round.  B) She started a great deal of paperwork.  C) The plan was his Achilles heel.  D) The plan had one serious weakness.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c12_syntax_for_effect
    label: "Syntax chosen for effect"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a short sentence used for impact? A) Nobody moved.  B) The room, still smelling of rain and old paper, filled slowly with people who had waited outside for hours.  C) Across the valley, past the fence line and the dry creek, the smoke was already rising.  D) She read the letter twice, folded it, put it in her pocket, and said nothing at all.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c12_language_change
    label: "How English changes over time"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word BORROWED from another language? A) podcast  B) smartphone  C) typhoon  D) software. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 12 English (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 12 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
