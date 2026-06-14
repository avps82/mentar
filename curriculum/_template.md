---
# Mentar curriculum template — schema v0.1
# Copy this file to curriculum/templates/<country>/<year-or-subject>.md and fill in.
# Validate with: mentar validate-template <path>   (or: python -m mentar.tools.validate_template <path>)
# Spec: docs/SPEC.md §9-10; schema: docs/PHASE0.md W3.1; tests: docs/TESTS.md T3.1.

template_id: country-yearN-subject                  # e.g. au-y4-math, pilot-fractions
country: AU                                          # ISO 3166-1 alpha-2, or null for cross-country pilot
year_level: "Year 4"                                # human-readable; "pilot" for pilot templates
subject: mathematics                                # mathematics | english | science | ...
curriculum_standard: "Australian Curriculum v9"     # null if not aligned to a published standard
schema_version: "0.1"

language_register:
  reading_level: "Year 4 / ~age 9"
  vocabulary_note: "Concrete examples; short sentences; minimal abstract jargon."

# concepts: the KST graph for this template.
# Rules (enforced by validate_template):
#   - id is unique within this template (snake_case).
#   - prereqs is a list of ids that appear earlier in this file (no cycles).
#   - every prereq id must exist in this concepts list.
#   - the graph must be a DAG with at least one root (empty prereqs).
#   - orphan nodes (unreachable from any root) emit a warning.
# Per-node:
#   - grounding: a vetted source the AI re-explains FROM (RAG, not free recall — SPEC §15 layer 1).
#   - transfer_seeds: ≥2 prompt seeds for generating transfer (NEW-surface) re-check questions (SPEC §13.2(3)).
#   - verifier: deterministic checker spec used at serve-time before any answer is shown (SPEC §15 layer 2).
#   - bkt_priors: optional per-node override of W3.3 defaults (guess 0.2/mc4 or 0.05/numeric, slip 0.1, learns 0.2, forgets 0).
concepts:
  - id: example_root_concept
    label: "Example root concept (no prereqs)"
    prereqs: []
    grounding:
      source: vikidia                              # vikidia | wikipedia_simple | wikibooks | parent_upload | builtin
      anchor: "https://en.vikidia.org/wiki/Example"
      passage_hint: "Definition section"
    transfer_seeds:
      - "A real-world scenario phrased differently from the example used in Help."
      - "Another framing — a different concrete surface, same underlying concept."
    verifier:
      answer_type: mc4                             # int | fraction | mc4 | free_text
      checker: mc_choice                           # int_exact | fraction_equiv | mc_choice | none
    bkt_priors:
      guess: 0.2
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: example_dependent_concept
    label: "Example concept that requires the root"
    prereqs: [example_root_concept]
    grounding:
      source: wikipedia_simple
      anchor: "https://simple.wikipedia.org/wiki/Example"
      passage_hint: "Worked example"
    transfer_seeds:
      - "A transfer prompt — same concept, different numbers/surface."
      - "Another transfer surface to vary the modality."
    verifier:
      answer_type: fraction
      checker: fraction_equiv
---

# <Subject> — <Year / Grade level>

<!--
Markdown body: human-facing guidance for parents and contributors.
The concept structure lives in the YAML frontmatter; this body explains the WHY
(prereq ordering rationale, calibration notes, age-appropriateness reminders) and
is also read by parents during template selection.
-->

## Overview

Brief 1-paragraph description of what this template covers and the spine of the prereq chain.

## Prerequisite rationale

Explain why the concept ordering is what it is — what concept builds on what, in plain language.
A reviewer reading this should be able to spot a misordered prereq without reading code.

## Calibration notes

- Sentence complexity: short sentences; one clause per sentence at this level.
- Concrete-before-abstract: use objects/quantities the learner has touched.
- Common misconceptions to flag in Help: list them.

## Out of scope

Topics at adjacent year levels that should be redirected if the learner asks
(e.g. "different denominators — Phase 1 / Year 5+", "decimals — separate template").

---

*Template format version 0.1 — see [docs/PHASE0.md](../docs/PHASE0.md) W3.1.*
*Contribute improvements via PR.*
