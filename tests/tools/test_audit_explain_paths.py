"""tools/audit_explain_paths.py — the explain-path auditor.

The tool itself is a REPORTER, not a gate: there is no correct number of
prose-only nodes to assert (English and science are 100% prose by construction).
So these tests lock the invariants that ARE meaningful, and guard the tool
against silently measuring nothing.

    python3 tests/tools/test_audit_explain_paths.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.tools import audit_explain_paths as auditor  # noqa: E402

# 40 draws is plenty for these invariants and keeps the suite fast; the tool's
# own default (200) is sized to expose a 1%-eligibility node, which is a
# reporting concern, not something asserted here.
auditor.DRAWS = 40
_ROWS = auditor.audit()
_NODES = [r for r in _ROWS if "error" not in r]


def test_every_template_loads_and_resolves_its_item_source():
    errors = [r for r in _ROWS if "error" in r]
    assert errors == [], f"templates failed to audit: {errors}"


def test_the_auditor_actually_covers_the_corpus():
    """Guards against the tool silently scanning nothing, which would make
    every other assertion here vacuously true."""
    assert len(_NODES) > 300, f"expected the full corpus, audited {len(_NODES)}"
    assert len({r["template"] for r in _NODES}) > 60


def test_every_node_produces_an_item_on_every_draw():
    """A node whose generator can return None would show the child an empty
    question. Cheap to check here across the whole corpus."""
    broken = [(r["node"], r["no_item"]) for r in _NODES if r["no_item"]]
    assert broken == [], f"nodes failed to produce an item: {broken}"


def test_every_node_routes_to_a_visual_scaffold():
    unscaffolded = [(r["node"], r["label"]) for r in _NODES if not r["scaffold"]]
    assert unscaffolded == [], f"nodes with no scaffold hint: {unscaffolded}"


def test_no_node_is_draw_dependent():
    """Regression gate on the real user-visible symptom: a node that shows a
    step-grid on some draws and prose on others, purely by chance.

    Phases A+B took this 16 -> 4, and Phase C closed the last 4 the same day,
    so the correct assertion is now EMPTY. Any node appearing here means new
    content has reintroduced the inconsistency."""
    partial = sorted(r["node"] for r in _NODES if 0 < r["grid_pct"] < 100)
    assert partial == [], (
        "a node became draw-dependent again -- the same concept now shows a step "
        f"grid on some draws and prose on others: {partial}"
    )


def test_decimal_and_signed_multiplication_are_no_longer_draw_dependent():
    """Phases A+B specifically. Named separately from the test above so a
    regression here reports the cause, not just a changed list."""
    for stem in ("mult_decimals", "mult_decimal_by_decimal", "negative_multiplication",
                 "integers_add_sub"):
        rows = [r for r in _NODES if r["node"].endswith(stem)]
        assert rows, f"no nodes matched {stem!r} — did the node ids change?"
        for r in rows:
            assert r["grid_pct"] == 100, (
                f"{r['node']} is {r['grid_pct']}% step-grid eligible; "
                f"Phases A/B/C should make it 100% (sample: {r['sample']!r})"
            )


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
