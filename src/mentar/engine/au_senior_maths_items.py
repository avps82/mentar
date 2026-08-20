"""Senior maths generators — Australia, Years 11–12, split by COURSE.

Maintainer decision 2026-08-20: senior maths splits into the four courses a
student actually enrols in — Essential, General, Mathematical Methods and
Specialist — mirroring the 2026-08-15 senior-science split (Physics/Chemistry/
Biology). The old single "Year 11/12 Maths" subject (4+3 quadratic-expression
topics) was the whole of senior maths until now; the maintainer's verdict was
"quite less and incomplete", and a comparison against the real course
structures (five strands each) agreed.

NO claimed alignment: senior courses are set by state certificate authorities
(VCE/HSC/QCE/SACE); course names and topic coverage here follow the common
national structure, content is 100% Mentar-authored (docs/CONTENT_LICENSES.md
§2b posture, same as senior science).

Every generator returns the itemgen tuple contract:
    (answer_type, checker, problem, answer[, choices][, method_steps][, format_hint])
Cards lead with the FORMULA where one exists (maintainer, 2026-08-19: "that
step reinforces the formula and its application") and always end "Answer: ...".
Formula-shaped questions put the formula in the cue slot (7th element) instead
of the generic type hint.
"""

from __future__ import annotations

__all__ = [
    "AU_ESSENTIAL_Y11_GENERATORS", "AU_ESSENTIAL_Y12_GENERATORS",
    "AU_GENERAL_Y11_GENERATORS", "AU_GENERAL_Y12_GENERATORS",
]


