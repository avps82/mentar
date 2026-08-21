"""Parametric item generator (Option B) — infinite, non-repeating checkable items.

Where the authored item bank (Option A, engine/itembank.py) is a finite list, this generates
fresh (problem, answer) items on demand with constrained random numbers and a computed
ground truth. The verifier stays authoritative; the LLM stays out of the correctness path.

Each generator returns an `Item` identical in shape to the bank's, so an `ItemGenerator`
duck-types `ItemBank` (`has` / `sample` / `example`) and is a drop-in for
`SessionController(item_bank=...)`.  `CompositeItemSource` chains a generator with the authored
bank so conceptual nodes the generator can't parametrise (e.g. equal-vs-unequal parts) still
get authored items.

Year-4 pilot scope: answers stay within the deterministic verifier's grammar (int / proper
fraction); fraction answers are intentionally left UNREDUCED — `fraction_equiv` accepts any
equivalent form, so the child may reduce or not.
"""

from __future__ import annotations

import random
from collections import deque
from collections.abc import Callable

from mentar.engine.itembank import Item

# A generator: rng -> (answer_type, checker, problem, answer)
# mc4 generators may return a 5-tuple instead: (answer_type, checker, STEM,
# answer, choices) -- the 3rd element is the question WITHOUT inline "A) ..."
# options (R2.1); compose_mc_problem() builds the full inline form centrally,
# once, for CLI/transcript surfaces (the web view shows the stem + radios).
# 4-tuple (answer_type, checker, problem/stem, answer) is the baseline every
# generator supports; a 5th element (mc4 structured choices) and/or a 6th
# (explain-mode method_steps, 2026-08-12) are optional extensions ItemGenerator
# ._make reads positionally -- see its docstring for the exact contract.
GenFn = Callable[[random.Random], tuple]

_LETTERS = "ABCD"


def compose_mc_problem(stem: str, choices: tuple[str, ...] | list[str]) -> str:
    """The single place that builds inline "A) … B) …" mc problem text — used
    by every mc generator via ItemGenerator._make, so CLI/transcript output
    (which has no radio buttons) still gets the full readable question."""
    opts = "  ".join(f"{ltr}) {opt}" for ltr, opt in zip(_LETTERS, choices, strict=True))
    return f"{stem} {opts}. Answer with the letter."


def mc_which_is(
    rng: random.Random, prompt: str, classes: dict[str, list[str]], *,
    glosses: dict[str, str] | None = None, concept_name: str | None = None,
):
    """Build a "Which of these is a <label>?"-shaped MC item from a
    {label: [members]} table. One correct member of a randomly chosen target
    label + three distractors drawn from the OTHER labels (classes are
    disjoint, so distractors are always wrong). Shared by science_items.py
    and practice_items.py -- any fact table with disjoint categories fits
    this shape (animal classes, states of matter, synonyms, rhymes...).

    `glosses`/`concept_name` (explain-mode, 2026-08-12, Type 4 — see
    docs/design/explain_mode_design.md §3): OPTIONAL, and independent of every
    existing call site (all still pass neither -- item.method_steps stays
    None, zero behaviour change). When BOTH are given, a Type-4 "fact in
    category" card is built: the concept's textbook name (rule: name the
    concept), the correct member's category + a one-line "because" gloss, and
    every distractor's TRUE category (built from a member->label reverse
    index, correct for any number of labels -- not just the common
    2-category case). `glosses` keys are category labels, not members: most
    fact tables only need one gloss per label, since the reason a member
    belongs to a category is usually shared across the whole category."""
    labels = list(classes)
    target = rng.choice(labels)
    correct = rng.choice(classes[target])
    pool = [m for lbl in labels if lbl != target for m in classes[lbl]]
    distractors = rng.sample(pool, 3)
    options = [*distractors, correct]
    rng.shuffle(options)
    letter = _LETTERS[options.index(correct)]
    stem = prompt.format(label=target)

    method_steps = None
    if glosses is not None and concept_name is not None:
        member_label = {m: lbl for lbl, members in classes.items() for m in members}
        gloss = glosses.get(target, "")
        why = f" ({gloss})" if gloss else ""
        # One line PER distractor (maintainer, 2026-08-20: "bit more space or
        # divider btw each option because it's not clear if they're together
        # or not") -- the old single "a · b · c" line ran the options together.
        other_lines = tuple(f"    {d} → {member_label[d]}" for d in distractors)
        method_steps = (
            concept_name,
            f"{stem} → {correct}",
            f"  {correct} → {target}{why}",
            "  The others:",
            *other_lines,
            # Every explain card ends by naming the answer (maintainer,
            # 2026-08-16). The numeric families already did; this "fact in
            # category" shape carried the answer only on the stem line, after a
            # → and ahead of two more lines. That is hardest to read exactly
            # where the options are whole sentences -- English, which is where
            # it was reported: "Which of these is a complex sentence? → She
            # writes poetry because it calms her." then two further lines each
            # containing other sentences and arrows.
            f"  Answer: {correct}",
        )

    # 3rd element is the STEM (no inline "A) ..." options — R2.1: the web view
    # shows stem + radios, the inline form is composed centrally for CLI/
    # transcript by ItemGenerator._make via compose_mc_problem() above.
    # 5th element: structured choices (A/B/C/D order) for the radio buttons.
    # 6th element: the Type-4 method card above, or None.
    return ("mc4", "mc_choice", stem, letter, options, method_steps)

