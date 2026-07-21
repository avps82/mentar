"""engine/visual_scaffold.py — keyword-routed OKF scaffold lookup."""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.visual_scaffold import load_visual_scaffold

_ROOT = REPO / "curriculum" / "visual_scaffolds"


def test_matches_real_fractions_scaffold_by_keyword():
    body = load_visual_scaffold(_ROOT, "mathematics", "Equivalent fractions")
    assert "Bar model" in body


def test_matches_real_vocabulary_scaffold_by_keyword():
    body = load_visual_scaffold(_ROOT, "english", "Vocabulary — synonym pairs")
    assert "Frayer model" in body


def test_no_keyword_match_returns_empty_string():
    assert load_visual_scaffold(_ROOT, "mathematics", "Telling the time") == ""


def test_unmapped_subject_returns_empty_string():
    assert load_visual_scaffold(_ROOT, "science", "Forces and motion") == ""


def test_missing_scaffold_root_returns_empty_string(tmp_path):
    assert load_visual_scaffold(tmp_path, "mathematics", "fractions") == ""


if __name__ == "__main__":
    test_matches_real_fractions_scaffold_by_keyword()
    print("  ✓ test_matches_real_fractions_scaffold_by_keyword")
    test_matches_real_vocabulary_scaffold_by_keyword()
    print("  ✓ test_matches_real_vocabulary_scaffold_by_keyword")
    test_no_keyword_match_returns_empty_string()
    print("  ✓ test_no_keyword_match_returns_empty_string")
    test_unmapped_subject_returns_empty_string()
    print("  ✓ test_unmapped_subject_returns_empty_string")
    test_missing_scaffold_root_returns_empty_string(pathlib.Path("/tmp/nonexistent_scaffold_root"))
    print("  ✓ test_missing_scaffold_root_returns_empty_string")