def _money(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s


def _card(title, problem, answer, *steps):
    return (title, problem, *steps, f"  Answer: {answer}")


# ─────────────────────────────────────────────────────────────────────────────
# ESSENTIAL — Year 11
# ─────────────────────────────────────────────────────────────────────────────

def gen_percentage_of_money(rng):
    pct = rng.choice([10, 20, 25, 50, 5, 15])
    amount = rng.choice([40, 60, 80, 120, 200, 240, 360])
    ans = _money(amount * pct / 100)
    p = f"A jacket costs ${amount}. It is discounted by {pct}%. How many dollars do you save?"
    card = _card("PERCENTAGE OF AN AMOUNT", p, ans,
                 "  Percentage of an amount = amount × percentage ÷ 100",
                 f"  1. {amount} × {pct} = {amount * pct}.",
                 f"  2. {amount * pct} ÷ 100 = {ans}.")
    return ("decimal", "decimal_exact", p, ans, None, card,
            "(Percentage of an amount = amount × percentage ÷ 100)")


def gen_best_buy(rng):
    unit = rng.choice([2, 3, 4, 5])
    good_n = rng.choice([4, 5, 6])
    bad_n = rng.choice([2, 3])
    good = good_n * unit                          # exact unit price
    bad = bad_n * (unit + rng.choice([1, 2]))     # exact, and worse per bar
    stem = (f"Pack A: {good_n} bars for ${good}. Pack B: {bad_n} bars for ${bad}. "
            "Which is the better buy (cheaper per bar)?")
    choices = ("Pack A", "Pack B", "They cost the same per bar", "It cannot be worked out")
    # Both divisions are EXACT by construction -- the first draft rounded
    # ("16 ÷ 3 = 5.33") and the claim-checker sweep rightly flagged the card
    # as asserting false arithmetic. Cards must never show approximations as
    # equalities.
    card = _card("BEST BUY (UNIT PRICE)", stem, "Pack A",
                 "  Unit price = total price ÷ number of items",
                 f"  1. Pack A: {good} ÷ {good_n} = {good // good_n} per bar.",
                 f"  2. Pack B: {bad} ÷ {bad_n} = {bad // bad_n} per bar.",
                 f"  3. {good // good_n} is less, so Pack A wins.")
    return ("mc4", "mc_choice", stem, "A", choices, card,
            "(Unit price = total price ÷ number of items)")


def gen_wages_overtime(rng):
    rate = rng.choice([20, 22, 24, 26, 30])
    normal = rng.choice([6, 7, 8])
    extra = rng.choice([1, 2, 3])
    total = normal * rate + extra * rate * 1.5
    p = (f"Sam earns ${rate} per hour for a {normal}-hour shift, then time-and-a-half "
         f"for {extra} extra hour{'s' if extra > 1 else ''}. How many dollars does Sam earn in total?")
    ans = _money(total)
    card = _card("WAGES WITH OVERTIME", p, ans,
                 "  Total pay = normal hours × rate + overtime hours × rate × 1.5",
                 f"  1. Normal: {normal} × {rate} = {normal * rate}.",
                 f"  2. Overtime: {extra} × {rate} × 1.5 = {_money(extra * rate * 1.5)}.",
                 f"  3. {normal * rate} + {_money(extra * rate * 1.5)} = {ans}.")
    return ("decimal", "decimal_exact", p, ans, None, card,
            "(Total pay = normal hours × rate + overtime hours × rate × 1.5)")


def gen_simple_interest(rng):
    principal = rng.choice([1000, 2000, 4000, 5000, 8000])
    rate = rng.choice([2, 3, 4, 5])
    years = rng.choice([2, 3, 4])
    interest = principal * rate * years // 100
    p = (f"${principal} is invested at {rate}% simple interest per year for {years} years. "
         "How many dollars of interest does it earn?")
    card = _card("SIMPLE INTEREST", p, interest,
                 "  Interest = principal × rate × time ÷ 100",
                 f"  1. {principal} × {rate} × {years} = {principal * rate * years}.",
                 f"  2. {principal * rate * years} ÷ 100 = {interest}.")
    return ("int", "int_exact", p, str(interest), None, card,
            "(Interest = principal × rate × time ÷ 100)")


def gen_budget_balance(rng):
    income = rng.choice([600, 750, 800, 900])
    rent, food, travel = rng.choice([220, 260, 300]), rng.choice([120, 150, 180]), rng.choice([40, 60, 80])
    left = income - rent - food - travel
    p = (f"Weekly income is ${income}. Rent is ${rent}, food ${food} and travel ${travel}. "
         "How many dollars are left over each week?")
    card = _card("BUDGET LEFTOVER", p, left,
                 "  Left over = income − all expenses",
                 f"  1. Expenses: {rent} + {food} + {travel} = {rent + food + travel}.",
                 f"  2. {income} − {rent + food + travel} = {left}.")
    return ("int", "int_exact", p, str(left), None, card,
            "(Left over = income − all expenses)")


def gen_composite_area(rng):
    big_w, big_h = rng.choice([(10, 8), (12, 6), (9, 7), (11, 8)])
    cut_w, cut_h = rng.choice([(3, 2), (4, 3), (2, 2)])
    area = big_w * big_h - cut_w * cut_h
    p = (f"An L-shaped floor is a {big_w} m by {big_h} m rectangle with a {cut_w} m by "
         f"{cut_h} m corner removed. What is its area, in square metres?")
    card = _card("COMPOSITE AREA (SUBTRACT THE CUT-OUT)", p, area,
                 "  Composite area = big rectangle − removed rectangle",
                 f"  1. Big: {big_w} × {big_h} = {big_w * big_h}.",
                 f"  2. Cut-out: {cut_w} × {cut_h} = {cut_w * cut_h}.",
                 f"  3. {big_w * big_h} − {cut_w * cut_h} = {area}.")
    return ("int", "int_exact", p, str(area), None, card,
            "(Composite area = big rectangle − removed rectangle)")


def gen_volume_box(rng):
    ln, w, h = rng.choice([(5, 4, 3), (6, 3, 2), (8, 5, 2), (4, 4, 3), (10, 4, 2)])
    vol = ln * w * h
    p = f"A storage box is {ln} m long, {w} m wide and {h} m high. What is its volume, in cubic metres?"
    card = _card("VOLUME OF A BOX", p, vol,
                 "  Volume = length × width × height",
                 f"  1. {ln} × {w} = {ln * w}.",
                 f"  2. {ln * w} × {h} = {vol}.")
    return ("int", "int_exact", p, str(vol), None, card,
            "(Volume = length × width × height)")


def gen_fuel_consumption(rng):
    per100 = rng.choice([6, 7, 8, 9])
    dist = rng.choice([200, 300, 400, 500])
    litres = per100 * dist // 100
    p = (f"A car uses {per100} L of fuel per 100 km. How many litres does it use "
         f"on a {dist} km trip?")
    card = _card("FUEL FOR A TRIP", p, litres,
                 "  Fuel used = (distance ÷ 100) × litres per 100 km",
                 f"  1. {dist} ÷ 100 = {dist // 100}.",
                 f"  2. {dist // 100} × {per100} = {litres}.")
    return ("int", "int_exact", p, str(litres), None, card,
            "(Fuel used = distance ÷ 100 × litres per 100 km)")


def gen_time_duration(rng):
    start_h = rng.choice([8, 9, 10])
    start_m = rng.choice([0, 15, 30, 45])
    dur = rng.choice([75, 90, 105, 120, 135])
    end_total = start_h * 60 + start_m + dur
    end_h, end_m = end_total // 60, end_total % 60
    p = (f"A class starts at {start_h}:{start_m:02d} and runs for {dur} minutes. "
         "How many minutes past the hour does it finish? (Give just the minutes part "
         f"of the finishing time.)")
    card = _card("FINISHING TIME", p, end_m,
                 "  Finish = start + duration; carry every 60 minutes into hours",
                 f"  1. Start in minutes: {start_h} × 60 + {start_m} = {start_h * 60 + start_m}.",
                 f"  2. Add {dur}: {end_total} minutes = {end_h}:{end_m:02d}.",
                 f"  3. The minutes part is {end_m}.")
    return ("int", "int_exact", p, str(end_m), None, card)


def gen_mean_of_data(rng):
    n = rng.choice([4, 5])
    target = rng.choice([6, 7, 8, 10])
    vals = [target + d for d in rng.sample([-3, -2, -1, 0, 1, 2, 3], n)]
    while sum(vals) % n != 0:
        vals[0] += 1
    mean = sum(vals) // n
    p = f"Scores: {', '.join(str(v) for v in vals)}. What is the mean score?"
    card = _card("MEAN (AVERAGE)", p, mean,
                 "  Mean = total of the scores ÷ how many scores",
                 f"  1. Total: {' + '.join(str(v) for v in vals)} = {sum(vals)}.",
                 f"  2. {sum(vals)} ÷ {n} = {mean}.")
    return ("int", "int_exact", p, str(mean), None, card,
            "(Mean = total ÷ how many)")


AU_ESSENTIAL_Y11_GENERATORS = {
    "au11e_percentage_of_money": gen_percentage_of_money,
    "au11e_best_buy": gen_best_buy,
    "au11e_wages_overtime": gen_wages_overtime,
    "au11e_simple_interest": gen_simple_interest,
    "au11e_budget_balance": gen_budget_balance,
    "au11e_composite_area": gen_composite_area,
    "au11e_volume_box": gen_volume_box,
    "au11e_fuel_consumption": gen_fuel_consumption,
    "au11e_time_duration": gen_time_duration,
    "au11e_mean_of_data": gen_mean_of_data,
}


# ─────────────────────────────────────────────────────────────────────────────
# ESSENTIAL — Year 12
# ─────────────────────────────────────────────────────────────────────────────

def gen_compound_growth(rng):
    principal = rng.choice([1000, 2000, 5000])
    rate = rng.choice([10, 20])
    after1 = principal * (100 + rate) // 100
    after2 = after1 * (100 + rate) // 100
    p = (f"${principal} grows by {rate}% each year, compounding. "
         "How many dollars is it worth after 2 years?")
    card = _card("COMPOUND GROWTH (TWO STEPS)", p, after2,
                 "  Each year: new value = old value × (100 + rate) ÷ 100",
                 f"  1. Year 1: {principal} × {100 + rate} ÷ 100 = {after1}.",
                 f"  2. Year 2: {after1} × {100 + rate} ÷ 100 = {after2}.")
    return ("int", "int_exact", p, str(after2), None, card,
            "(Each year: new value = old value × (100 + rate) ÷ 100)")


def gen_loan_total_cost(rng):
    payment = rng.choice([250, 300, 400])
    months = rng.choice([24, 36, 48])
    principal = rng.choice([6000, 8000, 10000])
    total = payment * months
    extra = total - principal
    p = (f"A ${principal} loan is repaid at ${payment} per month for {months} months. "
         "How many dollars MORE than the loan amount is repaid in total?")
    card = _card("TRUE COST OF A LOAN", p, extra,
                 "  Extra paid = (payment × number of payments) − amount borrowed",
                 f"  1. Total repaid: {payment} × {months} = {total}.",
                 f"  2. {total} − {principal} = {extra}.")
    return ("int", "int_exact", p, str(extra), None, card,
            "(Extra paid = payment × number of payments − amount borrowed)")


def gen_income_tax(rng):
    free = 18000
    rate = rng.choice([20, 25, 30])
    income = rng.choice([30000, 38000, 46000, 58000])
    tax = (income - free) * rate // 100
    p = (f"Tax is 0% on the first ${free} earned and {rate}% on the rest. "
         f"How many dollars of tax are paid on an income of ${income}?")
    card = _card("INCOME TAX (TWO BRACKETS)", p, tax,
                 "  Tax = (income − tax-free amount) × rate ÷ 100",
                 f"  1. Taxable part: {income} − {free} = {income - free}.",
                 f"  2. {income - free} × {rate} ÷ 100 = {tax}.")
    return ("int", "int_exact", p, str(tax), None, card,
            "(Tax = (income − tax-free amount) × rate ÷ 100)")


def gen_gst_price(rng):
    base = rng.choice([40, 60, 80, 120, 250])
    final = base * 110 // 100
    p = f"A service costs ${base} before GST. GST adds 10%. What is the final price, in dollars?"
    card = _card("ADDING GST", p, final,
                 "  Final price = base price × 110 ÷ 100",
                 f"  1. {base} × 110 = {base * 110}.",
                 f"  2. {base * 110} ÷ 100 = {final}.")
    return ("int", "int_exact", p, str(final), None, card,
            "(Final price = base price × 110 ÷ 100)")


def gen_scale_drawing(rng):
    scale = rng.choice([100, 200, 500])
    cm = rng.choice([3, 4, 5, 6, 8])
    metres = cm * scale // 100
    p = (f"A plan uses a scale of 1:{scale}. A wall measures {cm} cm on the plan. "
         "How long is the real wall, in metres?")
    card = _card("SCALE DRAWING", p, metres,
                 "  Real length = plan length × scale (then convert cm to m)",
                 f"  1. {cm} cm × {scale} = {cm * scale} cm.",
                 f"  2. {cm * scale} cm ÷ 100 = {metres} m.")
    return ("int", "int_exact", p, str(metres), None, card,
            "(Real length = plan length × scale)")


def gen_network_edges(rng):
    people = rng.choice([4, 5, 6, 7])
    edges = people * (people - 1) // 2
    p = (f"In a network, {people} towns are ALL connected directly to each other. "
         "How many roads (edges) is that?")
    card = _card("EDGES IN A COMPLETE NETWORK", p, edges,
                 "  Edges = n × (n − 1) ÷ 2, where n is the number of vertices",
                 f"  1. {people} × {people - 1} = {people * (people - 1)}.",
                 f"  2. {people * (people - 1)} ÷ 2 = {edges} — each road was counted from both ends.")
    return ("int", "int_exact", p, str(edges), None, card,
            "(Edges = n × (n − 1) ÷ 2)")


def gen_shortest_path(rng):
    a1, a2 = rng.choice([(5, 7), (6, 9), (4, 8)])
    b1, b2, b3 = rng.choice([(3, 4, 4), (2, 5, 4), (3, 3, 5)])
    best = min(a1 + a2, b1 + b2 + b3)
    p = (f"Route 1 from home to school: two roads of {a1} km and {a2} km. "
         f"Route 2: three roads of {b1} km, {b2} km and {b3} km. "
         "How long is the SHORTER route, in km?")
    card = _card("SHORTEST PATH", p, best,
                 "  Compare the total length of every route; the smallest total wins",
                 f"  1. Route 1: {a1} + {a2} = {a1 + a2}.",
                 f"  2. Route 2: {b1} + {b2} + {b3} = {b1 + b2 + b3}.",
                 f"  3. The shorter is {best} km.")
    return ("int", "int_exact", p, str(best), None, card)


def gen_relative_frequency(rng):
    # Constructed, never searched: the first draft re-rolled `trials` in a while
    # loop whose condition was unsatisfiable for hits=18 -- an INFINITE loop
    # that hung the generator sweep and the template build (caught 2026-08-20).
    hits = rng.choice([12, 15, 18, 24])
    trials = hits * rng.choice([3, 4, 5])
    p = (f"A spinner landed on red {hits} times out of {trials} spins. "
         "What is the relative frequency of red, as a fraction?")
    ans = f"{hits}/{trials}"
    card = _card("RELATIVE FREQUENCY", p, ans,
                 "  Relative frequency = times it happened / total trials",
                 f"  1. Red happened {hits} times in {trials} trials.",
                 f"  2. Relative frequency = {hits}/{trials} (any equivalent fraction is right).")
    return ("fraction", "fraction_equiv", p, ans, None, card,
            "(Relative frequency = times it happened / total trials)")


def gen_energy_cost(rng):
    kwh = rng.choice([2, 3, 4])
    hours = rng.choice([5, 10])
    cents = rng.choice([30, 40, 50])
    cost = kwh * hours * cents  # in cents
    dollars = _money(cost / 100)
    p = (f"A heater uses {kwh} kWh every hour and runs for {hours} hours. "
         f"Electricity costs {cents} cents per kWh. What is the total cost, in dollars?")
    card = _card("ENERGY COST", p, dollars,
                 "  Cost = kWh used × hours × cents per kWh (then cents → dollars)",
                 f"  1. Energy: {kwh} × {hours} = {kwh * hours} kWh.",
                 f"  2. {kwh * hours} × {cents} = {cost} cents.",
                 f"  3. {cost} cents = ${dollars}.")
    return ("decimal", "decimal_exact", p, dollars, None, card,
            "(Cost = kWh × hours × cents per kWh)")


def gen_speed_distance_time(rng):
    speed = rng.choice([60, 80, 100])
    hours = rng.choice([2, 3])
    halves = rng.choice([0, 1])
    dist = speed * hours + speed * halves // 2
    time_str = f"{hours}.5" if halves else str(hours)
    p = f"A car travels at {speed} km/h for {time_str} hours. How far does it go, in km?"
    card = _card("DISTANCE FROM SPEED AND TIME", p, dist,
                 "  Distance = speed × time",
                 f"  1. {speed} × {time_str} = {dist}.")
    return ("int", "int_exact", p, str(dist), None, card,
            "(Distance = speed × time)")


AU_ESSENTIAL_Y12_GENERATORS = {
    "au12e_compound_growth": gen_compound_growth,
    "au12e_loan_total_cost": gen_loan_total_cost,
    "au12e_income_tax": gen_income_tax,
    "au12e_gst_price": gen_gst_price,
    "au12e_scale_drawing": gen_scale_drawing,
    "au12e_network_edges": gen_network_edges,
    "au12e_shortest_path": gen_shortest_path,
    "au12e_relative_frequency": gen_relative_frequency,
    "au12e_energy_cost": gen_energy_cost,
    "au12e_speed_distance_time": gen_speed_distance_time,
}


# ─────────────────────────────────────────────────────────────────────────────
# GENERAL — Year 11
# ─────────────────────────────────────────────────────────────────────────────

def gen_arithmetic_nth(rng):
    a = rng.choice([2, 3, 5, 7])
    d = rng.choice([3, 4, 5, 6])
    n = rng.choice([8, 10, 12, 15])
    ans = a + (n - 1) * d
    p = (f"An arithmetic sequence starts at {a} and goes up by {d} each term. "
         f"What is term {n}?")
    card = _card("ARITHMETIC SEQUENCE — NTH TERM", p, ans,
                 "  Term n = first term + (n − 1) × common difference",
                 f"  1. n − 1 = {n - 1}.",
                 f"  2. {n - 1} × {d} = {(n - 1) * d}.",
                 f"  3. {a} + {(n - 1) * d} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Term n = first term + (n − 1) × difference)")


def gen_geometric_nth(rng):
    a = rng.choice([2, 3, 5])
    r = rng.choice([2, 3])
    n = rng.choice([4, 5])
    ans = a * r ** (n - 1)
    p = (f"A geometric sequence starts at {a} and multiplies by {r} each term. "
         f"What is term {n}?")
    card = _card("GEOMETRIC SEQUENCE — NTH TERM", p, ans,
                 "  Term n = first term × ratio^(n − 1)",
                 f"  1. Ratio applied {n - 1} times: {r}^{n - 1} = {r ** (n - 1)}.",
                 f"  2. {a} × {r ** (n - 1)} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(Term n = first term × ratio^(n − 1))")


def gen_matrix_addition(rng):
    a, b, c, d = (rng.randint(1, 9) for _ in range(4))
    e, f, g, h = (rng.randint(1, 9) for _ in range(4))
    p = (f"A = [{a} {b}; {c} {d}] and B = [{e} {f}; {g} {h}] "
         "(rows separated by ';'). What is the TOP-LEFT entry of A + B?")
    ans = a + e
    card = _card("MATRIX ADDITION", p, ans,
                 "  Matrices add entry by entry — each position adds to the same position",
                 f"  1. Top-left of A is {a}; top-left of B is {e}.",
                 f"  2. {a} + {e} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card)


def gen_matrix_scalar(rng):
    k = rng.choice([2, 3, 4, 5])
    a, b, c, d = (rng.randint(1, 9) for _ in range(4))
    which, val = rng.choice([("top-right", b), ("bottom-left", c), ("bottom-right", d)])
    p = (f"M = [{a} {b}; {c} {d}] (rows separated by ';'). "
         f"What is the {which} entry of {k}M?")
    ans = k * val
    card = _card("SCALAR MULTIPLE OF A MATRIX", p, ans,
                 "  kM multiplies EVERY entry by k",
                 f"  1. The {which} entry of M is {val}.",
                 f"  2. {k} × {val} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card)


def gen_linear_rule_value(rng):
    m = rng.choice([2, 3, 4, 5])
    c = rng.choice([-3, -1, 1, 2, 4])
    x = rng.choice([3, 4, 5, 6, 10])
    y = m * x + c
    sign = "+" if c >= 0 else "−"
    p = f"A line has the rule y = {m}x {sign} {abs(c)}. What is y when x = {x}?"
    card = _card("VALUE FROM A LINEAR RULE", p, y,
                 "  Substitute the x value into the rule, then follow the arithmetic",
                 f"  1. {m} × {x} = {m * x}.",
                 f"  2. {m * x} {sign} {abs(c)} = {y}.")
    return ("int", "int_exact", p, str(y), None, card)


def gen_pythagoras(rng):
    a, b, h = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17)])
    p = (f"A right-angled triangle has shorter sides {a} m and {b} m. "
         "How long is the hypotenuse, in metres?")
    card = _card("PYTHAGORAS' THEOREM", p, h,
                 "  hypotenuse² = a² + b²",
                 f"  1. {a}² + {b}² = {a * a} + {b * b} = {h * h}.",
                 f"  2. The hypotenuse is the square root of {h * h}, which is {h}.")
    return ("int", "int_exact", p, str(h), None, card,
            "(hypotenuse² = a² + b²)")


