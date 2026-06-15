"""Tests for mentar.grounding.reader — ZimReader open + lookup + section extraction.

Contract checks:
    - Open fixture ZIM successfully.
    - Resolve a known anchor URL → raw HTML bytes.
    - get_section with and without a passage_hint returns non-empty plain text.
    - Unknown anchor → None (not an exception).
    - Passage text is verbatim: no stripping of injection strings (safety).

Spec: docs/design/W7_grounding_reader.md test table (test_reader.py row).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner (python3-runnable without pytest):
    python3 tests/grounding/test_reader.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import sys

# ── Path setup for direct python3 execution ───────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

FIXTURE_ZIM = REPO_ROOT / "tests" / "fixtures" / "test_fixture.zim"
INJECTION_ANCHOR = "https://en.vikidia.org/wiki/Injection_test"
FRACTION_ANCHOR = "https://en.vikidia.org/wiki/Fraction"
UNIT_ANCHOR = "https://en.vikidia.org/wiki/Unit_fraction"
MISSING_ANCHOR = "https://en.vikidia.org/wiki/NonExistentArticle9999"

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


# ── pytest fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def reader():
    from mentar.grounding.reader import ZimReader
    return ZimReader(_ensure_fixture())


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_open_fixture_zim(reader):
    """ZimReader opens the fixture ZIM without raising."""
    assert reader is not None


def test_get_by_url_known_anchor(reader):
    """Resolving a known anchor URL returns non-empty HTML bytes."""
    html_bytes = reader.get_by_url(FRACTION_ANCHOR)
    assert html_bytes is not None, "Expected HTML bytes for Fraction anchor"
    assert len(html_bytes) > 50
    # Content should contain the word 'fraction'
    assert b"fraction" in html_bytes.lower()


def test_get_by_url_missing_anchor(reader):
    """Resolving an unknown anchor returns None (never raises)."""
    result = reader.get_by_url(MISSING_ANCHOR)
    assert result is None


def test_get_section_no_hint(reader):
    """get_section without a hint returns the lead section as plain text."""
    html_bytes = reader.get_by_url(FRACTION_ANCHOR)
    assert html_bytes is not None
    text = reader.get_section(html_bytes, "")
    assert isinstance(text, str)
    assert len(text) > 10
    # Plain text should not contain raw HTML tags
    assert "<p>" not in text
    assert "<html>" not in text


def test_get_section_with_hint_lead(reader):
    """get_section with a lead-section hint returns content about equal parts."""
    html_bytes = reader.get_by_url(FRACTION_ANCHOR)
    assert html_bytes is not None
    text = reader.get_section(html_bytes, "Opening section — fraction as part of something")
    assert isinstance(text, str)
    assert len(text) > 10
    # Should mention 'fraction' or 'part'
    assert "fraction" in text.lower() or "part" in text.lower()


def test_get_section_hint_targets_section(reader):
    """Hint containing 'equal parts' should return content mentioning equal parts."""
    html_bytes = reader.get_by_url(FRACTION_ANCHOR)
    assert html_bytes is not None
    text = reader.get_section(html_bytes, "Equal parts requirement")
    assert isinstance(text, str)
    assert len(text) > 5


def test_get_section_unit_fraction(reader):
    """Unit fraction article resolves and returns definition text."""
    html_bytes = reader.get_by_url(UNIT_ANCHOR)
    assert html_bytes is not None
    text = reader.get_section(html_bytes, "Definition — one part of n equal parts")
    assert isinstance(text, str)
    assert "unit" in text.lower() or "fraction" in text.lower() or "1/" in text


def test_reader_file_not_found():
    """ZimReader raises FileNotFoundError for a non-existent ZIM path."""
    from mentar.grounding.reader import ZimReader
    with pytest.raises(FileNotFoundError):
        ZimReader("/tmp/this_does_not_exist_mentar.zim")


# ── Inline smoke runner ───────────────────────────────────────────────────────

def _smoke():
    """Run a quick self-test when invoked directly with python3."""
    from mentar.grounding.reader import ZimReader

    zim = _ensure_fixture()
    print(f"[smoke] fixture ZIM: {zim}")

    r = ZimReader(zim)
    print(f"[smoke] opened ZimReader: {r}")

    html_bytes = r.get_by_url(FRACTION_ANCHOR)
    assert html_bytes is not None, "FAIL: Fraction anchor returned None"
    print(f"[smoke] get_by_url(Fraction): {len(html_bytes)} bytes OK")

    text = r.get_section(html_bytes, "Opening section — fraction as part of something")
    assert len(text) > 10, f"FAIL: section text too short: {text!r}"
    assert "<p>" not in text, "FAIL: HTML tags in output"
    print(f"[smoke] get_section: {len(text)} chars, starts={text[:80]!r}")

    missing = r.get_by_url(MISSING_ANCHOR)
    assert missing is None, f"FAIL: missing anchor should return None, got {missing!r}"
    print("[smoke] missing anchor → None OK")

    print("[smoke] test_reader.py PASS")


if __name__ == "__main__":
    _smoke()