_THINGS = ["stickers", "crayons", "grapes", "marbles", "sweets", "pencils", "apples", "cookies"]
_GROUPS = ["children", "friends", "baskets", "boxes", "bags", "plates", "pots"]
_WHOLES = ["a cake", "a pizza", "a chocolate bar", "a ribbon", "a pie"]

# One simple, kid-friendly emoji per noun — shown ONCE next to the word (not one
# icon per item; testing note 1). Emoji are plain Unicode, no external assets.
_THING_EMOJI = {
    "stickers": "⭐", "crayons": "🖍️", "grapes": "🍇", "marbles": "🔵",
    "sweets": "🍬", "pencils": "✏️", "apples": "🍎", "cookies": "🍪",
}
_WHOLE_EMOJI = {
    "a cake": "🍰", "a pizza": "🍕", "a chocolate bar": "🍫", "a ribbon": "🎀", "a pie": "🥧",
}


def _thing_with_icon(thing: str) -> str:
    icon = _THING_EMOJI.get(thing, "")
    return f"{thing} {icon}".strip()


def _whole_with_icon(whole: str) -> str:
    icon = _WHOLE_EMOJI.get(whole, "")
    return f"{whole.capitalize()} {icon}".strip()


def _equal_groups_diagram(groups: int, each: int, label: str) -> tuple[str, ...]:
    """`groups` boxes of `each` dots -- the picture for a sharing/division word
    problem, built from THIS item's numbers.

    maths/division_word_problems.md carries this shape with "12 apples shared
    between 3 children" baked in, which is a different question from whatever
    the item drew (see the 2026-08-16 place-value note in au_items). Word
    problems get no step grid either -- build_steps_grid only fires on
    "What is a x b?" forms -- so without this they have no picture at all.

    Capped: the generator draws at most 6 groups of 9, so the widest line is
    well inside a phone's monospace width.
    """
    if groups < 1 or each < 1 or groups > 8 or each > 10:
        return ()
    boxes = " ".join("[" + "●" * each + "]" for _ in range(groups))
    return (boxes, f"{groups} {label} · {each} each")


def _gen_whole_number_division(rng: random.Random):
    b = rng.randint(2, 6)          # groups
    q = rng.randint(2, 9)          # each gets
    a = b * q                      # total (divisible -> clean int answer)
    thing, who = rng.choice(_THINGS), rng.choice(_GROUPS)
    problem = (f"Share {a} {_thing_with_icon(thing)} equally among {b} {who}. "
               f"How many {thing} does each get?")
    card = (
        "SHARING EQUALLY (DIVISION)",
        f"{problem} → {q}",
        f"  1. Sharing equally means dividing: {a} ÷ {b}.",
        f"  2. Think \"how many {b}s make {a}?\" — {b} × {q} = {a}.",
        f"  3. So each of the {b} {who} gets {q}.",
        f"  Answer: {q}",
        "",
        *_equal_groups_diagram(b, q, who),
    )
    return ("int", "int_exact", problem, str(q), None, card)


