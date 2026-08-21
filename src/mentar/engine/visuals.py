"""ASCII pictures for QUESTIONS — pure, exact, and never stating the answer.

Visual-first (docs/design/visual_first_gap.md): for a "constitutive" topic the
picture IS the question, so it must be drawn from the item's own exact numbers
rather than retrieved from a generic scaffold.

Every renderer here obeys the contract the existing card-side helpers already
established:

  * pure `(exact params) -> tuple[str, ...]`, no I/O, no randomness;
  * return `()` when asked for something outside its supported range, so a
    caller gets NO picture rather than a broken one;
  * state the maximum column width in the docstring;
  * **pure ASCII, never emoji** -- emoji are double-width in most monospace
    stacks and would destroy the column alignment this whole module exists for
    (note `_THING_EMOJI` in itemgen.py legitimately puts emoji in problem PROSE;
    they must never reach a picture);
  * **never include the answer.** The card-side helpers end with a summary line
    ("1 of 5 equal parts shaded = 1/5") because a card is shown AFTER an attempt.
    A question is on screen while the child is still thinking, so anything here
    that would name the result is withheld. tests/engine/test_visuals.py pins it.

Lives in engine/ (not inside itemgen.py) so generators AND tools/ can import it
without dragging in itembank -- the same reason visual_scaffold.py sits here.
"""

from __future__ import annotations

import math

# ── grid shapes ──────────────────────────────────────────────────────────────

def grid_shape(cells: frozenset[tuple[int, int]] | set[tuple[int, int]],
               width: int, height: int) -> tuple[str, ...]:
    """A polygon shaded on squared paper -- the North Shore worksheet shape.

    `cells` is the explicit set of shaded (x, y) squares, so L-shapes, holes and
    (later) half-squares all work without changing this signature.

    Max width: 4*width + 3 characters, so width <= 9 keeps a phone happy.
    Deliberately carries NO area count -- counting the squares is the question.
    """
    if not 1 <= width <= 9 or not 1 <= height <= 9 or not cells:
        return ()
    if any(not (0 <= x < width and 0 <= y < height) for x, y in cells):
        return ()
    rule = "  +" + "---+" * width
    out = [rule]
    for y in range(height):
        row = "  |"
        for x in range(width):
            row += ("###|" if (x, y) in cells else "   |")
        out.append(row)
        out.append(rule)
    return tuple(out)


# ── clock faces ──────────────────────────────────────────────────────────────

# Character cells are roughly twice as tall as they are wide, so x is scaled to
# keep the dial round rather than squashed into an ellipse.
_CLOCK_ASPECT = 2.0


