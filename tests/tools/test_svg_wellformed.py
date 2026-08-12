"""Every .svg in the repo must be well-formed XML.

Why this exists (2026-08-12): the light-scattering sample SVG shipped TWICE with
defects — the second time with a `--` inside an XML comment, which is illegal in
XML and made the browser stop parsing at that line ("Double hyphen within
comment"). The maintainer's browser was the thing that caught it. Visual defects
genuinely need a render-and-look loop (see explain_mode_design.md), but WELL-
FORMEDNESS is machine-checkable, so it is CI-gated here: an SVG that cannot even
parse must never reach a render review, let alone a child.

    python3 tests/tools/test_svg_wellformed.py
"""

from __future__ import annotations

import pathlib
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parents[2]

# Directories that can legitimately hold authored SVGs, now or later.
_SCAN_ROOTS = ("docs", "src", "curriculum")


def _all_svgs() -> list[pathlib.Path]:
    return [p for root in _SCAN_ROOTS for p in (REPO / root).rglob("*.svg")]


def test_repo_has_the_sample_svg():
    """Guard the scan itself: if this glob ever finds nothing while the sample
    exists, the well-formedness test below would vacuously pass."""
    assert any(p.name == "light_scattering.svg" for p in _all_svgs())


def test_every_svg_parses_as_xml():
    for svg in _all_svgs():
        try:
            root = ET.parse(svg).getroot()
        except ET.ParseError as exc:
            raise AssertionError(f"{svg.relative_to(REPO)} is not well-formed XML: {exc}") from exc
        assert root.tag.endswith("svg"), f"{svg.relative_to(REPO)}: root element is {root.tag!r}, not <svg>"


def test_every_svg_is_self_contained():
    """Offline product: no external fetches (images, stylesheets) and no script
    elements inside authored SVGs — same posture as the web CSP."""
    for svg in _all_svgs():
        text = svg.read_text(encoding="utf-8").lower()
        for banned in ("<script", "http://", "https://", "xlink:href=\"/"):
            # the xmlns declaration is the one legitimate URL-shaped string
            if banned in ("http://", "https://"):
                stripped = text.replace("http://www.w3.org/2000/svg", "").replace(
                    "http://www.w3.org/1999/xlink", "")
                assert banned not in stripped, f"{svg.relative_to(REPO)}: external reference ({banned})"
            else:
                assert banned not in text, f"{svg.relative_to(REPO)}: {banned} not allowed"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