def gen_trig_opposite(rng):
    # tan(45°) = 1 keeps it exact without tables
    adj = rng.choice([5, 7, 9, 12, 15])
    p = (f"From {adj} m away, the angle up to the top of a pole is 45°. "
         "tan 45° = 1. How tall is the pole, in metres?")
    card = _card("HEIGHT FROM AN ANGLE (TAN)", p, adj,
                 "  opposite = adjacent × tan(angle)",
                 "  1. tan 45° = 1.",
                 f"  2. {adj} × 1 = {adj}.")
    return ("int", "int_exact", p, str(adj), None, card,
            "(opposite = adjacent × tan(angle))")


def gen_circle_circumference(rng):
    r = rng.choice([5, 10, 15, 20])
    approx = _money(2 * 3.14 * r)
    p = (f"A circular track has radius {r} m. Using π ≈ 3.14, what is its "
         "circumference, in metres?")
    card = _card("CIRCUMFERENCE OF A CIRCLE", p, approx,
                 "  Circumference = 2 × π × radius",
                 "  1. 2 × 3.14 = 6.28.",
                 f"  2. 6.28 × {r} = {approx}.")
    return ("decimal", "decimal_exact", p, approx, None, card,
            "(Circumference = 2 × π × radius)")


def gen_two_way_table(rng):
    a, b, c = rng.randint(5, 15), rng.randint(5, 15), rng.randint(5, 15)
    total = rng.randint(a + b + c + 3, a + b + c + 15)
    d = total - a - b - c
    p = (f"A two-way table of {total} students: plays sport AND music {a}; sport only {b}; "
         f"music only {c}. How many play NEITHER?")
    card = _card("TWO-WAY TABLE — THE MISSING CELL", p, d,
                 "  The four cells must add to the total",
                 f"  1. Accounted for: {a} + {b} + {c} = {a + b + c}.",
                 f"  2. {total} − {a + b + c} = {d}.")
    return ("int", "int_exact", p, str(d), None, card)


