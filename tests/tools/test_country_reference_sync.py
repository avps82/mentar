"""The generated country reference JSONs match their markdown sources.

`docs/design/country_references/*.md` are the maintainer-supplied originals;
`docs/design/curriculum_reference_{sg,in,us}.json` are machine translations the
coverage auditor reads. If someone edits a markdown reference and forgets to
re-run the translator, the auditor would silently report against stale
expectations -- the exact "claim drifted from source" failure the whole
curriculum-audit effort exists to prevent.

    python3 -m pytest tests/tools/test_country_reference_sync.py
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.tools.build_country_reference import SOURCES, build  # noqa: E402


def test_generated_json_matches_the_markdown_sources():
    stale = []
    for stem, (pack, subject) in SOURCES.items():
        country = pack.split("_")[0].lower()
        path = REPO_ROOT / "docs" / "design" / f"curriculum_reference_{country}.json"
        assert path.exists(), f"{path.name} missing — run mentar.tools.build_country_reference"
        stored = json.loads(path.read_text(encoding="utf-8")).get(subject)
        if stored != build(stem):
            stale.append(f"{path.name}:{subject} (source: {stem}_reference.md)")
    assert not stale, (
        "generated reference JSON is out of date with its markdown source — "
        "re-run `python3 -m mentar.tools.build_country_reference`:\n  "
        + "\n  ".join(stale)
    )


def test_every_reference_year_key_uses_its_packs_naming_convention():
    """Keys must be spelled the way that pack spells `year_level` ("Class 7",
    "Primary 4", "Grade 9") — a malformed key ("Secondary 3 & 4", "Year 3" in a
    Class-based pack) would audit as ABSENT forever and read as a content gap.

    A well-formed key with no template is NOT a failure: it is a real absence
    the auditor is supposed to report. That is how this test first surfaced
    that IN/SG/US have no Class 1 / Primary 1 / Grade 1 template at all, while
    all three references define Year-1 content (AU got Year 1 on 2026-08-21;
    the generic packs never did — a W8 gap, not a translation bug)."""
    import re

    import yaml
    bad = []
    for stem, (pack, subject) in SOURCES.items():
        words = set()
        for tpl in (REPO_ROOT / "curriculum" / "templates" / pack).glob("*.md"):
            if tpl.name in ("index.md", "log.md"):
                continue
            fm = yaml.safe_load(tpl.read_text(encoding="utf-8").split("\n---\n")[0])
            words.add(str(fm.get("year_level", "")).split()[0])
        for key in build(stem):
            if key.startswith("Pre-U"):
                continue  # SG's pre-university years, deliberately unmodelled
            m = re.fullmatch(r"([A-Za-z]+) (\d+)", key)
            if not m or m.group(1) not in words:
                bad.append(f"{pack}/{subject}: {key!r} is not spelled like this "
                           f"pack's year_level values ({sorted(words)})")
    assert not bad, "\n".join(bad)
