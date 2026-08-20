"""W5 of the curriculum depth program: the Y2-10 maths strand fill.

After W7's retro-tagging the auditor names ~30 missing maths strands across
Years 2-10; this module gives each one topic. Same contract and discipline as
every other generator module (exact-by-construction; mc4 only where the content
is genuinely categorical).
"""

from __future__ import annotations

from mentar.engine.au_senior_maths_items import _card
from mentar.engine.itemgen import GenFn, mc_which_is

# ── Year 2 ───────────────────────────────────────────────────────────────────

def gen_length_compare(rng):
    a = rng.choice([10, 12, 15, 18])
    b = rng.choice([4, 6, 8, 9])
    p = f"A pencil is {a} cm long. A crayon is {b} cm long. How many centimetres longer is the pencil?"
    card = _card("COMPARING LENGTHS", p, f"{a - b} cm",
                 "  How much longer = long length − short length",
                 f"  1. {a} − {b} = {a - b}, so the pencil is {a - b} cm longer.")
    return ("int", "int_exact", p, str(a - b), None, card,
            "(How much longer = big length − small length)")


def gen_money_coins(rng):
    coins = rng.choice([([2, 2, 1], 5), ([2, 1, 1], 4), ([2, 2, 2, 1], 7), ([1, 1, 1], 3)])
    vals, total = coins
    listing = " and ".join(f"${v}" for v in vals)
    p = f"You have these coins: {listing}. How many dollars altogether?"
    steps = " + ".join(str(v) for v in vals)
    card = _card("COUNTING MONEY", p, f"${total}",
                 "  Add the coins one at a time",
                 f"  1. {steps} = {total}, so you have ${total}.")
    return ("int", "int_exact", p, str(total), None, card,
            "(Add the coin values one at a time)")


def gen_time_oclock(rng):
    h = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    p = (f"On the clock, the little hand points at {h} and the big hand points "
         "straight up at 12. What o'clock is it?")
    card = _card("READING O'CLOCK TIME", p, h,
                 "  Big hand at 12 means an o'clock time; the little hand names the hour",
                 f"  1. Little hand at {h} → it is {h} o'clock.")
    return ("int", "int_exact", p, str(h), None, card,
            "(Big hand at 12 = o'clock; little hand tells the hour)")


_POSITIONS = {
    "BEHIND": ["the tree hiding the cat so you cannot see it",
               "the box that the ball rolled out of sight of"],
    "UNDER": ["the table with the dog lying beneath it",
              "the bed with slippers below it"],
    "BETWEEN": ["the cheese in the middle of two slices of bread",
                "the house with a shop on each side of it"],
}
_POSITIONS_GLOSSES = {
    "BEHIND": "behind means at the back of something",
    "UNDER": "under means lower than, beneath",
    "BETWEEN": "between means in the middle of two things",
}


def gen_position_words(rng):
    return mc_which_is(rng, "Which of these shows something {label} another thing?",
                       _POSITIONS, glosses=_POSITIONS_GLOSSES, concept_name="POSITION WORDS")


# ── Year 3 ───────────────────────────────────────────────────────────────────

def gen_number_pattern_add(rng):
    step = rng.choice([3, 4, 5, 10])
    start = rng.choice([2, 5, 7, 10])
    seq = [start, start + step, start + 2 * step]
    p = f"The pattern goes {seq[0]}, {seq[1]}, {seq[2]}, ... What number comes next?"
    card = _card("NUMBER PATTERNS", p, start + 3 * step,
                 "  Find the jump between numbers, then jump once more",
                 f"  1. {seq[1]} − {seq[0]} = {step}: the pattern adds {step}.",
                 f"  2. {seq[2]} + {step} = {start + 3 * step}.")
    return ("int", "int_exact", p, str(start + 3 * step), None, card,
            "(Find the jump, then jump once more)")


def gen_perimeter_count(rng):
    l_side = rng.choice([4, 5, 6, 7])
    w = rng.choice([2, 3])
    ans = 2 * (l_side + w)
    p = (f"A rectangle is {l_side} cm long and {w} cm wide. "
         "Walk all the way around it: what is its perimeter, in centimetres?")
    card = _card("PERIMETER — WALK AROUND", p, f"{ans} cm",
                 "  Perimeter = all four sides added",
                 f"  1. {l_side} + {w} + {l_side} + {w} = {ans}, so {ans} cm.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Add all four sides)")


