---
# Mentar testing template — science (Phase 0 testing variety)
# Multiple-choice only: the deterministic verifier (mc_choice) scores the child's
# letter against ground truth from curated fact tables (engine/science_items.py).
# The LLM never asserts the correct answer (SPEC §14 safety rule).

template_id: pilot-science
country: null
year_level: pilot
subject: science
curriculum_standard: null
schema_version: "0.1"
label: "Science 🔬"                                  # R3.1: web picker catalog fields
icon: "🔬"
description: "How the world around us works."
item_source: science
subject_key: science                                 # keep the pre-scan session-cookie key stable

language_register:
  reading_level: "~Year 3-4 / ages 8-9"
  vocabulary_note: "Short sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 concept nodes: living_nonliving (root) -> classify_animals; states_of_matter (root).
concepts:

  - id: living_nonliving
    label: "Living and non-living things"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a living thing? A) a rock  B) a tree  C) a spoon  D) a car. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: classify_animals
    label: "Animal groups (mammal, bird, fish, insect)"
    prereqs: [living_nonliving]
    grounding: {}
    transfer_seeds:
      - "Which of these is a mammal? A) shark  B) dog  C) eagle  D) ant. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: states_of_matter
    label: "Solids, liquids and gases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a liquid? A) a rock  B) water  C) air  D) ice. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Science (testing template)

A multiple-choice science sibling to the fractions pilot, for product-testing variety.
Questions are generated from small curated fact tables; the verifier checks the child's
letter against the table's ground truth, so the model never decides correctness.