def clock_face(hour: int, minute: int, radius: int = 6) -> tuple[str, ...]:
    """An analogue clock with both hands drawn at their true angles.

    `radius` selects the dial size -- 6 is the compact face, 7 the larger one
    with more room between the numbers and the hands. Both are rendered side by
    side on /gallery so the choice is made from a real render, not from source.

    Hands are distinguishable by glyph AND length, the way a real clock is:
    `#` short and thick for the hour, `+` long and thin for the minute. The hour
    hand advances with the minutes (at 4:30 it sits BETWEEN 4 and 5), because a
    hand frozen on the hour would teach the wrong thing.

    Max width: about 4*radius + 5 characters. Carries no digital time -- reading
    the hands is the question.
    """
    if not 3 <= radius <= 9 or not 0 <= minute < 60 or not 0 <= hour <= 12:
        return ()
    w = int(2 * radius * _CLOCK_ASPECT) + 5
    h = 2 * radius + 3
    cx, cy = w // 2, radius + 1
    grid = [[" "] * w for _ in range(h)]

    def plot(x: int, y: int, ch: str, over_blank_only: bool = True) -> None:
        if 0 <= y < h and 0 <= x < w and (grid[y][x] == " " or not over_blank_only):
            grid[y][x] = ch

    for deg in range(0, 360, 3):                     # rim
        a = math.radians(deg)
        plot(int(round(cx + (radius + 0.7) * math.cos(a) * _CLOCK_ASPECT)),
             int(round(cy - (radius + 0.7) * math.sin(a))), ".")
    for n in range(1, 13):                           # hour numbers
        a = math.radians(90 - 30 * n)
        x = int(round(cx + radius * math.cos(a) * _CLOCK_ASPECT))
        y = int(round(cy - radius * math.sin(a)))
        label = str(n)
        for i, ch in enumerate(label):
            plot(x + i - (len(label) - 1) // 2, y, ch, over_blank_only=False)

    def hand(angle_deg: float, length: float, ch: str) -> None:
        a = math.radians(90 - angle_deg)
        steps = max(int(length * 14), 1)
        for t in range(3, steps):
            r = length * t / steps
            plot(int(round(cx + r * math.cos(a) * _CLOCK_ASPECT)),
                 int(round(cy - r * math.sin(a))), ch)

    hand((hour % 12) * 30 + minute * 0.5, radius - 3.0, "#")   # hour: short
    hand(minute * 6, radius - 1.3, "+")                        # minute: long
    grid[cy][cx] = "o"
    return tuple("  " + "".join(row).rstrip()
                 for row in grid if "".join(row).strip())


# ── arrays ───────────────────────────────────────────────────────────────────

def array_of(rows: int, cols: int, glyph: str = "*") -> tuple[str, ...]:
    """`rows` x `cols` countable marks -- the picture behind times tables,
    division as sharing, and "how many altogether".

    Max width: 2*cols + 2 characters, so cols <= 12 fits a phone.
    Carries no total: counting (or multiplying) them is the question.
    """
    if not 1 <= rows <= 10 or not 1 <= cols <= 12 or len(glyph) != 1:
        return ()
    row = "  " + " ".join(glyph for _ in range(cols))
    return tuple(row for _ in range(rows))


# ── number lines ─────────────────────────────────────────────────────────────

def number_line(start: int, stop: int, step: int = 1,
                mark: int | None = None,
                unknown_next: bool = False) -> tuple[str, ...]:
    """A labelled line from `start` to `stop`, optionally with a caret under one
    value, and optionally with a `?` cell where the NEXT value would go.

          2  4  6  ?
          +--+--+--+

    `unknown_next` exists because a "what comes next" question needs somewhere
    for the answer to go (maintainer, 2026-08-21). Without it the line stopped at
    the last KNOWN value, so a child was asked what follows 6 while looking at a
    picture that ended at 6 -- the one place the answer belonged was missing.

    The `jumps` parameter this replaced drew underscore arcs between values and
    rendered as a row of stray `__ __` under the line. It had exactly one caller,
    which is the draw that was broken, so it is gone rather than fixed: a hop arc
    that has to be explained is not doing the job a picture is for.

    Handles negatives, so it is also the thermometer/integer picture.
    Max width: about (len(longest label) + 2) * number of ticks.
    Carries no answer -- the `?` marks the gap, it never fills it.
    """
    if step <= 0 or stop <= start:
        return ()
    values = list(range(start, stop + 1, step))
    if not 2 <= len(values) <= 12:
        return ()
    cell = max(len(str(v)) for v in values) + 2
    if unknown_next:
        cell = max(cell, 3)
    labels = "  " + "".join(f"{v:<{cell}}" for v in values)
    segments = len(values) - 1
    if unknown_next:
        labels += "?"
        segments += 1
    out = [labels.rstrip(), "  " + ("+" + "-" * (cell - 1)) * segments + "+"]
    if mark is not None and mark in values:
        out.append(("  " + " " * (cell * values.index(mark)) + "^").rstrip())
    return tuple(out)


# ── data displays ────────────────────────────────────────────────────────────

def scatterplot(points: tuple[tuple[int, int], ...],
                width: int = 12, height: int = 6) -> tuple[str, ...]:
    """A scatter of plotted points with bare x/y axes.

    The senior topics that use this ("what correlation is this?") currently STATE
    the relationship in prose -- "as temperature rises, heater use falls" -- which
    is the whole skill. Plotting the points hands the child the same job a real
    scatterplot does.

    Points are (x, y) in 0..width-1 / 0..height-1. Max width: width + 5.
    Deliberately unlabelled beyond the axes: naming the trend is the question.
    """
    if not 4 <= width <= 20 or not 3 <= height <= 10 or not points:
        return ()
    if any(not (0 <= x < width and 0 <= y < height) for x, y in points):
        return ()
    out = []
    for row in range(height - 1, -1, -1):
        cells = "".join("*" if (c, row) in points else " " for c in range(width))
        axis = "  y|" if row == height - 1 else "   |"
        out.append((axis + cells).rstrip())
    out.append("   +" + "-" * width + " x")
    return tuple(out)


def two_way_table(row_labels: tuple[str, str], col_labels: tuple[str, str],
                  cells: tuple[tuple[object, object], ...],
                  row_totals: tuple[object, object] | None = None,
                  col_totals: tuple[object, object] | None = None,
                  grand_total: object | None = None) -> tuple[str, ...]:
    """A two-way table, drawn. Cell values may be numbers or "?" for the unknown.

    Reading a two-way table IS the skill, and describing one in a sentence
    ("plays sport AND music 8; sport only 9; ...") does the reading for the child.
    Max width: about 4 label widths + 8.
    """
    if len(row_labels) != 2 or len(col_labels) != 2 or len(cells) != 2:
        return ()
    # +1 padding, not +2, and a tight total column: measured in chromium, only
    # ~35 monospace characters fit a 360px screen, and the roomier version came
    # out at 40 and scrolled sideways.
    lw = max(len(r) for r in row_labels) + 1
    cw = max(max(len(c) for c in col_labels), 4) + 1
    head = "  " + " " * lw + "".join(f"{c:<{cw}}" for c in col_labels)
    if row_totals is not None:
        head += "|total"
    out = [head.rstrip()]
    for i, label in enumerate(row_labels):
        line = "  " + f"{label:<{lw}}" + "".join(f"{str(v):<{cw}}" for v in cells[i])
        if row_totals is not None:
            line += f"|{row_totals[i]}"
        out.append(line.rstrip())
    if col_totals is not None:
        out.append("  " + "-" * (lw + 2 * cw + 6))
        line = "  " + f"{'total':<{lw}}" + "".join(f"{str(v):<{cw}}" for v in col_totals)
        if grand_total is not None:
            line += f"|{grand_total}"
        out.append(line.rstrip())
    return tuple(out)


# ── networks ─────────────────────────────────────────────────────────────────

# Hand-laid layout with weights substituted -- deliberately NOT a graph-layout
# engine. Four vertices in a square is enough for shortest-path and for counting
# odd-degree vertices, and a fixed shape is legible where an auto-layout is not.
# Positions are COMPUTED rather than written as fixed-width strings, because a
# two-digit weight would otherwise slide B sideways and leave the uprights
# pointing at nothing (caught on the first render).


def network_square(weights: dict[str, object],
                   diagonal: object | None = None) -> tuple[str, ...]:
    """A 4-vertex network A-B-D-C with an optional A-D diagonal.

    `weights` supplies ab/ac/bd/cd (edge labels, usually distances). With a
    diagonal the vertex degrees change, which is what an Eulerian-trail question
    turns on -- and counting those degrees off the PICTURE is the skill the prose
    version ("a network's vertices have 4 of ODD degree") gives away.

    Max width: about 12 + the widest horizontal weight. Carries no route totals:
    finding the short way through IS the question.
    """
    need = {"ab", "ac", "bd", "cd"}
    if not need <= set(weights):
        return ()
    ab, ac, bd, cd = (str(weights[k]) for k in ("ab", "ac", "bd", "cd"))
    top = f"A --{ab}-- B"
    bottom = f"C --{cd}-- D"
    span = max(len(top), len(bottom))
    top = top.ljust(span)
    bottom = bottom.ljust(span)
    right = span - 1                       # column of B / D
    def upright(label: str = "") -> str:
        row = [" "] * span
        row[0] = label[:1] if label else "|"
        row[right] = label[1:2] if len(label) > 1 else ("|" if not label else " ")
        return "".join(row).rstrip()
    side = [" "] * span
    side[0], side[right] = "|", "|"
    bar = "".join(side)
    labels = [" "] * span
    labels[0], labels[right] = ac[0], bd[0]
    if len(ac) > 1 or len(bd) > 1:         # multi-digit weights sit beside the upright
        labels = [" "] * span
        for i, ch in enumerate(ac):
            if i < span:
                labels[i] = ch
        for i, ch in enumerate(bd):
            if right + i - len(bd) + 1 >= 0:
                labels[right + i - len(bd) + 1] = ch
    out = ["  " + top, "  " + bar, "  " + "".join(labels).rstrip(),
           "  " + bar, "  " + bottom]
    if diagonal is not None:
        out.append(f"  (A to D directly: {diagonal})")
    return tuple(out)


def length_bars(label_a: str, length_a: int, label_b: str, length_b: int,
                unit: str = "cm", total_max: int = 29) -> tuple[str, ...]:
    """Two objects drawn side by side so one visibly outreaches the other.

        Pencil: [─────────────] 15 cm
        Crayon: [────────] 9 cm

    PROPORTIONAL, not literal (maintainer, 2026-08-21: "No need to be exact.
    Scale it properly... Are you draw car or truck exactly?"). The longer object
    fills the bar and the shorter is drawn to the same scale, so the picture is
    the same width whether the pencil is 5 cm or 100 cm -- a literal one-cell-
    per-centimetre bar would have been honest right up until it scrolled off a
    phone.

    That choice also settles a pedagogical problem rather than dodging it. In
    countable centimetre cells a child can read the gap straight off the picture
    and never subtract, which would quietly turn a subtraction node into a
    counting node while BKT recorded subtraction. A scaled bar has no unit to
    count, so the numbers must come from the question text. 10-vs-6 and 15-vs-9
    draw IDENTICALLY here -- same ratio -- which is the proof that the picture
    cannot give the answer away.

    The bar length is DERIVED from `total_max` rather than fixed, so the row
    fits the 29-column phone budget whatever the labels and however many digits
    the lengths have. Fixing the bar at 13 happened to fit 2-digit centimetres
    and would have silently overflowed the first 3-digit one.

    The one thing rounding must never do is lie about the ORDER: if a is longer
    than b, its bar is strictly longer, even where the two round to one cell.

    Carries no difference and no answer -- working out how much longer IS the
    question.
    """
    if length_a <= 0 or length_b <= 0 or not label_a or not label_b:
        return ()
    pad = max(len(label_a), len(label_b))
    tail = f" {max(length_a, length_b)}" + (f" {unit}" if unit else "")
    bar_max = total_max - (pad + 3) - (1 + len(tail))
    if bar_max < 2:
        return ()
    scale = bar_max / max(length_a, length_b)
    drawn_a = max(1, round(length_a * scale))
    drawn_b = max(1, round(length_b * scale))
    if length_a > length_b and drawn_a <= drawn_b:
        drawn_b = drawn_a - 1
    elif length_b > length_a and drawn_b <= drawn_a:
        drawn_a = drawn_b - 1
    if drawn_a < 1 or drawn_b < 1:
        return ()
    suffix = f" {unit}" if unit else ""
    return (f"{label_a:<{pad}}: [{'─' * drawn_a}] {length_a}{suffix}",
            f"{label_b:<{pad}}: [{'─' * drawn_b}] {length_b}{suffix}")
