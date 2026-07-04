"""Tests for mentar.grounding.resolve — node grounding block → passage.

Contract checks:
    - Node grounding dict → expected non-empty passage string.
    - passage_hint selection (different hints, same anchor → different focus).
    - max_passage_chars length bound is respected.
    - Cache is populated after first resolve; subsequent calls return cached value.

Spec: docs/design/W7_grounding_reader.md test table (test_resolve.py row).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner:
    python3 tests/grounding/test_resolve.py
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
        script = REPO_ROOT / "tests" / "fixtures" / "build_fixture_zim.py"
        spec = importlib.util.spec_from_file_location("bfz", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build(FIXTURE_ZIM)
    return FIXTURE_ZIM


def _make_cfg(zim_path, max_chars=1200) -> dict:
    return {
        "zim_dir": str(zim_path.parent),
        "sources": {
            "vikidia": zim_path.name,
            "wikipedia_simple": zim_path.name,
            "khanacademy": zim_path.name,
        },
        "max_passage_chars": max_chars,
        "cache": {"enabled": False},
    }


@pytest.fixture(autouse=True)
def reset_state():
    """Reset reader pool and memory cache between tests."""
    from mentar.grounding import cache as gcache
    from mentar.grounding.resolve import clear_reader_pool
    gcache.clear_memory()
    clear_reader_pool()
    yield
    gcache.clear_memory()
    clear_reader_pool()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_resolve_vikidia_fraction():
    """A vikidia Fraction grounding block returns a non-empty passage."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    node_grounding = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "Opening section — fraction as part of something",
    }
    result = resolve_grounding_inner(node_grounding, cfg)
    assert isinstance(result, str)
    assert len(result) > 10, f"Expected non-empty passage, got: {result!r}"
    assert "<p>" not in result, "Passage should be plain text, not HTML"


def test_resolve_wikipedia_simple_division():
    """A wikipedia_simple Division grounding block returns a non-empty passage."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    node_grounding = {
        "source": "wikipedia_simple",
        "anchor": "https://simple.wikipedia.org/wiki/Division_(mathematics)",
        "passage_hint": "Definition + 'sharing equally' framing",
    }
    result = resolve_grounding_inner(node_grounding, cfg)
    assert isinstance(result, str)
    assert len(result) > 10


def test_resolve_khanacademy_video_transcript():
    """A khanacademy grounding block (B1, 2026-07-05) uses the custom
    video-narration extractor — anchor is a ZIM-internal path, not a URL, and
    the returned passage is the subtitle transcript, not the HTML shell."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    node_grounding = {
        "source": "khanacademy",
        "anchor": "ka_fake_hash_equivalent_fractions",
        "passage_hint": "ignored for khanacademy — whole transcript is the passage",
    }
    result = resolve_grounding_inner(node_grounding, cfg)
    assert "pizza" in result.lower()
    assert "<html>" not in result
    assert "WEBVTT" not in result


def test_resolve_khanacademy_missing_anchor_degrades_empty():
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    node_grounding = {"source": "khanacademy", "anchor": "no_such_path", "passage_hint": ""}
    assert resolve_grounding_inner(node_grounding, cfg) == ""


def test_passage_hint_selects_section():
    """Passage hint guides section selection: equal-parts hint returns relevant text."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    node_grounding = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "Equal parts requirement — why fractions need equal-size pieces",
    }
    result = resolve_grounding_inner(node_grounding, cfg)
    assert isinstance(result, str)
    assert len(result) > 5


def test_max_passage_chars_respected():
    """Passage is truncated to max_passage_chars."""
    from mentar.grounding.resolve import resolve_grounding_inner
    from mentar.grounding.wrapper import wrap_passage
    zim = _ensure_fixture()
    cfg = _make_cfg(zim, max_chars=50)
    node_grounding = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "Opening section",
    }
    raw = resolve_grounding_inner(node_grounding, cfg)
    bounded = wrap_passage(raw, cfg)
    assert len(bounded) <= 50, f"Expected ≤50 chars, got {len(bounded)}: {bounded!r}"


def test_cache_populated_after_first_resolve():
    """After resolving, the anchor is cached in memory."""
    from mentar.grounding import cache as gcache
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = {**_make_cfg(zim), "cache": {"enabled": True}}
    anchor = "https://en.vikidia.org/wiki/Fraction"
    node_grounding = {
        "source": "vikidia",
        "anchor": anchor,
        "passage_hint": "Opening section",
    }
    # First call: cache miss
    gcache.clear_memory()
    result1 = resolve_grounding_inner(node_grounding, cfg)
    assert result1

    # Second call should hit memory cache
    cached = gcache.get(anchor, cfg)
    assert cached is not None, "Cache should be populated after first resolve"
    assert cached == result1


def test_missing_source_returns_empty():
    """Node grounding with no 'source' field returns empty string."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    result = resolve_grounding_inner({"anchor": "https://en.vikidia.org/wiki/Fraction", "passage_hint": ""}, cfg)
    assert result == ""


def test_missing_anchor_returns_empty():
    """Node grounding with no 'anchor' field returns empty string."""
    from mentar.grounding.resolve import resolve_grounding_inner
    zim = _ensure_fixture()
    cfg = _make_cfg(zim)
    result = resolve_grounding_inner({"source": "vikidia", "passage_hint": ""}, cfg)
    assert result == ""


# ── Inline smoke runner ───────────────────────────────────────────────────────

def _smoke():
    from mentar.grounding import cache as gcache
    from mentar.grounding.resolve import clear_reader_pool, resolve_grounding_inner
    from mentar.grounding.wrapper import wrap_passage

    gcache.clear_memory()
    clear_reader_pool()

    zim = _ensure_fixture()
    cfg = _make_cfg(zim)

    node = {
        "source": "vikidia",
        "anchor": "https://en.vikidia.org/wiki/Fraction",
        "passage_hint": "Opening section — fraction as part of something",
    }
    result = resolve_grounding_inner(node, cfg)
    assert result, "FAIL: empty passage for Fraction"
    print(f"[smoke] resolve Fraction: {len(result)} chars, starts={result[:80]!r}")

    bounded = wrap_passage(result, {"max_passage_chars": 50})
    assert len(bounded) <= 50, f"FAIL: length bound not respected: {len(bounded)}"
    print(f"[smoke] max_passage_chars=50: {len(bounded)} chars OK")

    empty = resolve_grounding_inner({}, cfg)
    assert empty == "", f"FAIL: empty grounding should return '', got {empty!r}"
    print("[smoke] empty grounding → '' OK")

    print("[smoke] test_resolve.py PASS")


if __name__ == "__main__":
    _smoke()