def gen_shape_3d(rng):
    shape, part, n = rng.choice([("cube", "faces", 6), ("cube", "corners (vertices)", 8),
                                 ("cube", "edges", 12), ("square pyramid", "faces", 5),
                                 ("triangular prism", "faces", 5)])
    p = f"How many {part} does a {shape} have?"
    card = _card("3D SHAPES", p, n,
                 "  Count systematically: top, bottom, then the sides",
                 f"  1. A {shape} has {n} {part}.")
    return ("int", "int_exact", p, str(n), None, card,
            "(Count top, bottom, then around the sides)")


def gen_picture_graph(rng):
    per = rng.choice([2, 5, 10])
    n = rng.choice([3, 4, 5])
    p = (f"In a picture graph, each ● stands for {per} apples. "
         f"Monday's row shows {'●' * n}. How many apples is that?")
    card = _card("PICTURE GRAPHS", p, per * n,
                 "  Count the symbols, then multiply by what each is worth",
                 f"  1. {n} symbols × {per} each = {per * n}.")
    return ("int", "int_exact", p, str(per * n), None, card,
            "(Symbols × value of each symbol)")


# ── Year 4 ───────────────────────────────────────────────────────────────────

def gen_area_count_squares(rng):
    l_side = rng.choice([4, 5, 6, 7])
    w = rng.choice([2, 3, 4])
    p = (f"A rectangle is covered by centimetre squares: {l_side} squares along, "
         f"{w} rows. What is its area in square centimetres?")
    card = _card("AREA BY COUNTING SQUARES", p, f"{l_side * w} cm²",
                 "  Area = squares in a row × number of rows",
                 f"  1. {l_side} × {w} = {l_side * w}, so {l_side * w} cm².")
    return ("int", "int_exact", p, str(l_side * w), None, card,
            "(Squares per row × rows)")


def gen_money_change(rng):
    pay = rng.choice([10, 20])
    cost = rng.choice([3, 4, 6, 7, 8])
    if cost >= pay:
        cost = pay - 3
    p = f"A toy costs ${cost}. You pay with a ${pay} note. How many dollars change do you get?"
    card = _card("GIVING CHANGE", p, f"${pay - cost}",
                 "  Change = what you paid − what it cost",
                 f"  1. {pay} − {cost} = {pay - cost}, so ${pay - cost} change.")
    return ("int", "int_exact", p, str(pay - cost), None, card,
            "(Change = paid − cost)")


def gen_angle_degrees(rng):
    name, n = rng.choice([("a right angle", 90), ("a straight line", 180),
                          ("a full turn", 360), ("half of a right angle", 45)])
    p = f"How many degrees are in {name}?"
    card = _card("ANGLES IN DEGREES", p, f"{n}°",
                 "  Right angle 90° · straight line 180° · full turn 360°",
                 f"  1. {name} = {n}°.")
    return ("int", "int_exact", p, str(n), None, card,
            "(Right angle 90°, straight line 180°, full turn 360°)")


_CHANCE = {
    "CERTAIN": ["the sun rising tomorrow morning", "picking a red marble from a bag of only red marbles"],
    "IMPOSSIBLE": ["rolling a 7 on a normal six-sided die", "a pet dog laying an egg"],
    "an EVEN CHANCE (could go either way)": ["a tossed coin landing on heads",
                                             "picking a blue marble from a bag of 2 blue and 2 green"],
}
_CHANCE_GLOSSES = {
    "CERTAIN": "it will definitely happen — probability 1",
    "IMPOSSIBLE": "it cannot happen — probability 0",
    "an EVEN CHANCE (could go either way)": "as likely to happen as not — probability one half",
}


def gen_chance_words(rng):
    return mc_which_is(rng, "Which of these is {label}?", _CHANCE,
                       glosses=_CHANCE_GLOSSES, concept_name="CHANCE WORDS")


