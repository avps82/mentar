---
type: Mentar Curriculum Template
title: "Science — Primary 6 (Singapore, general)"
tags: [SG, science, "Primary 6", generic]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Singapore, Primary 6 Science (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught primary/lower-secondary
# science at roughly this difficulty, 100% Mentar-authored/reused-generic
# (engine/science_items.py's generator functions, already tested and shipped as AU
# content — same fact-table generator shape, no new item logic); the level name is a
# display label, not a claim about what Singapore teaches at Primary 6.
# Items come from shared parametric generators (engine/generic_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-p6-science
country: SG
year_level: "Primary 6"
subject: science
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Science — Primary 6 🇸🇬 (general)"
icon: "6️⃣"
description: "Vertebrates and invertebrates, circuits, and reversible changes — general science at roughly Primary 6 level."
item_source: sg_p6_science

language_register:
  reading_level: "~ages 10-12"
  vocabulary_note: "Clear sentences. Plain everyday words. One idea per question."

# 3 independent nodes (separate science strands, no natural prereq chain). All mc4
# via engine/itemgen.py's shared mc_which_is helper, reusing the exact stage-6
# generator set (engine/generic_science_items.py::STAGE_CONCEPTS[6], derived from
# engine/science_items.py's AU Year 6 dict), so behaviour and fact tables are
# already tested/verified there. Those generators carry glosses, so every node also
# gets an explain-mode method card for free (docs/design/explain_mode_design.md Type 4).
concepts:

  - id: sg_p6_vertebrates
    label: "Vertebrates and invertebrates"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an invertebrate (no backbone)? A) a bird  B) a fish  C) a dog  D) a worm. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_circuits
    label: "Electrical conductors and insulators"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a good conductor of electricity? A) a glass rod  B) a wooden spoon  C) aluminium foil  D) a rubber band. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_p6_reversible_change
    label: "Reversible and irreversible changes"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an irreversible change (cannot be undone)? A) melting butter  B) dissolving salt in water  C) melting chocolate  D) burning paper. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Primary 6 Science (generic)

A board-agnostic science pack: universally-taught topics at roughly Primary 6 difficulty,
with **no claimed alignment** to any curriculum authority. Singapore MOE publishes prose syllabi with no open licence and no public standards-code scheme.

Node ids are prefixed `sg_p6_` and the item generators are shared across every
generic pack (`engine/generic_science_items.py` — one concept-progression table, reused
`engine/science_items.py` generator functions, zero new item logic). The deterministic
verifier scores every answer; the model never decides correctness (SPEC §14).
