---
type: Mentar Design Doc
title: "GAP: primary maths is visual-first, Mentar asks it in words"
description: "Flagged 2026-08-21 by the maintainer. Years 1-3 maths is taught concrete-then-pictorial and only becomes symbolic around Year 4; Mentar asks every year in the Year-4 register. Measured: 2 of 40 Y1-4 questions show the child anything. NOT a plan — a recorded gap awaiting a maintainer decision."
tags: [design, curriculum, pedagogy, gap, needs-decision]
timestamp: "2026-08-21T00:00:00Z"
---

# GAP: primary maths is visual-first, Mentar asks it in words

**Status: FLAGGED, not scheduled.** Nothing here is agreed or started. It
changes what a generator *is*, so it is a maintainer decision, not a wave.

## The observation (maintainer, 2026-08-21)

> "Because maths is visual first then goes into nonvisual by year 4"

This is the concrete → pictorial → abstract progression. Years 1-3 work on
things a child can see and count; the symbolic register that Mentar uses
everywhere only becomes age-appropriate around Year 4.

## The evidence

Prompted by two real Year-2 worksheets (North Shore Coaching College,
"Improve your Maths and General Ability Concepts", Level 2 Lesson 6):

* **Area** — twelve shapes drawn on a 1 cm grid (L-shapes, arrows, diamonds,
  hexagons, shapes with rectangles cut out, diagonals making half-squares).
  The child reads the shape and counts/computes shaded squares.
* **Time** — read an analogue clock face and write the time in words; then
  **draw the hands** on a blank clock to show 9:00, 4:30, 6:15, 9:45, 7:10,
  5:20, 6:40, 11:55.

Classifying every shipped AU Y1-Y4 maths question by whether it SHOWS a
visual, DESCRIBES one in prose, or is pure text:

| Year | Shows a picture | Describes one | Pure text |
|---|---|---|---|
| 1 | 1 | 0 | 5 |
| 2 | **0** | 2 | 7 |
| 3 | 1 | 0 | 9 |
| 4 | 0 | 1 | 9 |

**2 of 40 topics show the child anything.** The one Year-1 hit is
`au1_count_objects` ("Count the stars: ★★★★★★★"), which works precisely
because it shows.

Where prose stands in for a picture it also does the child's work:

* `au2_time_oclock` — *"the little hand points at 4 and the big hand points
  straight up at 12"*. Reading the hand positions IS the skill; describing
  them hands it over.
* `au4_area_count_squares` — *"a rectangle is covered by centimetre squares:
  7 squares along, 4 rows"*. That is a multiplication question wearing an
  area costume; the worksheet's L-shapes and half-squares are a different
  skill entirely.
* `au1_shape_sides` — *"How many sides does a hexagon have?"* is recall. A
  Year-1 child should count the sides of a shape in front of them.
* `au2_position_words` — a spatial question with nothing to look at.

## Why the coverage auditor cannot see this

`mentar.tools.audit_curriculum_coverage` reports AU at **0 gaps**. That
measures WHICH STRANDS EXIST, not whether a topic is askable in the right
mode. A strand-complete Year 2 asked entirely in prose is not delivering
Year 2. This is the same "counts, not claims" failure the auditor was built
to end, one level further out — and the auditor is structurally blind to it,
so the honest reading of "0 gaps" is "0 STRAND gaps".

## Two separable gaps

1. **Questions cannot SHOW.** Visuals today are generic teaching diagrams
   attached to explanations (`curriculum/visual_scaffolds/`), chosen by
   keyword and shared across many items. There is no per-item generated
   picture drawn with its own numbers.
2. **Answers cannot BE a drawing.** "Draw in the hands to show 6:40" has no
   representation in the answer path at all.

## What already exists (the plumbing is not the problem)

* SVG is rendered in-app today (the `/progress` concept graph, owned code, no
  library).
