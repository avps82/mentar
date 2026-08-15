---
type: Mentar Curriculum Template
title: "English — Year 9 (AU)"
tags: [AU, english, "Year 9"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 9 English.
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes are
# alignment REFERENCES and PROVISIONAL for this year level; all labels and
# questions are Mentar-authored — see docs/CONTENT_LICENSES.md; ACARA core
# content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR9_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while english stopped at Year 8, a gap nobody had ratified.

template_id: au-year9-english
country: AU
year_level: "Year 9"
subject: english
curriculum_standard: "ACARA v9 (AC9E9A Language, provisional)"
schema_version: "0.1"
label: "English — Year 9 🇦🇺"
icon: "📖"
description: "Modality, nominalisation, rhetorical devices and sentence types (Australian Year 9)."
item_source: au_english_year9

language_register:
  reading_level: "~Year 9 / ages 14-15"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 4 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU english template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: aue9_modality
    label: "High and low modality"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words shows LOW modality (tentative or hedged)? A) perhaps  B) must  C) definitely  D) certainly. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue9_nominalisation
    label: "Nominalisation (verb or adjective to noun)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a plain verb or adjective (not nominalised)? A) assess  B) decision  C) arrival  D) assessment. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue9_rhetorical_devices
    label: "Rhetorical devices in persuasive writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a repetition for emphasis? A) Your voice matters here.  B) Think about your own street.  C) Faster, cleaner, cheaper.  D) Who wouldn't want cleaner air?. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue9_sentence_types
    label: "Simple, compound and complex sentences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a complex sentence (a main clause plus a subordinate clause)? A) The lights went out, so we lit a candle.  B) She writes poetry and she paints.  C) She writes poetry because it calms her.  D) The train left early.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 9 English

Aligned to ACARA v9 content descriptions as REFERENCES only — every label and
question is Mentar-authored, and the codes are **provisional** for Year 9.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