def gen_correlation_direction(rng):
    stem_pairs = [
        ("hours of study and test scores rise together", "positive"),
        ("as daily temperature rises, heater use falls", "negative"),
        ("shoe size and favourite colour show no pattern", "no correlation"),
        ("as car age goes up, resale price goes down", "negative"),
        ("height and arm span rise together", "positive"),
    ]
    desc, kind = rng.choice(stem_pairs)
    stem = f"In a scatter plot, {desc}. What correlation is this?"
    kinds = ["positive", "negative", "no correlation"]
    others = [k for k in kinds if k != kind]
    choices = [kind, others[0], others[1], "perfect correlation"]
    rng.shuffle(choices)
    letter = "ABCD"[choices.index(kind)]
    card = _card("CORRELATION DIRECTION", stem, kind,
                 "  Rising together = positive · one rises, one falls = negative · no pattern = none",
                 f"  1. Here: {desc}.",
                 f"  2. That is a {kind} correlation.")
    return ("mc4", "mc_choice", stem, letter, tuple(choices), card)


AU_GENERAL_Y11_GENERATORS = {
    "au11g_arithmetic_nth": gen_arithmetic_nth,
    "au11g_geometric_nth": gen_geometric_nth,
    "au11g_matrix_addition": gen_matrix_addition,
    "au11g_matrix_scalar": gen_matrix_scalar,
    "au11g_linear_rule_value": gen_linear_rule_value,
    "au11g_pythagoras": gen_pythagoras,
    "au11g_trig_opposite": gen_trig_opposite,
    "au11g_circle_circumference": gen_circle_circumference,
    "au11g_two_way_table": gen_two_way_table,
    "au11g_correlation_direction": gen_correlation_direction,
}


