"""Tests for R3.1 — template catalog auto-discovery + named item-source registry.

    python3 tests/engine/test_template_catalog.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.curriculum import (  # noqa: E402
    derive_subject_key,
    load_curriculum,
    load_template_meta,
)
from mentar.engine.item_sources import build_registry  # noqa: E402

_TPL = REPO_ROOT / "curriculum" / "templates"

# The exact catalog the hardcoded SUBJECTS dict carried before R3.1 -- the scan
# must reproduce these keys/labels/item_sources exactly (session-cookie
# stability). Keys are now derived FULLY AUTOMATICALLY from directory
# structure (derive_subject_key) -- no template needs a subject_key: override,
# proven by its absence below.
_EXPECTED = {
    "curriculum/templates/_pilot/fractions.md": {
        "key": "fractions", "label": "Fractions 🍕", "item_source": "pilot_fractions",
    },
    "curriculum/templates/_pilot/arithmetic.md": {
        "key": "arithmetic", "label": "Maths: + − × 🔢", "item_source": "arithmetic",
    },
    "curriculum/templates/_pilot/science.md": {
        "key": "science", "label": "Science 🔬", "item_source": "science",
    },
    "curriculum/templates/AU_ACARA/year3_maths.md": {
        "key": "au_acara_year3_maths", "label": "Maths — Year 3 🇦🇺", "item_source": "au_year3",
    },
    "curriculum/templates/AU_ACARA/year4_maths.md": {
        "key": "au_acara_year4_maths", "label": "Maths — Year 4 🇦🇺", "item_source": "au_year4",
    },
    "curriculum/templates/AU_ACARA/year2_maths.md": {
        "key": "au_acara_year2_maths", "label": "Maths — Year 2 🇦🇺", "item_source": "au_year2",
    },
    "curriculum/templates/AU_ACARA/year2_science.md": {
        "key": "au_acara_year2_science", "label": "Science — Year 2 🇦🇺", "item_source": "au_science_year2",
    },
    "curriculum/templates/AU_ACARA/year3_science.md": {
        "key": "au_acara_year3_science", "label": "Science — Year 3 🇦🇺", "item_source": "au_science_year3",
    },
    "curriculum/templates/AU_ACARA/year4_science.md": {
        "key": "au_acara_year4_science", "label": "Science — Year 4 🇦🇺", "item_source": "au_science_year4",
    },
    "curriculum/templates/AU_ACARA/year5_science.md": {
        "key": "au_acara_year5_science", "label": "Science — Year 5 🇦🇺", "item_source": "au_science_year5",
    },
    "curriculum/templates/AU_ACARA/year6_science.md": {
        "key": "au_acara_year6_science", "label": "Science — Year 6 🇦🇺", "item_source": "au_science_year6",
    },
    "curriculum/templates/AU_ACARA/year7_science.md": {
        "key": "au_acara_year7_science", "label": "Science — Year 7 🇦🇺", "item_source": "au_science_year7",
    },
    "curriculum/templates/AU_ACARA/year8_science.md": {
        "key": "au_acara_year8_science", "label": "Science — Year 8 🇦🇺", "item_source": "au_science_year8",
    },
    "curriculum/templates/AU_ACARA/year5_maths.md": {
        "key": "au_acara_year5_maths", "label": "Maths — Year 5 🇦🇺", "item_source": "au_year5",
    },
    "curriculum/templates/AU_ACARA/year6_maths.md": {
        "key": "au_acara_year6_maths", "label": "Maths — Year 6 🇦🇺", "item_source": "au_year6",
    },
    "curriculum/templates/AU_ACARA/year7_maths.md": {
        "key": "au_acara_year7_maths", "label": "Maths — Year 7 🇦🇺", "item_source": "au_year7",
    },
    "curriculum/templates/AU_ACARA/year8_maths.md": {
        "key": "au_acara_year8_maths", "label": "Maths — Year 8 🇦🇺", "item_source": "au_year8",
    },
    "curriculum/templates/AU_ACARA/year9_maths.md": {
        "key": "au_acara_year9_maths", "label": "Maths — Year 9 🇦🇺", "item_source": "au_year9",
    },
    "curriculum/templates/AU_ACARA/year10_maths.md": {
        "key": "au_acara_year10_maths", "label": "Maths — Year 10 🇦🇺", "item_source": "au_year10",
    },
    "curriculum/templates/AU_ACARA/year11_maths.md": {
        "key": "au_acara_year11_maths", "label": "Maths — Year 11 🇦🇺", "item_source": "au_year11",
    },
    "curriculum/templates/AU_ACARA/year12_maths.md": {
        "key": "au_acara_year12_maths", "label": "Maths — Year 12 🇦🇺", "item_source": "au_year12",
    },
    "curriculum/templates/AU_ACARA/year7_english.md": {
        "key": "au_acara_year7_english", "label": "English — Year 7 🇦🇺", "item_source": "au_english_year7",
    },
    "curriculum/templates/AU_ACARA/year8_english.md": {
        "key": "au_acara_year8_english", "label": "English — Year 8 🇦🇺", "item_source": "au_english_year8",
    },
    "curriculum/templates/AU_ACARA/year2_english.md": {
        "key": "au_acara_year2_english", "label": "English — Year 2 🇦🇺", "item_source": "au_english_year2",
    },
    "curriculum/templates/AU_ACARA/year3_english.md": {
        "key": "au_acara_year3_english", "label": "English — Year 3 🇦🇺", "item_source": "au_english_year3",
    },
    "curriculum/templates/AU_ACARA/year4_english.md": {
        "key": "au_acara_year4_english", "label": "English — Year 4 🇦🇺", "item_source": "au_english_year4",
    },
    "curriculum/templates/AU_ACARA/year5_english.md": {
        "key": "au_acara_year5_english", "label": "English — Year 5 🇦🇺", "item_source": "au_english_year5",
    },
    "curriculum/templates/AU_ACARA/year6_english.md": {
        "key": "au_acara_year6_english", "label": "English — Year 6 🇦🇺", "item_source": "au_english_year6",
    },
    "curriculum/templates/practice/maths.md": {
        "key": "practice_maths", "label": "Maths practice ➗", "item_source": "maths_practice",
    },
    "curriculum/templates/practice/english.md": {
        "key": "practice_english", "label": "English practice 📖", "item_source": "english_practice",
    },
    "curriculum/templates/IN_GENERIC/class3_maths.md": {
        "key": "in_generic_class3_maths", "label": "Maths — Class 3 🇮🇳 (general)",
        "item_source": "in_generic_maths",
    },
    "curriculum/templates/SG_GENERIC/p2_maths.md": {
        "key": "sg_generic_p2_maths", "label": "Maths — Primary 2 🇸🇬 (general)", "item_source": "sg_p2_maths",
    },
    "curriculum/templates/SG_GENERIC/p3_maths.md": {
        "key": "sg_generic_p3_maths", "label": "Maths — Primary 3 🇸🇬 (general)", "item_source": "sg_p3_maths",
    },
    "curriculum/templates/SG_GENERIC/p4_maths.md": {
        "key": "sg_generic_p4_maths", "label": "Maths — Primary 4 🇸🇬 (general)", "item_source": "sg_p4_maths",
    },
    "curriculum/templates/SG_GENERIC/p5_maths.md": {
        "key": "sg_generic_p5_maths", "label": "Maths — Primary 5 🇸🇬 (general)", "item_source": "sg_p5_maths",
    },
    "curriculum/templates/SG_GENERIC/p6_maths.md": {
        "key": "sg_generic_p6_maths", "label": "Maths — Primary 6 🇸🇬 (general)", "item_source": "sg_p6_maths",
    },
    "curriculum/templates/SG_GENERIC/s1_maths.md": {
        "key": "sg_generic_s1_maths", "label": "Maths — Secondary 1 🇸🇬 (general)", "item_source": "sg_s1_maths",
    },
    "curriculum/templates/SG_GENERIC/s2_maths.md": {
        "key": "sg_generic_s2_maths", "label": "Maths — Secondary 2 🇸🇬 (general)", "item_source": "sg_s2_maths",
    },
    "curriculum/templates/US_GENERIC/g2_maths.md": {
        "key": "us_generic_g2_maths", "label": "Maths — Grade 2 🇺🇸 (general)", "item_source": "us_g2_maths",
    },
    "curriculum/templates/US_GENERIC/g3_maths.md": {
        "key": "us_generic_g3_maths", "label": "Maths — Grade 3 🇺🇸 (general)", "item_source": "us_g3_maths",
    },
    "curriculum/templates/US_GENERIC/g4_maths.md": {
        "key": "us_generic_g4_maths", "label": "Maths — Grade 4 🇺🇸 (general)", "item_source": "us_g4_maths",
    },
    "curriculum/templates/US_GENERIC/g5_maths.md": {
        "key": "us_generic_g5_maths", "label": "Maths — Grade 5 🇺🇸 (general)", "item_source": "us_g5_maths",
    },
    "curriculum/templates/US_GENERIC/g6_maths.md": {
        "key": "us_generic_g6_maths", "label": "Maths — Grade 6 🇺🇸 (general)", "item_source": "us_g6_maths",
    },
    "curriculum/templates/US_GENERIC/g7_maths.md": {
        "key": "us_generic_g7_maths", "label": "Maths — Grade 7 🇺🇸 (general)", "item_source": "us_g7_maths",
    },
    "curriculum/templates/US_GENERIC/g8_maths.md": {
        "key": "us_generic_g8_maths", "label": "Maths — Grade 8 🇺🇸 (general)", "item_source": "us_g8_maths",
    },
    "curriculum/templates/IN_GENERIC/c2_maths.md": {
        "key": "in_generic_c2_maths", "label": "Maths — Class 2 🇮🇳 (general)", "item_source": "in_c2_maths",
    },
    "curriculum/templates/IN_GENERIC/c4_maths.md": {
        "key": "in_generic_c4_maths", "label": "Maths — Class 4 🇮🇳 (general)", "item_source": "in_c4_maths",
    },
    "curriculum/templates/IN_GENERIC/c5_maths.md": {
        "key": "in_generic_c5_maths", "label": "Maths — Class 5 🇮🇳 (general)", "item_source": "in_c5_maths",
    },
    "curriculum/templates/IN_GENERIC/c6_maths.md": {
        "key": "in_generic_c6_maths", "label": "Maths — Class 6 🇮🇳 (general)", "item_source": "in_c6_maths",
    },
    "curriculum/templates/IN_GENERIC/c7_maths.md": {
        "key": "in_generic_c7_maths", "label": "Maths — Class 7 🇮🇳 (general)", "item_source": "in_c7_maths",
    },
    "curriculum/templates/IN_GENERIC/c8_maths.md": {
        "key": "in_generic_c8_maths", "label": "Maths — Class 8 🇮🇳 (general)", "item_source": "in_c8_maths",
    },
    "curriculum/templates/SG_GENERIC/p2_english.md": {
        "key": "sg_generic_p2_english", "label": "English — Primary 2 🇸🇬 (general)", "item_source": "sg_p2_english",
    },
    "curriculum/templates/SG_GENERIC/p3_english.md": {
        "key": "sg_generic_p3_english", "label": "English — Primary 3 🇸🇬 (general)", "item_source": "sg_p3_english",
    },
    "curriculum/templates/SG_GENERIC/p4_english.md": {
        "key": "sg_generic_p4_english", "label": "English — Primary 4 🇸🇬 (general)", "item_source": "sg_p4_english",
    },
    "curriculum/templates/SG_GENERIC/p5_english.md": {
        "key": "sg_generic_p5_english", "label": "English — Primary 5 🇸🇬 (general)", "item_source": "sg_p5_english",
    },
    "curriculum/templates/SG_GENERIC/p6_english.md": {
        "key": "sg_generic_p6_english", "label": "English — Primary 6 🇸🇬 (general)", "item_source": "sg_p6_english",
    },
    "curriculum/templates/SG_GENERIC/s1_english.md": {
        "key": "sg_generic_s1_english", "label": "English — Secondary 1 🇸🇬 (general)", "item_source": "sg_s1_english",
    },
    "curriculum/templates/SG_GENERIC/s2_english.md": {
        "key": "sg_generic_s2_english", "label": "English — Secondary 2 🇸🇬 (general)", "item_source": "sg_s2_english",
    },
    "curriculum/templates/US_GENERIC/g2_english.md": {
        "key": "us_generic_g2_english", "label": "English — Grade 2 🇺🇸 (general)", "item_source": "us_g2_english",
    },
    "curriculum/templates/US_GENERIC/g3_english.md": {
        "key": "us_generic_g3_english", "label": "English — Grade 3 🇺🇸 (general)", "item_source": "us_g3_english",
    },
    "curriculum/templates/US_GENERIC/g4_english.md": {
        "key": "us_generic_g4_english", "label": "English — Grade 4 🇺🇸 (general)", "item_source": "us_g4_english",
    },
    "curriculum/templates/US_GENERIC/g5_english.md": {
        "key": "us_generic_g5_english", "label": "English — Grade 5 🇺🇸 (general)", "item_source": "us_g5_english",
    },
    "curriculum/templates/US_GENERIC/g6_english.md": {
        "key": "us_generic_g6_english", "label": "English — Grade 6 🇺🇸 (general)", "item_source": "us_g6_english",
    },
    "curriculum/templates/US_GENERIC/g7_english.md": {
        "key": "us_generic_g7_english", "label": "English — Grade 7 🇺🇸 (general)", "item_source": "us_g7_english",
    },
    "curriculum/templates/US_GENERIC/g8_english.md": {
        "key": "us_generic_g8_english", "label": "English — Grade 8 🇺🇸 (general)", "item_source": "us_g8_english",
    },
    "curriculum/templates/IN_GENERIC/c2_english.md": {
        "key": "in_generic_c2_english", "label": "English — Class 2 🇮🇳 (general)", "item_source": "in_c2_english",
    },
    "curriculum/templates/IN_GENERIC/c3_english.md": {
        "key": "in_generic_c3_english", "label": "English — Class 3 🇮🇳 (general)", "item_source": "in_c3_english",
    },
    "curriculum/templates/IN_GENERIC/c4_english.md": {
        "key": "in_generic_c4_english", "label": "English — Class 4 🇮🇳 (general)", "item_source": "in_c4_english",
    },
    "curriculum/templates/IN_GENERIC/c5_english.md": {
        "key": "in_generic_c5_english", "label": "English — Class 5 🇮🇳 (general)", "item_source": "in_c5_english",
    },
    "curriculum/templates/IN_GENERIC/c6_english.md": {
        "key": "in_generic_c6_english", "label": "English — Class 6 🇮🇳 (general)", "item_source": "in_c6_english",
    },
    "curriculum/templates/IN_GENERIC/c7_english.md": {
        "key": "in_generic_c7_english", "label": "English — Class 7 🇮🇳 (general)", "item_source": "in_c7_english",
    },
    "curriculum/templates/IN_GENERIC/c8_english.md": {
        "key": "in_generic_c8_english", "label": "English — Class 8 🇮🇳 (general)", "item_source": "in_c8_english",
    },
    "curriculum/templates/IN_GENERIC/c2_science.md": {
        "key": "in_generic_c2_science", "label": "Science — Class 2 🇮🇳 (general)", "item_source": "in_c2_science",
    },
    "curriculum/templates/IN_GENERIC/c3_science.md": {
        "key": "in_generic_c3_science", "label": "Science — Class 3 🇮🇳 (general)", "item_source": "in_c3_science",
    },
    "curriculum/templates/IN_GENERIC/c4_science.md": {
        "key": "in_generic_c4_science", "label": "Science — Class 4 🇮🇳 (general)", "item_source": "in_c4_science",
    },
    "curriculum/templates/IN_GENERIC/c5_science.md": {
        "key": "in_generic_c5_science", "label": "Science — Class 5 🇮🇳 (general)", "item_source": "in_c5_science",
    },
    "curriculum/templates/IN_GENERIC/c6_science.md": {
        "key": "in_generic_c6_science", "label": "Science — Class 6 🇮🇳 (general)", "item_source": "in_c6_science",
    },
    "curriculum/templates/IN_GENERIC/c7_science.md": {
        "key": "in_generic_c7_science", "label": "Science — Class 7 🇮🇳 (general)", "item_source": "in_c7_science",
    },
    "curriculum/templates/IN_GENERIC/c8_science.md": {
        "key": "in_generic_c8_science", "label": "Science — Class 8 🇮🇳 (general)", "item_source": "in_c8_science",
    },
    "curriculum/templates/SG_GENERIC/p2_science.md": {
        "key": "sg_generic_p2_science", "label": "Science — Primary 2 🇸🇬 (general)", "item_source": "sg_p2_science",
    },
    "curriculum/templates/SG_GENERIC/p3_science.md": {
        "key": "sg_generic_p3_science", "label": "Science — Primary 3 🇸🇬 (general)", "item_source": "sg_p3_science",
    },
    "curriculum/templates/SG_GENERIC/p4_science.md": {
        "key": "sg_generic_p4_science", "label": "Science — Primary 4 🇸🇬 (general)", "item_source": "sg_p4_science",
    },
    "curriculum/templates/SG_GENERIC/p5_science.md": {
        "key": "sg_generic_p5_science", "label": "Science — Primary 5 🇸🇬 (general)", "item_source": "sg_p5_science",
    },
    "curriculum/templates/SG_GENERIC/p6_science.md": {
        "key": "sg_generic_p6_science", "label": "Science — Primary 6 🇸🇬 (general)", "item_source": "sg_p6_science",
    },
    "curriculum/templates/SG_GENERIC/s1_science.md": {
        "key": "sg_generic_s1_science", "label": "Science — Secondary 1 🇸🇬 (general)", "item_source": "sg_s1_science",
    },
    "curriculum/templates/SG_GENERIC/s2_science.md": {
        "key": "sg_generic_s2_science", "label": "Science — Secondary 2 🇸🇬 (general)", "item_source": "sg_s2_science",
    },
    "curriculum/templates/US_GENERIC/g2_science.md": {
        "key": "us_generic_g2_science", "label": "Science — Grade 2 🇺🇸 (general)", "item_source": "us_g2_science",
    },
    "curriculum/templates/US_GENERIC/g3_science.md": {
        "key": "us_generic_g3_science", "label": "Science — Grade 3 🇺🇸 (general)", "item_source": "us_g3_science",
    },
    "curriculum/templates/US_GENERIC/g4_science.md": {
        "key": "us_generic_g4_science", "label": "Science — Grade 4 🇺🇸 (general)", "item_source": "us_g4_science",
    },
    "curriculum/templates/US_GENERIC/g5_science.md": {
        "key": "us_generic_g5_science", "label": "Science — Grade 5 🇺🇸 (general)", "item_source": "us_g5_science",
    },
    "curriculum/templates/US_GENERIC/g6_science.md": {
        "key": "us_generic_g6_science", "label": "Science — Grade 6 🇺🇸 (general)", "item_source": "us_g6_science",
    },
    "curriculum/templates/US_GENERIC/g7_science.md": {
        "key": "us_generic_g7_science", "label": "Science — Grade 7 🇺🇸 (general)", "item_source": "us_g7_science",
    },
    "curriculum/templates/US_GENERIC/g8_science.md": {
        "key": "us_generic_g8_science", "label": "Science — Grade 8 🇺🇸 (general)", "item_source": "us_g8_science",
    },
    "curriculum/templates/AU_ACARA/year9_english.md": {
        "key": "au_acara_year9_english", "label": "English — Year 9 🇦🇺", "item_source": "au_english_year9",
    },
    "curriculum/templates/AU_ACARA/year10_english.md": {
        "key": "au_acara_year10_english", "label": "English — Year 10 🇦🇺", "item_source": "au_english_year10",
    },
    "curriculum/templates/AU_ACARA/year11_english.md": {
        "key": "au_acara_year11_english", "label": "English — Year 11 🇦🇺", "item_source": "au_english_year11",
    },
    "curriculum/templates/AU_ACARA/year12_english.md": {
        "key": "au_acara_year12_english", "label": "English — Year 12 🇦🇺", "item_source": "au_english_year12",
    },
    "curriculum/templates/AU_ACARA/year9_science.md": {
        "key": "au_acara_year9_science", "label": "Science — Year 9 🇦🇺", "item_source": "au_science_year9",
    },
    "curriculum/templates/AU_ACARA/year10_science.md": {
        "key": "au_acara_year10_science", "label": "Science — Year 10 🇦🇺", "item_source": "au_science_year10",
    },
    "curriculum/templates/AU_ACARA/year11_biology.md": {
        "key": "au_acara_year11_biology", "label": "Biology — Year 11 🇦🇺", "item_source": "au11_biology",
    },
    "curriculum/templates/AU_ACARA/year11_chemistry.md": {
        "key": "au_acara_year11_chemistry", "label": "Chemistry — Year 11 🇦🇺", "item_source": "au11_chemistry",
    },
    "curriculum/templates/AU_ACARA/year11_physics.md": {
        "key": "au_acara_year11_physics", "label": "Physics — Year 11 🇦🇺", "item_source": "au11_physics",
    },
    "curriculum/templates/AU_ACARA/year12_biology.md": {
        "key": "au_acara_year12_biology", "label": "Biology — Year 12 🇦🇺", "item_source": "au12_biology",
    },
    "curriculum/templates/AU_ACARA/year12_chemistry.md": {
        "key": "au_acara_year12_chemistry", "label": "Chemistry — Year 12 🇦🇺", "item_source": "au12_chemistry",
    },
    "curriculum/templates/AU_ACARA/year12_physics.md": {
        "key": "au_acara_year12_physics", "label": "Physics — Year 12 🇦🇺", "item_source": "au12_physics",
    },
    "curriculum/templates/IN_GENERIC/c11_biology.md": {
        "key": "in_generic_c11_biology", "label": "Biology — Class 11 🇮🇳", "item_source": "in_c11_biology",
    },
    "curriculum/templates/IN_GENERIC/c11_chemistry.md": {
        "key": "in_generic_c11_chemistry", "label": "Chemistry — Class 11 🇮🇳", "item_source": "in_c11_chemistry",
    },
    "curriculum/templates/IN_GENERIC/c11_physics.md": {
        "key": "in_generic_c11_physics", "label": "Physics — Class 11 🇮🇳", "item_source": "in_c11_physics",
    },
    "curriculum/templates/IN_GENERIC/c12_biology.md": {
        "key": "in_generic_c12_biology", "label": "Biology — Class 12 🇮🇳", "item_source": "in_c12_biology",
    },
    "curriculum/templates/IN_GENERIC/c12_chemistry.md": {
        "key": "in_generic_c12_chemistry", "label": "Chemistry — Class 12 🇮🇳", "item_source": "in_c12_chemistry",
    },
    "curriculum/templates/IN_GENERIC/c12_physics.md": {
        "key": "in_generic_c12_physics", "label": "Physics — Class 12 🇮🇳", "item_source": "in_c12_physics",
    },
    "curriculum/templates/SG_GENERIC/s3_biology.md": {
        "key": "sg_generic_s3_biology", "label": "Biology — Secondary 3 🇸🇬", "item_source": "sg_s3_biology",
    },
    "curriculum/templates/SG_GENERIC/s3_chemistry.md": {
        "key": "sg_generic_s3_chemistry", "label": "Chemistry — Secondary 3 🇸🇬", "item_source": "sg_s3_chemistry",
    },
    "curriculum/templates/SG_GENERIC/s3_physics.md": {
        "key": "sg_generic_s3_physics", "label": "Physics — Secondary 3 🇸🇬", "item_source": "sg_s3_physics",
    },
    "curriculum/templates/SG_GENERIC/s4_biology.md": {
        "key": "sg_generic_s4_biology", "label": "Biology — Secondary 4 🇸🇬", "item_source": "sg_s4_biology",
    },
    "curriculum/templates/SG_GENERIC/s4_chemistry.md": {
        "key": "sg_generic_s4_chemistry", "label": "Chemistry — Secondary 4 🇸🇬", "item_source": "sg_s4_chemistry",
    },
    "curriculum/templates/SG_GENERIC/s4_physics.md": {
        "key": "sg_generic_s4_physics", "label": "Physics — Secondary 4 🇸🇬", "item_source": "sg_s4_physics",
    },
    "curriculum/templates/US_GENERIC/g10_chemistry.md": {
        "key": "us_generic_g10_chemistry", "label": "Chemistry — Grade 10 🇺🇸", "item_source": "us_g10_chemistry",
    },
    "curriculum/templates/US_GENERIC/g11_physics.md": {
        "key": "us_generic_g11_physics", "label": "Physics — Grade 11 🇺🇸", "item_source": "us_g11_physics",
    },
    "curriculum/templates/US_GENERIC/g9_biology.md": {
        "key": "us_generic_g9_biology", "label": "Biology — Grade 9 🇺🇸", "item_source": "us_g9_biology",
    },
    "curriculum/templates/IN_GENERIC/c10_english.md": {
        "key": "in_generic_c10_english", "label": "English — Class 10 🇮🇳 (general)", "item_source": "in_c10_english",
    },
    "curriculum/templates/IN_GENERIC/c10_maths.md": {
        "key": "in_generic_c10_maths", "label": "Maths — Class 10 🇮🇳 (general)", "item_source": "in_c10_maths",
    },
    "curriculum/templates/IN_GENERIC/c11_english.md": {
        "key": "in_generic_c11_english", "label": "English — Class 11 🇮🇳 (general)", "item_source": "in_c11_english",
    },
    "curriculum/templates/IN_GENERIC/c11_maths.md": {
        "key": "in_generic_c11_maths", "label": "Maths — Class 11 🇮🇳 (general)", "item_source": "in_c11_maths",
    },
    "curriculum/templates/IN_GENERIC/c12_english.md": {
        "key": "in_generic_c12_english", "label": "English — Class 12 🇮🇳 (general)", "item_source": "in_c12_english",
    },
    "curriculum/templates/IN_GENERIC/c12_maths.md": {
        "key": "in_generic_c12_maths", "label": "Maths — Class 12 🇮🇳 (general)", "item_source": "in_c12_maths",
    },
    "curriculum/templates/IN_GENERIC/c9_english.md": {
        "key": "in_generic_c9_english", "label": "English — Class 9 🇮🇳 (general)", "item_source": "in_c9_english",
    },
    "curriculum/templates/IN_GENERIC/c9_maths.md": {
        "key": "in_generic_c9_maths", "label": "Maths — Class 9 🇮🇳 (general)", "item_source": "in_c9_maths",
    },
    "curriculum/templates/SG_GENERIC/s3_english.md": {
        "key": "sg_generic_s3_english", "label": "English — Secondary 3 🇸🇬 (general)", "item_source": "sg_s3_english",
    },
    "curriculum/templates/SG_GENERIC/s3_maths.md": {
        "key": "sg_generic_s3_maths", "label": "Maths — Secondary 3 🇸🇬 (general)", "item_source": "sg_s3_maths",
    },
    "curriculum/templates/SG_GENERIC/s4_english.md": {
        "key": "sg_generic_s4_english", "label": "English — Secondary 4 🇸🇬 (general)", "item_source": "sg_s4_english",
    },
    "curriculum/templates/SG_GENERIC/s4_maths.md": {
        "key": "sg_generic_s4_maths", "label": "Maths — Secondary 4 🇸🇬 (general)", "item_source": "sg_s4_maths",
    },
    "curriculum/templates/US_GENERIC/g10_english.md": {
        "key": "us_generic_g10_english", "label": "English — Grade 10 🇺🇸 (general)", "item_source": "us_g10_english",
    },
    "curriculum/templates/US_GENERIC/g10_maths.md": {
        "key": "us_generic_g10_maths", "label": "Maths — Grade 10 🇺🇸 (general)", "item_source": "us_g10_maths",
    },
    "curriculum/templates/US_GENERIC/g11_english.md": {
        "key": "us_generic_g11_english", "label": "English — Grade 11 🇺🇸 (general)", "item_source": "us_g11_english",
    },
    "curriculum/templates/US_GENERIC/g11_maths.md": {
        "key": "us_generic_g11_maths", "label": "Maths — Grade 11 🇺🇸 (general)", "item_source": "us_g11_maths",
    },
    "curriculum/templates/US_GENERIC/g12_english.md": {
        "key": "us_generic_g12_english", "label": "English — Grade 12 🇺🇸 (general)", "item_source": "us_g12_english",
    },
    "curriculum/templates/US_GENERIC/g12_maths.md": {
        "key": "us_generic_g12_maths", "label": "Maths — Grade 12 🇺🇸 (general)", "item_source": "us_g12_maths",
    },
    "curriculum/templates/US_GENERIC/g9_english.md": {
        "key": "us_generic_g9_english", "label": "English — Grade 9 🇺🇸 (general)", "item_source": "us_g9_english",
    },
    "curriculum/templates/US_GENERIC/g9_maths.md": {
        "key": "us_generic_g9_maths", "label": "Maths — Grade 9 🇺🇸 (general)", "item_source": "us_g9_maths",
    },
    "curriculum/templates/IN_GENERIC/c10_science.md": {
        "key": "in_generic_c10_science", "label": "Science — Class 10 🇮🇳 (general)", "item_source": "in_c10_science",
    },
    "curriculum/templates/IN_GENERIC/c9_science.md": {
        "key": "in_generic_c9_science", "label": "Science — Class 9 🇮🇳 (general)", "item_source": "in_c9_science",
    },
}


def test_all_shipped_templates_discovered_with_expected_meta():
    # OKF reserved filenames (index.md, log.md) are bundle metadata, not curriculum concepts.
    found = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in _TPL.glob("**/*.md")
        if p.name not in ("index.md", "log.md")
    )
    assert found == sorted(_EXPECTED), found

    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert meta["label"] == expected["label"], rel
        assert meta["item_source"] == expected["item_source"], rel


def test_no_shipped_template_needs_the_subject_key_escape_hatch():
    """The automatic directory-based rule must be sufficient on its own -- if
    a future template needed subject_key: to avoid a collision, that would be
    a signal something's off with the automatic rule, not routine authoring."""
    for rel in _EXPECTED:
        meta = load_template_meta(REPO_ROOT / rel)
        assert meta["subject_key"] is None, f"{rel} shouldn't need the escape hatch"


