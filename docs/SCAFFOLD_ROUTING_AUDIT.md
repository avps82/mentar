---
type: Mentar Audit Doc
title: "Scaffold Routing Audit — four mis-routed concept nodes"
description: "Audit of visual-scaffold keyword routing: three mis-routes fixed, five defects left open, plus the reason the coverage test stayed green throughout."
tags: [curriculum, visual-scaffold, routing, audit]
status: "Reviewed and merged 2026-08-22. All five OPEN items decided; four fixed, one left as recorded debt."
generated: { by: "claude/opus-5", at: "2026-08-22T01:40:00Z" }
---

# Scaffold Routing Audit — 2026-08-22

Produced by a Claude Code session rooted in `<local-llm-infra>`, working in this
repo on 2026-08-22 (~00:10–01:40). The changes it describes were left **uncommitted** for
maintainer review. **Reviewed, corrected and merged the same morning — see "Review" at the
bottom, which is now the authoritative part of this document.**

## TL;DR

Four concept nodes were routing to the **wrong** visual scaffold. Three are fixed here; the
fourth and three other defects are listed under OPEN and were deliberately left alone.

**No conflict with your work.** You changed `src/mentar/engine/visual_scaffold.py` + its test
(commit `67562c2`, 00:04). This session changed **only** `curriculum/visual_scaffolds/*.md`.
Zero file overlap. Every routing check below ran against your post-`67562c2` matcher.

## Root cause

A short generic `topic_keywords` entry silently wins labels it has nothing to do with.
Routing scores by MOST keywords matched, so a one-word claim on a common token beats a
specific file that happens to match nothing.

## Changed files (7)

Keyword narrowing — the actual bug:

```diff
- senior_vector3_magnitude.md  topic_keywords: [magnitude of a 3d, 3d vector, 3d]
+ senior_vector3_magnitude.md  topic_keywords: [magnitude of a 3d, 3d vector]

- senior_moving_average.md     topic_keywords: [moving average, moving]
+ senior_moving_average.md     topic_keywords: [moving average]

- year1_comparing.md           topic_keywords: [longer, shorter]
+ year1_comparing.md           topic_keywords: [longer, shorter, comparing lengths]
```

New scaffolds (needed, because removing the greedy keywords left two nodes genuinely
uncovered and `test_every_concept_node_has_a_scaffold` then fails):

- `maths/year3_shapes_3d.md` (32 lines) — faces/edges/corners of solids, for `au3_shape_3d`
- `maths/j_grid_move.md` (21 lines) — coordinate translation, for `au5_grid_move`

Docs:

- `maths/index.md` — both new files registered (hygiene test requires this)
- `visual_scaffolds/index.md` — the Routing paragraph was wrong in 3 of 4 clauses
  (claimed plain substring + first-match-wins). Rewritten to match the code, with a
  "keep keywords SPECIFIC" warning and the two mis-routes as worked examples.

## What was wrong, concretely

| node | label | was served | now |
|---|---|---|---|
| `au3_shape_3d` | "3D shapes" | `senior_vector3_magnitude.md` — √(x²+y²+z²) | `year3_shapes_3d.md` |
| `au5_grid_move` | "Moving on a grid" | `senior_moving_average.md` — sliding window | `j_grid_move.md` |
| `au2_length_compare` | "Comparing lengths" | `area_perimeter.md` — 6cm×4cm rectangle | `year1_comparing.md` |

The 3D one explains a real symptom: 3D-shape questions were generated with vector-magnitude
guidance in the prompt, producing a corners question hinted "count top, bottom, then around
the sides" — that is the FACES procedure, and applied to corners it yields 12 instead of 8.

## Verification already done

```bash
cd "<mentar-repo>"
python3 -m pytest -q                       # 1186 passed, exit 0, 19m29s
python3 -m ruff check curriculum           # clean
```

Content of the new 3D table was checked against known values and Euler's V − E + F = 2
(cube 8−12+6, triangular prism 6−9+5, square pyramid 5−8+5 — all = 2). Curved solids use the
stated primary convention and are flagged in the file's own guidelines.

Re-check routing directly:

