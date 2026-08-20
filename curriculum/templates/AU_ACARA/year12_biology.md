---
type: Mentar Curriculum Template
title: "Biology — Year 12 (Australia, senior)"
tags: [AU, biology, "Year 12", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Australia, Year 12 Biology.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by state certificate authorities (VCE/HSC/QCE/SACE),
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior biology, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: au12-biology
country: AU
year_level: "Year 12"
subject: biology
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Biology — Year 12 🇦🇺"
icon: "🧬"
description: "Genotype and phenotype, homeostasis, and trophic levels — senior biology at roughly Year 12 level."
item_source: au12_biology

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: au12_inheritance
    label: "Genotype and phenotype"
    strand: "Inheritance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a GENOTYPE (the alleles an organism carries)? A) Bb  B) tall stem  C) recessive  D) the b in Bb. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au12_homeostasis
    label: "Homeostasis and negative feedback"
    strand: "Homeostasis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an example of NEGATIVE feedback (the response reverses the change)? A) sweating when body temperature rises  B) growing taller over years  C) learning a new skill  D) hair turning grey with age. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au12_trophic_levels
    label: "Trophic levels in a food chain"
    strand: "Ecosystems"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRODUCER (makes its own food from light)? A) soil bacteria  B) a caterpillar eating leaves  C) a rabbit eating grass  D) grass. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_dna_protein
    label: "DNA and protein synthesis"
    strand: "DNA and protein synthesis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of DNA? A) it uses U (uracil) where DNA uses T  B) it stays in the nucleus while copies of its message leave  C) a single-stranded copy of a gene that travels to the ribosome  D) ribosomes read the message three bases at a time. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_evolution_evidence
    label: "Evidence for evolution"
    strand: "Evolution"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is evidence from COMPARATIVE ANATOMY? A) transitional forms like feathered dinosaurs  B) the same bone layout in a whale flipper, bat wing and human arm  C) humans and chimpanzees having nearly identical genes  D) older rock layers holding simpler life forms. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au12_disease_types
    label: "Disease and defence"
    strand: "Diseases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an INFECTIOUS disease (caused by a pathogen)? A) influenza spread by a virus  B) white blood cells engulfing invaders  C) type 2 diabetes  D) scurvy from a lack of vitamin C. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 12 Biology (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior biology at roughly this level.

Node ids are prefixed `au12_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
