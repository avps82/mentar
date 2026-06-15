"""Pytest bootstrap: make `mentar` (and the vendored PyYAML) importable without an editable install.

The sandbox has no `pip`, so `pip install -e .` isn't available. Newer test files insert `src/`
on sys.path themselves; this root conftest does it once for ALL tests (and adds `.vendor/` for the
vendored PyYAML the validator/fringe use), so `python3 -m pytest` collects the whole suite.
"""

import glob
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

for p in [os.path.join(ROOT, "src"), os.path.join(ROOT, ".vendor"), *glob.glob(os.path.join(ROOT, ".vendor*"))]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)
