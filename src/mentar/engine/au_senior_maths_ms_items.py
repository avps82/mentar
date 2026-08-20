"""AU senior mathematics — Methods and Specialist courses (W2 of the depth
program, docs/design/curriculum_depth_program.md).

Same contract as au_senior_maths_items.py (W1): every generator returns
(answer_type, checker, problem, answer[, choices][, method_steps][, format_hint]),
cards are formula-first and end with an Answer line, and every number is exact
BY CONSTRUCTION — no searching for valid values (a W1 while-loop hunt for
"nice" numbers was unsatisfiable and hung the sweep; build, never search).

The Methods dicts also absorb the pre-split merged year11/12_maths quadratic
nodes (au11_*/au12_* ids, generators still in au_items.py) so learner mastery
keyed on those node ids survives the course split.

curriculum_standard: null in the templates — senior certificates are owned by
state authorities (VCE/HSC/QCE/SACE), same posture as senior science.
"""

from __future__ import annotations

from .au_items import (
    gen_binomial_product_area,
    gen_combine_quadratic_linear,
    gen_combine_two_quadratics,
    gen_compound_shape_area,
    gen_difference_of_expressions,
    gen_revenue_expression,
    gen_word_to_quadratic_expression,
)
from .au_senior_maths_items import _card

__all__ = [
    "AU_METHODS_Y11_GENERATORS",
    "AU_METHODS_Y12_GENERATORS",
    "AU_SPECIALIST_Y11_GENERATORS",
    "AU_SPECIALIST_Y12_GENERATORS",
]


# ── Methods Year 11 ──────────────────────────────────────────────────────────

def gen_function_value(rng):
    b = rng.choice([2, 3, 4, 5, 6])
    c = rng.choice([1, 2, 3, 5, 7])
    k = rng.choice([2, 3, 4, 5])
    ans = k * k + b * k + c
    p = f"For the function f(x) = x² + {b}x + {c}, find f({k})."
    card = _card("EVALUATING A FUNCTION", p, ans,
                 "  Replace every x with the given number, then work it out",
                 f"  1. f({k}) = {k}² + {b}×{k} + {c}.",
                 f"  2. {k * k} + {b * k} + {c} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Replace every x with the given number)")


def gen_line_gradient(rng):
    m = rng.choice([2, 3, 4, 5])
    x1 = rng.choice([1, 2, 3])
    dx = rng.choice([1, 2, 3])
    y1 = rng.choice([1, 2, 4])
    x2, y2 = x1 + dx, y1 + m * dx
    p = (f"A straight line passes through ({x1}, {y1}) and ({x2}, {y2}). "
         "What is its gradient?")
    card = _card("GRADIENT BETWEEN TWO POINTS", p, m,
                 "  Gradient = rise ÷ run = (y₂ − y₁) ÷ (x₂ − x₁)",
                 f"  1. Rise: {y2} − {y1} = {m * dx}.",
                 f"  2. Run: {x2} − {x1} = {dx}.",
                 f"  3. {m * dx} ÷ {dx} = {m}.")
    return ("int", "int_exact", p, str(m), None, card,
            "(Gradient = rise ÷ run)")


def gen_quadratic_vertex(rng):
    a = rng.choice([1, 2, 3, 4, 5])
    c = rng.choice([1, 2, 3, 7])
    p = (f"The parabola y = x² − {2 * a}x + {c} has its vertex at x = ?")
    card = _card("VERTEX OF A PARABOLA", p, a,
                 "  For y = x² + bx + c, the vertex is at x = −b ÷ 2",
                 f"  1. Here b = −{2 * a}.",
                 f"  2. x = {2 * a} ÷ 2 = {a}.")
    return ("int", "int_exact", p, str(a), None, card,
            "(Vertex of y = x² + bx + c is at x = −b ÷ 2)")