```bash
python3 - <<'PY'
import sys, pathlib; sys.path.insert(0,"src")
from mentar.engine.visual_scaffold import load_visual_scaffold, first_diagram
R = pathlib.Path("curriculum/visual_scaffolds")
for l in ["3D shapes","Moving on a grid","Comparing lengths",
          "Magnitude of a 3d vector","Moving average","Area and perimeter of a rectangle"]:
    print(l, "->", (first_diagram(load_visual_scaffold(R,"mathematics",l)) or "(none)").splitlines()[0])
PY
```

The last three are the regression check: the senior/area scaffolds must still win their own
labels after the keyword narrowing.

## OPEN — found, deliberately NOT changed

1. **`probability.md` serves its first diagram (the 0–1 probability scale) to
   "Two-stage probability" and "Probability with two coins".** The file's own guideline says
   trees for those. Not pinned by any test, so a file split is safe. New instance of the
   documented one-topic-per-file class.

2. **"Multiplying negative numbers" is served a thermometer** from `negative_numbers.md`.
   The sign rule exists there only as prose, never as a diagram. **Left alone because
   `tests/engine/test_scaffold_coverage.py:236` PINS this label to `'10°C'`** — the pin
   was written from observed behaviour, so fixing the content means changing the expectation.
   Maintainer call.

3. **`grammar.md`** — 7 diagrams, 10 keywords; every label it wins gets diagram one, so
   English "Commas" is shown parts-of-speech. Already named in
   `test_scaffold_hygiene.py`'s docstring as known debt. Splitting English grammar is a
   design change, not an overnight fix.

4. **`year1_shapes.md` uses U+2B20 ⬠ and U+2B21 ⬡.** No monospace font on this machine
   covers them (`fc-list ":charset=2B20"` → only Unifont-JP, FreeSerif, DejaVu Sans, all
   proportional). `.ascii-art` renders with `--font-mono`, and DESIGN.md deliberately
   forbids downloaded fonts, so there is no fallback. △ U+25B3 and □ U+25A1 ARE covered by
   DejaVu Sans Mono. Expect broken column alignment or tofu on line 2. Consolas/Menlo/SF Mono
   also lack that block — verify on a real child-facing device before deciding whether to
   keep the pictures or drop to words.

5. **`english/vocabulary.md` is unreachable** — no concept label routes to it, a side effect
   of the 21 Aug containment tie-break. Dead, possibly reserved on purpose. Not touched.

## The structural point worth acting on

`test_every_concept_node_has_a_scaffold` asserts only that **some** scaffold matches. It was
**green** the entire time these three nodes were mis-routed, and went red only once the greedy
keywords were removed. It cannot distinguish "attached" from "correctly attached".

The per-label pins in `test_scaffold_coverage.py` are the mechanism that can — but item 2
above shows a pin written from observed behaviour freezes a bug instead of catching it.
Suggest adding pins for `3D shapes`, `Moving on a grid` and `Comparing lengths` now that
they are correct.

## Also checked, clean

- Arithmetic in every fenced diagram: 11 equation chains, 22 numeric segments, 0 mismatches.
  Thin coverage — most worked examples have a symbolic side and cannot be machine-checked.
- `src/mentar/web/static/style.css` was NOT left mutated by the long-running CSS mutation
  test; file and git status both clean, `/tmp/style.css.bak` intact.


---

# Review — 2026-08-22

Independently verified, then extended. The three mis-routes are real and the fixes are
sound; four further defects were found in the review itself, three of them introduced or
missed by the audit.

## Verified

* **All six routing labels correct**, including the three regression labels. Checked by
  filename, not by eyeballing the art.
* **Blast radius measured, not assumed.** Routing was recomputed for **all 934 nodes**
  against committed `HEAD`: exactly **3** changed, the three claimed. The "zero file
  overlap with 67562c2" claim also holds.
* **The 3D table is arithmetically right** — cube 8−12+6, triangular prism 6−9+5, square
  pyramid 5−8+5, all = 2; curved solids use the standard primary convention.

## Corrected during review

1. **`year3_shapes_3d.md` repeated the very mistake it documents.** Its corners line read
   "count the 4 on top, then the 4 on the bottom" — true only of a cube. This node's own
   first question is about a **triangular prism** (3 and 3), and a square pyramid is 4 plus
   an apex. Generalised, and the guidelines now name the trap explicitly.

