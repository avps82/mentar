"""BKT per-turn mastery update — cold-start priors + hinted-win discount.

Spec: docs/SPEC.md §11 (Mastery / BKT), §13.2 (hinted-win); docs/design/W3.3_bkt.md.
Tests: docs/TESTS.md T3.3.

This is Mentar's own deterministic BKT recurrence (Corbett & Anderson 1995),
used for the per-turn update in the session FSM `bkt_update` state. pyBKT is NOT
called here: it cannot fit parameters from one learner's cold-start (W3.3), so it
is reserved for OFFLINE parameter fitting post-pilot (N >= 100 scored responses
per skill, flipping skill_state.prior_mode -> 0). See design doc §1.

stdlib-only, pure, side-effect-free: the caller persists the result via
store.update_skill_state(). No DB, no I/O, no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass

# Initial mastery prior for a freshly-fringed concept (design §2). NOT 0.0:
# at exactly 0, no correct answer can ever move mastery (0*(1-slip)/... == 0).
P_L0 = 0.10

# How much a hinted-correct answer is discounted, as a fraction of the gap to a
# pure guess. 0.5 => guess_hinted is a coin-flip's worth of evidence (design §3.1).
# Deliberately strong: over-crediting a hinted win is the dangerous direction.
HINT_DISCOUNT = 0.5

# Node-class defaults keyed by verifier.answer_type (design §2). Template
# `bkt_priors:` overrides these per node.
_CLASS_DEFAULTS = {
    "mc4":     {"guess": 0.20, "slip": 0.10, "learns": 0.20, "forgets": 0.0},
    "numeric": {"guess": 0.05, "slip": 0.10, "learns": 0.20, "forgets": 0.0},
}
# answer_type -> node class
_NUMERIC_TYPES = frozenset({"int", "decimal", "fraction"})


@dataclass(frozen=True)
class BktParams:
    """Per-skill BKT parameters. forgets is stored for forward-compat; unused in v0."""

    guess: float
    slip: float
    learns: float
    forgets: float = 0.0


def params_for(answer_type: str, overrides: dict | None = None) -> BktParams:
    """Resolve params for a node: template `bkt_priors:` override wins, else the
    class default by answer_type (design §2). `mc4` -> MC default; int/decimal/
    fraction -> numeric default."""
    node_class = "mc4" if answer_type == "mc4" else (
        "numeric" if answer_type in _NUMERIC_TYPES else None
    )
    if node_class is None:
        raise ValueError(f"no BKT prior class for answer_type {answer_type!r}")
    base = dict(_CLASS_DEFAULTS[node_class])
    if overrides:
        base.update({k: v for k, v in overrides.items() if k in base})
    return BktParams(**base)


def _posterior_given_obs(p: float, correct: bool, guess: float, slip: float) -> float:
    """Bayesian conditioning of mastery on one observation (design §3 step a)."""
    if correct:
        num = p * (1.0 - slip)
        den = num + (1.0 - p) * guess
    else:
        num = p * slip
        den = num + (1.0 - p) * (1.0 - guess)
    return num / den if den > 0.0 else p


def bkt_update(
    p_prior: float | None,
    correct: bool,
    hinted: bool,
    params: BktParams,
) -> float:
    """Return the updated p_mastery after one scored observation.

    p_prior is the current skill_state.p_mastery; pass None (or 0.0) for an
    uninitialised skill -> seeded to P_L0 (design §2; regression guard for the
    degenerate-zero bug).

    Hinted-win discount (design §3.1): a *correct* answer after Help uses an
    elevated guess, so it raises mastery strictly less than a cold correct. A
    hinted *incorrect* uses the normal guess (we do not soften a wrong answer).
    """
    p = P_L0 if (p_prior is None or p_prior <= 0.0) else p_prior

    guess_eff = params.guess
    if correct and hinted:
        guess_eff = params.guess + (1.0 - params.guess) * HINT_DISCOUNT

    p_cond = _posterior_given_obs(p, correct, guess_eff, params.slip)
    # learning transition (within-session; forgets unused in v0)
    return p_cond + (1.0 - p_cond) * params.learns
