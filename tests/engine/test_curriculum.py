"""engine/curriculum.py — load_template_subject (A7)."""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.curriculum import load_template_subject


def test_reads_subject_field_from_real_pilot_templates():
    tpl = REPO / "curriculum" / "templates" / "_pilot"
    assert load_template_subject(tpl / "fractions.md") == "mathematics"
    assert load_template_subject(tpl / "science.md") == "science"


def test_defaults_to_maths_when_subject_field_absent(tmp_path):
    p = tmp_path / "no_subject.md"
    p.write_text("---\ntemplate_id: t\nconcepts: []\n---\n\nbody\n", encoding="utf-8")
    assert load_template_subject(p) == "maths"


if __name__ == "__main__":
    test_reads_subject_field_from_real_pilot_templates()
    print("  ✓ test_reads_subject_field_from_real_pilot_templates")
    test_defaults_to_maths_when_subject_field_absent(pathlib.Path("/tmp"))
    print("  ✓ test_defaults_to_maths_when_subject_field_absent")
