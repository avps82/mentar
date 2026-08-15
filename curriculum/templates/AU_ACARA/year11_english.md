---
type: Mentar Curriculum Template
title: "English — Year 11 (AU)"
tags: [AU, english, "Year 11"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 11 English.
# NO claimed alignment: senior English is set by state certificate authorities,
# not by a single national content-description set (docs/CONTENT_LICENSES.md).
# Senior English is state-certificate territory (VCE/HSC/QCE/SACE...), which is
# why curriculum_standard is null here: these nodes are universally-taught
# technique and argument naming, NOT a claimed alignment to any state's units.
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR11_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while english stopped at Year 8, a gap nobody had ratified.

template_id: au-year11-english
country: AU
year_level: "Year 11"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "English — Year 11 🇦🇺"
icon: "📖"
description: "Naming techniques in a quotation, argument structure and register (senior English)."
item_source: au_english_year11

language_register:
  reading_level: "~Year 11 / ages 16-17"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 3 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU english template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: aue11_textual_analysis
    label: "Naming the technique in a quotation"
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
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is INFORMAL register (suited to a message to a friend)? A) Yeah, that didn't go how we thought.  B) The evidence suggests a modest improvement.  C) This paper examines three competing explanations.  D) The results were inconsistent with the hypothesis.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 11 English

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught technique and argument naming at roughly this level.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
