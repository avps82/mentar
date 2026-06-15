"""Tests for the source/anchor scope guard in mentar.grounding.source_map.

Contract checks:
    - vikidia node with vikidia anchor → passes scope check.
    - vikidia node with simple.wikipedia.org anchor → ScopeError raised.
    - wikipedia_simple node with vikidia anchor → ScopeError raised.
    - Unknown source → ScopeError raised.
    - resolve_zim returns None (not raise) for scope violations, per degradation contract.
    - resolve_grounding returns "" (no exception) when scope guard rejects.

Spec: docs/design/W7_grounding_reader.md (Scope guard row + test_scope_guard.py).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner:
    python3 tests/grounding/test_scope_guard.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import pytest

from mentar.grounding.source_map import ScopeError, check_scope, resolve_zim


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_vikidia_anchor_passes():
    """A vikidia source with a vikidia.org anchor passes the scope check."""
    check_scope("vikidia", "https://en.vikidia.org/wiki/Fraction")  # must not raise


def test_simple_wiki_anchor_passes():
    """A wikipedia_simple source with a simple.wikipedia.org anchor passes."""
    check_scope("wikipedia_simple", "https://simple.wikipedia.org/wiki/Unit_fraction")


def test_vikidia_source_wrong_host_rejected():
    """A vikidia source node with a simple.wikipedia.org anchor raises ScopeError."""
    with pytest.raises(ScopeError, match="Scope violation"):
        check_scope("vikidia", "https://simple.wikipedia.org/wiki/Fraction")


def test_wikipedia_simple_source_wrong_host_rejected():
    """A wikipedia_simple node with a vikidia.org anchor raises ScopeError."""
    with pytest.raises(ScopeError, match="Scope violation"):
        check_scope("wikipedia_simple", "https://en.vikidia.org/wiki/Fraction")


def test_unknown_source_rejected():
    """An unknown source enum raises ScopeError."""
    with pytest.raises(ScopeError):
        check_scope("unknown_source_xyz", "https://en.vikidia.org/wiki/Fraction")


def test_parent_upload_no_host_check():
    """parent_upload source has no URL constraint — passes for any URL."""
    check_scope("parent_upload", "https://example.com/anything")  # must not raise


def test_builtin_no_host_check():
    """builtin source has no URL constraint — passes for any URL."""
    check_scope("builtin", "https://anything.example.org/page")  # must not raise


def test_resolve_zim_scope_violation_returns_none(tmp_path):
    """resolve_zim returns None (not ScopeError) on scope violation."""
    cfg = {
        "zim_dir": str(tmp_path),
        "sources": {"vikidia": "some.zim"},
    }
    # vikidia source but wikipedia anchor → scope violation
    result = resolve_zim(
        "vikidia",
        "https://simple.wikipedia.org/wiki/Fraction",
        cfg,
    )
    assert result is None, f"Expected None on scope violation, got {result!r}"


def test_resolve_grounding_returns_empty_on_scope_violation(tmp_path):
    """resolve_grounding returns '' when scope guard fires — never raises."""
    from mentar.grounding import resolve_grounding
    from mentar.grounding import cache as gcache
    gcache.clear_memory()

    cfg = {
        "zim_dir": str(tmp_path),
        "sources": {"vikidia": "nonexistent.zim"},
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    # Source says vikidia but anchor is wikipedia → scope error
    node_grounding = {
        "source": "vikidia",
        "anchor": "https://simple.wikipedia.org/wiki/Fraction",
        "passage_hint": "anything",
    }
    result = resolve_grounding(node_grounding, cfg)
    assert result == "", f"Expected '' from scope violation, got {result!r}"


# ── Inline smoke runner ───────────────────────────────────────────────────────

def _smoke():
    # Passing cases
    check_scope("vikidia", "https://en.vikidia.org/wiki/Fraction")
    print("[smoke] vikidia/vikidia.org → PASS")
    check_scope("wikipedia_simple", "https://simple.wikipedia.org/wiki/Unit_fraction")
    print("[smoke] wikipedia_simple/simple.wikipedia.org → PASS")

    # Rejection cases
    try:
        check_scope("vikidia", "https://simple.wikipedia.org/wiki/Fraction")
        print("[smoke] FAIL: expected ScopeError for vikidia+wikipedia anchor")
        sys.exit(1)
    except ScopeError as e:
        print(f"[smoke] vikidia+wikipedia → ScopeError (expected): {e}")

    try:
        check_scope("unknown_xyz", "https://en.vikidia.org/wiki/Fraction")
        print("[smoke] FAIL: expected ScopeError for unknown source")
        sys.exit(1)
    except ScopeError as e:
        print(f"[smoke] unknown source → ScopeError (expected): {e}")

    # resolve_zim returns None (not raise)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        cfg = {"zim_dir": d, "sources": {"vikidia": "fake.zim"}}
        result = resolve_zim("vikidia", "https://simple.wikipedia.org/wiki/Fraction", cfg)
        assert result is None, f"FAIL: expected None, got {result!r}"
        print("[smoke] resolve_zim scope violation → None OK")

    print("[smoke] test_scope_guard.py PASS")


if __name__ == "__main__":
    _smoke()
