"""Tests for the grounding degradation contract.

Contract checks (SAFETY §1.5 / SPEC §15):
    - Missing ZIM file → resolve_grounding returns "", logs, does NOT raise.
    - Bad/unknown anchor (ZIM present) → returns "", logs, does NOT raise.
    - Empty zim_dir / unconfigured source → returns "", does NOT raise.
    - Empty passage (ZIM present, article exists but no text) → returns "".
    - The public API resolve_grounding NEVER raises under any of the above.

Spec: docs/design/W7_grounding_reader.md (Failure mode row + test_degradation.py).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner:
    python3 tests/grounding/test_degradation.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

FIXTURE_ZIM = REPO_ROOT / "tests" / "fixtures" / "test_fixture.zim"

import pytest


def _ensure_fixture():
    if not FIXTURE_ZIM.exists():
        import importlib.util
        if importlib.util.find_spec("libzim") is None:
            pytest.skip("libzim not installed (grounding extra) and no prebuilt fixture ZIM")
        script = REPO_ROOT / "tests" / "fixtures" / "build_fixture_zim.py"
        spec = importlib.util.spec_from_file_location("bfz", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build(FIXTURE_ZIM)
    return FIXTURE_ZIM


@pytest.fixture(autouse=True)
def reset_state():
    from mentar.grounding import cache as gcache
    from mentar.grounding.resolve import clear_reader_pool
    gcache.clear_memory()
    clear_reader_pool()
    yield
    gcache.clear_memory()
    clear_reader_pool()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_missing_zim_returns_empty(tmp_path):
    """Missing ZIM file → resolve_grounding returns '' and does not raise."""
    from mentar.grounding import resolve_grounding
    cfg = {
        "zim_dir": str(tmp_path),
        "sources": {"vikidia": "nonexistent_totally.zim"},
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "Opening section",
    }
    # Must not raise; must return ""
    result = resolve_grounding(node, cfg)
    assert result == "", f"Expected '' for missing ZIM, got {result!r}"


def test_bad_anchor_returns_empty():
    """Unknown anchor in a real ZIM → resolve_grounding returns '' and does not raise."""
    from mentar.grounding import resolve_grounding
    zim = _ensure_fixture()
    cfg = {
        "zim_dir": str(zim.parent),
        "sources": {"vikidia": zim.name},
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/ArticleThatDoesNotExist12345",
        "passage_hint": "",
    }
    result = resolve_grounding(node, cfg)
    assert result == "", f"Expected '' for bad anchor, got {result!r}"


def test_empty_zim_dir_returns_empty():
    """Empty zim_dir → resolve_grounding returns ''."""
    from mentar.grounding import resolve_grounding
    cfg = {
        "zim_dir": "",
        "sources": {"vikidia": "vikidia_en.zim"},
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "",
    }
    result = resolve_grounding(node, cfg)
    assert result == "", f"Expected '' for empty zim_dir, got {result!r}"


def test_unconfigured_source_returns_empty(tmp_path):
    """Source not in config.sources → resolve_grounding returns ''."""
    from mentar.grounding import resolve_grounding
    cfg = {
        "zim_dir": str(tmp_path),
        "sources": {},  # empty — no sources configured
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "",
    }
    result = resolve_grounding(node, cfg)
    assert result == ""


def test_empty_grounding_block_returns_empty():
    """Completely empty node_grounding dict → resolve_grounding returns ''."""
    from mentar.grounding import resolve_grounding
    result = resolve_grounding({}, {})
    assert result == ""


def test_none_safe_does_not_raise():
    """resolve_grounding with None values in inputs returns '' without raising."""
    from mentar.grounding import resolve_grounding
    # Should degrade gracefully even with unusual input shapes
    result = resolve_grounding({"source": None, "anchor": None}, {})
    assert result == ""


def test_non_dict_grounding_does_not_raise():
    """node_grounding that is None / not a dict → returns '' without raising.

    A curriculum node may lack a ``grounding:`` block entirely; the controller
    could then pass None. The public API must absorb this (never crash a turn).
    """
    from mentar.grounding import resolve_grounding
    for bad in (None, "not-a-dict", 42, ["a", "list"]):
        result = resolve_grounding(bad, {})
        assert result == "", f"Expected '' for node_grounding={bad!r}, got {result!r}"


def test_missing_zim_logs_warning(tmp_path, caplog):
    """A missing ZIM logs a warning (not an error — a turn-degradation event)."""
    import logging

    from mentar.grounding import resolve_grounding
    cfg = {
        "zim_dir": str(tmp_path),
        "sources": {"vikidia": "missing_file.zim"},
        "max_passage_chars": 1200,
        "cache": {"enabled": False},
    }
    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "",
    }
    with caplog.at_level(logging.WARNING, logger="mentar.grounding"):
        result = resolve_grounding(node, cfg)
    assert result == ""
    # A warning should have been logged
    assert any("WARNING" in r.levelname or r.levelno >= logging.WARNING for r in caplog.records), (
        f"Expected a WARNING log entry; got: {[r.message for r in caplog.records]}"
    )


# ── Inline smoke runner ───────────────────────────────────────────────────────

def _smoke():
    import tempfile

    from mentar.grounding import cache as gcache
    from mentar.grounding import resolve_grounding
    from mentar.grounding.resolve import clear_reader_pool

    def reset():
        gcache.clear_memory()
        clear_reader_pool()

    # 1. Missing ZIM
    reset()
    with tempfile.TemporaryDirectory() as d:
        cfg = {"zim_dir": d, "sources": {"vikidia": "missing.zim"},
               "max_passage_chars": 1200, "cache": {"enabled": False}}
        r = resolve_grounding({"source": "vikidia", "anchor": "https://en.vikidia.org/wiki/Fraction"}, cfg)
        assert r == "", f"FAIL: missing ZIM should return '', got {r!r}"
        print("[smoke] missing ZIM → '' OK")

    # 2. Bad anchor
    reset()
    zim = _ensure_fixture()
    cfg = {"zim_dir": str(zim.parent), "sources": {"vikidia": zim.name},
           "max_passage_chars": 1200, "cache": {"enabled": False}}
    r = resolve_grounding({"source": "vikidia", "anchor": "https://en.vikidia.org/wiki/DoesNotExist999"}, cfg)
    assert r == "", f"FAIL: bad anchor should return '', got {r!r}"
    print("[smoke] bad anchor → '' OK")

    # 3. Empty grounding block
    reset()
    r = resolve_grounding({}, {})
    assert r == "", f"FAIL: empty block should return '', got {r!r}"
    print("[smoke] empty grounding block → '' OK")

    print("[smoke] test_degradation.py PASS")


if __name__ == "__main__":
    _smoke()