def gen_exact_trig(rng):
    facts = [("sin 30°", "1/2"), ("cos 60°", "1/2"), ("sin 90°", "1"),
             ("cos 0°", "1"), ("sin 0°", "0"), ("cos 90°", "0"), ("tan 45°", "1")]
    expr, val = rng.choice(facts)
    choices = ("0", "1/2", "1", "√3/2")
    letter = "ABCD"[choices.index(val)]
    stem = f"What is the exact value of {expr}?"
    card = _card("EXACT TRIG VALUES", stem, val,
                 "  Exact-value table (learn these):",
                 "  sin 0° = 0    sin 30° = 1/2    sin 90° = 1",
                 "  cos 0° = 1    cos 60° = 1/2    cos 90° = 0    tan 45° = 1",
                 f"  1. Read {expr} straight from the table: {val}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


def gen_trig_period(rng):
    k = rng.choice([2, 3, 4, 6, 9, 10, 12])
    ans = 360 // k
    p = f"What is the period, in degrees, of y = sin({k}x°)?"
    card = _card("PERIOD OF A SINE GRAPH", p, ans,
                 "  Period of sin(kx°) = 360 ÷ k",
                 f"  1. 360 ÷ {k} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Period of sin(kx°) = 360 ÷ k)")


def gen_derivative_power(rng):
    a = rng.choice([1, 2, 3, 4, 5])
    n = rng.choice([2, 3])
    k = rng.choice([1, 2, 3, 4])
    ans = a * n * k ** (n - 1)
    p = f"If f(x) = {a}x{'²' if n == 2 else '³'}, find f′({k})."
    card = _card("DERIVATIVE OF A POWER", p, ans,
                 "  Power rule: the derivative of axⁿ is n × a × xⁿ⁻¹",
                 f"  1. f′(x) = {n} × {a} × x{'²' if n == 3 else ''} = {a * n}x{'²' if n == 3 else ''}.",
                 f"  2. f′({k}) = {a * n} × {k ** (n - 1)} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Derivative of axⁿ = n × a × xⁿ⁻¹)")


def gen_curve_gradient(rng):
    b = rng.choice([1, 2, 3, 4, 6])
    k = rng.choice([1, 2, 3, 4])
    ans = 2 * k + b
    p = f"Find the gradient of the curve y = x² + {b}x at the point where x = {k}."
    card = _card("GRADIENT OF A CURVE", p, ans,
                 "  Differentiate first, then substitute the x-value",
                 f"  1. dy/dx = 2x + {b}.",
                 f"  2. At x = {k}: 2×{k} + {b} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Differentiate, then substitute the x-value)")


def gen_increasing_decreasing(rng):
    a = rng.choice([2, 3, 4, 5])
    k = rng.choice([x for x in (1, 2, 3, 6, 7, 8) ])
    slope = 2 * k - 2 * a
    correct = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stationary"
    if slope == 0:  # k == a cannot happen with these sets, but keep it exact
        k += 1
        slope = 2 * k - 2 * a
        correct = "increasing" if slope > 0 else "decreasing"
    choices = ("increasing", "decreasing", "stationary", "it cannot be told")
    letter = "ABCD"[choices.index(correct)]
    stem = (f"The curve y = x² − {2 * a}x has derivative dy/dx = 2x − {2 * a}. "
            f"At x = {k}, is the curve increasing or decreasing?")
    card = _card("INCREASING OR DECREASING", stem, correct,
                 "  Positive derivative → increasing; negative → decreasing",
                 f"  1. dy/dx at x = {k}: 2×{k} − {2 * a} = {slope}.",
                 f"  2. {slope} is {'positive' if slope > 0 else 'negative'}, so the curve is {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


def gen_two_coin_prob(rng):
    event, ans = rng.choice([("two heads", "0.25"), ("two tails", "0.25"),
                             ("at least one head", "0.75"), ("exactly one head", "0.5")])
    p = (f"Two fair coins are tossed. What is the probability of getting {event}? "
         "Give your answer as a decimal.")
    counts = {"two heads": 1, "two tails": 1, "at least one head": 3, "exactly one head": 2}
    n = counts[event]
    card = _card("PROBABILITY WITH TWO COINS", p, ans,
                 "  Probability = favourable outcomes ÷ total outcomes",
                 "  1. The four equally likely outcomes: HH, HT, TH, TT.",
                 f"  2. Outcomes giving {event}: {n} of the 4.",
                 f"  3. {n} ÷ 4 = {ans}.")
    return ("decimal", "decimal_exact", p, ans, None, card,
            "(Probability = favourable ÷ total; list HH, HT, TH, TT)")


def gen_expected_value(rng):
    m = rng.choice([1, 2, 3, 4, 5])
    vals = (m, m + 1, m + 2, m + 5)
    ev = m + 2                     # sum = 4m + 8, each value has probability 1/4
    p = (f"A fair spinner shows {vals[0]}, {vals[1]}, {vals[2]} or {vals[3]}, "
         "each with probability 1/4. What is the expected value?")
    card = _card("EXPECTED VALUE", p, ev,
                 "  Expected value = sum of (value × its probability)",
                 f"  1. Total of the values: {vals[0]} + {vals[1]} + {vals[2]} + {vals[3]} = {sum(vals)}.",
                 f"  2. Each has probability 1/4, so E = {sum(vals)} ÷ 4 = {ev}.")
    return ("int", "int_exact", p, str(ev), None, card,
            "(Expected value = sum of value × probability)")


# ── Methods Year 12 ──────────────────────────────────────────────────────────

def gen_chain_rule(rng):
    b = rng.choice([1, 2, 3, 5])
    k = rng.choice([1, 2, 3])
    inner = 2 * k + b
    ans = 4 * inner
    p = f"If f(x) = (2x + {b})², find f′({k})."
    card = _card("CHAIN RULE", p, ans,
                 "  Chain rule: derivative of (inner)² = 2 × (inner) × (derivative of inner)",
                 f"  1. f′(x) = 2 × (2x + {b}) × 2 = 4(2x + {b}).",
                 f"  2. f′({k}) = 4 × (2×{k} + {b}) = 4 × {inner} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Derivative of (inner)² = 2 × inner × inner′)")


def gen_product_rule(rng):
    a = rng.choice([2, 3, 4, 5, 6])
    k = rng.choice([1, 2, 3, 4])
    ans = 2 * k + a
    p = f"Using the product rule, find f′({k}) for f(x) = x(x + {a})."
    card = _card("PRODUCT RULE FOR DERIVATIVES", p, ans,
                 "  Product rule: (uv)′ = u′v + uv′",
                 f"  1. u = x, v = x + {a}, so u′ = 1 and v′ = 1.",
                 f"  2. f′(x) = 1×(x + {a}) + x×1 = 2x + {a}.",
                 f"  3. f′({k}) = 2×{k} + {a} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "((uv)′ = u′v + uv′)")


def gen_stationary_point(rng):
    a = rng.choice([1, 2, 3, 4, 5, 6])
    c = rng.choice([1, 3, 5])
    p = f"Find the x-value of the stationary point of y = x² − {2 * a}x + {c}."
    card = _card("STATIONARY POINT", p, a,
                 "  A stationary point has derivative 0: solve dy/dx = 0",
                 f"  1. dy/dx = 2x − {2 * a}.",
                 f"  2. 2x − {2 * a} = 0 → 2x = {2 * a} → x = {a}.")
    return ("int", "int_exact", p, str(a), None, card,
            "(Set dy/dx = 0 and solve)")


def gen_integral_2x(rng):
    k = rng.choice([2, 3, 4, 5, 6])
    ans = k * k
    p = f"Evaluate the definite integral of 2x from x = 0 to x = {k}."
    card = _card("INTEGRAL OF 2x", p, ans,
                 "  An antiderivative of 2x is x²; evaluate at the ends and subtract",
                 "  1. Antiderivative: x².",
                 f"  2. {k}² − 0² = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Antiderivative of 2x is x²; top end minus bottom end)")


def gen_integral_x_squared(rng):
    k = rng.choice([3, 6])
    ans = k ** 3 // 3
    p = f"Evaluate the definite integral of x² from x = 0 to x = {k}."
    card = _card("INTEGRAL OF x²", p, ans,
                 "  An antiderivative of x² is x³ ÷ 3",
                 "  1. Antiderivative: x³ ÷ 3.",
                 f"  2. {k}³ ÷ 3 = {k ** 3} ÷ 3 = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Antiderivative of x² is x³ ÷ 3)")


def gen_area_under_line(rng):
    m = rng.choice([1, 2, 3, 4])
    k = rng.choice([2, 4, 6])
    ans = m * k * k // 2
    p = f"Find the area between the line y = {m}x and the x-axis, from x = 0 to x = {k}."
    card = _card("AREA UNDER A LINE", p, ans,
                 "  The region is a triangle: area = ½ × base × height",
                 f"  1. Base: {k}. Height at x = {k}: {m}×{k} = {m * k}.",
                 f"  2. ½ × {k} × {m * k} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Area of a triangle = ½ × base × height)")


def gen_binomial_mean(rng):
    n, p_str, mean = rng.choice([
        (10, "0.2", 2), (20, "0.25", 5), (40, "0.1", 4),
        (50, "0.2", 10), (20, "0.5", 10), (30, "0.1", 3)])
    p = (f"A binomial random variable has n = {n} trials, each with success "
         f"probability p = {p_str}. What is its mean?")
    card = _card("MEAN OF A BINOMIAL", p, mean,
                 "  Mean of a binomial = n × p",
                 f"  1. {n} × {p_str} = {mean}.")
    return ("int", "int_exact", p, str(mean), None, card,
            "(Mean of a binomial = n × p)")


def gen_die_expected(rng):
    n = rng.choice([5, 7, 9, 11])
    ans = (n + 1) // 2
    p = (f"A fair {n}-sided die shows the numbers 1 to {n}. "
         "What is the expected value of one roll?")
    card = _card("EXPECTED VALUE OF A DIE", p, ans,
                 "  For a fair die numbered 1 to n, the expected value = (n + 1) ÷ 2",
                 f"  1. ({n} + 1) ÷ 2 = {n + 1} ÷ 2 = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Expected value of a fair 1-to-n die = (n + 1) ÷ 2)")


def gen_standard_error(rng):
    sigma, n, ans = rng.choice([(6, 4, 3), (6, 9, 2), (8, 16, 2), (10, 25, 2),
                                (12, 4, 6), (12, 9, 4), (12, 36, 2), (10, 4, 5)])
    root = {4: 2, 9: 3, 16: 4, 25: 5, 36: 6}[n]
    p = (f"A population has standard deviation {sigma}. A sample of {n} values "
         "is taken. What is the standard error of the sample mean?")
    card = _card("STANDARD ERROR", p, ans,
                 "  Standard error = population standard deviation ÷ √n",
                 f"  1. √{n} = {root}.",
                 f"  2. {sigma} ÷ {root} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Standard error = σ ÷ √n)")


def gen_ci_concept(rng):
    stem_v, correct = rng.choice([
        ("the sample size n is increased", "narrower"),
        ("the sample size n is decreased", "wider"),
        ("the confidence level is raised from 90% to 99%", "wider"),
        ("the confidence level is lowered from 99% to 90%", "narrower")])
    choices = ("narrower", "wider", "unchanged", "it cannot be told")
    letter = "ABCD"[choices.index(correct)]
    stem = (f"A confidence interval for a population mean is recalculated after "
            f"{stem_v}, with everything else unchanged. The new interval is…")
    card = _card("CONFIDENCE INTERVALS", stem, correct,
                 "  Width grows with the confidence level, shrinks as n grows",
                 "  1. More data (larger n) → less uncertainty → narrower.",
                 "  2. More confidence demanded → a wider net must be cast.",
                 f"  3. Here: {stem_v} → {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


# ── Specialist Year 11 ───────────────────────────────────────────────────────

def gen_permutations(rng):
    n = rng.choice([4, 5, 6])
    r = rng.choice([2, 3])
    ans, terms = 1, []
    for i in range(r):
        ans *= (n - i)
        terms.append(str(n - i))
    p = (f"How many ways can {r} different prizes be given to {r} of "
         f"{n} people (one prize each, order matters)?")
    card = _card("PERMUTATIONS", p, ans,
                 "  Ordered choices multiply: n × (n−1) × … for r factors",
                 f"  1. {r} choices in order from {n} people: {' × '.join(terms)}.",
                 f"  2. {' × '.join(terms)} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Multiply n × (n−1) × … for r factors)")


def gen_combinations(rng):
    n, r, ans = rng.choice([(5, 2, 10), (6, 2, 15), (6, 3, 20),
                            (7, 2, 21), (8, 2, 28), (4, 2, 6)])
    perm = 1
    for i in range(r):
        perm *= (n - i)
    fact_r = 1
    for i in range(1, r + 1):
        fact_r *= i
    p = (f"How many different teams of {r} can be chosen from {n} people "
         "(order does not matter)?")
    card = _card("COMBINATIONS", p, ans,
                 "  Unordered choices: divide the ordered count by r!",
                 f"  1. Ordered ways: {perm}.  r! = {fact_r}.",
                 f"  2. {perm} ÷ {fact_r} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Combinations = ordered count ÷ r!)")


def gen_vector_add(rng):
    a1, a2 = rng.choice([2, 3, 4]), rng.choice([1, 2, 5])
    b1, b2 = rng.choice([1, 3, 5]), rng.choice([2, 4, 6])
    ans = a1 + b1
    p = (f"For the vectors a = ({a1}, {a2}) and b = ({b1}, {b2}), "
         "what is the x-component of a + b?")
    card = _card("ADDING VECTORS", p, ans,
                 "  Add vectors component by component",
                 f"  1. x-components: {a1} + {b1} = {ans}.",
                 f"  2. (The y-component would be {a2} + {b2} = {a2 + b2}.)")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Add vectors component by component)")


def gen_vector_magnitude(rng):
    x, y, ans = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15)])
    p = f"Find the magnitude of the vector ({x}, {y})."
    card = _card("MAGNITUDE OF A VECTOR", p, ans,
                 "  Magnitude = √(x² + y²)",
                 f"  1. {x}² + {y}² = {x * x} + {y * y} = {x * x + y * y}.",
                 f"  2. √{x * x + y * y} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Magnitude = √(x² + y²))")