2. **The `au2_length_compare` re-route put a contradiction on the screen.** Routing it to
   `year1_comparing.md` made that file's diagram eligible for the explain card (the previous
   target, `area_perimeter.md`, has digits and was blocked). The result: a card reading
   *"the pencil is 9 cm longer"* with **`pencil (shorter)`** appended directly beneath it,
   plus a `⚖ heavier side goes DOWN` line on a length question. Fixed by SPLITTING
   `j_length_compare.md` out — the ratified one-topic-per-file remedy — with deliberately
   **no object names**, so it cannot contradict whatever the item happens to name.
   The audit checked routing but not what the routing then puts on a card.

3. **Frontmatter deviated from house style.** Both new files used
   `generated: { by: "claude/opus-5", ... }`; all 258 existing scaffolds use `timestamp:`.
   No test enforces this, which is why it slipped. Normalised — and model authorship does
   not belong stamped inside shipped curriculum content.

4. **The greedy-keyword mutation does not reproduce the original bug.** Re-adding `3d` to
   `senior_vector3_magnitude.md` leaves routing CORRECT, because `year3_shapes_3d.md` now
   matches two keywords and wins on count. The fix is more robust than the audit claimed —
   but it means that mutation proves nothing, and the pin below had to be proved a different
   way (by making the new file stop claiming the label).

## OPEN items — all five decided

| # | Item | Decision |
|---|---|---|
| 1 | `probability.md` serves the 0–1 scale to two-stage questions | **FIXED** — split `probability_tree.md` out |
| 2 | Thermometer for "Multiplying negative numbers", frozen by a pin | **FIXED** — split `j_multiplying_negatives.md` out; pin updated |
| 3 | `grammar.md`: 7 diagrams, 10 keywords | **LEFT** as recorded debt |
| 4 | `year1_shapes.md` uses ⬠ U+2B20 and ⬡ U+2B21 | **FIXED** — measured, then replaced |
| 5 | `english/vocabulary.md` unreachable | **NOT A BUG**, and the stated cause is wrong |

**Item 2** was right to flag the pin, and right that a maintainer had to call it. The call:
a pin written from observed behaviour freezes whatever was true, bug included. This is the
**second** instance — "Square numbers" was pinned to an area rectangle and fixed on
2026-08-21. A thermometer shows where a directed number *sits*, which is the right picture
for adding and subtracting and says nothing about why two negatives make a positive.

**Item 4 was measured, not reasoned about.** In headless chromium against this stylesheet's
`--font-mono`: ⬠ and ⬡ render at **1.37 and 1.38 monospace cells**, so every row beneath
them slides sideways. △ U+25B3, □ U+25A1 and ○ U+25CB all measure exactly **1.00**. The
audit inferred this from `fc-list` coverage and was right. Pentagon and hexagon are now
named rather than drawn — `DESIGN.md` forbids downloaded fonts, so there is no fallback.

**Item 5's cause is wrong and the correction matters.** The audit attributes the orphan to
the 21 Aug containment tie-break. Tested directly under the pre-21-Aug count-only matcher:
**zero of 141 English labels** reached `vocabulary.md` then either. It has never been
reachable, because nothing shipped owns `spelling`, `phonics`, `root word` or `decode` — the
four labels brushing its keywords are synonym/antonym nodes that win elsewhere **on count**.
It is dead content awaiting curriculum, not a routing regression. Left in place; the wrong
cause is corrected here so nobody "fixes" the tie-break chasing it.

## Acted on: the structural point

The audit's central observation is correct and is the most valuable thing in it —
`test_every_concept_node_has_a_scaffold` asserts only that *some* scaffold matches, so it
stayed green through months of mis-routing and went red only when the greedy keywords were
removed. Per-label pins are the mechanism that can tell "attached" from "attached to the
right thing", so pins were added for **3D shapes**, **Moving on a grid** and
**Comparing lengths**, and proved to bite.

The tension with item 2 is real: pins catch mis-routing, and pins written from observed
behaviour entrench it. A pin is only worth what the judgement behind it was worth — add one
when you have just *verified* the routing, never to record what the code currently does.
