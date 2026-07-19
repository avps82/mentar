# Year 7-12 mathematics visual templates (2026-07-19)

Maintainer dump, LOGGED ONLY (same pattern as the other reference docs logged
the same session — no action requested). 15 ASCII templates across 5
sections, spanning Year 7 through senior secondary (Years 11-12), including
calculus, trigonometry, matrices, and financial mathematics — well beyond
anything currently scoped for this project (Phase 0 pilot is fractions;
shipped curriculum breadth tops out around Year 7-8, see
[[project_r15_partial_au_y78]]). Companion to
`docs/design/year1_6_math_templates_reference.md` and
`docs/design/comprehensive_math_templates_reference.md` — read those files'
scope notes too, they apply identically here: none of this is a small
extension of `engine/arithmetic_steps.py`, each topic needs its own design
pass, and several of these (calculus, matrices, financial math) are content
areas that don't exist ANYWHERE in the shipped curriculum yet, not just
missing a visual template.

## Section 1: Lower secondary (Years 7-8) — foundations of algebra & ratios

### Template 1 — two-sided equation balance beam

For introducing solving linear equations by visualizing "doing the same
operation to both sides."

```text
                 [  Left Side Expression  ] = [ Right Side Expression ]
                                    \     |     /
                                     \____|____/
                                         / \
                                        /   \
                                       /_____\
```

### Template 2 — integers multiplication & division sign pyramid

Cover the two signs being multiplied/divided to reveal the result's sign.

```text
           / \
          / + \
         /-----\
        / - | - \
       /____|____\
```

### Template 3 — ratio unit box method

For split-share and inverse proportion problems.

```text
  Ratio A : B  ==>  [ Box 1 ] : [ Box 2 ]

  [ Unit Value ] | [  Value  ] | [  Value  ] | [  Value  ] | (Part A)
  [ Unit Value ] | [  Value  ] | [  Value  ] |               (Part B)
```

## Section 2: Middle secondary (Years 9-10) — advanced algebra & functions

### Template 4 — two-variable linear graph grid (y = mx + c)

For plotting linear equations, identifying intercepts, estimating gradient.

```text
                 +Y
                  |
             4    |         / (Line of equation)
             3    |       /
             2    |     /    <-- y-intercept (0, c)
             1    |   /
  -X ---------+---+---+---+--------- +X
    -4  -3  -2|-1 | 0 | 1   2   3   4
            -1|   /
            -2| /            <-- x-intercept
            -3|
            -4|
                  |
                 -Y
```

### Template 5 — quadratic parabola function template (y = ax² + bx + c)

Visualizes roots, line of symmetry, vertex.

```text

                  |          | Axis of Symmetry (x = -b/2a)
              \   |   /      v
               \  |  /
    ------------\-+-/------------
     Roots -->   \ /  <-- Vertex (h, k)
                  |
```

### Template 6 — algebraic grid array (FOIL expansion / box method)

Visual tool for binomial expansions like (ax + b)(cx + d).

```text

           |    cx     |    +d     |
    -------|-----------|-----------|
      ax   |   acx²    |   adx     |
    -------|-----------|-----------|
      +b   |   bcx     |    bd     |
    -------|-----------|-----------|
```

## Section 3: Geometry & trigonometry (Years 9-11)

### Template 7 — right-angled triangle (SOH-CAH-TOA)

For trig ratios, Pythagoras, angles of elevation/depression.

```text
                   |\
                   | \
                   |  \  [Hypotenuse]
     [Opposite]    |   \
   (to Theta θ)    |    \
                   |_____\  <-- Theta (θ)
                   +-----+
                 [Adjacent]
```

### Template 8 — non-right-angled triangle reference (sine & cosine rules)

```text
                     Angle A
                       / \
                      /   \
           Side c    /     \   Side b
                    /       \
                   /_________\
               Angle B         Angle C
                       Side a
```

### Template 9 — the unit circle (four quadrants)

Trig sign behaviour (+/-) for Sine, Cosine, Tangent across 360°.

```text
                     90° (0, 1)
                  Quadrant II | Quadrant I
                     Sine (+) | All (+)
                              |
       180° (-1, 0) ----------+---------- 0° / 360° (1, 0)
                              |
                 Quadrant III | Quadrant IV
                     Tan (+)  | Cos (+)
                    270° (0, -1)
```

## Section 4: Senior applied & math methods (Years 11-12) — calculus & vectors

### Template 10 — calculus derivative rate curve

Secant line turning into a tangent line, instantaneous rate of change f'(x).

```text
  Y |            / [Tangent Line: Gradient = f'(x)]
    |          /
    |      * /   <-- Point of Tangency (x, f(x))
    |    / . \
    |  /   .   \______ Curve f(x)
    +----------------------- X
```

### Template 11 — Riemann sum integral area (calculus integration)

Splitting the area under a curve into rectangles to approximate a definite
integral.

```text
  Y |        ____

    |       |    |___
    |    ___|    |   |___      Area ≈ ∫ f(x) dx
    |   |   |    |   |   |
    +---+---+----+---+---+--- X
        a                 b
```

### Template 12 — 2D & 3D component vector grid

```text
           +Y
            |        / ^ Resultant Vector [u]

            |      /   |
            |    /     | [y-component]
            |  / θ     |
            +----------+---- +X
             \_________/
            [x-component]
```

## Section 5: Senior probability, financial math & matrices (Years 11-12)

### Template 13 — normal distribution bell curve (standard deviation Z-score)

68-95-99.7% empirical probability splits.

```text
                    /\
                   /  \
                  /    \
                _/      \_
      _________/| |  |  | \_________
               -3 -2 -1 μ +1 +2 +3

                |<- 68% ->|
              |◄---- 95% ----►|
            |◄------ 99.7% ------►|
```

### Template 14 — matrix system grid (M × N)

```text

         |  a11  a12  a13  |
     M = |  a21  a22  a23  |

         |  a31  a32  a33  |
```

### Template 15 — financial math cash flow / time value timeline

For annuities, compound interest periods, reducing-balance loans.

```text
  [ PV ]                                                    [ FV ]
  Present                                                   Future
   Value                                                    Value

     |--------|--------|--------|--------|--------|--------|
     t0       t1       t2       t3       t4       t5       tn
           [ PMT ]  [ PMT ]  [ PMT ]  [ PMT ]  [ PMT ]  <-- Recurring Payment
```

## Related files

- `docs/design/year1_6_math_templates_reference.md` — the Year 1-6 companion.
- `docs/design/comprehensive_math_templates_reference.md` — the earlier,
  less grade-banded dump from the same session.
- Memory: [[project_comprehensive_math_templates_idea]].
