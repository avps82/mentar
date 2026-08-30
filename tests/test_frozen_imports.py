"""The packaged (PyInstaller) binary must be able to IMPORT the app.

Why this file exists: on 2026-08-30 all three single-file builds failed at
startup with "could not get source code" — `inflect` calls
`inspect.getsource()` while importing, and a frozen bundle ships no .py source.
One module-level `import inflect` (engine/wording.py, imported by itemgen,
which everything imports) took out the web app AND the entire item registry.

The whole time, `pytest` and `ruff` were green and CI was green: nothing in the
release gate touches the packaging path, so this rotted for days behind checks
that could not see it. These tests are the cheap part of that gap — they run in
the normal suite and fail the moment an import-time source-reader reappears.

They do NOT replace building the binary (`scripts/build_binary.py`), which is
the only thing that proves a bundle actually runs.
"""

import importlib
import inspect
import sys


def _import_under_frozen_conditions(module_name: str):
    """Import `module_name` with inspect.getsource() failing as it does in a
    PyInstaller bundle. Returns the exception, or None on success."""
    for name in [m for m in sys.modules if m.startswith("mentar")]:
        del sys.modules[name]
    real = inspect.getsource

    def no_source(_obj):
        raise OSError("could not get source code")

    inspect.getsource = no_source
    try:
        importlib.import_module(module_name)
        return None
    except Exception as exc:  # noqa: BLE001 — the point is to report it
        return exc
    finally:
        inspect.getsource = real
        for name in [m for m in sys.modules if m.startswith("mentar")]:
            del sys.modules[name]


def test_the_web_app_imports_without_reading_its_own_source():
    exc = _import_under_frozen_conditions("mentar.web.app")
    assert exc is None, (
        "mentar.web.app cannot be imported in a frozen binary: "
        f"{type(exc).__name__}: {exc}. Something in the import chain reads "
        "Python source at import time (inflect does this) — import it lazily, "
        "inside the function that needs it.")


def test_the_item_registry_imports_without_reading_its_own_source():
    exc = _import_under_frozen_conditions("mentar.engine.item_sources")
    assert exc is None, (
        "mentar.engine.item_sources cannot be imported in a frozen binary: "
        f"{type(exc).__name__}: {exc}")


def test_the_cli_entry_point_imports_without_reading_its_own_source():
    """The binary's actual entry point — if this cannot import, nothing runs."""
    exc = _import_under_frozen_conditions("mentar.cli.__main__")
    assert exc is None, f"mentar.cli.__main__: {type(exc).__name__}: {exc}"


def test_inflect_is_never_imported_at_module_scope_in_src():
    """The specific regression, named. inflect is fine to USE; importing it at
    module scope is what breaks the bundle."""
    import pathlib
    import re

    src = pathlib.Path(__file__).resolve().parents[1] / "src" / "mentar"
    offenders = []
    for py in src.rglob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^(import inflect|from inflect\b)", line):
                offenders.append(f"{py.relative_to(src)}:{i}")
    assert not offenders, (
        "module-scope `import inflect` breaks every frozen build "
        f"(inspect.getsource fails there): {offenders}")