# ── Year 5 ───────────────────────────────────────────────────────────────────

def gen_perimeter_formula_y5(rng):
    l_side = rng.choice([8, 9, 11, 12])
    w = rng.choice([4, 5, 6, 7])
    ans = 2 * (l_side + w)
    p = f"A rectangle has length {l_side} m and width {w} m. What is its perimeter, in metres?"
    card = _card("PERIMETER OF A RECTANGLE", p, f"{ans} m",
                 "  Perimeter = 2 × (length + width)",
                 f"  1. {l_side} + {w} = {l_side + w}.",
                 f"  2. 2 × {l_side + w} = {ans}, so {ans} m.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Perimeter = 2 × (length + width))")


def gen_grid_move(rng):
    x = rng.choice([1, 2, 3])
    dx = rng.choice([2, 3, 4])
    y = rng.choice([1, 2, 5])
    p = (f"A point starts at ({x}, {y}) on a grid. It moves {dx} squares to the right. "
         "What is its new first (across) number?")
    card = _card("MOVING ON A GRID", p, x + dx,
                 "  Moving right adds to the ACROSS number; the up number stays",
                 f"  1. {x} + {dx} = {x + dx}: the point is now at ({x + dx}, {y}).")
    return ("int", "int_exact", p, str(x + dx), None, card,
            "(Right = add to the across number)")


def gen_mean_small(rng):
    m = rng.choice([4, 5, 6, 10])
    a, b, c = m - 2, m, m + 2
    p = f"Three scores are {a}, {b} and {c}. What is their average (mean)?"
    card = _card("FINDING THE AVERAGE", p, m,
                 "  Average = total ÷ how many scores",
                 f"  1. {a} + {b} + {c} = {3 * m}.",
                 f"  2. {3 * m} ÷ 3 = {m}.")
    return ("int", "int_exact", p, str(m), None, card,
            "(Average = total ÷ count)")


# ── Year 6 ───────────────────────────────────────────────────────────────────

def gen_sequence_rule(rng):
    start = rng.choice([2, 3, 5])
    k = rng.choice([2, 3])
    seq = [start, start * k, start * k * k]
    p = (f"A sequence follows the rule 'multiply by {k}': "
         f"{seq[0]}, {seq[1]}, {seq[2]}, ... What number comes next?")
    card = _card("SEQUENCE RULES", p, seq[2] * k,
                 f"  The rule is ×{k}: apply it to the last number",
                 f"  1. {seq[2]} × {k} = {seq[2] * k}.")
    return ("int", "int_exact", p, str(seq[2] * k), None, card,
            "(Apply the stated rule to the last number)")


def gen_quadrant(rng):
    x = rng.choice([-4, -2, 2, 4])
    y = rng.choice([-3, -1, 1, 3])
    q = {(True, True): "first", (False, True): "second",
         (False, False): "third", (True, False): "fourth"}[(x > 0, y > 0)]
    choices = ("first quadrant", "second quadrant", "third quadrant", "fourth quadrant")
    correct = f"{q} quadrant"
    letter = "ABCD"[choices.index(correct)]
    stem = f"On the Cartesian plane, in which quadrant is the point ({x}, {y})?"
    card = _card("CARTESIAN QUADRANTS", stem, correct,
                 "  Quadrants go anticlockwise: 1st (+,+), 2nd (−,+), 3rd (−,−), 4th (+,−)",
                 f"  1. x = {x} is {'positive' if x > 0 else 'negative'}; "
                 f"y = {y} is {'positive' if y > 0 else 'negative'}.",
                 f"  2. That sign pair is the {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


def gen_probability_decimal(rng):
    red, total, ans = rng.choice([(1, 2, "0.5"), (1, 4, "0.25"), (3, 4, "0.75"),
                                  (1, 10, "0.1"), (3, 10, "0.3"), (7, 10, "0.7")])
    p = (f"A bag holds {total} marbles and {red} of them are red. "
         "What is the probability of picking a red marble? Give a decimal.")
    card = _card("PROBABILITY AS A DECIMAL", p, ans,
                 "  Probability = red marbles ÷ total marbles",
                 f"  1. {red} ÷ {total} = {ans}.")
    return ("decimal", "decimal_exact", p, ans, None, card,
            "(Probability = favourable ÷ total)")


# ── Year 7 ───────────────────────────────────────────────────────────────────

def gen_area_triangle(rng):
    b = rng.choice([4, 6, 8, 10])
    h = rng.choice([3, 5, 7])
    ans = b * h // 2
    p = f"A triangle has base {b} cm and height {h} cm. What is its area, in square centimetres?"
    card = _card("AREA OF A TRIANGLE", p, f"{ans} cm²",
                 "  Area = ½ × base × height (half the surrounding rectangle)",
                 f"  1. {b} × {h} = {b * h}.",
                 f"  2. {b * h} ÷ 2 = {ans}, so {ans} cm².")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Area = ½ × base × height)")