def test_derived_keys_match_the_pre_r3_hardcoded_dict():
    """derive_subject_key() must reproduce every shipped template's key exactly
    (originally 5, at the R3 migration; more added since), with ZERO manual
    input from any template -- an already-issued session cookie must keep
    resolving to the same subject after this change."""
    for rel, expected in _EXPECTED.items():
        meta = load_template_meta(REPO_ROOT / rel)
        assert derive_subject_key(REPO_ROOT / rel, meta) == expected["key"], rel


def test_subject_key_front_matter_still_wins_when_present():
    """The escape hatch itself still works, for the rare genuine collision."""
    meta = {"subject_key": "custom_key"}
    assert derive_subject_key(REPO_ROOT / "curriculum/templates/AU_ACARA/year3_maths.md", meta) == "custom_key"


def test_authority_dir_resolved_past_a_year_subfolder():
    """R-MC: derive_subject_key must resolve the AUTHORITY dir (the one
    directly under templates/), not just the immediate parent -- so a future
    templates/<AUTHORITY>/<year>/*.md shape (MULTI_COUNTRY.md §2b, not built
    yet) can't silently change a template's key. Simulated with a path that
    doesn't need to exist on disk (derive_subject_key does no I/O)."""
    meta = {"subject_key": None}
    flat = derive_subject_key(REPO_ROOT / "curriculum/templates/AU_ACARA/year3_maths.md", meta)
    nested = derive_subject_key(
        REPO_ROOT / "curriculum/templates/AU_ACARA/2027/year3_maths.md", meta
    )
    assert flat == nested == "au_acara_year3_maths"


