"""Science item generators — multiple-choice questions built from small CURATED
fact tables.

Why this shape: science facts can't be *computed* like maths, and an LLM that
invents the "correct" option could teach a child a wrong fact. So the fact tables
below are the authoritative ground truth (authored once, small), and questions are
generated automatically with random distractors. The deterministic verifier
(`mc_choice`) scores the child's letter against that ground truth — the LLM never
decides correctness (same safety rule as the maths path; see SPEC §14).

Each generator returns the GenFn tuple `(answer_type, checker, problem, answer)`
so it drops into `ItemGenerator(generators=SCIENCE_GENERATORS)`.
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is

# ── Curated fact tables (the ground truth) — Year-4 friendly, disjoint classes ──

_ANIMAL_CLASSES = {
    "mammal": ["dog", "cat", "whale", "bat", "horse", "elephant"],
    "bird": ["eagle", "owl", "penguin", "robin", "duck"],
    "fish": ["shark", "salmon", "tuna", "goldfish"],
    "insect": ["ant", "bee", "butterfly", "beetle"],
}

_MATTER_CLASSES = {
    "solid": ["a rock", "ice", "a book", "a coin"],
    "liquid": ["water", "milk", "juice", "oil"],
    "gas": ["air", "steam", "oxygen", "helium"],
}

_LIVING_CLASSES = {
    "living thing": ["a tree", "a dog", "a flower", "a child", "a fish"],
    "non-living thing": ["a rock", "a car", "a spoon", "a cloud", "a chair"],
}

_SOUND_CLASSES = {
    "makes a sound by vibrating": ["a guitar string", "a drum", "a bell", "a tuning fork"],
    "does not make a sound on its own": ["a rock", "a book", "a pillow", "a chair"],
}

_SOLAR_SYSTEM_CLASSES = {
    "is a planet": ["Earth", "Mars", "Jupiter", "Saturn", "Venus"],
    "is not a planet": ["the Sun", "the Moon", "a comet", "a star"],
}

_MATERIALS_CLASSES = {
    "can be bent, twisted or stretched": ["a rubber band", "a pipe cleaner", "playdough", "a piece of string"],
    "stays the same shape unless broken": ["a glass cup", "a wooden ruler", "a ceramic plate", "a china bowl"],
}

# ── Year 3 ─────────────────────────────────────────────────────────────────

_LIFE_CYCLE_CLASSES = {
    "a stage in a living thing's life cycle": ["an egg", "a caterpillar", "a tadpole", "a seedling", "a chick"],
    "not a life-cycle stage": ["a rock", "a car", "a chair", "a spoon"],
}

_HEAT_SOURCE_CLASSES = {
    "a source of heat": ["the Sun", "a campfire", "a stove", "a heater"],
    "not a source of heat": ["an ice cube", "a fan", "a mirror", "a window"],
}

_HABITAT_CLASSES = {
    "lives mainly in water": ["a fish", "a dolphin", "a crab", "an octopus"],
    "lives mainly on land": ["a lion", "a spider", "a snail", "a rabbit"],
}

# ── Year 4 ─────────────────────────────────────────────────────────────────

_FOOD_CHAIN_CLASSES = {
    "a producer (makes its own food, e.g. using sunlight)": ["a tree", "grass", "a sunflower", "seaweed"],
    "a consumer (eats other living things for food)": ["a lion", "a rabbit", "a shark", "a caterpillar"],
}

_MAGNETIC_CLASSES = {
    # NB: no "tin can" here -- food cans are tin-plated steel (magnetic) but drink
    # cans are aluminium (not), so a child testing one at home could fairly conclude
    # the tutor is wrong. Every member must be unambiguously ferrous.
    "attracted to a magnet": ["an iron nail", "a steel paperclip", "a steel spoon", "a steel screw"],
    "not attracted to a magnet": ["a wooden pencil", "a plastic ruler", "a rubber band", "a glass marble"],
}

_STATE_CHANGE_CLASSES = {
    "caused by ADDING heat": [
        "ice melting into water", "butter melting in a warm pan",
        "chocolate melting in your hand", "water boiling into steam",
    ],
    "caused by REMOVING heat": [
        "water freezing into ice", "juice freezing into ice blocks",
        "melted wax cooling and hardening", "steam cooling back into water droplets",
    ],
}

# ── Year 5 ─────────────────────────────────────────────────────────────────

_ADAPTATION_CLASSES = {
    "a body feature that helps an animal survive in its habitat": [
        "a polar bear's thick fur", "a camel's hump", "a duck's webbed feet", "a giraffe's long neck",
    ],
    "not linked to survival in a habitat": [
        "a dog's collar", "a horse's saddle", "a bird's cage", "a fish tank",
    ],
}

_DISSOLVING_CLASSES = {
    "dissolves in water": ["salt", "sugar", "instant coffee powder", "cordial powder"],
    "does not dissolve in water": ["sand", "oil", "pepper", "small stones"],
}

_LIGHT_MATERIAL_CLASSES = {
    "transparent (lets light pass through clearly)": [
        "clear glass", "clean water", "clear plastic wrap", "a clear plastic bottle",
    ],
    "opaque (blocks light completely)": [
        "a brick wall", "a wooden door", "a metal spoon", "a thick book",
    ],
}

# ── Year 6 ─────────────────────────────────────────────────────────────────

_VERTEBRATE_CLASSES = {
    "a vertebrate (has a backbone)": ["a dog", "a snake", "a fish", "a bird"],
    "an invertebrate (no backbone)": ["a worm", "a spider", "a snail", "a jellyfish"],
}

_CIRCUIT_CLASSES = {
    "a good conductor of electricity": ["copper wire", "a steel key", "aluminium foil", "a silver spoon"],
    "an insulator (does not conduct electricity)": [
        "a rubber band", "a plastic ruler", "a wooden spoon", "a glass rod",
    ],
}

_REVERSIBLE_CHANGE_CLASSES = {
    "a reversible change (can be undone)": [
        "melting chocolate", "freezing water", "dissolving salt in water", "melting butter",
    ],
    "an irreversible change (cannot be undone)": [
        "burning paper", "baking a cake", "rusting iron", "cooking an egg",
    ],
}

# ── Year 7 ─────────────────────────────────────────────────────────────────

_BODY_SYSTEM_CLASSES = {
    "part of the digestive system": ["the stomach", "the intestines", "the oesophagus", "the liver"],
    "part of the circulatory system": ["the heart", "the veins", "the arteries", "red blood cells"],
}

_FORCE_CLASSES = {
    "a contact force (needs touching)": [
        "pushing a door", "kicking a ball", "friction between shoes and the ground", "pulling a rope",
    ],
    "a non-contact force (acts at a distance)": [
        "magnetism pulling a paperclip", "gravity pulling an apple down",
        "static electricity attracting hair", "a magnet repelling another magnet",
    ],
}

_MIXTURE_CLASSES = {
    "a pure substance (only one type of particle)": [
        "oxygen gas", "pure gold", "distilled water", "table salt (sodium chloride)",
    ],
    "a mixture (more than one substance mixed together)": [
        "salt water", "air", "soil", "orange juice with pulp",
    ],
}

# ── Year 8 ─────────────────────────────────────────────────────────────────

_CELL_STRUCTURE_CLASSES = {
    "found in a plant cell but not in an animal cell": [
        "a cell wall", "a chloroplast", "a large permanent vacuole",
    ],
    "found in both plant and animal cells": ["a nucleus", "mitochondria", "a cell membrane"],
}

_ENERGY_SOURCE_CLASSES = {
    "a renewable energy source": ["solar power", "wind power", "hydroelectric power", "biomass"],
    "a non-renewable energy source": ["coal", "oil", "natural gas", "nuclear fuel (uranium)"],
}

_ELEMENT_COMPOUND_CLASSES = {
    "an element (only one type of atom)": ["oxygen", "iron", "gold", "carbon"],
    "a compound (two or more elements chemically joined)": [
        "water (H2O)", "carbon dioxide (CO2)", "table salt (NaCl)", "sugar (glucose)",
    ],
}


# ── Explain-mode (2026-08-12): one 'because' gloss per category label + a
# textbook concept name per fact table -- docs/design/explain_mode_design.md
# §3 Type 4. Passed to mc_which_is() so a drawn item's method_steps card
# states WHY the correct answer's category is true and what each wrong
# option's own true category is, instead of the child having to infer it.

_ANIMAL_GLOSSES = {
    'mammal': 'mammals have fur or hair and feed their babies milk',
    'bird': 'birds have feathers and lay eggs',
    'fish': 'fish live in water and breathe through gills',
    'insect': 'insects have six legs and a body in three parts',
}

_MATTER_GLOSSES = {
    'solid': 'a solid keeps its own shape',
    'liquid': 'a liquid takes the shape of its container but keeps the same amount of space',
    'gas': 'a gas spreads out to fill all the space it can',
}

_LIVING_GLOSSES = {
    'living thing': 'living things grow, feed, and can reproduce',
    'non-living thing': "non-living things don't grow, feed, or reproduce on their own",
}

_SOUND_GLOSSES = {
    'makes a sound by vibrating': 'sound is made when something vibrates (shakes) very fast',
    'does not make a sound on its own': "nothing is vibrating, so there's no sound to hear",
}

_SOLAR_SYSTEM_GLOSSES = {
    'is a planet': 'a planet is a large round body that orbits the Sun',
    'is not a planet': "it orbits the Sun too, but it's a star, a moon, or a comet -- not a planet itself",
}

_MATERIALS_GLOSSES = {
    'can be bent, twisted or stretched': 'flexible materials change shape easily and often spring back',
    'stays the same shape unless broken': 'rigid materials hold their shape until real force breaks them',
}

_LIFE_CYCLE_GLOSSES = {
    "a stage in a living thing's life cycle": 'living things change through stages as they grow up',
    'not a life-cycle stage': "it isn't part of how a living thing grows and changes",
}

_HEAT_SOURCE_GLOSSES = {
    'a source of heat': 'it gives off heat energy you can feel',
    'not a source of heat': "it doesn't produce heat itself",
}

_HABITAT_GLOSSES = {
    'lives mainly in water': 'its body is suited for swimming and breathing in water',
    'lives mainly on land': 'its body is suited for moving and breathing on land',
}

_FOOD_CHAIN_GLOSSES = {
    'a producer (makes its own food, e.g. using sunlight)': 'producers use sunlight to make their own food',
    'a consumer (eats other living things for food)': "consumers can't make their own food, so they eat other living things",
}

_MAGNETIC_GLOSSES = {
    'attracted to a magnet': 'magnets pull things made of iron or steel',
    'not attracted to a magnet': "it isn't made of iron or steel, so a magnet can't pull it",
}

_STATE_CHANGE_GLOSSES = {
    'caused by ADDING heat': 'adding heat energy makes particles move more and change solid to liquid to gas',
    'caused by REMOVING heat': 'removing heat energy makes particles move less and change gas to liquid to solid',
}

_ADAPTATION_GLOSSES = {
    'a body feature that helps an animal survive in its habitat': 'adaptations are body features shaped by living in a particular habitat',
    'not linked to survival in a habitat': "it's something added by people, not a body feature suited to a habitat",
}

_DISSOLVING_GLOSSES = {
    'dissolves in water': 'its particles spread evenly through the water and seem to disappear',
    'does not dissolve in water': 'its particles stay separate and settle instead of spreading through the water',
}

_LIGHT_MATERIAL_GLOSSES = {
    'transparent (lets light pass through clearly)': 'light passes straight through, so you can see clearly through it',
    'opaque (blocks light completely)': "light can't pass through, so it blocks your view completely",
}

_VERTEBRATE_GLOSSES = {
    'a vertebrate (has a backbone)': 'vertebrates have a backbone inside their body for support',
    'an invertebrate (no backbone)': 'invertebrates have no backbone at all',
}

_CIRCUIT_GLOSSES = {
    'a good conductor of electricity': 'metals let electricity flow through them easily',
    'an insulator (does not conduct electricity)': 'it blocks the flow of electricity',
}

_REVERSIBLE_CHANGE_GLOSSES = {
    'a reversible change (can be undone)': 'no new substance is made, so it can be changed back',
    'an irreversible change (cannot be undone)': "a new substance is made, so it can't be changed back",
}

_BODY_SYSTEM_GLOSSES = {
    'part of the digestive system': 'the digestive system breaks down food so the body can use it',
    'part of the circulatory system': 'the circulatory system pumps blood around the body',
}

_FORCE_GLOSSES = {
    'a contact force (needs touching)': 'contact forces only work when two things are touching',
    'a non-contact force (acts at a distance)': 'non-contact forces can act without the objects touching',
}

_MIXTURE_GLOSSES = {
    'a pure substance (only one type of particle)': 'a pure substance has only ONE type of particle throughout',
    'a mixture (more than one substance mixed together)': 'a mixture has two or more substances mixed together, each keeping its own properties',
}

_CELL_STRUCTURE_GLOSSES = {
    'found in a plant cell but not in an animal cell': 'plant cells need these extra structures for support and making food',
    'found in both plant and animal cells': 'every cell, plant or animal, needs these basic structures to live',
}

_ENERGY_SOURCE_GLOSSES = {
    'a renewable energy source': "renewable sources are naturally replaced and won't run out",
    'a non-renewable energy source': 'non-renewable sources take millions of years to form, so they can run out',
}

_ELEMENT_COMPOUND_GLOSSES = {
    'an element (only one type of atom)': 'an element is made of just one type of atom',
    'a compound (two or more elements chemically joined)': 'a compound forms when two or more elements bond together chemically',
}

def _gen_classify_animals(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _ANIMAL_CLASSES, glosses=_ANIMAL_GLOSSES, concept_name='ANIMAL GROUPS')


def _gen_states_of_matter(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _MATTER_CLASSES, glosses=_MATTER_GLOSSES, concept_name='STATES OF MATTER')


def _gen_living_nonliving(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _LIVING_CLASSES, glosses=_LIVING_GLOSSES, concept_name='LIVING VS NON-LIVING')


def _gen_sound_vibration(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _SOUND_CLASSES, glosses=_SOUND_GLOSSES, concept_name='SOUND AND VIBRATION')


def _gen_solar_system(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _SOLAR_SYSTEM_CLASSES, glosses=_SOLAR_SYSTEM_GLOSSES, concept_name='THE SOLAR SYSTEM')


def _gen_materials_change(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _MATERIALS_CLASSES, glosses=_MATERIALS_GLOSSES, concept_name='MATERIALS AND THEIR PROPERTIES')


def _gen_life_cycle(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LIFE_CYCLE_CLASSES, glosses=_LIFE_CYCLE_GLOSSES, concept_name='LIFE CYCLES')


def _gen_heat_sources(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _HEAT_SOURCE_CLASSES, glosses=_HEAT_SOURCE_GLOSSES, concept_name='SOURCES OF HEAT')


def _gen_habitats(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _HABITAT_CLASSES, glosses=_HABITAT_GLOSSES, concept_name='HABITATS')


def _gen_food_chain_roles(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _FOOD_CHAIN_CLASSES, glosses=_FOOD_CHAIN_GLOSSES, concept_name='FOOD CHAINS')


def _gen_magnetic_materials(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MAGNETIC_CLASSES, glosses=_MAGNETIC_GLOSSES, concept_name='MAGNETISM')


def _gen_state_change_heat(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _STATE_CHANGE_CLASSES, glosses=_STATE_CHANGE_GLOSSES, concept_name='CHANGES OF STATE')


def _gen_adaptations(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ADAPTATION_CLASSES, glosses=_ADAPTATION_GLOSSES, concept_name='ADAPTATIONS')


def _gen_dissolving(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _DISSOLVING_CLASSES, glosses=_DISSOLVING_GLOSSES, concept_name='DISSOLVING')


def _gen_light_materials(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LIGHT_MATERIAL_CLASSES, glosses=_LIGHT_MATERIAL_GLOSSES, concept_name='LIGHT AND MATERIALS')


def _gen_vertebrates(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _VERTEBRATE_CLASSES, glosses=_VERTEBRATE_GLOSSES, concept_name='VERTEBRATES AND INVERTEBRATES')


def _gen_circuits(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CIRCUIT_CLASSES, glosses=_CIRCUIT_GLOSSES, concept_name='CONDUCTORS AND INSULATORS')


def _gen_reversible_change(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _REVERSIBLE_CHANGE_CLASSES, glosses=_REVERSIBLE_CHANGE_GLOSSES, concept_name='REVERSIBLE AND IRREVERSIBLE CHANGES')


def _gen_body_systems(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _BODY_SYSTEM_CLASSES, glosses=_BODY_SYSTEM_GLOSSES, concept_name='BODY SYSTEMS')


def _gen_forces(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _FORCE_CLASSES, glosses=_FORCE_GLOSSES, concept_name='CONTACT AND NON-CONTACT FORCES')


def _gen_mixtures(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MIXTURE_CLASSES, glosses=_MIXTURE_GLOSSES, concept_name='PURE SUBSTANCES AND MIXTURES')


def _gen_cell_structures(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CELL_STRUCTURE_CLASSES, glosses=_CELL_STRUCTURE_GLOSSES, concept_name='PLANT AND ANIMAL CELLS')


def _gen_energy_sources(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ENERGY_SOURCE_CLASSES, glosses=_ENERGY_SOURCE_GLOSSES, concept_name='RENEWABLE AND NON-RENEWABLE ENERGY')


def _gen_elements_compounds(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ELEMENT_COMPOUND_CLASSES, glosses=_ELEMENT_COMPOUND_GLOSSES, concept_name='ELEMENTS AND COMPOUNDS')


# Registry — node_id -> generator (matches the science curriculum template node ids).
SCIENCE_GENERATORS: dict[str, GenFn] = {
    "classify_animals": _gen_classify_animals,
    "states_of_matter": _gen_states_of_matter,
    "living_nonliving": _gen_living_nonliving,
    "au2_science_sound": _gen_sound_vibration,
    "au2_science_solar_system": _gen_solar_system,
    "au2_science_materials": _gen_materials_change,
    "au3_science_life_cycle": _gen_life_cycle,
    "au3_science_heat_sources": _gen_heat_sources,
    "au3_science_habitats": _gen_habitats,
    "au4_science_food_chain_roles": _gen_food_chain_roles,
    "au4_science_magnetic_materials": _gen_magnetic_materials,
    "au4_science_state_change_heat": _gen_state_change_heat,
    "au5_science_adaptations": _gen_adaptations,
    "au5_science_dissolving": _gen_dissolving,
    "au5_science_light_materials": _gen_light_materials,
    "au6_science_vertebrates": _gen_vertebrates,
    "au6_science_circuits": _gen_circuits,
    "au6_science_reversible_change": _gen_reversible_change,
    "au7_science_body_systems": _gen_body_systems,
    "au7_science_forces": _gen_forces,
    "au7_science_mixtures": _gen_mixtures,
    "au8_science_cell_structures": _gen_cell_structures,
    "au8_science_energy_sources": _gen_energy_sources,
    "au8_science_elements_compounds": _gen_elements_compounds,
}

AU_SCIENCE_YEAR3_GENERATORS: dict[str, GenFn] = {
    "au3_science_life_cycle": _gen_life_cycle,
    "au3_science_heat_sources": _gen_heat_sources,
    "au3_science_habitats": _gen_habitats,
}

AU_SCIENCE_YEAR4_GENERATORS: dict[str, GenFn] = {
    "au4_science_food_chain_roles": _gen_food_chain_roles,
    "au4_science_magnetic_materials": _gen_magnetic_materials,
    "au4_science_state_change_heat": _gen_state_change_heat,
}

AU_SCIENCE_YEAR5_GENERATORS: dict[str, GenFn] = {
    "au5_science_adaptations": _gen_adaptations,
    "au5_science_dissolving": _gen_dissolving,
    "au5_science_light_materials": _gen_light_materials,
}

AU_SCIENCE_YEAR6_GENERATORS: dict[str, GenFn] = {
    "au6_science_vertebrates": _gen_vertebrates,
    "au6_science_circuits": _gen_circuits,
    "au6_science_reversible_change": _gen_reversible_change,
}

AU_SCIENCE_YEAR7_GENERATORS: dict[str, GenFn] = {
    "au7_science_body_systems": _gen_body_systems,
    "au7_science_forces": _gen_forces,
    "au7_science_mixtures": _gen_mixtures,
}

AU_SCIENCE_YEAR8_GENERATORS: dict[str, GenFn] = {
    "au8_science_cell_structures": _gen_cell_structures,
    "au8_science_energy_sources": _gen_energy_sources,
    "au8_science_elements_compounds": _gen_elements_compounds,
}