def _fraction_bar(numerator: int, denominator: int, summary: bool = True) -> tuple[str, ...]:
    """A bar of `denominator` cells with `numerator` shaded -- the picture for
    THIS fraction.

    maths/fractions.md carries this shape with 1/2 and 2/4 baked in, a different
    fraction from whatever the item drew.

    TWO characters a cell, not four (fixed 2026-08-21). The old width claimed in
    this docstring to "stay inside a phone's monospace width" was measured and
    did not: at 15.2px monospace only ~35 characters fit a 360px screen, and a
    4-wide cell put d=8 at 41 and d=10 at 51. The bar then scrolled sideways --
    and a fraction bar you cannot see all of at once is exactly the picture that
    stops working, because comparing the parts IS the point. At 2 wide, d=10 is
    31 characters and fits. Verified in chromium, not asserted.

    `summary=False` drops the trailing "... = 1/3" line. That line is right on
    the CARD (shown after an attempt) and fatal on the QUESTION (shown while the
    child is still thinking) -- it states the answer. Every renderer used
    question-side must be able to withhold it; see docs/design/visual_first_gap.md
    and the give-away guard in tests/engine/test_visuals.py.
    """
    if denominator < 1 or denominator > 12 or not 0 <= numerator <= denominator:
        return ()
    cells = "|" + "|".join("██" if i < numerator else "  " for i in range(denominator)) + "|"
    if not summary:
        return (cells,)
    return (cells, f"{numerator} of {denominator} equal parts shaded = {numerator}/{denominator}")


def _gen_unit_fractions(rng: random.Random):
    d = rng.randint(2, 10)
    whole = rng.choice(_WHOLES)
    problem = f"{_whole_with_icon(whole)} is split into {d} equal parts. What fraction is ONE part?"
    card = (
        "UNIT FRACTIONS",
        f"{problem} → 1/{d}",
        f"  1. The whole is cut into {d} equal parts, so {d} is the DENOMINATOR (the bottom).",
        "  2. You are asked about ONE part, so 1 is the numerator (the top).",
        f"  Answer: 1/{d}",
        "",
        *_fraction_bar(1, d),
    )
    # The picture goes on the QUESTION too (visual-first, 2026-08-21), without
    # its summary line -- the bar shows one part of d shaded; naming that as a
    # fraction is the skill, and "= 1/d" underneath would hand it over.
    return ("fraction", "fraction_equiv", problem, f"1/{d}", None, card, None,
            _fraction_bar(1, d, summary=False))


def _gen_fraction_as_part_of_whole(rng: random.Random):
    d = rng.randint(3, 10)
    n = rng.randint(1, d - 1)
    whole = rng.choice(_WHOLES)
    problem = (f"{_whole_with_icon(whole)} is cut into {d} equal slices and you take {n}. "
               f"What fraction did you take?")
    card = (
        "A FRACTION OF A WHOLE",
        f"{problem} → {n}/{d}",
        f"  1. Bottom number = how many equal parts the whole was cut into: {d}.",
        f"  2. Top number = how many of those parts you have: {n}.",
        f"  Answer: {n}/{d}",
        "",
        *_fraction_bar(n, d),
    )
    return ("fraction", "fraction_equiv", problem, f"{n}/{d}", None, card)


def _gen_equivalent_fractions(rng: random.Random):
    d = rng.randint(2, 6)
    n = rng.randint(1, d - 1)
    k = rng.randint(2, 4)
    problem = f"Write a fraction equal to {n}/{d} but with denominator {d * k}."
    card = (
        "EQUIVALENT FRACTIONS",
        f"{problem} → {n * k}/{d * k}",
        f"  1. What times {d} gives {d * k}?  {d} × {k} = {d * k}.",
        f"  2. Whatever you do to the bottom, do to the top: {n} × {k} = {n * k}.",
        f"  3. {n}/{d} and {n * k}/{d * k} are the same amount, written differently.",
        f"  Answer: {n * k}/{d * k}",
    )
    return ("fraction", "fraction_equiv", problem, f"{n * k}/{d * k}", None, card)


def _gen_adding_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a = rng.randint(1, d - 1)
    b = rng.randint(1, d - a)      # a + b <= d  -> proper (<= 1 whole)
    problem = f"What is {a}/{d} + {b}/{d}?"
    card = (
        "ADDING FRACTIONS WITH THE SAME DENOMINATOR",
        f"{problem} → {a + b}/{d}",
        f"  1. The parts are the same size ({d}ths), so they can be added directly.",
        f"  2. Add the TOP numbers only: {a} + {b} = {a + b}.",
        f"  3. The bottom stays {d} — the size of each part has not changed.",
        f"  Answer: {a + b}/{d}",
    )
    return ("fraction", "fraction_equiv", problem, f"{a + b}/{d}", None, card)


def _gen_subtracting_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a = rng.randint(2, d - 1)
    b = rng.randint(1, a - 1)      # a > b -> positive result
    problem = f"What is {a}/{d} - {b}/{d}?"
    card = (
        "SUBTRACTING FRACTIONS WITH THE SAME DENOMINATOR",
        f"{problem} → {a - b}/{d}",
        f"  1. Same-size parts ({d}ths), so subtract directly.",
        f"  2. Subtract the TOP numbers only: {a} - {b} = {a - b}.",
        f"  3. The bottom stays {d}.",
        f"  Answer: {a - b}/{d}",
    )
    return ("fraction", "fraction_equiv", problem, f"{a - b}/{d}", None, card)