def test_item_source_registry_has_every_referenced_name():
    registry = build_registry(REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    for rel, expected in _EXPECTED.items():
        assert expected["item_source"] in registry, (rel, expected["item_source"])
        entry = registry[expected["item_source"]]
        assert "generators" in entry and "itembank" in entry


def test_unregistered_item_source_is_detectable():
    """The exact check web/app.py performs at startup (name not in the
    registry) — proven here at the unit level since a full app-module reload
    against a swapped-in bad template would need env-overriding a hardcoded
    templates directory, which is out of scope for this fix."""
    registry = build_registry(REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    assert "not_a_real_item_source" not in registry
    assert None not in registry  # a template with no item_source: field at all


def test_no_skill_id_collides_across_any_shipped_template():
    """R6.2/practice-pack guard: skill_id is NOT auto-namespaced the way the
    subject_key is -- individual node ids inside a template's `concepts:`
    list must be manually kept collision-free (AU's au3_/au4_ prefixes, the
    practice pack's practice_ prefix, the in_generic_ prefix). A collision
    would silently merge two unrelated skills' skill_state mastery rows in
    the DB. As of R10 every pack ships under curriculum/templates/ (India
    moved there from the old downloadable_packs/), so scanning templates/
    covers every shipped pack -- and a new one dropped in later is covered
    automatically, not just the ones in _EXPECTED."""
    owners: dict[str, str] = {}
    # OKF reserved filenames (index.md, log.md) are bundle metadata, not curriculum concepts.
    paths = sorted(p for p in _TPL.glob("**/*.md") if p.name not in ("index.md", "log.md"))
    for path in paths:
        curriculum = load_curriculum(path)
        for skill_id in curriculum:
            rel = str(path.relative_to(REPO_ROOT))
            assert skill_id not in owners, (
                f"skill_id {skill_id!r} used by both {owners.get(skill_id)!r} and {rel!r}"
            )
            owners[skill_id] = rel


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} template-catalog tests passed.")
