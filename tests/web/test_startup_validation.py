"""A16 — curriculum templates are validated at web-app startup, not just via the
CLI validate-template subcommand. A cyclic/bad-prereq template must refuse to
serve with a clear error, not silently produce an empty fringe and a false
"you've mastered everything!" completion.
"""
from __future__ import annotations

import importlib
import os
import pathlib
import sys
import tempfile

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

_CYCLIC_TEMPLATE = """---
template_id: cyclic-fixture
country: null
year_level: test
subject: mathematics
curriculum_standard: null
schema_version: "0.1"
concepts:
  - id: concept_a
    label: 'Concept A'
    prereqs: [concept_b]
  - id: concept_b
    label: 'Concept B'
    prereqs: [concept_a]
---

# Deliberately cyclic fixture (A16 regression).
"""


def test_cyclic_fixture_template_refuses_to_serve(tmp_path, monkeypatch):
    try:
        import flask  # noqa: F401
    except ImportError:
        pytest.skip("flask not installed (web extra)")

    bad_template = tmp_path / "cyclic.md"
    bad_template.write_text(_CYCLIC_TEMPLATE, encoding="utf-8")

    monkeypatch.setenv("MENTAR_CURRICULUM", str(bad_template))
    monkeypatch.setenv("MENTAR_DB_PATH", os.path.join(tempfile.mkdtemp(), "a16.db"))

    # Whether mentar.web.app is already cached (import is a no-op, only reload
    # re-executes top-level code) or this is the first import in the process
    # (the plain import itself executes and raises) — either way it's caught here.
    with pytest.raises(RuntimeError, match="(?i)cycle"):
        import mentar.web.app as app_mod
        importlib.reload(app_mod)

    # Restore a valid config so later tests importing mentar.web.app aren't left broken.
    monkeypatch.delenv("MENTAR_CURRICULUM", raising=False)
    import mentar.web.app as app_mod
    importlib.reload(app_mod)


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-v"]))
