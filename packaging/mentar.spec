# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the single-file Mentar build.

    pyinstaller packaging/mentar.spec          (run from the repo root)

What this produces is Mentar WITHOUT the language model: it is multi-gigabyte, so
the binary (26-41 MB by platform) fetches it on first run.

UNDECIDED (2026-08-15, maintainer): the downloadable build is to ship ONE fixed
model rather than the source install's roster auto-selection. Which one is not
chosen, so nothing here hard-codes a model or quotes a size. "No install" is true of Mentar; it is not true
of the whole first-run experience, and docs/RUNNING.md says so plainly.

The layout below is not arbitrary. `mentar.paths.bundle_root()` returns
`sys._MEIPASS` when frozen, so shipped assets must sit at the SAME relative
paths they occupy in the repo, and `db/store.py` finds schema.sql next to its
own module — hence `mentar/db/schema.sql` rather than a top-level copy.
"""

import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# PyInstaller injects SPECPATH. Anchor everything to it: relative `datas` entries
# are resolved against the CWD, not the spec, so a build launched from anywhere but
# the repo root would silently ship an EMPTY curriculum. Absolute paths make the
# build work from any directory and fail loudly rather than quietly if a path moves.
ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))  # noqa: F821 - injected


def _r(*parts):
    p = os.path.join(ROOT, *parts)
    if not os.path.exists(p):
        raise SystemExit(f"mentar.spec: required asset missing: {p}")
    return p


datas = [
    # Read-only shipped assets — must mirror their repo-relative paths, because
    # bundle_root() is the repo root from source and _MEIPASS when frozen.
    (_r("prompts"), "prompts"),
    (_r("curriculum", "templates"), "curriculum/templates"),
    (_r("curriculum", "visual_scaffolds"), "curriculum/visual_scaffolds"),
    (_r("curriculum", "itembank"), "curriculum/itembank"),
    (_r("curriculum", "packs.json"), "curriculum"),
    (_r("config", "model_roster.yaml"), "config"),
    # Flask resolves these relative to the mentar.web package, not the repo root.
    (_r("src", "mentar", "web", "templates"), "mentar/web/templates"),
    (_r("src", "mentar", "web", "static"), "mentar/web/static"),
    # db/store.py does Path(__file__).parent / "schema.sql".
    (_r("src", "mentar", "db", "schema.sql"), "mentar/db"),
]

# pint ships its unit definitions as package data; without them every conversion
# raises at runtime, and only at runtime.
datas += collect_data_files("pint")
datas += collect_data_files("num2words")

hiddenimports = [
    "waitress",          # imported inside _serve(), so the static analyser misses it
    "mentar.paths",
    "sympy",
    "pint",
    "inflect",
]
# num2words picks its locale module by string at call time.
hiddenimports += collect_submodules("num2words")
# Every mentar import in cli/__main__.py is function-local (deliberately — it keeps
# `mentar --help` fast). PyInstaller usually follows those, but "usually" is how a
# binary ships without its web app. Our own code is ~1 MB; take the whole package
# and remove a class of works-from-source-missing-in-the-binary failures.
hiddenimports += collect_submodules("mentar")

excludes = [
    # Dev-only.
    "pytest", "hypothesis", "_pytest", "ruff",
    # Optional extras deliberately NOT in the binary: libzim has patchy wheels
    # (it is why grounding is an extra at all) and pyBKT is offline-fit tooling.
    # Both degrade gracefully; bundling them would make the build fragile on the
    # exact platforms this binary exists to serve.
    "libzim", "pyBKT", "smbprotocol",
    # Never pulled in on purpose; excluded so a transitive import cannot silently
    # add ~100 MB to a download aimed at families on ordinary connections.
    "matplotlib", "scipy", "numpy", "pandas", "IPython", "tkinter", "PyQt5", "PySide6",
]

a = Analysis(
    [_r("packaging", "entry.py")],
    pathex=[_r("src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="mentar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX-packed binaries trip antivirus heuristics far more often
    console=True,  # the window IS the status display: it prints the URL and errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