def gen_complex_add(rng):
    a, b = rng.choice([2, 3, 5]), rng.choice([1, 2, 4])
    c, d = rng.choice([1, 4, 6]), rng.choice([3, 5, 7])
    ans = b + d
    p = (f"For the complex numbers ({a} + {b}i) and ({c} + {d}i), "
         "what is the imaginary part of their sum?")
    card = _card("ADDING COMPLEX NUMBERS", p, ans,
                 "  Add real parts together, and imaginary parts together",
                 f"  1. Imaginary parts: {b} + {d} = {ans}.",
                 f"  2. (The real part would be {a} + {c} = {a + c}.)")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Add real parts together, imaginary parts together)")


def gen_complex_multiply(rng):
    a, b = rng.choice([3, 4, 5]), rng.choice([1, 2])
    c, d = rng.choice([2, 3]), rng.choice([1, 2])
    ans = a * c - b * d            # positive: a×c ≥ 6, b×d ≤ 4
    p = (f"What is the real part of ({a} + {b}i)({c} + {d}i)?")
    card = _card("MULTIPLYING COMPLEX NUMBERS", p, ans,
                 "  Expand with i² = −1: real part = ac − bd",
                 f"  1. ac = {a}×{c} = {a * c};  bd = {b}×{d} = {b * d}.",
                 f"  2. Real part = {a * c} − {b * d} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Real part of (a+bi)(c+di) = ac − bd, because i² = −1)")


