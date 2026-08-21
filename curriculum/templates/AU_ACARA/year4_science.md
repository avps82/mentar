---
type: Mentar Curriculum Template
title: "Science — Year 4 (AU)"
tags: [AU, science, "Year 4"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 4 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat
# year2_science.md/year3_science.md already carry for their own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR4_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year4-science
country: AU
year_level: "Year 4"
subject: science
curriculum_standard: "ACARA v9 (AC9S4 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 4 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Food chain roles, magnetic materials, and changes of state (Australian Year 4 Science)."
item_source: au_science_year4

language_register:
  reading_level: "~Year 4 / ages 9-10"
  vocabulary_note: "Short sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 nodes: food chain roles, magnetic materials, changes of state -- all independent
# roots, same shape as year2_science.md/year3_science.md.
concepts:

  - id: au4_science_food_chain_roles
    label: "Producers and consumers"                                 # AC9S4U01 (provisional)
    strand: "Life in environments"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a producer (makes its own food)? A) a tree  B) a lion  C) a shark  D) a rabbit. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_science_magnetic_materials
    label: "Materials attracted to a magnet"                         # AC9S4U02 (provisional)
    strand: "Forces and friction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is attracted to a magnet? A) an iron nail  B) a wooden pencil  C) a plastic ruler  D) a rubber band. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au4_science_state_change_heat
    label: "Changes of state — adding or removing heat"              # AC9S4U03 (provisional)
    strand: "Materials and rocks"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is caused by ADDING heat? A) ice melting into water  B) water freezing into ice  C) juice freezing into ice blocks  D) melted wax cooling and hardening. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: au4_science_sun_moon_earth
    label: "Sun, Earth and Moon"
    strand: "Earth and space"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of the MOON? A) it spins around once every day, giving us day and night  B) it is the only one of the three with life on it  C) it is a star that makes its own light and heat  D) it shines only by reflecting sunlight. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 4 Science

Extends `year2_science.md`/`year3_science.md`'s proven 3-node shape one year further:
producers/consumers (Biological sciences), magnetic materials (Physical sciences), and
changes of state driven by adding/removing heat (Chemical sciences) — the last one a direct
continuation of `year3_science.md`'s heat-sources node into what heat actually DOES to
matter. Every node reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a NEW,
hand-verified pairwise-disjoint fact table — the LLM never decides correctness (SPEC §14).

**Alignment note:** the AC9S4U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md`/`year3_science.md` already carry for their own codes. Question text,
labels and fact tables are Mentar-authored. ACARA core curriculum content is CC BY 4.0
(verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced
in this template.
