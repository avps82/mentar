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


---

# SLICE 1 SHIPPED (2026-08-21) — the channel exists

Plan approved and the whole pipe is built, proved on `unit_fractions` (existing
`_fraction_bar`, so zero new art):

* **Generator → screen channel.** 8th positional slot on the generator tuple
  (`itemgen._make`), `Item.visual`, `SessionController.current_visual`,
  `TurnResult.visual` (so the CLI and the durable transcript carry the picture —
  a constitutive question without it is unanswerable), `_turn_context`'s
  `visual_lines`, and a `_question_visual.html` partial. **8 slots is recorded as
  the ceiling**: a 9th means moving `GenFn` to a keyword builder.
* **Rendered in `.ascii-art`, not `.steps-pre`** — the latter is `overflow-x:
  hidden`, which would silently CLIP a picture the question depends on.
  `.question` gained `flex-wrap` so the picture takes its own full row.
* **Browser-verified** (the actual gate): picture above the text, full width,
  **truly monospaced** — proved by rendering `iiii` vs `MMMM` at equal width, not
  by string-matching a font name, because style.css records the mono token once
  being silently unset.
* **The no-repeat window is fixed.** `_dedup_key` now includes the picture;
  previously a visual node burned all 8 re-rolls, "collided" every time and
  served the last roll — the guarantee was dead for exactly the questions that
  most need variety.
* **The summary-line inversion is guarded.** Every existing renderer ends with an
  answer-bearing line ("1 of 5 equal parts shaded = 1/5") — correct on the card,
  fatal on the question. `_fraction_bar` gained `summary=False`; a test asserts no
  question picture contains its own answer, mutation-proved by re-adding the line.
* **Review, both surfaces:** `python3 -m mentar.tools.show_question_visuals`
  (node-derived seeds so re-runs diff rather than scramble) and a `/gallery`
  section fed by the **real renderers**, never hand-typed art.

The fix propagated to all four country packs automatically — the generic packs
derive from the same generator dicts, so 6 nodes now draw a picture from one change.

## Accessibility limitation (recorded, not papered over)

