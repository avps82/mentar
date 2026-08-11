"""tools/check_doc_paths.py — prose docs must not reference paths that don't exist.

The point of this test is the FIRST one: it is the standing gate that stops the
doc rot three manual audits (2026-07-22, 2026-07-23, 2026-08-11) each had to
re-find by hand. The rest verify the checker's own logic, so a future change that
quietly neuters it (over-broad allowlist, parsing that matches nothing) fails here
rather than silently passing everything.

    python3 tests/tools/test_check_doc_paths.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.tools.check_doc_paths import (  # noqa: E402
    _clean,
    _looks_like_path,
    _prose_docs,
    find_broken,
)


def test_no_broken_path_references_in_prose_docs():
    """THE gate. A failure here means a doc names a file that isn't there —
    usually a rename the docs missed. Fix the doc, or if the file is genuinely
    planned/runtime, add it to the checker's allowlist WITH the reason."""
    broken = find_broken()
    assert broken == [], (
        "docs reference paths that don't resolve:\n"
        + "\n".join(f"  {d}:{ln} -> {ref}" for d, ln, ref in broken)
    )


def test_checker_actually_scans_the_real_docs():
    """Guards against the checker silently scanning nothing (which would make
    the gate above vacuously pass)."""
    docs = _prose_docs()
    names = {p.name for p in docs}
    assert len(docs) > 40, f"expected the full prose-doc set, got {len(docs)}"
    for expected in ("README.md", "SPEC.md", "SAFETY.md", "PHASE0_STATUS.md"):
        assert expected in names, f"{expected} not scanned"


def test_clean_preserves_leading_dot_directories():
    """Regression: an earlier cut used lstrip('./'), which ate the dot of
    '.github/workflows/ci.yml' and reported a false break."""
    assert _clean(".github/workflows/ci.yml") == ".github/workflows/ci.yml"
    assert _clean("./docs/SPEC.md") == "docs/SPEC.md"
    assert _clean("src/mentar/web/app.py:833") == "src/mentar/web/app.py"


def test_looks_like_path_rejects_non_paths():
    """API references and prose shorthand must not be treated as file paths."""
    assert not _looks_like_path("engine/curriculum.py::load_template_subject()")
    assert not _looks_like_path("year2/5/6_maths.md")   # numeric enumeration
    assert not _looks_like_path("https://example.com/a.md")
    assert not _looks_like_path("some file.md")          # contains a space
    assert _looks_like_path("docs/SPEC.md")
    assert _looks_like_path("src/mentar/engine/bkt.py")


def test_rename_arrow_left_side_is_not_a_break(tmp_path, monkeypatch):
    """A changelog/audit row recording `old.py` -> `new.py` names the old path on
    purpose. Without this rule every doc that documents a rename trips the check,
    which is how the first cut behaved."""
    import mentar.tools.check_doc_paths as mod

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "log.md").write_text(
        "Renamed `curriculum/packs.py` -> `curriculum/packs.json` this week.\n"
        "Also `docs/OLD.md` → `docs/NEW.md`.\n",
        encoding="utf-8",
    )
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum" / "packs.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "docs" / "NEW.md").write_text("x\n", encoding="utf-8")

    monkeypatch.setattr(mod, "REPO", tmp_path)
    broken = mod.find_broken()
    assert broken == [], f"rename left-hand sides should not be reported: {broken}"


def test_a_genuinely_missing_path_is_reported(tmp_path, monkeypatch):
    """The checker must actually fail on a real break, not just always pass."""
    import mentar.tools.check_doc_paths as mod

    fake_repo = tmp_path
    (fake_repo / "docs").mkdir()
    (fake_repo / "docs" / "thing.md").write_text(
        "See `src/mentar/definitely_not_here.py` for details.\n", encoding="utf-8"
    )
    (fake_repo / "src").mkdir()
    (fake_repo / "src" / "real.py").write_text("x = 1\n", encoding="utf-8")

    monkeypatch.setattr(mod, "REPO", fake_repo)
    broken = mod.find_broken()
    assert any("definitely_not_here.py" in ref for _, _, ref in broken), broken


if __name__ == "__main__":
    test_no_broken_path_references_in_prose_docs()
    print("  ✓ test_no_broken_path_references_in_prose_docs")
    test_checker_actually_scans_the_real_docs()
    print("  ✓ test_checker_actually_scans_the_real_docs")
    test_clean_preserves_leading_dot_directories()
    print("  ✓ test_clean_preserves_leading_dot_directories")
    test_looks_like_path_rejects_non_paths()
    print("  ✓ test_looks_like_path_rejects_non_paths")
    print("  (skipped the tmp_path test — needs pytest fixtures)")
