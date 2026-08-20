"""The serious curriculum check (maintainer, 2026-08-20).

Compares every AU template against the maintainer-supplied reference strand
structure (docs/design/curriculum_reference_au.json) and reports, per year and
subject: topic count, strands present, strands MISSING, and topics that carry
no `strand:` tag at all.

Why this exists, verbatim from the maintainer: "You guaranteed me that all is
in and I thought it was done. I tested it and found it missing." The README's
"Y2-12 coverage" table and the changelog's "breadth COMPLETE" were technically
true (every year existed) and materially misleading (Year 11 maths held 4
topics from one strand). This tool makes the claim auditable instead of
asserted: coverage is what the report says, nothing more.

A REPORT, deliberately not a failing test: today it names many known gaps
(Year 1 does not exist at all; junior years miss strands). Turning it into a
gate before the depth waves land would just be a permanently red light.

    python3 -m mentar.tools.audit_curriculum_coverage
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
REFERENCE = REPO / "docs" / "design" / "curriculum_reference_au.json"
TEMPLATES = REPO / "curriculum" / "templates" / "AU_ACARA"

# Course-split senior templates map onto the reference's parenthesised entries.
_COURSE_KEYS = {"essential": "Essential", "general": "General",
                "methods": "Methods", "specialist": "Specialist"}


def _template_year_key(fm: dict, filename: str) -> str:
    year = fm.get("year_level", "?")
    for k, label in _COURSE_KEYS.items():
        if k in filename:
            return f"{year} ({label})"
    return str(year)


def audit() -> list[dict]:
    ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
    rows = []
    for path in sorted(TEMPLATES.glob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("\n---\n")[0])
        subject = fm.get("subject", "?")
        concepts = fm.get("concepts", []) or []
        strands_present = {c.get("strand") for c in concepts if c.get("strand")}
        unstranded = sum(1 for c in concepts if not c.get("strand"))
        year_key = _template_year_key(fm, path.name)
        expected = ref.get(subject, {}).get(year_key)
        missing = sorted(set(expected) - strands_present) if expected else None
        rows.append({
            "file": path.name, "subject": subject, "year": year_key,
            "topics": len(concepts), "strands": sorted(strands_present),
            "unstranded": unstranded, "expected": expected, "missing": missing,
        })
    # Years in the reference with NO template at all — the loudest gap.
    covered = {(r["subject"], r["year"]) for r in rows}
    for subject, years in ref.items():
        if subject == "_meta":
            continue
        for year in years:
            if (subject, year) not in covered:
                rows.append({"file": "— ABSENT —", "subject": subject, "year": year,
                             "topics": 0, "strands": [], "unstranded": 0,
                             "expected": years[year], "missing": years[year]})
    return rows


def main() -> int:
    rows = audit()
    print(f"{'subject':12} {'year':22} {'topics':>6}  strand coverage")
    print("-" * 100)
    gaps = 0
    for r in sorted(rows, key=lambda x: (x["subject"], x["year"])):
        if r["expected"] is None:
            status = f"(no reference entry) strands: {', '.join(r['strands']) or '—'}"
        elif not r["missing"] and not r["unstranded"]:
            status = "COMPLETE vs reference"
        else:
            gaps += 1
            parts = []
            if r["missing"]:
                parts.append(f"MISSING: {', '.join(r['missing'])}")
            if r["unstranded"]:
                parts.append(f"{r['unstranded']} topics untagged")
            status = " · ".join(parts)
        print(f"{r['subject']:12} {r['year']:22} {r['topics']:>6}  {status}")
    print("-" * 100)
    print(f"{gaps} year/subject entries with gaps against the reference. "
          "This report IS the coverage claim — cite nothing stronger.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