* A dedicated non-LLM path renders fenced ASCII art (`<pre class="ascii-art">`,
  `steps-pre`), deliberately bypassing the markdown-lite sanitiser because it
  was never model output (U-32).
* Generators already produce exact-by-construction values, so a shape's area
  or a clock's time would be known exactly, not parsed back out of a picture.

What is missing is that visuals are *retrieved* rather than *generated per
item*. A grid polygon, a clock face, an array, a number line, a fraction bar
are each the same pattern every generator already follows — emit a picture
alongside the exact answer.

## Cost, honestly

* **Showing** (grid shapes, clock faces, arrays, number lines): achievable,
  and the biggest single win — it makes Years 1-3 work as Years 1-3.
* **Drawing as an answer**: a genuinely new answer widget (draggable hands,
  clickable grid squares). Sidesteppable by showing the clock and asking the
  child to TYPE the time, which recovers most of the value.

## Related

* [[curriculum_depth_program]] — breadth work; this gap says breadth is the
  *lesser* problem for Y1-3, since more years in the wrong register do not
  help.
* The same root issue makes **Year 1 unusable for its age group**: a
  five-year-old can neither read the prompt nor type the answer. Read-aloud
  exists (`web/static/tts.js`, offline speech synthesis); voice INPUT does
  not, and the browser's recogniser is a cloud-backed trap against U-80.


---

# Build-pattern inventory (compiled 2026-08-21, maintainer request)

*"Compile a list where we need build patterns for this. It will be mostly
Maths we can do. Not sure for other subjects."*

Compiled against every shipped AU topic. A pattern is listed when the picture
IS the question — not when a picture would merely be nice. Ranked by leverage
(how many shipped topics one pattern unlocks).

## Maths — 13 patterns, ranked

| # | Pattern | Topics unlocked | Where |
|---|---|---|---|
| 1 | **Fraction bar / part-whole shape** (shape split into parts, some shaded) | **7** | Y2 halves & quarters · Y3 unit fractions · Y3 fractions of a whole · Y4 equivalent fractions · Y4 adding fractions · Y5 fraction × whole · Y6 fraction↔decimal |
| 2 | **Grid shape** (polygon on squared paper, incl. diagonals/holes) | **5** | Y3 perimeter · Y4 area by counting squares · Y5 perimeter of a rectangle · Y6 area & perimeter · Y7 area of a triangle |
| 3 | **Array / grouped objects** (rows × columns of countable things) | **5** | Y1 counting objects · Y1 adding small numbers · Y2 times tables · Y4 times tables to 10×10 · Y4 division facts & sharing |
| 4 | **Number line** (marked line, jumps, negatives) | **5** | Y1 counting by 2s · Y3 number patterns · Y5 decimal place value · Y5 negative numbers (thermometer) · Y7 integer add/subtract |
| 5 | **Place-value columns / base-ten blocks** | **4** | Y2 place value to 99 · Y3 to 999 · Y4 to 9999 · Y5 decimal place value |
| 6 | **Data display** (picture graph, bar chart, dot plot) | **4** | Y1 comparing votes · Y3 picture graphs · Y5 average · Y7 median |
| 7 | **2D / 3D shape** (drawn shape, countable sides/faces) | **3** | Y1 sides of a shape · Y3 3D shapes · (Y4 angle drawing, below) |
| 8 | **Angle / protractor** (drawn angle, degrees) | **2** | Y4 angles in degrees · Y7 angles on a straight line |
| 9 | **Coordinate grid** (labelled axes, plotted point) | **2** | Y5 moving on a grid · Y6 Cartesian quadrants |
| 10 | **Clock face** (analogue, hands at a known time) | **1 (+3 missing)** | Y2 reading o'clock — and the half-past / quarter-past / 5-minute topics Y2 does not yet have |
| 11 | **Money** (coins and notes shown) | **2** | Y2 counting money · Y4 giving change |
| 12 | **Chance device** (spinner, dice, coins) | **2** | Y4 chance words · Y6 probability as a decimal |
| 13 | **Comparison pair** (two objects side by side to judge) | **3** | Y1 longer/shorter/heavier · Y2 comparing lengths · Y2 position words |

