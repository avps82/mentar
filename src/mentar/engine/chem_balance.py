"""Chemical-equation balancing — thin owned glue over sympy (no chempy).

Why this exists INSTEAD of chempy (2026-08-11, maintainer decision "keep it
minimal... see if the core is enough"): chempy's balance_stoichiometry() was
the one function the chemistry wave needed, but chempy's HARD requirements
(not extras) include matplotlib, pyneqsys/pyodesys (the ODE stack) and
dot2tex — an unacceptable transitive tree for a family install. Balancing
itself is textbook linear algebra: the nullspace of the element-count matrix.
sympy (already a core dependency, B0) does that exactly; this module is only
the parsing + scaling glue around it — the house dependency philosophy's
"own the thin glue" case, not hand-rolling a solved problem.

Validated at adoption time against chempy's own output on a 10-equation
education-level battery (combustion, synthesis, decomposition, neutralization
with parenthesized formulas, photosynthesis) — byte-identical coefficients on
all 10; both refusal cases below returned None where appropriate.

Safety posture (same as every verifier path): computed ground truth, exact
rational arithmetic (no float), STRICT formula parsing (unknown syntax raises,
it is never guessed), and refusal over guessing — a non-unique or impossible
balance returns None rather than a "best effort" wrong equation.

ponytail: neutral molecules only — no ionic charge balancing (Y11+ redox
half-equations). The upgrade path is one more conservation row (net charge)
in the matrix, not a new dependency; add it when ionic content is authored.
"""

from __future__ import annotations

import re
from functools import reduce
from math import gcd

# One token of a formula: an element symbol with optional count, or a
# parenthesis with optional group count. Strict by construction — anything
# this regex can't consume raises, so a typo'd formula fails loudly at
# authoring/test time, never silently mis-balances at runtime.
_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)|(\()|(\))(\d*)")


def parse_formula(formula: str) -> dict[str, int]:
    """"C6H6" / "Ca(OH)2" / "Fe2O3" -> {element: count}. Raises ValueError on
    anything that isn't a well-formed neutral molecular formula."""
    if not formula or not formula.strip():
        raise ValueError("empty formula")
    stack: list[dict[str, int]] = [{}]
    i = 0
    while i < len(formula):
        m = _FORMULA_TOKEN.match(formula, i)
        if not m or m.start() != i or m.end() == i:
            raise ValueError(f"bad formula syntax at {formula[i:]!r}")
        elem, count, open_p, close_p, close_mult = m.groups()
        if elem:
            stack[-1][elem] = stack[-1].get(elem, 0) + (int(count) if count else 1)
        elif open_p:
            stack.append({})
        elif close_p:
            if len(stack) < 2:
                raise ValueError(f"unbalanced ')' in {formula!r}")
            group = stack.pop()
            mult = int(close_mult) if close_mult else 1
            for e, n in group.items():
                stack[-1][e] = stack[-1].get(e, 0) + n * mult
        i = m.end()
    if len(stack) != 1:
        raise ValueError(f"unbalanced '(' in {formula!r}")
    if not stack[0]:
        raise ValueError(f"no elements in {formula!r}")
    return stack[0]


def balance_equation(
    reactants: list[str], products: list[str]
) -> tuple[dict[str, int], dict[str, int]] | None:
    """Smallest positive-integer coefficients balancing reactants -> products,
    or None when no unique valid balance exists (refusal over guessing).

    sympy is imported lazily (same pattern as verify_numeric's expression
    path) so this module imports without it; callers treat an ImportError
    the same as any other unavailability.
    """
    import sympy

    species = list(reactants) + list(products)
    counts = [parse_formula(f) for f in species]  # raises on a bad formula
    elements = sorted({e for c in counts for e in c})
    n_reac = len(reactants)
    # Rows = elements, columns = species. Reactant counts positive, product
    # counts negative: a balanced equation is exactly a nullspace vector.
    mat = sympy.Matrix([
        [counts[j].get(e, 0) * (1 if j < n_reac else -1) for j in range(len(species))]
        for e in elements
    ])
    null = mat.nullspace()
    if len(null) != 1:
        return None  # impossible (0) or non-unique (2+): refuse, never guess
    vec = null[0]
    scale = sympy.lcm([sympy.fraction(x)[1] for x in vec])
    coeffs = [int(x * scale) for x in vec]
    if coeffs[0] < 0:
        coeffs = [-c for c in coeffs]
    if any(c <= 0 for c in coeffs):
        return None  # a zero/negative coefficient is not a valid reaction split
    g = reduce(gcd, coeffs)
    coeffs = [c // g for c in coeffs]
    return (
        dict(zip(reactants, coeffs[:n_reac], strict=True)),
        dict(zip(products, coeffs[n_reac:], strict=True)),
    )