# ─────────────────────────────────────────────────────────────────────────────
# GENERAL — Year 12
# ─────────────────────────────────────────────────────────────────────────────

def gen_arithmetic_series_sum(rng):
    a = rng.choice([1, 2, 3])
    d = rng.choice([2, 3])
    n = rng.choice([10, 12, 20])
    last = a + (n - 1) * d
    total = n * (a + last) // 2
    p = (f"An arithmetic sequence starts at {a}, goes up by {d}, and has {n} terms. "
         "What is the sum of all the terms?")
    card = _card("SUM OF AN ARITHMETIC SERIES", p, total,
                 "  Sum = n × (first + last) ÷ 2",
                 f"  1. Last term: {a} + {n - 1} × {d} = {last}.",
                 f"  2. {n} × ({a} + {last}) ÷ 2 = {total}.")
    return ("int", "int_exact", p, str(total), None, card,
            "(Sum = n × (first + last) ÷ 2)")


def gen_growth_application(rng):
    start = rng.choice([100, 200, 500])
    r = rng.choice([2, 3])
    steps = rng.choice([3, 4])
    ans = start * r ** steps
    p = (f"A bacteria colony of {start} cells {'doubles' if r == 2 else 'triples'} "
         f"every hour. How many cells after {steps} hours?")
    card = _card("REPEATED GROWTH", p, ans,
                 "  After n steps: amount = start × ratio^n",
                 f"  1. {r}^{steps} = {r ** steps}.",
                 f"  2. {start} × {r ** steps} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(amount = start × ratio^n)")