def gen_angles_straight_line(rng):
    a = rng.choice([35, 48, 62, 75, 110, 125])
    p = (f"Two angles sit together on a straight line. One is {a}°. "
         "How many degrees is the other?")
    card = _card("ANGLES ON A STRAIGHT LINE", p, f"{180 - a}°",
                 "  Angles on a straight line add to 180°",
                 f"  1. 180 − {a} = {180 - a}, so the other angle is {180 - a}°.")
    return ("int", "int_exact", p, str(180 - a), None, card,
            "(Angles on a straight line add to 180°)")


def gen_median_odd(rng):
    m = rng.choice([6, 8, 10, 12])
    d1, d2 = rng.choice([(1, 3), (2, 5), (1, 4)])
    vals = sorted([m - d2, m - d1, m, m + d1, m + d2])
    listed = ", ".join(str(v) for v in [vals[2], vals[0], vals[4], vals[1], vals[3]])
    p = f"Find the median of these five numbers: {listed}."
    card = _card("FINDING THE MEDIAN", p, m,
                 "  Put the numbers in order; the median is the MIDDLE one",
                 f"  1. In order: {', '.join(str(v) for v in vals)}.",
                 f"  2. The middle (3rd of 5) is {m}.")
    return ("int", "int_exact", p, str(m), None, card,
            "(Order the numbers; take the middle one)")


# ── Year 8 ───────────────────────────────────────────────────────────────────

def gen_volume_prism(rng):
    l_side, w, h = rng.choice([(5, 3, 2), (6, 4, 2), (4, 3, 3), (7, 2, 3), (8, 5, 2)])
    ans = l_side * w * h
    p = (f"A rectangular prism is {l_side} cm long, {w} cm wide and {h} cm high. "
         "What is its volume, in cubic centimetres?")
    card = _card("VOLUME OF A RECTANGULAR PRISM", p, f"{ans} cm³",
                 "  Volume = length × width × height",
                 f"  1. {l_side} × {w} = {l_side * w}.",
                 f"  2. {l_side * w} × {h} = {ans}, so {ans} cm³.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Volume = length × width × height)")


_TRANSFORMS = {
    "a TRANSLATION (a slide)": ["a shape moved 3 squares right without turning",
                                "a stamp pressed again further along the page"],
    "a ROTATION (a turn)": ["a shape turned a quarter-turn about its corner",
                            "the hands moving around a clock face"],
    "a REFLECTION (a flip)": ["a shape flipped over a mirror line",
                              "a letter b becoming a letter d"],
}
_TRANSFORMS_GLOSSES = {
    "a TRANSLATION (a slide)": "every point moves the same distance, same direction",
    "a ROTATION (a turn)": "the shape turns about a fixed point",
    "a REFLECTION (a flip)": "the shape flips to its mirror image",
}


def gen_transformations(rng):
    return mc_which_is(rng, "Which of these is {label}?", _TRANSFORMS,
                       glosses=_TRANSFORMS_GLOSSES, concept_name="TRANSFORMATIONS")