The picture carries **no `aria-hidden` and no `aria-label`**. `aria-hidden` would
declare it decorative, which is false — it *is* the question. An `aria-label` would
have to describe it, and any accurate description states the answer ("a bar with 1
of 5 parts shaded" IS 1/5). The app's own read-aloud is silent on it structurally
(the `<pre>` is a sibling of `.question-text`, which is what `tts.js` reads).

So: **a constitutive visual question is not screen-reader answerable.** That is a
property of the pedagogy, not a bug to be clevered away, and it is the honest
counterweight to the gap this work closes.

## Bug-hunt pass, 2026-08-21 (post-ship)

Three defects, all found by measuring rather than reading. Each is mutation-proved.

### 1. Every earlier "phone width" measurement was fiction

The first probes squeezed a **container** (`main{max-width:360px}`) and left the
viewport wide, so `@media` rules never fired. They reported "no problems" and the
number they produced was 6 characters too generous. Real device metrics
(`Emulation.setDeviceMetricsOverride`) tell a different story:

| Viewport | Characters that fit `.ascii-art` | Effect on the 8 shipped pictures |
|---|---|---|
| 360px | 29 | 4 scroll (by 1–6 columns) |
| 390px | 32 | 1 scrolls (the two-way table) |
| 414px | 35 | all fit |
| 768px | 69 | all fit |

`.ascii-art` side padding was cut 18px → 8px below 420px, worth **4 characters** —
the difference between a 30-column clock face fitting a 390px phone and not.
Shrinking the font was rejected: this is a picture a six-year-old has to read.
Pictures still over budget scroll, which is what `overflow-x: auto` is for.
Pinned by `test_a_question_picture_gets_a_usable_width_on_a_real_phone`, which
asserts the *budget* (≥29 chars) and that the metrics actually applied — a test
that silently measures a 1280px window is the fiction it replaces.

### 2. The fraction bar was 51 columns while claiming to fit a phone

`_fraction_bar` drew 4-wide cells, so d=8 was 41 columns and d=10 was 51 — its own
docstring said denominators to 10 "stays inside a phone's monospace width". Cells
are now 2 wide (d=10 = 31). The two-way table went 40 → 35 the same way.
`PHONE_COLUMNS = 35` now caps every generator across a 40-seed sweep.

### 3. A skip-counting question was shown the count-by-ones picture

Checking whether a question picture and an explain-mode scaffold diagram can
contradict each other turned up a routing bug instead. "Counting by 2s" matched
`year1_counting.md` on `counting` and `year1_skip_counting.md` on `counting by 2s`
— one keyword each, so the alphabetical tie-break gave the generic file the win. A
child asked to count 2, 4, 6, 8 got ★ ★ ★ ★ ★ / "touch each one once": not a
different example, the **wrong method**.

`load_visual_scaffold` now breaks ties on **containment** — a keyword that strictly
contains a rival's is a refinement of it. Keyword *length* was tried first and is
wrong: `vocabulary` is longer than `synonym` but more generic, and length sent a
synonym question to the generic Frayer box. Both directions are pinned.

This is the tie-break half of the defect class in `one-scaffold-file-per-concept`.

**The tie-break change is global, so its blast radius was measured, not assumed:**
routing was recomputed for all **934 curriculum labels** under both rules. Nine
changed, across three concepts — and the two that were not the target were both
worse under the old rule:

| Label | Was shown | Now shown |
|---|---|---|
| Counting by 2s | count-the-stars one-by-one | skip-count number line |
| Electrochemical cells (4 packs) | **plant-cell vs animal-cell diagram** | galvanic/electrolytic cell |
| Compound interest — two years (4 packs) | flat-percentage hundred grid | year-on-year growth factor |

The chemistry one is the costliest and nobody was looking for it: `cell_structures.md`
matched `cell` + `cells` and `senior_electrochemistry.md` matched `electrochemical` +
`electrochemical cells` — two keywords each, so alphabetical order handed a senior
chemistry question a **biology** picture, in four country packs. Diffing every label
found it; reading the code would not have.

### 4. Two scaffolds never matched the node they were written for

Listing every label whose scaffold is *still* decided by alphabetical order (18 of
934) turned up two files that existed for exactly the node they never reached,
because their keywords were written in a different register than the label:

* `senior_matrix_addition.md` claimed `[adding matrices, matrices]` — **plural** —
  against the label "Matrix addition". Zero hits on its own node, so a Year-11
  matrix question was shown the **primary number-line jump strategy**.
* `senior_organic_families.md` claimed `[organic families, organic]` and tied with
  a reaction-**rates** file on `reaction`, losing on filename order — so an
  organic-families question was illustrated with collision theory.

Both fixed by giving the right file a compound keyword containing its rival's,
which is the steering the containment tie-break exists to enable.

### 5. The periodic table had claimed the word "group"

`periodic_groups.md` listed the bare keywords `group` **and** `groups`. That is two
hits on any label containing the word, which beat `vertebrates.md`'s single
`vertebrate` on **count** — so no tie-break could have rescued it:

* "Vertebrate groups" (fish / bird / mammal) → the periodic table
* "Grouping materials" (Year-3 natural vs manufactured) → the periodic table

Narrowed to `periodic group` / `periodic groups`. "Vertebrate groups" now reaches
`vertebrates.md`, and the real chemistry labels keep theirs.

"Grouping materials" had no correct file at all — `materials_change.md` is about
bending and stretching, a different concept — so removing the wrong picture left it
bare and tripped `test_every_concept_node_has_a_scaffold`, which is that invariant
doing its job. A `grouping_materials.md` was authored for it (natural vs
manufactured, with paper and steel called out as the hard cases, since "starts from
something natural but needs people to make it" IS the concept).

Note the shape: findings 3 and 4 were tie-break bugs, this one is an
over-broad-keyword bug that wins outright. Both produce the same symptom, so
finding it needed the routing table, not the tie-break code.

### 6. "Square numbers" was illustrated with a rectangle's area

Third instance of the register mismatch, found by sweeping every label for one
served a scaffold sharing no word with the file's own name or title.
`squares_roots.md` claimed `squaring` and `perfect square` but not `square
number`, so it scored **zero** on the label "Square numbers" and the node fell to
`area_perimeter.md` on the bare word `square` — as in *area of a square*. A
question about 4, 9, 16, 25 got a rectangle's area and perimeter, in the US, IN
and SG packs.

Worth noting where this had been hiding: `test_senior_nodes_route_to_their_own_diagram`
**pinned** the node to `+──────────────+`, the area rectangle. A test whose name
says nodes must route to their own topic had recorded the opposite as expected.
Pin tables lock in whatever was true when they were written, including the bugs.

Routing was recomputed for all 934 nodes before and after: exactly 3 changed, all
of them this label, and the legitimate area labels ("Area of a square", "Perimeter
of a square", "Surface area of a cube") keep `area_perimeter.md`.

### Still decided by alphabetical order — maintainer's call, not guessed

16 labels remain where two files tie and neither keyword contains the other. Most
are defensible (`Halves and quarters` → bar model, `Perimeter formula` → labelled
rectangle). Three are **content gaps rather than routing bugs** — the right picture
does not exist, so no tie-break can find it:

| Label | Currently served | Gap |
|---|---|---|
| Product rule for derivatives | primary "equal groups" | no product-rule diagram exists |
| Scalar multiple of a matrix | primary "equal groups" | no scalar-multiple diagram exists |
| Reducing-balance loan (one month) | an authoring instruction, not a diagram | no loan diagram exists |
| Similar shapes and scale factor | multiplication's area model (on `factor`) | no scale-factor diagram exists |

Recorded rather than invented: authoring three senior diagrams is content work with
a pedagogical choice in it, not a bug fix.

### Checked and clean

The question picture correctly survives the whole Help round (`HELP_RECHECK_AWAIT`
is in `_QUESTION_AWAIT`), so a child re-answering still has the picture. When the
method card appears alongside it, both are drawn from the **same item**, so the two
pictures agree — the risk-5 contradiction does not occur. The card is only reached
via an explicit "Show me how" press, never a plain wrong answer.