def _gen_comparing_equal_denom(rng: random.Random):
    d = rng.randint(3, 10)
    a, b = rng.sample(range(1, d), 2)   # distinct numerators
    hi = max(a, b)
    problem = f"Which is bigger: {a}/{d} or {b}/{d}? Give the bigger fraction."
    card = (
        "COMPARING FRACTIONS WITH THE SAME DENOMINATOR",
        f"{problem} → {hi}/{d}",
        f"  1. Both are {d}ths, so every part is the same size.",
        f"  2. With equal-sized parts, more parts means more: {max(a, b)} > {min(a, b)}.",
        f"  Answer: {hi}/{d}",
    )
    return ("fraction", "fraction_equiv", problem, f"{hi}/{d}", None, card)


# ── Maths: whole-number arithmetic (subject = mathematics, beyond fractions) ──

def _gen_multiplication(rng: random.Random):
    a, b = rng.randint(2, 9), rng.randint(2, 9)
    return ("int", "int_exact", f"What is {a} × {b}?", str(a * b))


def _gen_addition(rng: random.Random):
    a, b = rng.randint(10, 99), rng.randint(10, 99)
    return ("int", "int_exact", f"What is {a} + {b}?", str(a + b))


def _gen_subtraction(rng: random.Random):
    a = rng.randint(20, 99)
    b = rng.randint(1, a - 1)          # positive result
    return ("int", "int_exact", f"What is {a} − {b}?", str(a - b))


# Registry — node_id -> generator. Conceptual/visual nodes (equal_vs_unequal_parts) are
# intentionally absent; CompositeItemSource falls back to the authored bank for those.
DEFAULT_GENERATORS: dict[str, GenFn] = {
    "whole_number_division": _gen_whole_number_division,
    "unit_fractions": _gen_unit_fractions,
    "fraction_as_part_of_whole": _gen_fraction_as_part_of_whole,
    "equivalent_fractions": _gen_equivalent_fractions,
    "adding_equal_denom": _gen_adding_equal_denom,
    "subtracting_equal_denom": _gen_subtracting_equal_denom,
    "comparing_equal_denom": _gen_comparing_equal_denom,
}

# Maths arithmetic subject (separate curriculum) — node_id -> generator.
ARITHMETIC_GENERATORS: dict[str, GenFn] = {
    "addition": _gen_addition,
    "subtraction": _gen_subtraction,
    "multiplication": _gen_multiplication,
}


def _dedup_key(item: Item) -> str:
    """What sample()'s no-repeat window treats as "the same question".

    Keyed on the STEM for mc4: the same question with reshuffled distractors is
    still exactly the same question to the child.

    The PICTURE is part of the identity (2026-08-21). A visual item's prose is
    often identical across draws -- "What is the area of the shaded shape?" --
    while only the picture changes, so keying on prose alone made every draw
    look like a repeat: the window burned all 8 re-rolls, served the last roll
    anyway, and the no-repeat guarantee was silently dead for exactly the
    questions that most need variety (measured, not theorised).

    Deliberately NOT "skip dedup when there is a picture": small-domain visual
    generators genuinely repeat (a clock face has 12 hour positions), which is
    the 2026-08-14 defect this window exists for. Two draws sharing prose AND
    picture really are the same question, so the original guarantee is kept.

    Accepted consequence: a scatterplot node may repeat its ANSWER ("positive")
    across draws while the plotted points differ. That is correct -- reading a
    NEW plot is the skill -- so it must not be "fixed" later.
    """
    base = item.stem or item.problem
    return base if not item.visual else base + "\n" + "\n".join(item.visual)