def gen_range_data(rng):
    lo = rng.choice([3, 5, 8])
    hi = rng.choice([17, 21, 25, 30])
    mid1, mid2 = lo + 2, hi - 3
    p = f"A data set is: {mid1}, {lo}, {hi}, {mid2}. What is the range?"
    card = _card("RANGE OF A DATA SET", p, hi - lo,
                 "  Range = biggest value − smallest value",
                 f"  1. Biggest {hi}, smallest {lo}.",
                 f"  2. {hi} − {lo} = {hi - lo}.")
    return ("int", "int_exact", p, str(hi - lo), None, card,
            "(Range = biggest − smallest)")


# ── Year 9 ───────────────────────────────────────────────────────────────────

def gen_simple_interest_y9(rng):
    principal = rng.choice([200, 400, 500, 1000])
    rate = rng.choice([2, 5, 10])
    years = rng.choice([2, 3, 4])
    ans = principal * rate * years // 100
    p = (f"${principal} is invested at {rate}% simple interest per year for {years} years. "
         "How many dollars of interest does it earn?")
    card = _card("SIMPLE INTEREST", p, f"${ans}",
                 "  Interest = principal × rate × years ÷ 100",
                 f"  1. {principal} × {rate} = {principal * rate}.",
                 f"  2. {principal * rate} × {years} = {principal * rate * years}.",
                 f"  3. {principal * rate * years} ÷ 100 = {ans}, so ${ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Interest = P × R × T ÷ 100)")


def gen_scale_factor(rng):
    side = rng.choice([3, 4, 5, 6])
    k = rng.choice([2, 3, 4])
    p = (f"Two triangles are similar with scale factor {k}. A side of the small "
         f"triangle is {side} cm. How long is the matching side of the large one?")
    card = _card("SIMILAR SHAPES AND SCALE FACTOR", p, f"{side * k} cm",
                 "  Matching side = small side × scale factor",
                 f"  1. {side} × {k} = {side * k}, so {side * k} cm.")
    return ("int", "int_exact", p, str(side * k), None, card,
            "(Multiply by the scale factor)")


def gen_scatter_trend_y9(rng):
    ctx, correct = rng.choice([
        ("taller plants tended to have deeper roots", "positive"),
        ("older cars tended to sell for less", "negative"),
        ("shoe size showed no pattern against test score", "no association")])
    choices = ("positive", "negative", "no association", "it cannot be told")
    letter = "ABCD"[choices.index(correct)]
    stem = f"A scatterplot shows that {ctx}. What association is this?"
    card = _card("READING A SCATTERPLOT TREND", stem, correct,
                 "  Rise together → positive; one falls as the other rises → negative",
                 f"  1. {ctx} → {correct}.")
    return ("mc4", "mc_choice", stem, letter, choices, card)


# ── Year 10 ──────────────────────────────────────────────────────────────────

def gen_compound_two_years(rng):
    principal = rng.choice([100, 200, 400])
    rate = rng.choice([10, 20, 50])
    y1 = principal * (100 + rate) // 100
    y2 = y1 * (100 + rate) // 100
    p = (f"${principal} is invested at {rate}% compound interest per year. "
         "What is the balance, in dollars, after two years?")
    card = _card("COMPOUND INTEREST — TWO YEARS", p, f"${y2}",
                 "  Each year: balance = balance + balance × rate ÷ 100",
                 f"  1. Year 1: {principal} + {principal * rate // 100} = {y1}.",
                 f"  2. Year 2: {y1} + {y1 * rate // 100} = {y2}, so ${y2}.")
    return ("int", "int_exact", p, str(y2), None, card,
            "(Apply the growth year by year, on the NEW balance)")


def gen_two_stage_probability(rng):
    ev, ans = rng.choice([("two heads from two coin tosses", "0.25"),
                          ("two tails from two coin tosses", "0.25"),
                          ("a head then a tail, in that order", "0.25"),
                          ("a head on a single toss followed by any result", "0.5")])
    p = (f"A fair coin is tossed twice. What is the probability of {ev}? "
         "Give a decimal.")
    card = _card("TWO-STAGE PROBABILITY", p, ans,
                 "  Multiply along the branches: ½ × ½ for two named results",
                 "  1. Each toss: probability ½ for either face.",
                 f"  2. For {ev}: the multiplication gives {ans}.")
    return ("decimal", "decimal_exact", p, ans, None, card,
            "(Multiply the probability along each branch)")


