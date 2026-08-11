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
    "attracted to a magnet": ["an iron nail", "a steel paperclip", "a steel spoon", "a tin can"],
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


def _gen_classify_animals(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _ANIMAL_CLASSES)


def _gen_states_of_matter(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _MATTER_CLASSES)


def _gen_living_nonliving(rng: random.Random):
    return mc_which_is(rng, "Which of these is a {label}?", _LIVING_CLASSES)


def _gen_sound_vibration(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _SOUND_CLASSES)


def _gen_solar_system(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _SOLAR_SYSTEM_CLASSES)


def _gen_materials_change(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _MATERIALS_CLASSES)


def _gen_life_cycle(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LIFE_CYCLE_CLASSES)


def _gen_heat_sources(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _HEAT_SOURCE_CLASSES)


def _gen_habitats(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _HABITAT_CLASSES)


def _gen_food_chain_roles(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _FOOD_CHAIN_CLASSES)


def _gen_magnetic_materials(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MAGNETIC_CLASSES)


def _gen_state_change_heat(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _STATE_CHANGE_CLASSES)


def _gen_adaptations(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ADAPTATION_CLASSES)


def _gen_dissolving(rng: random.Random):
    return mc_which_is(rng, "Which of these {label}?", _DISSOLVING_CLASSES)


def _gen_light_materials(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _LIGHT_MATERIAL_CLASSES)


def _gen_vertebrates(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _VERTEBRATE_CLASSES)


def _gen_circuits(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CIRCUIT_CLASSES)


def _gen_reversible_change(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _REVERSIBLE_CHANGE_CLASSES)


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