def gen_matrix_product_entry(rng):
    a, b = rng.randint(1, 6), rng.randint(1, 6)
    x, y = rng.randint(1, 9), rng.randint(1, 9)
    ans = a * x + b * y
    p = (f"Row [{a} {b}] multiplies column [{x}; {y}]. "
         "What single number does this row-times-column give?")
    card = _card("ROW × COLUMN", p, ans,
                 "  Multiply matching entries, then add the products",
                 f"  1. {a} × {x} = {a * x}.",
                 f"  2. {b} × {y} = {b * y}.",
                 f"  3. {a * x} + {b * y} = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(row × column = multiply matching entries, then add)")


def gen_determinant(rng):
    a, b, c, d = (rng.randint(1, 8) for _ in range(4))
    det = a * d - b * c
    p = f"M = [{a} {b}; {c} {d}] (rows separated by ';'). What is the determinant of M?"
    card = _card("DETERMINANT OF A 2×2 MATRIX", p, det,
                 "  det = a×d − b×c (main diagonal minus the other diagonal)",
                 f"  1. {a} × {d} = {a * d}.",
                 f"  2. {b} × {c} = {b * c}.",
                 f"  3. {a * d} − {b * c} = {det}.")
    return ("int", "int_exact", p, str(det), None, card,
            "(det = a×d − b×c)")