def gen_compare_means(rng):
    m = rng.choice([10, 12, 20])
    d = rng.choice([2, 3, 5])
    a = [m - d, m, m + d]
    b = [m, m + d, m + 2 * d]
    p = (f"Class A scored {a[0]}, {a[1]}, {a[2]}. Class B scored {b[0]}, {b[1]}, {b[2]}. "
         "How much higher is Class B's mean than Class A's?")
    card = _card("COMPARING TWO DATA SETS", p, d,
                 "  Find each mean, then subtract",
                 f"  1. Class A mean: ({a[0]} + {a[1]} + {a[2]}) ÷ 3 = {m}.",
                 f"  2. Class B mean: ({b[0]} + {b[1]} + {b[2]}) ÷ 3 = {m + d}.",
                 f"  3. {m + d} − {m} = {d}.")
    return ("int", "int_exact", p, str(d), None, card,
            "(Mean of each set, then the difference)")


AU_JUNIOR_MATHS_FILL: dict[int, dict[str, tuple[GenFn, str, str]]] = {
    # year -> node id -> (generator, strand, label)
    2: {
        "au2_length_compare": (gen_length_compare, "Measurement", "Comparing lengths"),
        "au2_money_coins": (gen_money_coins, "Money and time", "Counting money"),
        "au2_time_oclock": (gen_time_oclock, "Money and time", "Reading o'clock time"),
        "au2_position_words": (gen_position_words, "Space and location", "Position words"),
    },
    3: {
        "au3_number_pattern": (gen_number_pattern_add, "Algebra", "Number patterns"),
        "au3_perimeter_count": (gen_perimeter_count, "Measurement and time", "Perimeter — walk around"),
        "au3_shape_3d": (gen_shape_3d, "Space", "3D shapes"),
        "au3_picture_graph": (gen_picture_graph, "Statistics", "Picture graphs"),
    },
    4: {
        "au4_area_count_squares": (gen_area_count_squares, "Measurement", "Area by counting squares"),
        "au4_money_change": (gen_money_change, "Money", "Giving change"),
        "au4_angle_degrees": (gen_angle_degrees, "Space", "Angles in degrees"),
        "au4_chance_words": (gen_chance_words, "Statistics and probability", "Chance words"),
    },
    5: {
        "au5_perimeter_rectangle": (gen_perimeter_formula_y5, "Measurement", "Perimeter of a rectangle"),
        "au5_grid_move": (gen_grid_move, "Space", "Moving on a grid"),
        "au5_mean_small": (gen_mean_small, "Statistics", "Finding the average"),
    },
    6: {
        "au6_sequence_rule": (gen_sequence_rule, "Algebra", "Sequence rules"),
        "au6_quadrant": (gen_quadrant, "Space", "Cartesian quadrants"),
        "au6_probability_decimal": (gen_probability_decimal, "Statistics and probability", "Probability as a decimal"),
    },
    7: {
        "au7_area_triangle": (gen_area_triangle, "Measurement", "Area of a triangle"),
        "au7_angles_straight_line": (gen_angles_straight_line, "Space", "Angles on a straight line"),
        "au7_median": (gen_median_odd, "Statistics and probability", "Finding the median"),
    },
    8: {
        "au8_volume_prism": (gen_volume_prism, "Measurement", "Volume of a rectangular prism"),
        "au8_transformations": (gen_transformations, "Space", "Transformations"),
        "au8_range": (gen_range_data, "Statistics", "Range of a data set"),
    },
    9: {
        "au9_simple_interest": (gen_simple_interest_y9, "Number and finance", "Simple interest"),
        "au9_scale_factor": (gen_scale_factor, "Space", "Similar shapes and scale factor"),
        "au9_scatter_trend": (gen_scatter_trend_y9, "Statistics", "Reading a scatterplot trend"),
    },
    10: {
        "au10_compound_two_years": (gen_compound_two_years, "Number and finance", "Compound interest — two years"),
        "au10_two_stage_probability": (gen_two_stage_probability, "Probability", "Two-stage probability"),
        "au10_compare_means": (gen_compare_means, "Statistics", "Comparing two data sets"),
    },
}
