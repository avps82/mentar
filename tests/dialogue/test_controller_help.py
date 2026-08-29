import inspect


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


def test_no_prompt_template_ships_an_unsubstituted_slot():
    """Every {{slot}} used by a prompt must be filled by SOME render path.
    system_prompt.md renders through _render_system_prompt, not
    _render_template, so a slot added to one and not the other reaches the
    model as a literal "{{learner_register}}" (caught 2026-08-29)."""
    import pathlib
    import re

    from mentar.dialogue import controller as C

    prompts = pathlib.Path(__file__).resolve().parents[2] / "prompts"
    filled = set()
    for fn in ("_render_template", "_render_system_prompt"):
        src = inspect.getsource(getattr(C.SessionController, fn))
        filled |= set(re.findall(r'\.replace\("\{\{(\w+)\}\}"', src))
    missing = {}
    for f in sorted(prompts.glob("*.md")):
        if f.name == "README.md":
            continue
        for slot in set(re.findall(r"\{\{(\w+)\}\}", f.read_text(encoding="utf-8"))):
            if slot not in filled:
                missing.setdefault(f.name, []).append(slot)
    assert not missing, f"prompt slots no render path fills: {missing}"


def test_the_explanation_register_follows_the_year_level():
    """The pilot's "8-9 years old" was hardcoded in every template, so a Year 12
    student got quadratics explained as sorting a box of toys (seen with a live
    model, 2026-08-29)."""
    from mentar.dialogue.controller import learner_register as reg

    assert "6–7" in reg("Year 1") and "young child" in reg("Year 1")
    assert "9–10" in reg("Year 4")
    assert "14–15" in reg("Year 9") and "never talk down" in reg("Year 9")
    senior = reg("Year 12")
    assert "17–18" in senior and "senior-secondary" in senior
    assert "young child" not in senior, "a Year 12 student is not a young child"
    # other countries' systems
    assert "16–17" in reg("Class 11") and "16–17" in reg("Secondary 4")
    assert "8–9" in reg("Primary 2") and "10–11" in reg("Grade 5")
    # unknown/pilot falls back to the original wording, never a crash
    for unknown in ("pilot", None, "", "Stage 3", "Reception"):
        assert "8–9" in reg(unknown), unknown


def test_python_power_syntax_in_prose_is_not_rendered_as_bold():
    """Models emit "x**2" constantly for algebra, and markdown-lite renders bold
    with the same characters — so a Year 12 explanation showed
    "4x**2 + 3x**2 = 7x**2" with "2 + 3x" in BOLD, mangling the maths (live
    model, 2026-08-29). Converted only when a DIGIT follows, so deliberate bold
    still works; caret not superscript, because the verifier accepts a caret and
    safe-rejects a superscript.
    """
    from mentar.dialogue.controller import _normalise_llm_math as norm

    assert norm("4x**2 + 3x**2 = 7x**2") == "4x^2 + 3x^2 = 7x^2"
    assert norm("A term like x**2 differs from x") == "A term like x^2 differs from x"
    # deliberate emphasis is untouched, even beside a power
    assert norm("This is **important**.") == "This is **important**."
    assert norm("The **key idea** is x**2 vs x") == "The **key idea** is x^2 vs x"
