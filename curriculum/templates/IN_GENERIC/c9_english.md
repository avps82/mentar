---
type: Mentar Curriculum Template
title: "English — Class 9 (India, general)"
tags: [IN, english, "Class 9", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 9 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior english at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 9.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c9-english
country: IN
year_level: "Class 9"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 9 🇮🇳 (general)"
icon: "📖"
description: "Modality, nominalisation, rhetorical devices and sentence types — general senior english at roughly Class 9 level."
item_source: in_c9_english

language_register:
  reading_level: "~ages 14-15"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c9_modality
    label: "High and low modality"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words shows HIGH modality (very certain or forceful)? A) must  B) possibly  C) could  D) perhaps. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_nominalisation
    label: "Nominalisation (verb or adjective to noun)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a nominalisation (a noun made from a verb or adjective)? A) assessment  B) decide  C) assess  D) happy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_rhetorical_devices
    label: "Rhetorical devices in persuasive writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a repetition for emphasis? A) You can change this today.  B) Who wouldn't want cleaner air?  C) We tried, we failed, we tried again.  D) Think about your own street.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c9_sentence_types
    label: "Simple, compound and complex sentences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a complex sentence (a main clause plus a subordinate clause)? A) When the lights went out, we lit a candle.  B) The lights went out.  C) She writes poetry.  D) The train left early.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 9 English (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 9 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
