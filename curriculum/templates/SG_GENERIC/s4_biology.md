---
type: Mentar Curriculum Template
title: "Biology — Secondary 4 (Singapore, senior)"
tags: [SG, biology, "Secondary 4", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 4 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the Singapore-Cambridge examination syllabuses,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-s4-biology
country: SG
year_level: "Secondary 4"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Secondary 4 🇸🇬"
icon: "🧬"
description: "Genotype and phenotype, homeostasis, and trophic levels — senior biology at roughly Secondary 4 level."
item_source: sg_s4_biology

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: sg_s4_inheritance
    label: "Genotype and phenotype"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a GENOTYPE (the alleles an organism carries)? A) Bb  B) tall stem  C) recessive  D) the b in Bb. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s4_homeostasis
    label: "Homeostasis and negative feedback"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of NEGATIVE feedback (the response reverses the change)? A) sweating when body temperature rises  B) growing taller over years  C) learning a new skill  D) hair turning grey with age. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s4_trophic_levels
    label: "Trophic levels in a food chain"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCER (makes its own food from light)? A) soil bacteria  B) a caterpillar eating leaves  C) a rabbit eating grass  D) grass. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s4_dna_protein
    label: "DNA and protein synthesis"
    strand: "DNA and protein synthesis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of DNA? A) each three-base codon calls for one amino acid  B) a double helix of paired bases (A-T, G-C)  C) ribosomes read the message three bases at a time  D) it uses U (uracil) where DNA uses T. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s4_evolution_evidence
    label: "Evidence for evolution"
    strand: "Evolution"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is evidence from COMPARATIVE ANATOMY? A) the same bone layout in a whale flipper, bat wing and human arm  B) humans and chimpanzees having nearly identical genes  C) older rock layers holding simpler life forms  D) closely related species sharing more of their genetic code. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s4_disease_types
    label: "Disease and defence"
    strand: "Diseases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a DEFENCE the body mounts? A) tuberculosis caused by bacteria  B) scurvy from a lack of vitamin C  C) white blood cells engulfing invaders  D) type 2 diabetes. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Secondary 4 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `sg_s4_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