**Leverage note:** patterns 1-4 alone cover **22 topics** — over half of shipped
primary maths. Patterns 1 and 2 are also the two the maintainer's Year-2
worksheets actually test.

**Already partly solved:** the vertical algorithm for column addition,
subtraction and division is itself the visual, and step grids for it already
ship (`_arithmetic_steps.html`, `render_steps_grid_lines`). Y2/Y3 add-and-
subtract therefore need no NEW pattern — they need the existing grid attached
to the QUESTION, not only to the explanation.

## Science — mostly optional, 1 genuine case

Primary science here is overwhelmingly **classification** (living/non-living,
grouping animals, grouping materials, producers/consumers, materials attracted
to a magnet). Those are legitimately answerable in words: naming a category
from a list is the actual skill, and a picture would raise engagement without
changing what is being tested. Not a gap.

The exceptions, weakest to strongest:

* **Life cycle stages (Y3)** — a cycle IS a diagram; egg→caterpillar→
  chrysalis→butterfly in prose loses the cyclic structure. The only primary
  science topic where the picture is arguably the question.
* Sun/Earth/Moon (Y4), day and night sky (Y1), how things move (Y2) — a
  diagram helps a lot; the question survives without one.

**Verdict: one pattern (cycle diagram), plus reuse of the maths shape/array
work where it happens to fit.** Science does not need its own programme.

## English — essentially none, with one irony

Phonics, rhyme, synonyms/antonyms, plurals, prefixes/suffixes, homophones,
contractions, word classes, sentence structure, punctuation, comprehension —
all inherently linguistic. Text is the correct medium; adding pictures would
be decoration.

Two exceptions:

* **"Pictures that carry meaning" (Y4 visual literacy)** — a topic *about*
  interpreting photographs, diagrams and maps, currently taught with no image
  at all. The one English topic where the absence is self-defeating.
* **"Big and small letters" (Y1)** — letterform display would help a child who
  cannot yet read the prompt describing the letters.

**Verdict: English does not need this work.** That answers the maintainer's
open question directly.

## Summary

* **Maths: 13 patterns, 4 of them covering half of primary.** This is the work.
* **Science: 1 pattern (cycle diagram)** and some optional reuse.
* **English: none** beyond the single visual-literacy topic.
* Answer-side drawing ("draw the hands to show 6:40") remains separate and
  unaddressed by any of the above.


---

# SECOND COMPILE (2026-08-21) — full sweep, and it CORRECTS the first

The list above was compiled from **primary maths plus Y1-Y4 science/English**
— roughly 60 of the 378 shipped AU topics. This pass classifies **all 378**.
Two of its conclusions survive unchanged; one does not.

## Measured across every shipped AU topic

| Subject | Shows a picture | Describes one in prose | Pure text |
|---|---|---|---|
| mathematics (182) | 3 | 9 | 170 |
| science (57) | 0 | 0 | 57 |
| physics (13) | 0 | 0 | 13 |
| chemistry (13) | 0 | 0 | 13 |
| biology (12) | 0 | 0 | 12 |
| earth & environmental (9) | 0 | 0 | 9 |
| english (92) | 0 | 0 | 92 |
| **total (378)** | **3** | **9** | **366** |

## CORRECTION: this is not a primary-only problem

The first compile framed the gap as Years 1-3. The full sweep shows the same
defect running through **senior** maths, and there it is sharper, because
describing the picture often hands over the very skill being tested:

| Topic | Asked as | What is lost |
|---|---|---|
| `au12e_shortest_path` | *"Route 1: two roads of 5 km and 7 km. Route 2: three roads of 2, 5 and 4 km. Which is shorter?"* | Searching a weighted network. As asked it is "add 12 vs add 11" — arithmetic, not graph theory. |
| `au12g_eulerian_trail` | *"A network's vertices have 4 vertices of ODD degree…"* | **Counting the odd-degree vertices from a diagram IS the skill.** The question states the answer's input. |
| `au11g_correlation_direction` | *"as daily temperature rises, heater use falls"* | Reading direction off a scatterplot. The question states the relationship. |
| `au12e_scatter_trend` | *"A scatterplot shows that as price increases, number sold decreases"* | Same. |
| `au11g_two_way_table` | *"A two-way table of 37 students: sport AND music 8; sport only 9…"* | Reading a two-way table. |
| `au2_time_oclock` | *"the little hand points at 4, the big hand straight up at 12"* | Reading a clock face. |

So the honest scope is **primary + the data/networks/geometry strands of
secondary and senior maths** — not Years 1-3 alone.

## CONFIRMED: science genuinely does not need this

Across all **104** science topics (junior + physics + chemistry + biology +
earth & environmental), **not one describes a picture it cannot show**. They
are classification items — "which of these is a producer / an alkane / an
igneous rock" — where naming the category from a list is the actual skill.
The first compile's verdict holds, now on complete data rather than a sample.
Life cycles remains the single case where a diagram would be the natural
representation.

## CONFIRMED: English needs none

**92 of 92** English topics are pure text, and correctly so. The only
exception remains Y4 "Pictures that carry meaning", which teaches visual
literacy with no image.

## Additional patterns the senior sweep adds

Beyond the 13 primary patterns above:

| # | Pattern | Topics | Notes |
|---|---|---|---|
| 14 | **Function graph / curve** | ~11 | Y11-12 Methods (vertex, gradient of a curve, increasing/decreasing, sine period, stationary point, area under a line) + Y11 General linear/non-linear rules. Mostly *helpful*: senior students are expected to work symbolically, so the picture supports rather than constitutes the question. |
| 15 | **Scatterplot with trend** | 7 | Y9, Y10, Y11 General, Y12 Essential ×2, Y12 General ×2. **Constitutive** — reading a plot is the skill. |
| 16 | **Network / graph diagram** | 4 | shortest path, complete-network edges, spanning tree, Eulerian trail. **Constitutive for two of the four**; the other two are formula recall (n−1, n(n−1)/2) that is legitimately verbal. |
| 17 | **Matrix grid** | 6 | Y11 Essential ×2, Y11 General ×2, Y12 General ×2. **Already solved in one place** — `au11e_matrix_read` prints an ASCII grid today, which is existence proof that the pattern works in the current architecture. |
| 18 | **Right-triangle / trig diagram** | 3 | Pythagoras, tan height, similar shapes. |
| 19 | **Circle diagram** | 3 | circumference, angle at the centre, radius from equation. |
| 20 | **Vector arrows** | 4 | 2D/3D addition, magnitude, dot product. |
| 21 | **Argand diagram** | 4 | complex add/multiply, modulus, argument (argument is currently *described*). |
| 22 | **3D solid** | 3 | prism volume, box volume, composite area. |
| 23 | **Two-way table** | 1 | constitutive. |
| 24 | **Globe / meridian** | 2 | time zones, distance along a meridian. |

## Revised summary

* **Maths: 24 patterns.** The four primary ones (fraction bar, grid shape,
  array, number line) still carry the most topics (22); scatterplot, matrix
  grid and function graph lead the senior half.
* **Constitutive vs supportive is the useful split.** Where the picture IS
  the question — grid area, clock faces, scatterplots, two-way tables,
  networks, fraction bars — the topic is currently mis-taught, not merely
  plain. Where it merely supports — most senior algebra and calculus —
  text is defensible.
* **Science: 1 pattern.** Confirmed on all 104 topics.
* **English: 0 patterns.** Confirmed on all 92.
* One pattern is already proven in-tree (the ASCII matrix), and column
  arithmetic already has step grids — so the first implementation is smaller
  than the pattern count suggests.
