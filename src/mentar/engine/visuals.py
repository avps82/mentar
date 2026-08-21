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
