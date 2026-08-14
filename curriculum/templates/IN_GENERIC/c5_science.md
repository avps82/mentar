---
type: Mentar Curriculum Template
title: "Science — Class 5 (India, general)"
tags: [IN, science, "Class 5", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — India, Class 5 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what India teaches at Class 5.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c5-science
country: IN
year_level: "Class 5"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Class 5 🇮🇳 (general)"
icon: "5️⃣"
description: "Adaptations, dissolving, and transparent or opaque materials — general science at roughly Class 5 level."
item_source: in_c5_science

language_register:
  reading_level: "~ages 9-11"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-5
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[5], derived from
# engine/science_items.py's AU Year 5 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: in_c5_adaptations
    label: "Body features that help survival (adaptations)"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a body feature that helps an animal survive in its habitat? A) a fish tank  B) a bird's cage  C) a duck's webbed feet  D) a dog's collar. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c5_dissolving
    label: "What dissolves in water"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these dissolves in water? A) small stones  B) pepper  C) instant coffee powder  D) sand. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c5_light_materials
    label: "Transparent and opaque materials"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is opaque (blocks light completely)? A) a clear plastic bottle  B) clear plastic wrap  C) clear glass  D) a brick wall. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 5 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Class 5 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

Node ids are prefixed `in_c5_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