def gen_spanning_tree_edges(rng):
    n = rng.choice([5, 6, 7, 8, 10])
    p = (f"A network has {n} towns. A spanning tree connects all of them with no loops. "
         "How many edges does the spanning tree have?")
    ans = n - 1
    card = _card("EDGES IN A SPANNING TREE", p, ans,
                 "  A spanning tree on n vertices always has n − 1 edges",
                 f"  1. n = {n}.",
                 f"  2. {n} − 1 = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(spanning tree edges = n − 1)")


def gen_eulerian_trail(rng):
    odd = rng.choice([0, 2, 4])
    stem = (f"A network's vertices have {odd} vertices of ODD degree. "
            "Can you walk every edge exactly once (an Eulerian trail)?")
    if odd == 0:
        correct = "Yes — and you can finish where you started"
    elif odd == 2:
        correct = "Yes — starting and ending at the two odd vertices"
    else:
        correct = "No — more than two odd vertices makes it impossible"
    pool = [
        "Yes — and you can finish where you started",
        "Yes — starting and ending at the two odd vertices",
        "No — more than two odd vertices makes it impossible",
        "Only if the network has no loops",
    ]
    choices = [correct] + [c for c in pool if c != correct][:3]
    rng.shuffle(choices)
    letter = "ABCD"[choices.index(correct)]
    card = _card("EULERIAN TRAILS", stem, correct,
                 "  Rule: 0 odd vertices = closed trail · exactly 2 = open trail · more = impossible",
                 f"  1. This network has {odd} odd vertices.",
                 f"  2. So: {correct}.")
    return ("mc4", "mc_choice", stem, letter, tuple(choices), card)


