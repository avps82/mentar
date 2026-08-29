

def test_a_bare_algebraic_symbol_is_unwrapped_but_money_survives():
    """Seen with a live model on Year 12 algebra (2026-08-29): "The $y$ terms
    are like the cars." reached the screen. The unwrap guard required a maths
    OPERATOR inside the dollars — a guard that exists so prices survive — and a
    lone variable has none, so LaTeX leaked to a child.

    Money is always $<digits>, so a short letter-led token cannot be a price.
    """
    from mentar.dialogue.controller import _normalise_llm_math as norm

    assert norm("The $y$ terms are like the cars.") == "The y terms are like the cars."
    assert norm("Look at the $x$ and $y$ terms.") == "Look at the x and y terms."
    assert norm("The $x2$ term") == "The x2 term"
    assert norm("so $2 × 10 = 20$ joules") == "so 2 × 10 = 20 joules"
    # ...and the prices the guard was built for are untouched:
    assert norm("between $5 and $8") == "between $5 and $8"
    assert norm("$130 increases by 20%") == "$130 increases by 20%"
    assert norm("It costs $5 and $8 for two.") == "It costs $5 and $8 for two."