def gen_circle_angle(rng):
    theta = rng.choice([20, 25, 30, 35, 40, 45, 50])
    ans = 2 * theta
    p = (f"An arc of a circle subtends an angle of {theta}° at the circumference. "
         "What angle, in degrees, does the same arc subtend at the centre?")
    card = _card("ANGLE AT THE CENTRE", p, ans,
                 "  Circle theorem: angle at the centre = 2 × angle at the circumference",
                 f"  1. 2 × {theta} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Angle at the centre = 2 × angle at the circumference)")


def gen_circle_radius(rng):
    r = rng.choice([3, 4, 5, 6, 7, 8, 9])
    p = f"The circle x² + y² = {r * r} has what radius?"
    card = _card("RADIUS FROM A CIRCLE EQUATION", p, r,
                 "  x² + y² = r² describes a circle of radius r centred at the origin",
                 f"  1. r² = {r * r}.",
                 f"  2. r = √{r * r} = {r}.")
    return ("int", "int_exact", p, str(r), None, card,
            "(x² + y² = r² has radius r)")


def gen_parity_proof(rng):
    claim, correct = rng.choice([
        ("the sum of two odd numbers", "always even"),
        ("the product of two odd numbers", "always odd"),
        ("the sum of an odd number and an even number", "always odd"),
        ("the sum of two even numbers", "always even")])
    choices = ("always even", "always odd", "sometimes even, sometimes odd",
               "never a whole number")
    letter = "ABCD"[choices.index(correct)]
    stem = f"In a proof about parity, {claim} is…"
    card = _card("PARITY PROOF", stem, correct,
                 "  Write odd numbers as 2k + 1 and even numbers as 2k, then add or multiply",
                 "  1. odd + odd = (2a+1) + (2b+1) = 2(a+b+1) → even.",
                 "  2. odd × odd = (2a+1)(2b+1) = 2(2ab+a+b) + 1 → odd.",
                 "  3. odd + even = (2a+1) + 2b = 2(a+b) + 1 → odd; even + even → even.",
                 f"  4. Here: {claim} → {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


def gen_counterexample(rng):
    claim, correct, others = rng.choice([
        ("every prime number is odd", "2", ("9", "15", "21")),
        ("n² is greater than n for every whole number n", "1", ("3", "5", "10")),
        ("every multiple of 5 ends in the digit 5", "10", ("15", "25", "35"))])
    order = [correct, *others]
    rng.shuffle(order)
    choices = tuple(order)
    letter = "ABCD"[choices.index(correct)]
    stem = (f"To DISPROVE the claim “{claim}”, which number is a counterexample?")
    card = _card("FINDING A COUNTEREXAMPLE", stem, correct,
                 "  A counterexample fits the claim's conditions but breaks its conclusion",
                 f"  1. The claim: {claim}.",
                 f"  2. Test {correct}: it meets the conditions but not the conclusion.",
                 "  3. One counterexample is enough to disprove a universal claim.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


# ── Specialist Year 12 ───────────────────────────────────────────────────────

def gen_vector3_magnitude(rng):
    x, y, z, ans = rng.choice([(1, 2, 2, 3), (2, 3, 6, 7), (4, 4, 7, 9),
                               (2, 6, 9, 11), (6, 6, 7, 11), (1, 4, 8, 9)])
    p = f"Find the magnitude of the 3D vector ({x}, {y}, {z})."
    s = x * x + y * y + z * z
    card = _card("MAGNITUDE OF A 3D VECTOR", p, ans,
                 "  Magnitude = √(x² + y² + z²)",
                 f"  1. {x}² + {y}² + {z}² = {x * x} + {y * y} + {z * z} = {s}.",
                 f"  2. √{s} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Magnitude = √(x² + y² + z²))")


def gen_dot_product(rng):
    a = (rng.choice([1, 2, 3]), rng.choice([2, 4]), rng.choice([1, 3]))
    b = (rng.choice([2, 3]), rng.choice([1, 3]), rng.choice([2, 5]))
    ans = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    p = f"Find the dot product of a = ({a[0]}, {a[1]}, {a[2]}) and b = ({b[0]}, {b[1]}, {b[2]})."
    card = _card("DOT PRODUCT", p, ans,
                 "  Dot product = multiply matching components, then add",
                 f"  1. {a[0]}×{b[0]} + {a[1]}×{b[1]} + {a[2]}×{b[2]} "
                 f"= {a[0] * b[0]} + {a[1] * b[1]} + {a[2] * b[2]}.",
                 f"  2. {a[0] * b[0]} + {a[1] * b[1]} + {a[2] * b[2]} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Dot product = sum of matching components multiplied)")


def gen_complex_modulus(rng):
    a, b, ans = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15)])
    p = f"Find the modulus of the complex number {a} + {b}i."
    card = _card("MODULUS OF A COMPLEX NUMBER", p, ans,
                 "  Modulus |a + bi| = √(a² + b²) — its distance from the origin",
                 f"  1. {a}² + {b}² = {a * a} + {b * b} = {a * a + b * b}.",
                 f"  2. √{a * a + b * b} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(|a + bi| = √(a² + b²))")


