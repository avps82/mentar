"""engine/visual_scaffold.py — keyword-routed OKF scaffold lookup."""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.visual_scaffold import load_visual_scaffold

_ROOT = REPO / "curriculum" / "visual_scaffolds"


def test_matches_real_fractions_scaffold_by_keyword():
    body = load_visual_scaffold(_ROOT, "mathematics", "Equivalent fractions")
    assert "Bar model" in body


def test_matches_real_vocabulary_scaffold_by_keyword():
    """2026-08-15: this asserted that a SYNONYM label reached the generic Frayer
    word-box, which was true only because vocabulary.md also claimed the keyword
    "synonym". Keyword ownership is unique now (test_scaffold_hygiene.py), and a
    synonym question gets the synonyms/antonyms diagram -- which is the better
    answer, not a regression. The general vocabulary box is still reachable for
    the labels it actually owns."""
    synonyms = load_visual_scaffold(_ROOT, "english", "Vocabulary — synonym pairs")
    assert "SYNONYMS (same)" in synonyms, synonyms[:120]

    general = load_visual_scaffold(_ROOT, "english", "Vocabulary — word meaning and definition")
    assert "Frayer model" in general, general[:120]


def test_no_keyword_match_returns_empty_string():
    assert load_visual_scaffold(_ROOT, "mathematics", "Telling the time") == ""


def test_unmapped_subject_returns_empty_string():
    # "science" is itself mapped (see _SUBJECT_TO_SCAFFOLD_DIR) and "Forces and motion"
    # legitimately matches forces.md now that AU Science Year 7 shipped a forces topic --
    # that's correct routing, not a regression. Use a genuinely unmapped subject instead,
    # matching what this test's name actually claims to check.
    assert load_visual_scaffold(_ROOT, "history", "Forces and motion") == ""


def test_missing_scaffold_root_returns_empty_string(tmp_path):
    assert load_visual_scaffold(tmp_path, "mathematics", "fractions") == ""


if __name__ == "__main__":
    test_matches_real_fractions_scaffold_by_keyword()
    print("  ✓ test_matches_real_fractions_scaffold_by_keyword")
    test_matches_real_vocabulary_scaffold_by_keyword()
    print("  ✓ test_matches_real_vocabulary_scaffold_by_keyword")
    test_no_keyword_match_returns_empty_string()
    print("  ✓ test_no_keyword_match_returns_empty_string")
    test_unmapped_subject_returns_empty_string()
    print("  ✓ test_unmapped_subject_returns_empty_string")
    test_missing_scaffold_root_returns_empty_string(pathlib.Path("/tmp/nonexistent_scaffold_root"))
    print("  ✓ test_missing_scaffold_root_returns_empty_string")


def test_a_refining_keyword_beats_the_general_one_it_contains():
    """Found 2026-08-21 while checking whether a question picture and a scaffold
    diagram can contradict each other on screen.

    "Counting by 2s" matches year1_counting.md on 'counting' and
    year1_skip_counting.md on 'counting by 2s' -- one keyword each. The old
    tie-break was alphabetical, so the generic file won on filename order and a
    skip-counting question was shown a count-the-stars-one-by-one diagram: not a
    different example of the right method, but the WRONG method, sitting under a
    number line jumping in 2s.
    """
    skip = load_visual_scaffold(_ROOT, "mathematics", "Counting by 2s")
    assert "+2" in skip, skip[:200]
    # the general file stays reachable for the labels it actually owns
    ones = load_visual_scaffold(_ROOT, "mathematics", "Counting to 20")
    assert "touch each one once" in ones, ones[:200]


def test_containment_not_length_decides_a_tie():
    """Length was the first attempt at this tie-break and is wrong: 'vocabulary'
    is longer than 'synonym' yet far more generic, so ranking by length sent a
    synonym question to the generic Frayer box. Pinned so the cheaper-looking
    rule cannot come back."""
    body = load_visual_scaffold(_ROOT, "english", "Vocabulary — synonym pairs")
    assert "SYNONYMS (same)" in body, body[:200]


def test_a_chemistry_cell_does_not_get_the_biology_cell_diagram():
    """The costliest thing the containment tie-break fixed, and it was found by
    diffing routing for all 934 curriculum labels rather than by looking for it.

    "Electrochemical cells" matched cell_structures.md on 'cell' + 'cells' and
    senior_electrochemistry.md on 'electrochemical' + 'electrochemical cells' --
    two keywords each, so alphabetical order won and a senior CHEMISTRY question
    was illustrated with a plant-cell-vs-animal-cell comparison. Wrong subject
    entirely, in four country packs at once.
    """
    body = load_visual_scaffold(_ROOT, "chemistry", "Electrochemical cells")
    assert "anode" in body.lower(), body[:200]
    assert "PLANT CELL" not in body, "chemistry question got the biology cell diagram"


