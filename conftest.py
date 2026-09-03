"""Pytest bootstrap: make `mentar` (and the vendored PyYAML) importable without an editable install.

The sandbox has no `pip`, so `pip install -e .` isn't available. Newer test files insert `src/`
on sys.path themselves; this root conftest does it once for ALL tests (and adds `.vendor/` for the
vendored PyYAML the validator/fringe use), so `python3 -m pytest` collects the whole suite.
"""

import glob
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))

for p in [os.path.join(ROOT, "src"), os.path.join(ROOT, ".vendor"), *glob.glob(os.path.join(ROOT, ".vendor*"))]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)


# ── Never let a test read the developer's real pack state ────────────────────
# curriculum/pack_state.json is WRITTEN BY THE RUNNING APP: switch a curriculum
# on in the browser and it changes. Seven test helpers tried to isolate
# themselves by POPPING MENTAR_PACK_STATE, which is the opposite of isolation --
# with no override the app resolves the DEFAULT path, i.e. that same real file.
#
# It bit on 2026-09-03: turning on Australia + Year 5 in the UI made
# test_setup_gate fail, because /setup correctly stops sending a returning user
# to the curriculum picker once packs beyond the starter set are on. Green in
# CI, where the file does not exist, so the suite only ever went red on a
# machine where someone had actually used the product -- and blamed setup.
#
# Default the variable to a path that does not exist, so the app falls back to
# the shipped starter set. Tests that need real state (test_curriculum_toggle)
# still set the variable themselves and win, because this only fills a default.
_PACK_STATE_SCRATCH = os.path.join(
    tempfile.mkdtemp(prefix="mentar-pack-state-"), "pack_state.json")
os.environ.setdefault("MENTAR_PACK_STATE", _PACK_STATE_SCRATCH)