def gen_polar_argument(rng):
    z, correct = rng.choice([("i", "90°"), ("−1", "180°"), ("1 + i", "45°"), ("1", "0°")])
    choices = ("0°", "45°", "90°", "180°")
    letter = "ABCD"[choices.index(correct)]
    stem = f"On an Argand diagram, what is the argument of the complex number {z}?"
    card = _card("ARGUMENT OF A COMPLEX NUMBER", stem, correct,
                 "  The argument is the anticlockwise angle from the positive real axis",
                 "  1. 1 lies ON the positive real axis → 0°;  i is straight up → 90°.",
                 "  2. −1 points along the negative real axis → 180°.",
                 "  3. 1 + i is the diagonal between them → 45°.",
                 f"  4. Here: arg({z}) = {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


def gen_second_derivative(rng):
    a = rng.choice([1, 2, 3, 4])
    k = rng.choice([1, 2, 3, 5])
    ans = 6 * a * k
    p = f"If f(x) = {a}x³, find the second derivative f″({k})."
    card = _card("SECOND DERIVATIVE", p, ans,
                 "  Differentiate twice, one power at a time",
                 f"  1. f′(x) = 3 × {a}x² = {3 * a}x².",
                 f"  2. f″(x) = 2 × {3 * a}x = {6 * a}x.",
                 f"  3. f″({k}) = {6 * a} × {k} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Differentiate twice, one power at a time)")


def gen_integral_3x_squared(rng):
    k = rng.choice([2, 3, 4, 5])
    ans = k ** 3
    p = f"Evaluate the definite integral of 3x² from x = 0 to x = {k}."
    card = _card("INTEGRAL OF 3x²", p, ans,
                 "  An antiderivative of 3x² is x³",
                 "  1. Antiderivative: x³.",
                 f"  2. {k}³ − 0³ = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Antiderivative of 3x² is x³)")


def gen_force_ma(rng):
    m = rng.choice([2, 3, 4, 5, 8, 10])
    a = rng.choice([2, 3, 4, 5])
    ans = m * a
    p = (f"A {m} kg mass accelerates at {a} m/s². "
         "What net force, in newtons (N), acts on it?")
    card = _card("FORCE FROM MASS AND ACCELERATION", p, f"{ans} N",
                 "  Newton's second law: F = m × a",
                 f"  1. {m} × {a} = {ans}.",
                 f"  2. Units: kg × m/s² = N, so the force is {ans} N.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(F = m × a, in newtons)")


def gen_momentum(rng):
    m = rng.choice([2, 3, 4, 6, 10])
    v = rng.choice([3, 4, 5, 8])
    ans = m * v
    p = (f"A {m} kg object moves at {v} m/s. "
         "What is its momentum, in kg·m/s?")
    card = _card("MOMENTUM", p, f"{ans} kg·m/s",
                 "  Momentum p = m × v",
                 f"  1. {m} × {v} = {ans}.",
                 f"  2. Units: kg × m/s = kg·m/s, so p = {ans} kg·m/s.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Momentum = mass × velocity)")


def gen_sampling_mean(rng):
    mu = rng.choice([20, 30, 40, 50, 60, 75])
    n = rng.choice([16, 25, 36])
    p = (f"A population has mean {mu}. Samples of size {n} are repeatedly drawn. "
         "What is the mean of the sampling distribution of the sample mean?")
    card = _card("MEAN OF THE SAMPLING DISTRIBUTION", p, mu,
                 "  The sampling distribution of the mean is centred on the population mean",
                 f"  1. Its mean equals the population mean: {mu}.",
                 "  2. Sample size changes the SPREAD (standard error), never the centre.")
    return ("int", "int_exact", p, str(mu), None, card,
            "(The sampling distribution's mean = the population mean)")


def gen_se_sampling(rng):
    sigma, n, ans = rng.choice([(20, 16, 5), (30, 25, 6), (18, 36, 3),
                                (24, 16, 6), (40, 25, 8), (12, 16, 3)])
    root = {16: 4, 25: 5, 36: 6}[n]
    p = (f"A population has standard deviation {sigma}. For samples of size {n}, "
         "what is the standard deviation of the sampling distribution "
         "(the standard error)?")
    card = _card("SPREAD OF THE SAMPLING DISTRIBUTION", p, ans,
                 "  Standard error = population standard deviation ÷ √n",
                 f"  1. √{n} = {root}.",
                 f"  2. {sigma} ÷ {root} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Standard error = σ ÷ √n)")


# ── registries ───────────────────────────────────────────────────────────────

AU_METHODS_Y11_GENERATORS = {
    "au11m_function_value": gen_function_value,
    "au11m_line_gradient": gen_line_gradient,
    "au11m_quadratic_vertex": gen_quadratic_vertex,
    "au11m_exact_trig": gen_exact_trig,
    "au11m_trig_period": gen_trig_period,
    "au11m_derivative_power": gen_derivative_power,
    "au11m_curve_gradient": gen_curve_gradient,
    "au11m_increasing_decreasing": gen_increasing_decreasing,
    "au11m_two_coin_prob": gen_two_coin_prob,
    "au11m_expected_value": gen_expected_value,
    # absorbed from the retired merged year11_maths (ids kept: mastery survives)
    "au11_binomial_product_area": gen_binomial_product_area,
    "au11_word_to_quadratic_expression": gen_word_to_quadratic_expression,
    "au11_combine_quadratic_linear": gen_combine_quadratic_linear,
    "au11_difference_of_expressions": gen_difference_of_expressions,
}

AU_METHODS_Y12_GENERATORS = {
    "au12m_chain_rule": gen_chain_rule,
    "au12m_product_rule": gen_product_rule,
    "au12m_stationary_point": gen_stationary_point,
    "au12m_integral_2x": gen_integral_2x,
    "au12m_integral_x_squared": gen_integral_x_squared,
    "au12m_area_under_line": gen_area_under_line,
    "au12m_binomial_mean": gen_binomial_mean,
    "au12m_die_expected": gen_die_expected,
    "au12m_standard_error": gen_standard_error,
    "au12m_ci_concept": gen_ci_concept,
    # absorbed from the retired merged year12_maths (ids kept: mastery survives)
    "au12_revenue_expression": gen_revenue_expression,
    "au12_combine_two_quadratics": gen_combine_two_quadratics,
    "au12_compound_shape_area": gen_compound_shape_area,
}

AU_SPECIALIST_Y11_GENERATORS = {
    "au11s_permutations": gen_permutations,
    "au11s_combinations": gen_combinations,
    "au11s_vector_add": gen_vector_add,
    "au11s_vector_magnitude": gen_vector_magnitude,
    "au11s_complex_add": gen_complex_add,
    "au11s_complex_multiply": gen_complex_multiply,
    "au11s_circle_angle": gen_circle_angle,
    "au11s_circle_radius": gen_circle_radius,
    "au11s_parity_proof": gen_parity_proof,
    "au11s_counterexample": gen_counterexample,
}

AU_SPECIALIST_Y12_GENERATORS = {
    "au12s_vector3_magnitude": gen_vector3_magnitude,
    "au12s_dot_product": gen_dot_product,
    "au12s_complex_modulus": gen_complex_modulus,
    "au12s_polar_argument": gen_polar_argument,
    "au12s_second_derivative": gen_second_derivative,
    "au12s_integral_3x_squared": gen_integral_3x_squared,
    "au12s_force_ma": gen_force_ma,
    "au12s_momentum": gen_momentum,
    "au12s_sampling_mean": gen_sampling_mean,
    "au12s_se_sampling": gen_se_sampling,
}
