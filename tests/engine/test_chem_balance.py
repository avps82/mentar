"""Tests for engine/chem_balance.py — sympy-only equation balancing.

The 10-equation battery below was validated byte-identical against chempy's
balance_stoichiometry() at adoption time (2026-08-11) before chempy was
dropped for its transitive weight — these are the pinned expected outputs,
so the owned balancer can never silently drift from the reference.

Inline smoke runner: python3 tests/engine/test_chem_balance.py
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.chem_balance import balance_equation, parse_formula


class TestParseFormula:
    def test_simple(self):
        assert parse_formula("H2O") == {"H": 2, "O": 1}

    def test_multi_letter_element(self):
        assert parse_formula("Fe2O3") == {"Fe": 2, "O": 3}

    def test_parenthesized_group(self):
        assert parse_formula("Ca(OH)2") == {"Ca": 1, "O": 2, "H": 2}

    def test_nested_parens(self):
        assert parse_formula("Mg3(Si2O5)2(OH)2") == {"Mg": 3, "Si": 4, "O": 12, "H": 2}

    def test_bad_syntax_raises(self):
        for bad in ("", "  ", "h2o", "H2O)", "(H2O", "H2O + O2", "123", "H_2O"):
            with pytest.raises(ValueError):
                parse_formula(bad)


class TestBalanceBattery:
    """Pinned against chempy's outputs (see module docstring)."""

    CASES = [
        (["C6H6", "O2"], ["CO2", "H2O"], {"C6H6": 2, "O2": 15}, {"CO2": 12, "H2O": 6}),
        (["H2", "O2"], ["H2O"], {"H2": 2, "O2": 1}, {"H2O": 2}),
        (["CH4", "O2"], ["CO2", "H2O"], {"CH4": 1, "O2": 2}, {"CO2": 1, "H2O": 2}),
        (["Fe", "O2"], ["Fe2O3"], {"Fe": 4, "O2": 3}, {"Fe2O3": 2}),
        (["N2", "H2"], ["NH3"], {"N2": 1, "H2": 3}, {"NH3": 2}),
        (["CO2", "H2O"], ["C6H12O6", "O2"], {"CO2": 6, "H2O": 6}, {"C6H12O6": 1, "O2": 6}),
        (["Ca(OH)2", "HCl"], ["CaCl2", "H2O"], {"Ca(OH)2": 1, "HCl": 2}, {"CaCl2": 1, "H2O": 2}),
        (["KClO3"], ["KCl", "O2"], {"KClO3": 2}, {"KCl": 2, "O2": 3}),
        (["Al", "O2"], ["Al2O3"], {"Al": 4, "O2": 3}, {"Al2O3": 2}),
        (["C3H8", "O2"], ["CO2", "H2O"], {"C3H8": 1, "O2": 5}, {"CO2": 3, "H2O": 4}),
    ]

    def test_battery(self):
        for reac, prod, want_r, want_p in self.CASES:
            got = balance_equation(reac, prod)
            assert got == (want_r, want_p), (reac, prod, got)

    def test_benzene_is_the_july_regression_case(self):
        """The 2026-07-25 chemistry test's equation — phi4-mini reached the right
        answer on fabricated reasoning; this is the computed replacement."""
        got = balance_equation(["C6H6", "O2"], ["CO2", "H2O"])
        assert got == ({"C6H6": 2, "O2": 15}, {"CO2": 12, "H2O": 6})


class TestRefusalOverGuessing:
    """None over a wrong guess — the same posture as every verifier path."""

    def test_impossible_balance(self):
        assert balance_equation(["H2"], ["O2"]) is None

    def test_non_unique_balance(self):
        # Two independent reactions mixed — nullspace dimension 2, refuse.
        assert balance_equation(["C", "O2", "H2"], ["CO2", "H2O", "CH4"]) is None

    def test_bad_formula_raises_not_guesses(self):
        with pytest.raises(ValueError):
            balance_equation(["NotAFormula!"], ["H2O"])


if __name__ == "__main__":
    import inspect
    n = 0
    for cls_name, cls in sorted(globals().items()):
        if inspect.isclass(cls) and cls_name.startswith("Test"):
            inst = cls()
            for name in sorted(dir(inst)):
                if name.startswith("test_"):
                    getattr(inst, name)()
                    n += 1
                    print(f"  ✓ {cls_name}.{name}")
    print(f"\n{n} chem-balance tests passed.")
