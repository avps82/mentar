"""Senior science generators — Physics, Chemistry and Biology as SEPARATE subjects.

Why this file exists rather than more entries in `science_items.py`: at senior
level science stops being one subject. An Australian Year 11 student enrols in
Physics, Chemistry or Biology; an Indian Class 11 student takes them as separate
papers; a Singaporean Secondary 3 student sits Pure Physics / Chemistry /
Biology. Shipping a merged "Science — Year 11" would misrepresent what a student
actually studies (maintainer decision, 2026-08-15: "senior science needs to
split... let's follow the curriculum"). Junior years stay combined, because there
they genuinely are combined.

Same discipline as every other generator module here:

* Fact tables with DISJOINT categories fed to `itemgen.mc_which_is`, so the
  deterministic verifier scores every answer and the model never decides
  correctness.
* Every generator passes `glosses`/`concept_name`, so every senior-science node
  gets an explain-mode Type-4 method card (docs/design/explain_mode_design.md).
* Content is common to all three countries at this level, so the progression
  lives ONCE here keyed by senior STAGE (1 = first senior year, 2 = second) and
  `SENIOR_LEVELS` maps each country's level names onto it — the same shape
  `generic_items.py` uses for the junior stages.

No claimed alignment: senior science is set by state/board certificate
authorities (VCE/HSC/QCE/SACE, CBSE/ICSE, Singapore-Cambridge), not by one
national content-description set. Content is universally-taught senior science.
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is

# ── Physics ──────────────────────────────────────────────────────────────────

_SCALAR_VECTOR = {
    "a VECTOR quantity (it has a direction as well as a size)": [
        "velocity", "force", "acceleration", "displacement", "momentum",
    ],
    "a SCALAR quantity (size only, no direction)": [
        "speed", "mass", "temperature", "energy", "distance",
    ],
}
_SCALAR_VECTOR_GLOSSES = {
    "a VECTOR quantity (it has a direction as well as a size)": "quoting it without a direction leaves the answer incomplete",
    "a SCALAR quantity (size only, no direction)": "a number and a unit say everything there is to say",
}

_ENERGY_FORMS = {
    "gravitational potential energy": [
        "a book held above a desk", "water stored behind a dam", "a raised pile driver",
    ],
    "kinetic energy": ["a rolling ball", "a moving car", "wind turning a turbine"],
    "elastic potential energy": ["a stretched rubber band", "a compressed spring"],
}
_ENERGY_FORMS_GLOSSES = {
    "gravitational potential energy": "stored because of HEIGHT in a gravitational field",
    "kinetic energy": "energy a thing has because it is MOVING",
    "elastic potential energy": "stored by stretching or squashing something springy",
}

_NEWTON_LAWS = {
    "Newton's FIRST law (an object keeps doing what it is doing unless a force acts)": [
        "a puck sliding on frictionless ice at constant speed",
        "passengers lurching forward when a bus brakes",
    ],
    "Newton's SECOND law (force = mass x acceleration)": [
        "the same push accelerating a light trolley more than a heavy one",
        "a harder kick giving the ball a greater acceleration",
    ],
    "Newton's THIRD law (every action has an equal and opposite reaction)": [
        "a rocket pushing gas down and rising up",
        "a swimmer pushing water back and moving forward",
    ],
}
_NEWTON_LAWS_GLOSSES = {
    "Newton's FIRST law (an object keeps doing what it is doing unless a force acts)": "no resultant force means no CHANGE in motion -- inertia",
    "Newton's SECOND law (force = mass x acceleration)": "a resultant force changes motion, and how much depends on the mass",
    "Newton's THIRD law (every action has an equal and opposite reaction)": "forces come in pairs, on two DIFFERENT objects",
}

_CIRCUIT_ARRANGEMENT = {
    "true of a SERIES circuit": [
        "the same current flows through every component",
        "removing one lamp breaks the whole circuit",
        "the supply voltage is shared between components",
    ],
    "true of a PARALLEL circuit": [
        "each branch gets the full supply voltage",
        "one lamp can fail while the others stay lit",
        "the total current splits between the branches",
    ],
}
_CIRCUIT_ARRANGEMENT_GLOSSES = {
    "true of a SERIES circuit": "one single loop, so current has nowhere else to go",
    "true of a PARALLEL circuit": "separate branches, each connected straight across the supply",
}

_EM_SPECTRUM = {
    "higher in energy than visible light": ["ultraviolet", "X-rays", "gamma rays"],
    "lower in energy than visible light": ["infrared", "microwaves", "radio waves"],
}
_EM_SPECTRUM_GLOSSES = {
    "higher in energy than visible light": "shorter wavelength and higher frequency than light we can see",
    "lower in energy than visible light": "longer wavelength and lower frequency than light we can see",
}

_CONSERVATION = {
    "conserved in every collision (total before = total after)": [
        "total momentum", "total energy", "total mass-energy",
    ],
    "NOT conserved in an inelastic collision": [
        "total kinetic energy", "the shape of the objects", "the objects' separate speeds",
    ],
}
_CONSERVATION_GLOSSES = {
    "conserved in every collision (total before = total after)": "the total is the same before and after, however messy the collision",
    "NOT conserved in an inelastic collision": "some of it is turned into heat, sound and deformation",
}


def gen_scalars_vectors(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _SCALAR_VECTOR,
                       glosses=_SCALAR_VECTOR_GLOSSES, concept_name="SCALARS AND VECTORS")


def gen_energy_forms(rng: random.Random):
    return mc_which_is(rng, "Which of these stores mainly {label}?", _ENERGY_FORMS,
                       glosses=_ENERGY_FORMS_GLOSSES, concept_name="FORMS OF ENERGY")


def gen_newton_laws(rng: random.Random):
    return mc_which_is(rng, "Which of these is an example of {label}?", _NEWTON_LAWS,
                       glosses=_NEWTON_LAWS_GLOSSES, concept_name="NEWTON'S LAWS OF MOTION")


def gen_circuit_arrangements(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CIRCUIT_ARRANGEMENT,
                       glosses=_CIRCUIT_ARRANGEMENT_GLOSSES, concept_name="SERIES AND PARALLEL CIRCUITS")


def gen_em_spectrum(rng: random.Random):
    return mc_which_is(rng, "Which of these radiations is {label}?", _EM_SPECTRUM,
                       glosses=_EM_SPECTRUM_GLOSSES, concept_name="THE ELECTROMAGNETIC SPECTRUM")


def gen_conservation_laws(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CONSERVATION,
                       glosses=_CONSERVATION_GLOSSES, concept_name="CONSERVATION IN COLLISIONS")


# ── Chemistry ────────────────────────────────────────────────────────────────

_BONDING = {
    "an IONIC compound (a metal with a non-metal, electrons transferred)": [
        "sodium chloride", "magnesium oxide", "calcium fluoride",
    ],
    "a COVALENT substance (non-metals sharing electrons)": [
        "water", "carbon dioxide", "methane",
    ],
    "a METALLIC structure (positive ions in a sea of delocalised electrons)": [
        "copper", "iron", "aluminium",
    ],
}
_BONDING_GLOSSES = {
    "an IONIC compound (a metal with a non-metal, electrons transferred)": "a metal gives electrons to a non-metal, and the opposite charges attract",
    "a COVALENT substance (non-metals sharing electrons)": "non-metals share pairs of electrons instead of transferring them",
    "a METALLIC structure (positive ions in a sea of delocalised electrons)": "the free electrons are why metals conduct and can be bent",
}

_PERIODIC_TRENDS = {
    "a Group 1 alkali metal (very reactive, one outer electron)": ["lithium", "sodium", "potassium"],
    "a Group 17 halogen (very reactive, seven outer electrons)": ["fluorine", "chlorine", "bromine"],
    "a Group 18 noble gas (full outer shell, almost unreactive)": ["helium", "neon", "argon"],
}
_PERIODIC_TRENDS_GLOSSES = {
    "a Group 1 alkali metal (very reactive, one outer electron)": "losing that single outer electron is easy, so they react readily",
    "a Group 17 halogen (very reactive, seven outer electrons)": "one electron short of a full shell, so they grab one",
    "a Group 18 noble gas (full outer shell, almost unreactive)": "nothing to gain or lose, so they barely react at all",
}

_MOLE_CONCEPT = {
    "a measure of the AMOUNT of substance": ["the mole", "number of particles", "6.02 x 10^23 particles"],
    "a measure of MASS": ["grams", "kilograms", "molar mass in g/mol"],
    "a measure of CONCENTRATION": ["mol/L", "moles per litre", "molarity"],
}
_MOLE_CONCEPT_GLOSSES = {
    "a measure of the AMOUNT of substance": "the mole counts particles, the way a dozen counts eggs",
    "a measure of MASS": "how heavy the sample is, not how many particles it holds",
    "a measure of CONCENTRATION": "how much substance is dissolved in each litre of solution",
}

_ACIDS_BASES = {
    "a STRONG acid (fully ionised in water)": ["hydrochloric acid", "sulfuric acid", "nitric acid"],
    "a WEAK acid (only partly ionised in water)": ["ethanoic acid", "citric acid", "carbonic acid"],
    "a BASE (accepts hydrogen ions, pH above 7)": [
        "sodium hydroxide", "ammonia solution", "calcium hydroxide",
    ],
}
_ACIDS_BASES_GLOSSES = {
    "a STRONG acid (fully ionised in water)": "nearly every molecule releases its hydrogen ion",
    "a WEAK acid (only partly ionised in water)": "most molecules stay whole, so far fewer hydrogen ions are released",
    "a BASE (accepts hydrogen ions, pH above 7)": "it takes hydrogen ions out of solution instead of adding them",
}

_REDOX = {
    "OXIDATION (loses electrons, oxidation number rises)": [
        "iron rusting in damp air", "magnesium burning in oxygen", "a metal atom becoming a positive ion",
    ],
    "REDUCTION (gains electrons, oxidation number falls)": [
        "copper ions plating onto an electrode", "iron oxide turning to iron in a blast furnace",
        "a non-metal atom becoming a negative ion",
    ],
}
_REDOX_GLOSSES = {
    "OXIDATION (loses electrons, oxidation number rises)": "OIL RIG -- Oxidation Is Loss of electrons",
    "REDUCTION (gains electrons, oxidation number falls)": "OIL RIG -- Reduction Is Gain of electrons",
}

_RATES = {
    "speeds a reaction up": [
        "raising the temperature", "increasing the concentration", "grinding a solid into powder",
        "adding a catalyst",
    ],
    "slows a reaction down": [
        "cooling the mixture", "diluting the solution", "using one large lump instead of powder",
    ],
}
_RATES_GLOSSES = {
    "speeds a reaction up": "more frequent collisions, or more of them with enough energy to react",
    "slows a reaction down": "fewer collisions, or fewer with enough energy to react",
}


def gen_bonding_types(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _BONDING,
                       glosses=_BONDING_GLOSSES, concept_name="IONIC, COVALENT AND METALLIC BONDING")


def gen_periodic_trends(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _PERIODIC_TRENDS,
                       glosses=_PERIODIC_TRENDS_GLOSSES, concept_name="GROUPS OF THE PERIODIC TABLE")


def gen_mole_concept(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MOLE_CONCEPT,
                       glosses=_MOLE_CONCEPT_GLOSSES, concept_name="THE MOLE")


def gen_acids_bases(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ACIDS_BASES,
                       glosses=_ACIDS_BASES_GLOSSES, concept_name="STRONG ACIDS, WEAK ACIDS AND BASES")


def gen_redox(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _REDOX,
                       glosses=_REDOX_GLOSSES, concept_name="OXIDATION AND REDUCTION")


def gen_reaction_rates(rng: random.Random):
    return mc_which_is(rng, "Which of these changes {label}?", _RATES,
                       glosses=_RATES_GLOSSES, concept_name="RATES OF REACTION")


# ── Biology ──────────────────────────────────────────────────────────────────

_TRANSPORT = {
    "DIFFUSION (particles spread from high to low concentration, no energy needed)": [
        "oxygen moving from the alveoli into the blood", "a scent spreading across a room",
    ],
    "OSMOSIS (water moving across a partially permeable membrane)": [
        "water entering a root hair cell", "a raisin swelling in pure water",
    ],
    "ACTIVE TRANSPORT (moves against the gradient and needs energy)": [
        "a root absorbing minerals from dilute soil water",
        "the gut absorbing glucose when blood glucose is already higher",
    ],
}
_TRANSPORT_GLOSSES = {
    "DIFFUSION (particles spread from high to low concentration, no energy needed)": "down the gradient, so it happens on its own",
    "OSMOSIS (water moving across a partially permeable membrane)": "diffusion, but specifically of WATER through a membrane",
    "ACTIVE TRANSPORT (moves against the gradient and needs energy)": "uphill against the gradient, so it costs the cell ATP",
}

_ENZYMES = {
    "true of enzymes": [
        "they are proteins", "they lower the activation energy",
        "they are specific to their substrate", "they are not used up in the reaction",
    ],
    "NOT true of enzymes": [
        "they are carbohydrates", "they work equally well at any pH",
        "they are consumed by the reaction",
    ],
}
_ENZYMES_GLOSSES = {
    "true of enzymes": "a protein catalyst with an active site shaped for one substrate",
    "NOT true of enzymes": "each of these contradicts what a protein catalyst does",
}

# Every member must be right for EXACTLY ONE category, and here that needs the
# process named in the member itself: carbon dioxide and water are reactants of
# photosynthesis AND products of respiration, so bare "carbon dioxide" as a
# distractor for "a product of aerobic respiration" would be a second correct
# answer marked wrong (found by a cross-category overlap sweep, 2026-08-15).
# The qualifiers make each option unambiguous and turn the overlap itself into
# the thing being taught: the two processes run opposite ways.
_PHOTO_RESP = {
    "a REACTANT of photosynthesis": [
        "carbon dioxide taken in by the leaf",
        "water drawn up from the roots",
        "light energy from the Sun",
    ],
    "a PRODUCT of photosynthesis": [
        "glucose stored as the plant's food",
        "oxygen released into the air",
    ],
    "a PRODUCT of aerobic respiration": [
        "carbon dioxide breathed out",
        "water given off as the cell releases energy",
        "ATP energy the cell can use",
    ],
}
_PHOTO_RESP_GLOSSES = {
    "a REACTANT of photosynthesis": "what goes IN when a plant builds glucose using light",
    "a PRODUCT of photosynthesis": "what comes OUT of that reaction",
    "a PRODUCT of aerobic respiration": "respiration runs the other way -- glucose and oxygen in, these out",
}

_INHERITANCE = {
    "a GENOTYPE (the alleles an organism carries)": ["Bb", "BB", "bb"],
    "a PHENOTYPE (the characteristic you can observe)": ["brown eyes", "tall stem", "white flowers"],
    "a term for an allele that is masked when a dominant one is present": [
        "recessive", "the b in Bb",
    ],
}
_INHERITANCE_GLOSSES = {
    "a GENOTYPE (the alleles an organism carries)": "written as letters -- the genes themselves",
    "a PHENOTYPE (the characteristic you can observe)": "what you can actually see or measure",
    "a term for an allele that is masked when a dominant one is present": "it only shows when both alleles are recessive",
}

_HOMEOSTASIS = {
    "an example of NEGATIVE feedback (the response reverses the change)": [
        "sweating when body temperature rises", "shivering when body temperature falls",
        "insulin lowering blood glucose after a meal",
    ],
    "NOT homeostasis (nothing is being held steady)": [
        "growing taller over years", "learning a new skill", "hair turning grey with age",
    ],
}
_HOMEOSTASIS_GLOSSES = {
    "an example of NEGATIVE feedback (the response reverses the change)": "the body detects a change and acts to undo it, back toward the set point",
    "NOT homeostasis (nothing is being held steady)": "a one-way change, not a correction back to a set point",
}

_TROPHIC = {
    "a PRODUCER (makes its own food from light)": ["grass", "an oak tree", "phytoplankton"],
    "a PRIMARY consumer (eats producers)": ["a rabbit eating grass", "a caterpillar eating leaves"],
    "a DECOMPOSER (breaks down dead material)": ["a fungus on a fallen log", "soil bacteria"],
}
_TROPHIC_GLOSSES = {
    "a PRODUCER (makes its own food from light)": "the first level -- energy enters the food chain here",
    "a PRIMARY consumer (eats producers)": "the level directly above the producers",
    "a DECOMPOSER (breaks down dead material)": "returns nutrients to the soil from every other level",
}


def gen_cell_transport(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _TRANSPORT,
                       glosses=_TRANSPORT_GLOSSES, concept_name="DIFFUSION, OSMOSIS AND ACTIVE TRANSPORT")


def gen_enzymes(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ENZYMES,
                       glosses=_ENZYMES_GLOSSES, concept_name="ENZYMES")


def gen_photosynthesis_respiration(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _PHOTO_RESP,
                       glosses=_PHOTO_RESP_GLOSSES, concept_name="PHOTOSYNTHESIS AND RESPIRATION")


def gen_inheritance(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _INHERITANCE,
                       glosses=_INHERITANCE_GLOSSES, concept_name="GENOTYPE AND PHENOTYPE")


def gen_homeostasis(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _HOMEOSTASIS,
                       glosses=_HOMEOSTASIS_GLOSSES, concept_name="HOMEOSTASIS AND NEGATIVE FEEDBACK")


def gen_trophic_levels(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _TROPHIC,
                       glosses=_TROPHIC_GLOSSES, concept_name="TROPHIC LEVELS")


# ── Stage tables ─────────────────────────────────────────────────────────────
# Senior STAGE 1 = the first senior year, STAGE 2 = the second. Slugs are the
# stable part of a node id (renaming one orphans that skill's mastery rows).

STAGE_CONCEPTS: dict[str, dict[int, dict[str, GenFn]]] = {
    "physics": {
        1: {
            "scalars_vectors": gen_scalars_vectors,
            "energy_forms": gen_energy_forms,
            "newton_laws": gen_newton_laws,
        },
        2: {
            "circuits_series_parallel": gen_circuit_arrangements,
            "em_spectrum": gen_em_spectrum,
            "conservation_collisions": gen_conservation_laws,
        },
    },
    "chemistry": {
        1: {
            "bonding_types": gen_bonding_types,
            "periodic_groups": gen_periodic_trends,
            "mole_concept": gen_mole_concept,
        },
        2: {
            "acids_bases": gen_acids_bases,
            "redox": gen_redox,
            "reaction_rates": gen_reaction_rates,
        },
    },
    "biology": {
        1: {
            "cell_transport": gen_cell_transport,
            "enzymes": gen_enzymes,
            "photosynthesis_respiration": gen_photosynthesis_respiration,
        },
        2: {
            "inheritance": gen_inheritance,
            "homeostasis": gen_homeostasis,
            "trophic_levels": gen_trophic_levels,
        },
    },
}

# W3 depth (docs/design/curriculum_depth_program.md): the reference-strand
# concepts live in senior_science_depth_items.py and merge in here, so every
# country's senior packs share them exactly like the original trio.
from mentar.engine.senior_science_depth_items import (  # noqa: E402
    DEPTH_STAGE_CONCEPTS,
    EARTH_ENV_STAGE_CONCEPTS,
)

for _subj, _stages in DEPTH_STAGE_CONCEPTS.items():
    for _stage, _extra in _stages.items():
        STAGE_CONCEPTS[_subj][_stage].update(_extra)

# Authority -> [(node-id prefix, level display name, senior stage)]. AU's au11/
# au12 prefixes are already used by its maths pack; the subject slugs differ, so
# ids stay unique (test_no_skill_id_collides_across_any_shipped_template).
# US lives in US_SEQUENCE below, not here: its high-school science is SEQUENCED
# by grade rather than taken in parallel.
SENIOR_LEVELS: dict[str, list[tuple[str, str, int]]] = {
    "AU_ACARA": [("au11", "Year 11", 1), ("au12", "Year 12", 2)],
    "IN_GENERIC": [("in_c11", "Class 11", 1), ("in_c12", "Class 12", 2)],
    "SG_GENERIC": [("sg_s3", "Secondary 3", 1), ("sg_s4", "Secondary 4", 2)],
}

SUBJECTS = ("physics", "chemistry", "biology")

# Levels that ship NO science at all, and why. US Grade 12 science is electives
# (AP, anatomy, environmental science, or none), which has no single shape to
# model -- so it is absent BY DECISION, recorded here rather than left as a hole
# for the coverage guard to report every run.
NO_SCIENCE_LEVELS = {"us_g12"}


def build_generators(prefix: str, subject: str, stage: int) -> dict[str, GenFn]:
    """One pack's node_id -> generator map, e.g. build_generators("sg_s3",
    "physics", 1) -> {"sg_s3_scalars_vectors": ..., ...}."""
    return {f"{prefix}_{slug}": fn for slug, fn in STAGE_CONCEPTS[subject][stage].items()}


# The US takes the same three subjects but ONE PER YEAR, in a sequence, rather
# than three in parallel: the common pattern is Biology in Grade 9, Chemistry in
# Grade 10, Physics in Grade 11. A whole year on one subject covers both senior
# stages of it, so each US pack is stage 1 AND stage 2 of its subject -- six
# nodes, where a parallel-country pack has three.
#
# Grade 12 is deliberately absent: it is electives (AP, anatomy, environmental
# science, or none at all), which varies by state and school. Inventing a
# "Grade 12 Science" would be a claim about a curriculum that has no single shape.
US_SEQUENCE: list[tuple[str, str, str]] = [
    ("us_g9", "Grade 9", "biology"),
    ("us_g10", "Grade 10", "chemistry"),
    ("us_g11", "Grade 11", "physics"),
]


def build_full_subject(prefix: str, subject: str) -> dict[str, GenFn]:
    """Both senior stages of one subject, for a year spent entirely on it."""
    out: dict[str, GenFn] = {}
    for stage in sorted(STAGE_CONCEPTS[subject]):
        out.update(build_generators(prefix, subject, stage))
    return out


# item_source name -> generators, e.g. "au11_physics", "in_c12_biology",
# "us_g9_biology".
SENIOR_SCIENCE_ITEM_SOURCES: dict[str, dict[str, GenFn]] = {
    # Earth & Environmental Science: a fourth senior subject, AU-ONLY until the
    # other countries' syllabus shapes are verified (they teach it under
    # different names/structures -- verify, never assume).
    "au11_earth_env": {f"au11_{slug}": fn for slug, fn in EARTH_ENV_STAGE_CONCEPTS[1].items()},
    "au12_earth_env": {f"au12_{slug}": fn for slug, fn in EARTH_ENV_STAGE_CONCEPTS[2].items()},
    **{
        f"{prefix}_{subject}": build_generators(prefix, subject, stage)
        for levels in SENIOR_LEVELS.values()
        for prefix, _level_name, stage in levels
        for subject in SUBJECTS
    },
    **{
        f"{prefix}_{subject}": build_full_subject(prefix, subject)
        for prefix, _level_name, subject in US_SEQUENCE
    },
}
