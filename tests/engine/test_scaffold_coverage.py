"""Brute-force scaffold coverage — every concept node in every shipped
curriculum template must have a matching visual scaffold.

If this test fails, add keywords to an existing scaffold or create a new
scaffold file in curriculum/visual_scaffolds/<subject>/.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.visual_scaffold import _scan_scaffold_dir, load_visual_scaffold

TEMPLATES = REPO / "curriculum" / "templates"
SCAFFOLD_ROOT = REPO / "curriculum" / "visual_scaffolds"


def test_every_concept_node_has_a_scaffold():
    _scan_scaffold_dir.cache_clear()
    missing = []
    for tmpl in sorted(TEMPLATES.glob("**/*.md")):
        if tmpl.name in ("index.md", "log.md"):
            continue
        text = tmpl.read_text(encoding="utf-8")
        parts = text.split("\n---\n", 1)
        raw = yaml.safe_load(parts[0].removeprefix("---\n")) or {}
        subject = raw.get("subject", "")
        tid = raw.get("template_id", tmpl.stem)
        for node in raw.get("concepts", []):
            label = node.get("label", "")
            if not load_visual_scaffold(SCAFFOLD_ROOT, subject, label):
                missing.append(f"[{tid}] {label!r} ({subject})")
    assert not missing, (
        "These concept nodes have no matching visual scaffold "
        "(add keywords or a new file under curriculum/visual_scaffolds/):\n"
        + "\n".join(f"  {m}" for m in missing)
    )


def test_scaffold_routing_prefers_most_specific_match():
    """E1 Findings 1+2 regression (2026-08-11): most-keywords-matched wins.

    Finding 2: 'Adding fractions...' labels matched addition_subtraction.md
    first (alphabetical first-match) instead of fractions.md. Finding 1:
    whole-number place-value labels matched decimals.md via its bare
    'place value' keyword (now narrowed to 'decimal place value'; whole
    numbers route to the new place_value.md)."""
    _scan_scaffold_dir.cache_clear()
    cases = [
        # (label, unique marker of the CORRECT scaffold's body)
        ("Place value to 99", "Hundreds | Tens | Ones"),          # place_value.md
        ("Decimal place value (tenths and hundredths)", "place-value chart"),  # decimals.md
        ("Adding fractions with the same denominator", "1/2 shaded"),          # fractions.md
        ("Adding and subtracting fractions with unlike denominators", "1/2 shaded"),
        ("Adding numbers to 100", "number line"),                  # addition_subtraction.md
        # Finding 6 (full-corpus re-audit, 2026-08-11): the *_order_of_ops_negatives
        # nodes generate "What is -13 + 6 x 6?" -- the skill under test is PRECEDENCE,
        # but the label matched negative_numbers.md 3-2 (it had explicitly claimed the
        # keyword "order of operations with negative") and a child was shown a
        # thermometer/number-line where they needed a priority ladder. Fixing this
        # needed BOTH sides: dropping the keyword alone still lost the resulting 2-2
        # tie on the alphabetical tie-break ("negative_numbers" < "order_of_operations").
        ("Order of operations with negative numbers", "priority ladder"),
        ("Order of operations with negatives", "priority ladder"),
        # ...and the plain negatives nodes must NOT be dragged along with them.
        ("Negative numbers (temperature contexts)", "thermometer"),
    ]
    for label, marker in cases:
        body = load_visual_scaffold(SCAFFOLD_ROOT, "mathematics", label)
        assert body and marker.lower() in body.lower(), (
            f"label {label!r} routed to the wrong scaffold "
            f"(wanted body containing {marker!r}; got: {body[:120]!r})"
        )


def test_no_mc4_question_leaks_its_own_answer():
    """A meaning-label must never contain the word it is asking for.

    Found 2026-08-12: the homophone item asked "Which word means 'over there'
    or 'in that place'?" with the correct answer "there" -- printed inside its
    own stem, so a child could score it without knowing the homophone at all.
    Swept across every mc4 generator in the registry rather than one node,
    because the generic SG/US/IN packs reuse the same generator functions and
    replicated the same defect three times.
    """
    import random as _random

    from mentar.engine.item_sources import build_registry

    registry = build_registry(REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl")
    leaks, seen = [], set()
    for src in registry.values():
        for node, fn in src["generators"].items():
            if node in seen:
                continue
            seen.add(node)
            rng = _random.Random(11)
            for _ in range(40):
                res = fn(rng)
                if res[0] != "mc4" or len(res) < 5:
                    break
                idx = "ABCD".find(str(res[3]).strip().upper())
                if idx < 0 or idx >= len(res[4]):
                    continue
                correct = str(res[4][idx]).lower()
                stem = res[2].split("A)")[0].lower()
                if len(correct) > 3 and correct in stem:
                    others = [str(c).lower() for i, c in enumerate(res[4]) if i != idx]
                    # if the stem quotes every option it is a legitimate "which of
                    # these" framing; only a lone correct answer in the stem leaks
                    if not any(o in stem for o in others if len(o) > 3):
                        leaks.append((node, res[2][:120], correct))
                        break
    assert leaks == [], f"mc4 questions containing their own answer: {leaks}"

# The senior (Year 9-12) nodes added 2026-08-14, and the FIRST fenced diagram each
# one must route to. explain-mode's card path shows exactly that first block to a
# child (visual_scaffold.first_diagram), and keyword matching is count-based, so a
# later keyword edit elsewhere can silently steal a node: the routing check that
# built these found SIX real mis-routes (an irony question showing the simile
# table, a cohesion question showing claim/evidence, syntax-for-effect showing
# word origins...). Pinning the marker is what makes that regression loud.
_SENIOR_ROUTING = {
    # EVERY node label in the corpus, pinned to the first line of the diagram it
    # must receive. Built by walking the shipped templates, so it covers all 142
    # packs rather than the handful a hand-written list would.
    ('biology', 'Diffusion, osmosis and active transport'): 'DIFFUSION         high -> low conc',
    ('biology', 'Enzymes'): 'a PROTEIN catalyst',
    ('biology', 'Genotype and phenotype'): 'GENOTYPE   the alleles themselves ',
    ('biology', 'Homeostasis and negative feedback'): 'set point',
    ('biology', 'Photosynthesis and respiration'): 'PHOTOSYNTHESIS   carbon dioxide + ',
    ('biology', 'Trophic levels in a food chain'): 'PRODUCER (makes its own food)     ',
    ('chemistry', 'Groups of the periodic table'): 'GROUP 1   alkali metals   1 outer ',
    ('chemistry', 'Ionic, covalent and metallic bonding'): 'IONIC       metal + non-metal     ',
    ('chemistry', 'Oxidation and reduction'): 'Oxidation Is Loss    of electrons ',
    ('chemistry', 'Strong acids, weak acids and bases'): 'STRONG acid   nearly every molecul',
    ('chemistry', 'The mole and amount of substance'): 'HOW MANY particles?    amount of s',
    ('chemistry', 'What changes the rate of a reaction'): 'CHANGE                       EFFEC',
    ('english', 'Active and passive voice'): 'ACTIVE:   [SUBJECT does the action',
    ('english', 'Adverbial phrases'): 'ADVERBIAL PHRASE (tells HOW, WHEN ',
    ('english', 'Adverbs, pronouns and verbs'): 'The  quick  fox   jumps  gracefull',
    ('english', 'Allusion'): 'ALLUSION                          ',
    ('english', 'Antonyms (nuanced vocabulary)'): 'SYNONYMS (same)              ANTON',
    ('english', 'Antonyms (opposite words)'): 'SYNONYMS (same)              ANTON',
    ('english', 'Antonyms (richer vocabulary)'): 'SYNONYMS (same)              ANTON',
    ('english', 'Biased and balanced wording'): '"A MOB of protesters SWARMED the s',
    ('english', 'Claim, evidence and rebuttal'): 'CLAIM      what you are arguing   ',
    ('english', 'Cohesive devices between sentences'): 'CONTRAST          however, neverth',
    ('english', 'Common and proper nouns'): 'COMMON NOUN (no capital)     PROPE',
    ('english', 'Comparative and superlative adjectives'): 'PLAIN        TWO THINGS (-er)     ',
    ('english', 'Compound words'): 'sun + flower   =  sunflower     a ',
    ('english', 'Conjunctions and prepositions'): 'CONJUNCTION -- joins two ideas    ',
    ('english', "Contractions (don't, can't, it's)"): 'TWO WORDS      ->  CONTRACTION    ',
    ('english', 'Evaluative and neutral language'): 'EVALUATIVE (it judges)          NE',
    ('english', 'Formal and informal language'): 'FORMAL                        INFO',
    ('english', 'High and low modality'): 'LOW  <────────────────────────────',
    ('english', 'Homophones (their/there, to/too)'): 'SOUNDS THE SAME        MEANS      ',
    ('english', 'How English changes over time'): 'BORROWED from another language    ',
    ('english', 'Identifying tone'): 'CRITICAL    "careless", "ignored t',
    ('english', 'Idioms'): 'Phrase                          Li',
    ('english', 'Irony and satire'): 'LITERAL   means exactly what it sa',
    ('english', 'Main and subordinate clauses'): 'SIMPLE    [ The train left early. ',
    ('english', 'Matching register to audience'): 'FORMAL                        INFO',
    ('english', 'Naming the technique in a quotation'): 'Simile   → uses "like" or "as"    ',
    ('english', 'Naming, doing and describing words'): 'The  quick  fox   jumps  gracefull',
    ('english', 'Nominalisation (verb or adjective to noun)'): 'VERB / ADJECTIVE        NOMINALISA',
    ('english', 'Odd one out'): 'apple   banana   carrot   grape',
    ('english', 'Onomatopoeia'): 'buzz    crash    sizzle    whoosh ',
    ('english', 'Personification'): 'NON-HUMAN THING   +   A HUMAN ACTI',
    ('english', 'Plural forms'): 'Ending          Rule             E',
    ('english', 'Rhetorical devices in persuasive writing'): 'rhetorical question   asks without',
    ('english', 'Rhyming words'): 'pig   ->  big   dig   wig        (',
    ('english', "Similes (using 'like' or 'as')"): 'Simile   → uses "like" or "as"    ',
    ('english', 'Similes and metaphors'): 'Simile   → uses "like" or "as"    ',
    ('english', 'Simple synonyms'): 'SYNONYMS (same)              ANTON',
    ('english', 'Simple, compound and complex sentences'): 'SIMPLE    [ The train left early. ',
    ('english', 'Synonyms (nuanced vocabulary)'): 'SYNONYMS (same)              ANTON',
    ('english', 'Synonyms (richer vocabulary)'): 'SYNONYMS (same)              ANTON',
    ('english', 'Synonyms and antonyms'): 'SYNONYMS (same)              ANTON',
    ('english', 'Syntax chosen for effect'): 'SHORT sentence     "It failed."   ',
    ('english', 'Word connotation (positive/negative)'): 'POSITIVE          NEUTRAL         ',
    ('english', 'Word prefixes (un-, re-, dis-)'): 'PREFIX   MEANS            EXAMPLE ',
    ('english', 'Word suffixes (-ful, -less, -ness)'): 'SUFFIX   MEANS               EXAMP',
    ('mathematics', 'Adding and subtracting decimals'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Adding and subtracting integers'): '+6',
    ('mathematics', 'Adding fractions (different denominators)'): '|████|████|    |    |',
    ('mathematics', 'Adding fractions (same denominator)'): '|████|████|    |    |',
    ('mathematics', 'Adding fractions with different denominators'): '|████|████|    |    |',
    ('mathematics', 'Adding fractions with equal denominators'): '|████|████|    |    |',
    ('mathematics', 'Adding numbers'): '+6',
    ('mathematics', 'Adding numbers to 100'): '+6',
    ('mathematics', 'Adding numbers to 1000'): '+6',
    ('mathematics', 'Adding whole numbers'): '+6',
    ('mathematics', 'Addition (2-digit numbers)'): '+6',
    ('mathematics', 'Area and perimeter'): '+──────────────+',
    ('mathematics', 'Area and perimeter of a rectangle'): '+──────────────+',
    ('mathematics', 'Area as an algebraic expression'): 'width  = x',
    ('mathematics', 'Area as an algebraic expression (binomial sides)'): 'width  = x',
    ('mathematics', 'Combined perimeter as an algebraic expression'): 'width  = x',
    ('mathematics', 'Combining a quadratic and a linear expression'): 'a  =  3x + 2',
    ('mathematics', 'Combining algebraic expressions'): 'a  =  3x + 2',
    ('mathematics', 'Combining three algebraic expressions'): 'a  =  3x + 2',
    ('mathematics', 'Combining two quadratic expressions'): 'a  =  3x + 2',
    ('mathematics', 'Comparing fractions with equal denominators'): '|████|████|    |    |',
    ('mathematics', 'Compound-shape area as an algebraic expression'): 'width  = x',
    ('mathematics', 'Decimal place value'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Decimal place value (tenths)'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Difference of two related expressions'): 'a  =  3x + 2',
    ('mathematics', 'Distributive-law expressions from words'): '"3 more than"     ->   + 3',
    ('mathematics', 'Dividing a decimal by a decimal'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Dividing decimals'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Division facts'): '12 apples shared between 3 childre',
    ('mathematics', 'Division facts from the times tables'): '12 apples shared between 3 childre',
    ('mathematics', 'Division with a remainder (as a decimal)'): '12 apples shared between 3 childre',
    ('mathematics', 'Division with a remainder (as a fraction)'): '12 apples shared between 3 childre',
    ('mathematics', 'Division with a remainder, as a decimal'): '12 apples shared between 3 childre',
    ('mathematics', 'Division with a remainder, as a mixed number'): '12 apples shared between 3 childre',
    ('mathematics', 'Doubles and halves'): 'Count by 3s:',
    ('mathematics', 'Equal vs. unequal parts'): '|████|████|    |    |',
    ('mathematics', 'Equivalent fractions'): '|████|████|    |    |',
    ('mathematics', 'Equivalent fractions (1/2 = 2/4 = 3/6)'): '|████|████|    |    |',
    ('mathematics', 'Fraction as a part of a whole'): '|████|████|    |    |',
    ('mathematics', 'Fraction-to-decimal conversion'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Fractions as decimals'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Fractions as parts of a whole'): '|████|████|    |    |',
    ('mathematics', 'Fractions of a whole'): '|████|████|    |    |',
    ('mathematics', 'Halves and quarters'): '|████|████|    |    |',
    ('mathematics', 'Multiplying a decimal by a decimal'): '| Ones | . | Tenths | Hundredths |',
    ('mathematics', 'Multiplying a fraction by a whole number'): '|████|████|    |    |',
    ('mathematics', 'Multiplying decimals'): '| Ones | . | Tenths | Hundredths |',
    # Was pinned to '10°C' -- negative_numbers.md's THERMOMETER. The pin was
    # written from observed behaviour, so it froze the defect: a thermometer
    # shows where a directed number sits (right for adding/subtracting) and
    # says nothing about why two negatives multiply to a positive, which that
    # file carried only as one line of prose. Split out 2026-08-22. Second
    # time a pin here has recorded a bug as the expectation -- cf. 'Square
    # numbers', pinned to an area rectangle.
    ('mathematics', 'Multiplying negative numbers'): '(-) x (-) = (+)',
    ('mathematics', 'Multiplying whole numbers'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Negative numbers'): '10°C',
    ('mathematics', 'Negative numbers (temperature contexts)'): '10°C',
    ('mathematics', 'One-step equations'): 'x + 5        = 12',
    ('mathematics', 'Order of operations'): 'Step 1  B — Brackets          ( ) ',
    ('mathematics', 'Order of operations with negative numbers'): 'Step 1  B — Brackets          ( ) ',
    ('mathematics', 'Order of operations with negatives'): 'Step 1  B — Brackets          ( ) ',
    ('mathematics', 'Percentage increase'): '██████████  ← 10 shaded cells',
    ('mathematics', 'Percentage increase and decrease'): '██████████  ← 10 shaded cells',
    ('mathematics', 'Percentage of a quantity'): '██████████  ← 10 shaded cells',
    ('mathematics', 'Percentages of a quantity (10%, 25%, 50%, 75%)'): '██████████  ← 10 shaded cells',
    ('mathematics', 'Perimeter as an algebraic expression'): 'width  = x',
    ('mathematics', 'Place value'): 'Hundreds | Tens | Ones',
    ('mathematics', 'Place value to 99'): 'Hundreds | Tens | Ones',
    ('mathematics', 'Place value to 999'): 'Hundreds | Tens | Ones',
    ('mathematics', 'Place value to 9999'): 'Hundreds | Tens | Ones',
    ('mathematics', 'Revenue as a quadratic expression'): '"3 more than"     ->   + 3',
    ('mathematics', 'Sharing and grouping word problems'): '12 apples shared between 3 childre',
    ('mathematics', 'Sharing equally (word problems)'): '12 apples shared between 3 childre',
    ('mathematics', 'Skip counting and number patterns'): 'Count by 3s:',
    ('mathematics', 'Solving one-step equations'): 'x + 5        = 12',
    ('mathematics', 'Solving two-step equations'): 'x + 5        = 12',
    # Was pinned to '+──────────────+' -- area_perimeter.md's rectangle box --
    # which is precisely what this test's NAME says must not happen. The pin
    # had recorded the bug: squares_roots.md claimed 'squaring' but not
    # 'square number', so it scored zero on this label (fixed 2026-08-21).
    # Added 2026-08-22 after three nodes were found mis-routed for months while
    # test_every_concept_node_has_a_scaffold stayed green -- it asserts only that
    # SOME scaffold matches, so it cannot tell "attached" from "attached to the
    # right thing". "3D shapes" was being served a 3d-VECTOR magnitude formula.
    ('mathematics', '3D shapes'): 'triangular prism',
    ('mathematics', 'Moving on a grid'): '(3, 2) move 3 right',
    ('mathematics', 'Comparing lengths'): 'the bit sticking out',
    ('mathematics', 'Square numbers'): '4² = 4 × 4 = 16',
    ('mathematics', 'Squared expressions (area of a square)'): 'width  = x',
    ('mathematics', 'Squaring numbers'): '4² = 4 × 4 = 16',
    ('mathematics', 'Subtracting fractions with equal denominators'): '|████|████|    |    |',
    ('mathematics', 'Subtracting numbers'): '+6',
    ('mathematics', 'Subtracting numbers to 100'): '+6',
    ('mathematics', 'Subtracting numbers to 1000'): '+6',
    ('mathematics', 'Subtracting whole numbers'): '+6',
    ('mathematics', 'Subtraction (2-digit numbers)'): '+6',
    ('mathematics', 'Times tables'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Times tables (1-12)'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Times tables to 10 × 10'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Times tables: 2, 5 and 10'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Times tables: 3, 4, 5 and 10'): '(●●●)  (●●●)  (●●●)  (●●●)',
    ('mathematics', 'Two-step equations'): 'x + 5        = 12',
    ('mathematics', 'Unit fractions'): '|████|████|    |    |',
    ('mathematics', 'Unit fractions (1/2, 1/3, 1/4, 1/5, 1/10)'): '|████|████|    |    |',
    ('mathematics', 'Unit fractions (1/n)'): '|████|████|    |    |',
    ('mathematics', 'Whole-number division'): '12 apples shared between 3 childre',
    ('mathematics', 'Writing algebraic expressions from words'): '"3 more than"     ->   + 3',
    ('mathematics', 'Writing quadratic expressions from words'): '"3 more than"     ->   + 3',
    ('physics', 'Forms of energy'): 'GRAVITATIONAL POTENTIAL   lifted u',
    ('physics', "Newton's laws of motion"): 'FIRST   no resultant force  ->  no',
    ('physics', 'Scalars and vectors'): 'SCALAR   size only                ',
    ('physics', 'Series and parallel circuits'): 'SERIES                            ',
    ('physics', 'The electromagnetic spectrum'): 'LOWER ENERGY  <-------------------',
    ('physics', 'What is conserved in a collision'): 'ALWAYS conserved        total mome',
    ('science', 'Animal groups (mammal, bird, fish, insect)'): 'M — Movement',
    ('science', 'Body features that help survival (adaptations)'): 'BODY FEATURE (helps it survive)   ',
    ('science', 'Changes of state — adding or removing heat'): 'Property       | Solid      | Liqu',
    ('science', "Changing a material's shape (bend, twist, stretch)"): 'CAN BE BENT, TWISTED, STRETCHED   ',
    ('science', 'Contact and non-contact forces'): 'CONTACT FORCE (needs touching)    ',
    ('science', 'DNA, genes and chromosomes'): 'CELL  >  NUCLEUS  >  CHROMOSOME  >',
    ('science', 'Digestive and circulatory systems'): 'DIGESTIVE SYSTEM (breaks down food',
    ('science', 'Earth is a planet in the solar system'): 'IS A PLANET                     IS',
    ('science', 'Electrical conductors and insulators'): 'CONDUCTOR (lets electricity flow) ',
    ('science', 'Elements and compounds'): 'ELEMENT (only one type of atom)   ',
    ('science', 'Evidence for evolution'): 'FOSSIL RECORD      older rock laye',
    ('science', 'How sound is made (vibration)'): 'OBJECT MOVES BACK AND FORTH  →  AI',
    ('science', 'Inside the atom — protons, neutrons, electrons'): 'ELECTRONS  (negative, tiny, orbit ',
    ('science', 'Life cycle stages'): 'EGG  →  YOUNG FORM  →  ADULT FORM ',
    ('science', 'Living and non-living things'): 'M — Movement',
    ('science', 'Materials attracted to a magnet'): 'ATTRACTED TO A MAGNET             ',
    ('science', 'Plant and animal cell structures'): 'PLANT CELL ONLY                   ',
    ('science', 'Plate boundaries and the landforms they make'): 'MOVING APART            <──  │  ──',
    ('science', 'Producers and consumers'): 'PRODUCER (makes its own food)     ',
    ('science', 'Pure substances and mixtures'): 'PURE SUBSTANCE (one type of partic',
    ('science', 'Renewable and non-renewable energy'): 'RENEWABLE (naturally replaced,    ',
    ('science', 'Reversible and irreversible changes'): 'REVERSIBLE (can be undone)        ',
    ('science', 'Solids, liquids and gases'): 'Property       | Solid      | Liqu',
    ('science', 'Sources of heat'): 'GIVES OUT HEAT (a heat source)   D',
    ('science', 'Transparent and opaque materials'): 'TRANSPARENT (light passes through ',
    ('science', 'Transverse and longitudinal waves'): 'TRANSVERSE  — the shaking is ACROS',
    ('science', 'Types of chemical reaction'): 'COMBUSTION       fuel + oxygen    ',
    ('science', 'Vertebrates and invertebrates'): 'VERTEBRATE (has a backbone)      I',
    ('science', 'What dissolves in water'): 'DISSOLVES IN WATER              DO',
    ('science', 'Where living things live (habitats)'): 'LIVES MAINLY IN WATER           LI',
}


def test_senior_nodes_route_to_their_own_diagram():
    from mentar.engine.visual_scaffold import first_diagram

    _scan_scaffold_dir.cache_clear()
    wrong = []
    for (subject, label), marker in _SENIOR_ROUTING.items():
        body = load_visual_scaffold(SCAFFOLD_ROOT, subject, label)
        diagram = first_diagram(body) or ""
        if marker not in diagram:
            wrong.append(f"{label!r} -> {diagram.splitlines()[0][:60] if diagram else 'NO DIAGRAM'!r}")
    assert not wrong, (
        "these nodes' first scaffold diagram is not their own topic:\n"
        + "\n".join(f"  {w}" for w in wrong)
    )
