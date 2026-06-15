"""Tests for the pure resolution helpers in scripts/fetch_zim.py.

These need no network: parse a sample Kiwix directory-index HTML and confirm the
newest matching ZIM is chosen.

Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / W7.4).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner:
    python3 tests/grounding/test_fetch_zim.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_zim import parse_index, pick_latest  # noqa: E402

_SAMPLE_INDEX = """
<html><body><pre>
<a href="../">../</a>
<a href="vikidia_en_all_nopic_2024-03.zim">vikidia_en_all_nopic_2024-03.zim</a>  120M
<a href="vikidia_en_all_nopic_2024-09.zim">vikidia_en_all_nopic_2024-09.zim</a>  130M
<a href="vikidia_en_all_nopic_2024-09.zim.sha256">...sha256</a>
<a href="vikidia_en_all_maxi_2024-09.zim">vikidia_en_all_maxi_2024-09.zim</a>  900M
</pre></body></html>
"""


def test_parse_index_lists_zims_only():
    files = parse_index(_SAMPLE_INDEX)
    assert "vikidia_en_all_nopic_2024-09.zim" in files
    assert "vikidia_en_all_maxi_2024-09.zim" in files
    # .sha256 and the parent-dir link are not .zim files
    assert all(f.endswith(".zim") for f in files)
    assert "../" not in files


def test_pick_latest_chooses_newest_matching():
    files = parse_index(_SAMPLE_INDEX)
    latest = pick_latest(files, r"vikidia_en_all_nopic_.*\.zim$")
    assert latest == "vikidia_en_all_nopic_2024-09.zim"  # 2024-09 > 2024-03


def test_pick_latest_respects_pattern():
    files = parse_index(_SAMPLE_INDEX)
    # 'maxi' pattern must not match the 'nopic' files
    assert pick_latest(files, r"vikidia_en_all_maxi_.*\.zim$") == "vikidia_en_all_maxi_2024-09.zim"


def test_pick_latest_no_match_returns_none():
    assert pick_latest(parse_index(_SAMPLE_INDEX), r"does_not_exist_.*\.zim$") is None


# ── Inline smoke runner ─────────────────────────────────────────────────────

def _smoke():
    files = parse_index(_SAMPLE_INDEX)
    assert all(f.endswith(".zim") for f in files), files
    assert pick_latest(files, r"vikidia_en_all_nopic_.*\.zim$") == "vikidia_en_all_nopic_2024-09.zim"
    assert pick_latest(files, r"nope_.*\.zim$") is None
    print("[smoke] test_fetch_zim.py PASS")


if __name__ == "__main__":
    _smoke()