def test_compound_interest_gets_growth_not_a_percent_grid():
    """Same diff, same cause: 'interest' (percentages.md) vs 'compound interest'
    (senior_compound_growth.md), one hit each. A two-year compounding question
    was shown a hundred-grid for shading a flat percentage."""
    body = load_visual_scaffold(_ROOT, "mathematics", "Compound interest — two years")
    assert "year 2" in body.lower() or "factor" in body.lower(), body[:200]
    assert "Hundred grid" not in body, "compound growth got the flat-percentage grid"


def test_a_scaffold_matches_the_label_its_own_node_actually_uses():
    """Two files existed for exactly the node that never reached them, because
    their keywords were written in a different register than the curriculum
    label (found 2026-08-21 by listing every label still decided by alphabetical
    order and reading what it was being served):

    * senior_matrix_addition.md claimed [adding matrices, matrices] -- PLURAL --
      while the label is "Matrix addition", singular. It scored zero on its own
      node, so a Year-11 matrix question got the primary number-line jump
      strategy from addition_subtraction.md.
    * senior_organic_families.md claimed [organic families, organic] and tied
      with a reaction-RATES file on 'reaction', losing on filename order: an
      organic-families question was illustrated with collision theory.

    Both were fixed by giving the right file a compound keyword that CONTAINS
    its rival's, which is the steering the containment tie-break was built for.
    The sibling labels are asserted too -- a keyword edit that fixes one label by
    stealing another is not a fix.
    """
    matrices = load_visual_scaffold(_ROOT, "mathematics", "Matrix addition")
    assert "1+5" in matrices, matrices[:200]
    assert "Number line" not in matrices, "matrix question got the primary number line"
    assert "1+5" in load_visual_scaffold(_ROOT, "mathematics", "Adding matrices")

    organic = load_visual_scaffold(_ROOT, "chemistry", "Organic reaction types")
    assert "alkane" in organic, organic[:200]
    assert "collisions" not in load_visual_scaffold(_ROOT, "chemistry",
                                                    "Organic reaction types")
    assert "collisions" in load_visual_scaffold(_ROOT, "chemistry", "Rate of reaction")


def test_the_periodic_table_does_not_claim_the_word_group():
    """periodic_groups.md claimed the bare keywords 'group' AND 'groups', which
    beat vertebrates.md's single 'vertebrate' on COUNT -- so no tie-break could
    have saved it, and "Vertebrate groups" (fish/bird/mammal) was illustrated
    with the periodic table. "Grouping materials", a Year-3 natural-vs-
    manufactured question, got it too.

    Narrowed to 'periodic group'/'periodic groups'. "Grouping materials" now
    matches nothing, which is the right answer: materials_change.md is about
    bending and stretching, a different concept, and no picture beats a wrong
    one. The real chemistry labels are asserted to still have theirs.
    """
    vertebrates = load_visual_scaffold(_ROOT, "science", "Vertebrate groups")
    assert "invertebrate" in vertebrates.lower(), vertebrates[:200]
    for label in ("Groups of the periodic table", "Alkali metals", "Noble gases"):
        body = load_visual_scaffold(_ROOT, "chemistry", label)
        assert body.strip(), f"{label} lost its periodic-table scaffold"


def test_square_numbers_is_not_a_question_about_area():
    """Third instance of the same shape (2026-08-21): the right file exists but
    its keywords are written in a different register than the curriculum label.

    squares_roots.md claimed 'squaring' and 'perfect square' but not 'square
    number', so it scored ZERO on the label "Square numbers" and the node fell
    to area_perimeter.md on the bare word 'square' -- as in *area of a square*.
    A question about 4, 9, 16, 25 was illustrated with a rectangle's area and
    perimeter, in the US, IN and SG packs.

    The area labels are asserted too: 'square' legitimately belongs to
    area_perimeter.md for "Area of a square", and a fix that steals those is not
    a fix.
    """
    for label in ("Square numbers", "Squaring numbers", "Square roots"):
        body = load_visual_scaffold(_ROOT, "mathematics", label)
        assert "√" in body or "root" in body.lower(), f"{label}: {body[:160]}"
    for label in ("Area of a square", "Perimeter of a square", "Area of a rectangle"):
        body = load_visual_scaffold(_ROOT, "mathematics", label)
        assert "perimeter" in body.lower(), f"{label} lost the area/perimeter scaffold"