class ItemGenerator:
    """Generates fresh checkable items per node. Duck-types ItemBank (has/sample/example)."""

    def __init__(self, generators: dict[str, GenFn] | None = None,
                 rng: random.Random | None = None) -> None:
        self._gens = generators if generators is not None else DEFAULT_GENERATORS
        self._rng = rng or random.Random()
        self._recent: dict[str, deque[str]] = {}  # per-node no-repeat window (see sample)

    def has(self, node_id: str) -> bool:
        return node_id in self._gens

    def _make(self, node_id: str) -> Item | None:
        gen = self._gens.get(node_id)
        if gen is None:
            return None
        result = gen(self._rng)
        answer_type, checker, third, answer = result[:4]
        # mc generators return a 5th element (the structured choice texts, A/B/C/D
        # order) -- when present, `third` is the STEM (no inline options) and the
        # full inline problem is composed centrally (R2.1); 4-tuples are unaffected.
        choices = tuple(result[4]) if len(result) > 4 and result[4] else None
        stem = third if choices else None
        problem = compose_mc_problem(third, choices) if choices else third
        # explain-mode (2026-08-12): an optional 6th element -- a migrated
        # generator's computed method card, one line per step. Position 4 is
        # already choices' slot (present-or-None for EVERY migrated generator,
        # mc4 or not), so this is always unambiguous: a non-mc4 generator that
        # wants a card explicitly passes None at index 4.
        method_steps = tuple(result[5]) if len(result) > 5 and result[5] else None
        # A 7th element (2026-08-19): a per-item answer-format hint, used by
        # formula questions to put the FORMULA in the cue slot. Same
        # present-or-None positional rule as choices/method_steps above.
        format_hint = result[6] if len(result) > 6 and result[6] else None
        # An 8th element (2026-08-21, visual-first): the picture for THIS item,
        # shown beneath the question text. Same present-or-None positional rule again.
        # Item is frozen, so this must be a tuple, not the caller's list.
        #
        # EIGHT IS THE CEILING. This positional contract is readable at 8 slots
        # and not at 9 -- if a 9th is ever wanted, that is the signal to move
        # GenFn to a keyword builder rather than count commas one more time.
        visual = tuple(result[7]) if len(result) > 7 and result[7] else None
        return Item(
            id=f"gen-{node_id}-{self._rng.randrange(10 ** 9)}",
            node=node_id, problem=problem, answer=answer,
            answer_type=answer_type, checker=checker, choices=choices, stem=stem,
            method_steps=method_steps, format_hint=format_hint, visual=visual,
        )

    _NO_REPEAT_WINDOW = 8  # remember this many recent problems per node

    def sample(self, node_id: str) -> Item | None:
        """A fresh item, avoiding the last _NO_REPEAT_WINDOW problems for this node.

        2026-08-14: a small-domain generator (e.g. an mc_which_is synonym set with a
        handful of targets) draws with replacement, so "Which word means the SAME as
        'happy'?" came up twice in one 10-question session. Re-roll a few times against
        a bounded recent-window instead: once the domain really is that small, a repeat
        is unavoidable and we serve it rather than loop.
        """
        recent = self._recent.setdefault(node_id, deque(maxlen=self._NO_REPEAT_WINDOW))
        item = None
        for _ in range(self._NO_REPEAT_WINDOW):
            item = self._make(node_id)
            if item is None or _dedup_key(item) not in recent:
                break
        if item is not None:
            recent.append(_dedup_key(item))
        return item

    def example(self, node_id: str, exclude_id: str | None = None) -> Item | None:
        # Doesn't consume/record — an example must not push a live question out of
        # the no-repeat window. exclude_id is irrelevant (ids are unique per draw).
        return self._make(node_id)


class CompositeItemSource:
    """Chain item sources: first source that `has` a node serves it.

    Typical use: CompositeItemSource(generator, authored_bank) — generator for parametrisable
    nodes, authored bank for conceptual ones.
    """

    def __init__(self, *sources) -> None:
        self._sources = [s for s in sources if s is not None]

    def _for(self, node_id: str):
        for s in self._sources:
            if s.has(node_id):
                return s
        return None

    def has(self, node_id: str) -> bool:
        return self._for(node_id) is not None

    def sample(self, node_id: str):
        s = self._for(node_id)
        return s.sample(node_id) if s else None

    def example(self, node_id: str, exclude_id: str | None = None):
        s = self._for(node_id)
        return s.example(node_id, exclude_id=exclude_id) if s else None


def default_item_generator(rng: random.Random | None = None) -> ItemGenerator:
    return ItemGenerator(rng=rng)


def build_item_source(mode: str, bank=None, rng: random.Random | None = None):
    """Build the checkable-item source for the controller from a config `item_source`.

    mode:
      "composite" (default) — generator for parametrisable nodes, authored bank for the rest.
      "generator"           — parametric only (conceptual nodes fall through to the LLM path).
      "bank"                — authored bank only (Option A).
    Returns an object with has/sample/example, or None when nothing is available.
    """
    mode = (mode or "composite").lower()
    if mode == "bank":
        return bank
    gen = default_item_generator(rng=rng)
    if mode == "generator":
        return gen
    # composite (default): generator first, authored bank as fallback
    return CompositeItemSource(gen, bank) if bank is not None else gen