def gen_best_fit_prediction(rng):
    m = rng.choice([2, 3, 5])
    c = rng.choice([10, 20, 40])
    x = rng.choice([4, 6, 8, 10])
    y = m * x + c
    p = (f"A line of best fit is: cost = {m} × hours + {c}. "
         f"Predict the cost for {x} hours.")
    card = _card("PREDICTING WITH A LINE OF BEST FIT", p, y,
                 "  Substitute the known value into the best-fit rule",
                 f"  1. {m} × {x} = {m * x}.",
                 f"  2. {m * x} + {c} = {y}.")
    return ("int", "int_exact", p, str(y), None, card)


def gen_residual(rng):
    predicted = rng.choice([40, 50, 60, 70])
    diff = rng.choice([-6, -4, -3, 3, 4, 6])
    actual = predicted + diff
    p = (f"A model predicted {predicted}, the actual value was {actual}. "
         "What is the residual (actual − predicted)?")
    card = _card("RESIDUAL", p, diff,
                 "  Residual = actual − predicted",
                 f"  1. {actual} − {predicted} = {diff}.",
                 "  2. Positive = the model under-predicted; negative = over-predicted.")
    return ("int", "int_exact", p, str(diff), None, card,
            "(Residual = actual − predicted)")


def gen_reducing_balance(rng):
    balance = rng.choice([1000, 2000, 4000])
    rate = rng.choice([1, 2])
    payment = rng.choice([200, 250, 300])
    interest = balance * rate // 100
    new_balance = balance + interest - payment
    p = (f"A loan balance is ${balance}. This month {rate}% interest is added, "
         f"then a ${payment} payment is made. What is the new balance, in dollars?")
    card = _card("REDUCING-BALANCE LOAN (ONE MONTH)", p, new_balance,
                 "  New balance = old balance + interest − payment",
                 f"  1. Interest: {balance} × {rate} ÷ 100 = {interest}.",
                 f"  2. {balance} + {interest} − {payment} = {new_balance}.")
    return ("int", "int_exact", p, str(new_balance), None, card,
            "(New balance = old balance + interest − payment)")


def gen_inflation_price(rng):
    # Prices divisible by 100 keep every rate exact -- the first draft's $50 at
    # 5% truncated to "5250 ÷ 100 = 52" and the claim sweep flagged the card.
    price = rng.choice([100, 200, 300])
    rate = rng.choice([10, 20, 5])
    ans = price * (100 + rate) // 100
    p = (f"Inflation is {rate}% this year. Something costing ${price} now will cost "
         "how many dollars after one year of that inflation?")
    card = _card("INFLATION-ADJUSTED PRICE", p, ans,
                 "  New price = old price × (100 + inflation rate) ÷ 100",
                 f"  1. {price} × {100 + rate} = {price * (100 + rate)}.",
                 f"  2. {price * (100 + rate)} ÷ 100 = {ans}.")
    return ("int", "int_exact", p, str(ans), None, card,
            "(New price = old price × (100 + rate) ÷ 100)")


AU_GENERAL_Y12_GENERATORS = {
    "au12g_arithmetic_series_sum": gen_arithmetic_series_sum,
    "au12g_growth_application": gen_growth_application,
    "au12g_matrix_product_entry": gen_matrix_product_entry,
    "au12g_determinant": gen_determinant,
    "au12g_spanning_tree_edges": gen_spanning_tree_edges,
    "au12g_eulerian_trail": gen_eulerian_trail,
    "au12g_best_fit_prediction": gen_best_fit_prediction,
    "au12g_residual": gen_residual,
    "au12g_reducing_balance": gen_reducing_balance,
    "au12g_inflation_price": gen_inflation_price,
}
