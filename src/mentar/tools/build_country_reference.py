"""Convert the maintainer's markdown country references into auditor JSON.

`docs/design/country_references/*.md` hold the reference syllabi verbatim as
supplied (2026-08-21). `audit_curriculum_coverage.py` needs the same shape as
`curriculum_reference_au.json`: {subject: {year_key: [strand, ...]}}, keyed by
the SAME `year_level` strings the templates use, so a country's coverage can be
reported per strand instead of only as a total against AU.

This is a TRANSLATOR, not an authority: every strand name here comes from the
markdown verbatim (the text before the first colon in each bullet). It invents
no curriculum content. Where the source is irregular the rule applied is
recorded in the output's `_meta.normalisation` so the judgement is auditable
rather than buried:

  * SG headings carry both namings ("Year 3 (Primary 3)") -- the PARENTHETICAL
    is kept, because that is what SG templates put in `year_level`.
  * Bands supplied as one block (SG English "Year 9 & 10", US English
    "Grades 9 & 10") are assigned to BOTH years, unchanged. The source did not
    split them; splitting them here would be inventing a distinction.
  * US maths high school is course-named ("Algebra 1 (typically Grade 9)") --
    the parenthetical grade is used as the key, and the course name is kept as
    a strand so the pathway stays visible.
  * US science grades 6-8 are three pillar blocks stating mastery "by end of
    Grade 8" -- the union is assigned to all three grades, as the source says.

KNOWN LIMITATION (not guessed at, left for a maintainer decision): SG/IN/US
senior science is a SPLIT subject in the templates (subject: physics /
chemistry / biology) but the reference markdown lists those as BULLETS under
one "science" year -- so the translated strands for e.g. SG "Secondary 3"
science are the words "Physics", "Chemistry", "Biology", and the split
templates audit as "(no reference entry)". Restructuring those blocks into
three subjects would change what a strand MEANS in this file, so it is
recorded here rather than done silently.

    python3 -m mentar.tools.build_country_reference          # writes the JSON
    python3 -m mentar.tools.build_country_reference --check  # verify, no write
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REFS = REPO / "docs" / "design" / "country_references"

# reference filename stem -> (country pack dir, subject key used in templates)
SOURCES = {
    "sg_maths": ("SG_GENERIC", "mathematics"),
    "sg_science": ("SG_GENERIC", "science"),
    "sg_english": ("SG_GENERIC", "english"),
    "in_maths": ("IN_GENERIC", "mathematics"),
    "in_science": ("IN_GENERIC", "science"),
    "in_english": ("IN_GENERIC", "english"),
    "us_maths": ("US_GENERIC", "mathematics"),
    "us_science": ("US_GENERIC", "science"),
    "us_english": ("US_GENERIC", "english"),
}

_PARENTHETICAL = re.compile(r"\((?:typically\s+)?([A-Za-z-]+ [0-9]+(?: & [0-9]+)?)\)")
_BAND = re.compile(r"^([A-Za-z]+)\s+(\d+)\s*&\s*(\d+)")
_PLAIN = re.compile(r"^(Grade|Class|Primary|Secondary|Year)\s+(\d+)")


def _year_keys(heading: str) -> list[str]:
    """Template-matching year_level key(s) for one `###` heading, or []."""
    head = heading.split("—")[0].split(":")[0].strip()

    # "Year 3 (Primary 3)" / "Algebra 1 (typically Grade 9)" -> parenthetical wins
    paren = _PARENTHETICAL.search(head)
    if paren:
        inner = paren.group(1)
        band = _BAND.match(inner)
        if band:                       # "Secondary 3 & 4"
            word = inner.split()[0]
            return [f"{word} {band.group(2)}", f"{word} {band.group(3)}"]
        return [inner]

    band = _BAND.match(head)           # "Grades 9 & 10"
    if band:
        word = {"Grades": "Grade", "Years": "Year"}.get(band.group(1), band.group(1))
        return [f"{word} {band.group(2)}", f"{word} {band.group(3)}"]

    plain = _PLAIN.match(head)         # "Class 7", "Grade 4"
    if plain:
        return [f"{plain.group(1)} {plain.group(2)}"]
    return []                          # pillar headings etc. -- caller decides


def _strands(block: str) -> list[str]:
    """Strand names = the text before the first colon of each top-level bullet."""
    out: list[str] = []
    for line in block.splitlines():
        if not line.startswith("- "):
            continue               # sub-bullets ("  - ") are detail, not strands
        name = line[2:].split(":", 1)[0].strip()
        if name and name not in out:
            out.append(name)
    return out


def _sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^### ", text, flags=re.M)[1:]
    return [(p.split("\n", 1)[0].strip(), p.split("\n", 1)[1] if "\n" in p else "") for p in parts]


def build(stem: str) -> dict[str, list[str]]:
    text = (REFS / f"{stem}_reference.md").read_text(encoding="utf-8")
    years: dict[str, list[str]] = {}
    orphans: list[str] = []            # headings with no year (US science pillars)
    for heading, body in _sections(text):
        strands = _strands(body)
        if not strands:
            continue
        keys = _year_keys(heading)
        if not keys:
            orphans.extend(strands)
            continue
        for key in keys:
            for s in strands:
                years.setdefault(key, [])
                if s not in years[key]:
                    years[key].append(s)
    if orphans:                        # "mastery by end of Grade 8" -> 6, 7 and 8
        for grade in ("Grade 6", "Grade 7", "Grade 8"):
            for s in orphans:
                years.setdefault(grade, [])
                if s not in years[grade]:
                    years[grade].append(s)
    return years


def main() -> int:
    check = "--check" in sys.argv
    out: dict[str, dict] = {}
    for stem, (pack, subject) in SOURCES.items():
        out.setdefault(pack, {})[subject] = build(stem)

    for pack, subjects in out.items():
        payload = {
            "_meta": {
                "source": "docs/design/country_references/ (maintainer-supplied, 2026-08-21), "
                          "translated by mentar.tools.build_country_reference",
                "authority": "Strand names are the AUDIT VOCABULARY, taken verbatim from the "
                             "reference markdown. Not a licence claim, not an alignment claim.",
                "normalisation": [
                    "SG: the parenthetical level (Primary/Secondary/Pre-U N) is the key, "
                    "matching what SG templates put in year_level.",
                    "Bands supplied as one block are assigned to BOTH years unchanged "
                    "(SG English Sec 3&4, US English Grades 9&10) -- the source did not split them.",
                    "US maths high school is course-named; the parenthetical grade is the key "
                    "and the course name is kept as a strand so the pathway stays visible.",
                    "US science grades 6-8 state mastery 'by end of Grade 8'; the pillar union "
                    "is assigned to all three grades, as the source says.",
                ],
            },
            **subjects,
        }
        path = REPO / "docs" / "design" / f"curriculum_reference_{pack.split('_')[0].lower()}.json"
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if check:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            status = "OK" if existing == text else "STALE — re-run without --check"
            print(f"{path.name}: {status}")
        else:
            path.write_text(text, encoding="utf-8")
            n = sum(len(v) for s in subjects.values() for v in s.values())
            print(f"wrote {path.name}: {len(subjects)} subjects, {n} strand entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
