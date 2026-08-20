"""W3 of the curriculum depth program: senior science to the reference strands,
plus Earth & Environmental Science (a subject Mentar lacked entirely).

Additive companion to `senior_science_items.py` — same discipline (disjoint
fact tables -> `mc_which_is`, glosses on every category so each node carries an
explain-mode card, no claimed alignment). `senior_science_items.py` merges
`DEPTH_STAGE_CONCEPTS` into `STAGE_CONCEPTS` at import, so every country's
senior packs can draw the new nodes; Earth & Env ships AU-only until the other
countries' syllabus shapes are verified (docs/design/curriculum_depth_program.md
W8 rule: verify, never assume).
"""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is

# ── Physics stage 1: heating, nuclear, circuits ──────────────────────────────

_HEATING = {
    "heat transfer by CONDUCTION (through a material, particle to particle)": [
        "a metal spoon handle warming in hot soup",
        "a saucepan base heating on an electric hotplate",
    ],
    "heat transfer by CONVECTION (carried by a moving fluid)": [
        "warm air rising above a heater",
        "water circulating as it boils in a pot",
    ],
    "heat transfer by RADIATION (no matter needed at all)": [
        "the Sun warming your face across empty space",
        "feeling a campfire's warmth from metres away",
    ],
}
_HEATING_GLOSSES = {
    "heat transfer by CONDUCTION (through a material, particle to particle)":
        "particles pass vibration to their neighbours; solids, especially metals",
    "heat transfer by CONVECTION (carried by a moving fluid)":
        "the warm fluid itself moves, carrying its energy along",
    "heat transfer by RADIATION (no matter needed at all)":
        "infrared waves travel even through a vacuum",
}


def gen_heating_processes(rng: random.Random):
    return mc_which_is(rng, "Which of these is an example of {label}?", _HEATING,
                       glosses=_HEATING_GLOSSES, concept_name="HEAT TRANSFER PROCESSES")


_NUCLEAR = {
    "ALPHA radiation (helium nuclei — heavy, stopped by paper)": [
        "the radiation stopped by a sheet of paper",
        "the most ionising but least penetrating type",
    ],
    "BETA radiation (fast electrons — stopped by aluminium)": [
        "the radiation stopped by a few millimetres of aluminium",
        "fast electrons ejected from a decaying nucleus",
    ],
    "GAMMA radiation (electromagnetic waves — needs thick lead)": [
        "the radiation that needs thick lead or concrete to block",
        "an electromagnetic wave from the nucleus, not a particle",
    ],
}
_NUCLEAR_GLOSSES = {
    "ALPHA radiation (helium nuclei — heavy, stopped by paper)":
        "two protons + two neutrons: big, slow, easily stopped",
    "BETA radiation (fast electrons — stopped by aluminium)":
        "light and fast: more penetrating than alpha, less than gamma",
    "GAMMA radiation (electromagnetic waves — needs thick lead)":
        "pure energy, no mass or charge — hardest to stop",
}


def gen_nuclear_radiation(rng: random.Random):
    return mc_which_is(rng, "Which of these describes {label}?", _NUCLEAR,
                       glosses=_NUCLEAR_GLOSSES, concept_name="TYPES OF NUCLEAR RADIATION")


_CIRCUIT_QUANTITIES = {
    "VOLTAGE (the push, measured in volts)": [
        "the energy given to each coulomb of charge by the battery",
        "what a voltmeter placed across a component reads",
    ],
    "CURRENT (the flow, measured in amperes)": [
        "the rate at which charge passes a point in the wire",
        "what an ammeter placed in the loop reads",
    ],
    "RESISTANCE (the opposition, measured in ohms)": [
        "what makes a narrow wire harder for charge to pass through",
        "the ratio of voltage across a component to current through it",
    ],
}
_CIRCUIT_QUANTITIES_GLOSSES = {
    "VOLTAGE (the push, measured in volts)": "the electrical push driving charge around",
    "CURRENT (the flow, measured in amperes)": "how much charge flows each second",
    "RESISTANCE (the opposition, measured in ohms)": "V = I × R ties all three together",
}


def gen_circuit_quantities(rng: random.Random):
    return mc_which_is(rng, "Which of these describes {label}?", _CIRCUIT_QUANTITIES,
                       glosses=_CIRCUIT_QUANTITIES_GLOSSES, concept_name="VOLTAGE, CURRENT AND RESISTANCE")


# ── Physics stage 2: gravity, waves, quantum, relativity ─────────────────────

_GRAVITY = {
    "true of a gravitational FIELD": [
        "it points toward the mass creating it",
        "its strength falls off with the square of the distance",
    ],
    "true of WEIGHT (the force on a mass in a field)": [
        "it equals mass times gravitational field strength (W = mg)",
        "it changes when you move to the Moon; your mass does not",
    ],
    "true of ORBITAL motion": [
        "a satellite is continually falling toward Earth while moving sideways fast enough to keep missing it",
        "the Moon is held in its path by Earth's gravity alone",
    ],
}
_GRAVITY_GLOSSES = {
    "true of a gravitational FIELD": "a region where any mass feels a force toward the source",
    "true of WEIGHT (the force on a mass in a field)": "weight is a FORCE (newtons); mass is the amount of matter (kg)",
    "true of ORBITAL motion": "an orbit is free fall with enough sideways speed",
}


def gen_gravity_fields(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _GRAVITY,
                       glosses=_GRAVITY_GLOSSES, concept_name="GRAVITY AND ORBITS")


_WAVES = {
    "a property of wave FREQUENCY": [
        "the number of complete waves passing a point each second",
        "measured in hertz",
    ],
    "a property of WAVELENGTH": [
        "the distance from one crest to the next",
        "measured in metres",
    ],
    "a property of wave AMPLITUDE": [
        "the maximum displacement from the middle position",
        "what determines how loud a sound or bright a light is",
    ],
}
_WAVES_GLOSSES = {
    "a property of wave FREQUENCY": "how OFTEN the wave repeats; v = f × λ links it to wavelength",
    "a property of WAVELENGTH": "how LONG one repeat of the wave is",
    "a property of wave AMPLITUDE": "how BIG the oscillation is — the energy carrier",
}


def gen_wave_properties(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _WAVES,
                       glosses=_WAVES_GLOSSES, concept_name="WAVE PROPERTIES")


_QUANTUM = {
    "evidence that light behaves as PARTICLES (photons)": [
        "the photoelectric effect — dim blue light frees electrons where bright red cannot",
        "light energy arriving in discrete lumps proportional to frequency",
    ],
    "evidence that light behaves as a WAVE": [
        "the double-slit experiment producing an interference pattern",
        "light spreading out after passing a narrow gap",
    ],
    "a quantum idea about ATOMS": [
        "electrons occupying only fixed energy levels",
        "atoms emitting light at only certain exact colours",
    ],
}
_QUANTUM_GLOSSES = {
    "evidence that light behaves as PARTICLES (photons)":
        "each photon carries E = hf; below a threshold frequency nothing happens",
    "evidence that light behaves as a WAVE":
        "only waves overlap to reinforce and cancel in patterns",
    "a quantum idea about ATOMS":
        "energy in atoms comes in steps, not a smooth ramp — hence line spectra",
}


def gen_quantum_ideas(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _QUANTUM,
                       glosses=_QUANTUM_GLOSSES, concept_name="QUANTUM IDEAS")


_RELATIVITY = {
    "a postulate of special relativity": [
        "the speed of light in a vacuum is the same for every observer",
        "the laws of physics are the same in every non-accelerating frame",
    ],
    "a CONSEQUENCE of special relativity": [
        "a fast-moving clock ticks more slowly as seen from the ground",
        "a fast-moving object is measured shorter along its direction of travel",
    ],
    "everyday evidence that relativity is REAL": [
        "GPS satellite clocks needing correction to stay accurate",
        "short-lived muons from cosmic rays reaching the ground",
    ],
}
_RELATIVITY_GLOSSES = {
    "a postulate of special relativity": "the two starting assumptions — everything else is derived",
    "a CONSEQUENCE of special relativity": "time dilation and length contraction follow from the postulates",
    "everyday evidence that relativity is REAL": "engineering already has to correct for it",
}


def gen_relativity_ideas(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _RELATIVITY,
                       glosses=_RELATIVITY_GLOSSES, concept_name="SPECIAL RELATIVITY")


# ── Chemistry stage 1: atomic structure, gas laws, reactions, organic ────────

_ATOMIC = {
    "true of PROTONS": [
        "their count defines which element the atom is",
        "positively charged particles in the nucleus",
    ],
    "true of NEUTRONS": [
        "changing their count makes an isotope of the same element",
        "uncharged particles that add mass to the nucleus",
    ],
    "true of ELECTRONS": [
        "they occupy shells around the nucleus and set the chemistry",
        "the particles lost or gained when ions form",
    ],
}
_ATOMIC_GLOSSES = {
    "true of PROTONS": "atomic number = proton count — the element's identity",
    "true of NEUTRONS": "same protons + different neutrons = isotopes",
    "true of ELECTRONS": "bonding and reactions are electron business",
}


def gen_atomic_structure(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _ATOMIC,
                       glosses=_ATOMIC_GLOSSES, concept_name="ATOMIC STRUCTURE")


_GAS_LAWS = {
    "what happens when a gas is HEATED at fixed volume": [
        "its pressure rises as particles hit the walls harder and more often",
    ],
    "what happens when a gas is COMPRESSED at fixed temperature": [
        "its pressure rises because the same particles hit the walls more often",
        "its volume falls while pressure × volume stays constant",
    ],
    "what happens when a gas is HEATED at fixed pressure": [
        "it expands, taking up more volume",
        "a balloon in the sun swelling up",
    ],
}
_GAS_LAWS_GLOSSES = {
    "what happens when a gas is HEATED at fixed volume": "hotter particles move faster: more, harder wall collisions",
    "what happens when a gas is COMPRESSED at fixed temperature": "Boyle's law: P × V constant when T is fixed",
    "what happens when a gas is HEATED at fixed pressure": "Charles' law: V grows with T at constant P",
}


def gen_gas_laws(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _GAS_LAWS,
                       glosses=_GAS_LAWS_GLOSSES, concept_name="GAS LAWS")


_REACTION_KINDS = {
    "a COMBUSTION reaction": [
        "methane burning in oxygen to give carbon dioxide and water",
        "a fuel reacting with oxygen and releasing heat",
    ],
    "a PRECIPITATION reaction": [
        "two clear solutions mixed and an insoluble solid forming",
        "silver nitrate and salt solution giving a white solid",
    ],
    "a DECOMPOSITION reaction": [
        "one compound breaking into simpler substances when heated",
        "hydrogen peroxide breaking down into water and oxygen",
    ],
}
_REACTION_KINDS_GLOSSES = {
    "a COMBUSTION reaction": "fuel + oxygen → oxides + energy",
    "a PRECIPITATION reaction": "soluble + soluble → one insoluble product falls out",
    "a DECOMPOSITION reaction": "one substance in, several out — energy usually needed",
}


def gen_reaction_kinds(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _REACTION_KINDS,
                       glosses=_REACTION_KINDS_GLOSSES, concept_name="KINDS OF CHEMICAL REACTION")


_ORGANIC = {
    "an ALKANE (single bonds only)": ["methane", "ethane", "propane"],
    "an ALKENE (contains a C=C double bond)": ["ethene", "propene"],
    "an ALCOHOL (contains an -OH group)": ["ethanol", "methanol"],
}
_ORGANIC_GLOSSES = {
    "an ALKANE (single bonds only)": "saturated hydrocarbons: C-C single bonds, ending -ane",
    "an ALKENE (contains a C=C double bond)": "unsaturated: the double bond makes them reactive, ending -ene",
    "an ALCOHOL (contains an -OH group)": "the -OH functional group sets the family's chemistry, ending -ol",
}


def gen_organic_basics(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ORGANIC,
                       glosses=_ORGANIC_GLOSSES, concept_name="ORGANIC FAMILIES")


# ── Chemistry stage 2: equilibrium, electrochemistry, organic synthesis ──────

_EQUILIBRIUM = {
    "true AT chemical equilibrium": [
        "the forward and reverse reactions run at equal rates",
        "the amounts of reactants and products stay constant, though both reactions continue",
    ],
    "a change that SHIFTS an equilibrium": [
        "adding more of a reactant",
        "raising the temperature of the mixture",
    ],
    "NOT affected by a catalyst": [
        "the final equilibrium position of the reaction",
        "the yield the reaction eventually settles at",
    ],
}
_EQUILIBRIUM_GLOSSES = {
    "true AT chemical equilibrium": "a dynamic balance — both directions still running",
    "a change that SHIFTS an equilibrium": "Le Chatelier: the system counteracts the change imposed",
    "NOT affected by a catalyst": "a catalyst speeds BOTH directions equally — same balance, reached sooner",
}


def gen_equilibrium(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _EQUILIBRIUM,
                       glosses=_EQUILIBRIUM_GLOSSES, concept_name="CHEMICAL EQUILIBRIUM")


_ELECTROCHEM = {
    "true of a galvanic (voltaic) CELL": [
        "a spontaneous reaction generates an electric current",
        "chemical energy is converted into electrical energy",
    ],
    "true of an ELECTROLYTIC cell": [
        "an external power supply forces a non-spontaneous reaction",
        "used to electroplate metals and split molten salts",
    ],
    "true of the ELECTRODES": [
        "oxidation happens at the anode",
        "reduction happens at the cathode",
    ],
}
_ELECTROCHEM_GLOSSES = {
    "true of a galvanic (voltaic) CELL": "a battery: the reaction wants to run, and you harvest the electrons",
    "true of an ELECTROLYTIC cell": "electrolysis: you pay energy to drive the reaction backwards",
    "true of the ELECTRODES": "AN-OX and RED-CAT hold in both kinds of cell",
}


def gen_electrochemistry(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ELECTROCHEM,
                       glosses=_ELECTROCHEM_GLOSSES, concept_name="ELECTROCHEMICAL CELLS")


_ORGANIC_SYNTH = {
    "an ADDITION reaction": [
        "ethene + hydrogen becoming ethane across the double bond",
        "bromine adding across a C=C double bond, decolourising",
    ],
    "a SUBSTITUTION reaction": [
        "one hydrogen on an alkane swapped for a chlorine atom",
    ],
    "ESTERIFICATION": [
        "an alcohol and a carboxylic acid joining to give a fruity-smelling product",
        "the reaction that makes an ester plus water",
    ],
}
_ORGANIC_SYNTH_GLOSSES = {
    "an ADDITION reaction": "the double bond opens; two molecules become one",
    "a SUBSTITUTION reaction": "an atom swapped for another; needs UV light for alkanes",
    "ESTERIFICATION": "alcohol + acid → ester + water, with an acid catalyst",
}


def gen_organic_synthesis(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ORGANIC_SYNTH,
                       glosses=_ORGANIC_SYNTH_GLOSSES, concept_name="ORGANIC REACTION TYPES")


# ── Biology stage 1: ecosystems, adaptations, transport systems ──────────────

_ECOSYSTEM_ROLES = {
    "a PRODUCER": ["grass on a plain", "phytoplankton in the ocean", "a gum tree"],
    "a CONSUMER": ["a kangaroo grazing", "a shark hunting fish"],
    "a DECOMPOSER": ["fungi breaking down a fallen log", "soil bacteria recycling dead leaves"],
}
_ECOSYSTEM_ROLES_GLOSSES = {
    "a PRODUCER": "makes its own food from sunlight — every food chain starts here",
    "a CONSUMER": "eats other organisms for energy",
    "a DECOMPOSER": "returns nutrients from the dead to the soil — the recyclers",
}


def gen_ecosystem_roles(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ECOSYSTEM_ROLES,
                       glosses=_ECOSYSTEM_ROLES_GLOSSES, concept_name="ROLES IN AN ECOSYSTEM")


_ADAPTATIONS = {
    "a STRUCTURAL adaptation (a body feature)": [
        "a cactus storing water in a thick stem",
        "a polar bear's layer of blubber",
    ],
    "a BEHAVIOURAL adaptation (something the organism does)": [
        "desert animals feeding only at night",
        "birds migrating before winter",
    ],
    "a PHYSIOLOGICAL adaptation (an internal process)": [
        "a snake producing venom",
        "kidneys concentrating urine in desert mammals",
    ],
}
_ADAPTATIONS_GLOSSES = {
    "a STRUCTURAL adaptation (a body feature)": "you could see it on the body itself",
    "a BEHAVIOURAL adaptation (something the organism does)": "an action or habit, not a body part",
    "a PHYSIOLOGICAL adaptation (an internal process)": "chemistry inside the body doing the adapting",
}


def gen_adaptation_types(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ADAPTATIONS,
                       glosses=_ADAPTATIONS_GLOSSES, concept_name="TYPES OF ADAPTATION")


_TRANSPORT = {
    "part of a PLANT's transport system": [
        "xylem carrying water up from the roots",
        "phloem moving sugars from the leaves",
    ],
    "part of the CIRCULATORY system": [
        "arteries carrying blood away from the heart",
        "capillaries exchanging materials with tissues",
    ],
    "part of the RESPIRATORY system's transport job": [
        "oxygen diffusing across the alveoli into the blood",
        "carbon dioxide leaving the blood to be breathed out",
    ],
}
_TRANSPORT_GLOSSES = {
    "part of a PLANT's transport system": "xylem up (water), phloem around (food)",
    "part of the CIRCULATORY system": "the heart-and-vessels delivery network",
    "part of the RESPIRATORY system's transport job": "gas exchange happens across huge, thin, moist surfaces",
}


def gen_transport_systems(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _TRANSPORT,
                       glosses=_TRANSPORT_GLOSSES, concept_name="TRANSPORT SYSTEMS")


# ── Biology stage 2: DNA, evolution, disease ─────────────────────────────────

_DNA = {
    "true of DNA": [
        "a double helix of paired bases (A-T, G-C)",
        "it stays in the nucleus while copies of its message leave",
    ],
    "true of mRNA": [
        "a single-stranded copy of a gene that travels to the ribosome",
        "it uses U (uracil) where DNA uses T",
    ],
    "true of PROTEIN synthesis": [
        "ribosomes read the message three bases at a time",
        "each three-base codon calls for one amino acid",
    ],
}
_DNA_GLOSSES = {
    "true of DNA": "the master copy, kept safe in the nucleus",
    "true of mRNA": "the working copy sent out to the factory floor",
    "true of PROTEIN synthesis": "transcription writes the copy; translation builds the protein",
}


def gen_dna_protein(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _DNA,
                       glosses=_DNA_GLOSSES, concept_name="DNA AND PROTEIN SYNTHESIS")


_EVOLUTION = {
    "evidence for evolution from FOSSILS": [
        "older rock layers holding simpler life forms",
        "transitional forms like feathered dinosaurs",
    ],
    "evidence from COMPARATIVE ANATOMY": [
        "the same bone layout in a whale flipper, bat wing and human arm",
        "vestigial organs like the human tailbone",
    ],
    "evidence from DNA": [
        "closely related species sharing more of their genetic code",
        "humans and chimpanzees having nearly identical genes",
    ],
}
_EVOLUTION_GLOSSES = {
    "evidence for evolution from FOSSILS": "a time-ordered record in the rocks",
    "evidence from COMPARATIVE ANATOMY": "shared structure points to shared ancestry",
    "evidence from DNA": "the molecular family tree matches the visible one",
}


def gen_evolution_evidence(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _EVOLUTION,
                       glosses=_EVOLUTION_GLOSSES, concept_name="EVIDENCE FOR EVOLUTION")


_DISEASE = {
    "an INFECTIOUS disease (caused by a pathogen)": [
        "influenza spread by a virus",
        "tuberculosis caused by bacteria",
    ],
    "a NON-INFECTIOUS disease": [
        "type 2 diabetes", "scurvy from a lack of vitamin C",
    ],
    "a DEFENCE the body mounts": [
        "white blood cells engulfing invaders",
        "antibodies tagging a specific pathogen",
    ],
}
_DISEASE_GLOSSES = {
    "an INFECTIOUS disease (caused by a pathogen)": "caused by an invading organism; can spread",
    "a NON-INFECTIOUS disease": "no pathogen — lifestyle, genetics or deficiency",
    "a DEFENCE the body mounts": "the immune system: general defenders plus precision antibodies",
}


def gen_disease_types(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _DISEASE,
                       glosses=_DISEASE_GLOSSES, concept_name="DISEASE AND DEFENCE")


# ── Earth & Environmental Science (NEW SUBJECT — AU-only until verified) ─────

_EARTH_STRUCTURE = {
    "true of the CRUST": [
        "the thin, solid outer layer we live on",
        "thinnest under the oceans, thickest under mountains",
    ],
    "true of the MANTLE": [
        "the thick layer of hot rock that slowly flows",
        "the layer whose slow currents move the plates above",
    ],
    "true of the CORE": [
        "a metal centre — liquid outside, solid inside",
        "the source of Earth's magnetic field",
    ],
}
_EARTH_STRUCTURE_GLOSSES = {
    "true of the CRUST": "a few km to ~70 km thin — an eggshell on the planet",
    "true of the MANTLE": "solid rock that creeps over millions of years",
    "true of the CORE": "mostly iron and nickel; the outer part's flow makes the magnetism",
}


def gen_earth_structure(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _EARTH_STRUCTURE,
                       glosses=_EARTH_STRUCTURE_GLOSSES, concept_name="EARTH'S LAYERS")


_MINERALS = {
    "a property used to IDENTIFY a mineral": [
        "its hardness on the Mohs scale",
        "the colour of its streak on a plate",
        "how it splits or breaks (cleavage)",
    ],
    "true of a MINERAL": [
        "a naturally occurring solid with a fixed chemical make-up",
        "quartz and feldspar are examples",
    ],
    "true of an ORE": [
        "rock worth mining because of the metal it holds",
        "bauxite mined as the source of aluminium",
    ],
}
_MINERALS_GLOSSES = {
    "a property used to IDENTIFY a mineral": "tests you can run: scratch, streak, split",
    "true of a MINERAL": "natural, solid, definite composition and structure",
    "true of an ORE": "a mineral deposit that is ECONOMIC to mine",
}


def gen_minerals(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _MINERALS,
                       glosses=_MINERALS_GLOSSES, concept_name="MINERALS AND ORES")


_ROCK_CYCLE = {
    "an IGNEOUS rock (cooled from molten rock)": ["basalt", "granite", "pumice"],
    "a SEDIMENTARY rock (layers pressed together)": ["sandstone", "limestone", "shale"],
    "a METAMORPHIC rock (changed by heat and pressure)": ["marble", "slate"],
}
_ROCK_CYCLE_GLOSSES = {
    "an IGNEOUS rock (cooled from molten rock)": "fast cooling = small crystals; slow = large",
    "a SEDIMENTARY rock (layers pressed together)": "often holds fossils — laid down in layers",
    "a METAMORPHIC rock (changed by heat and pressure)": "an existing rock cooked and squeezed into a new one",
}


def gen_rock_cycle(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _ROCK_CYCLE,
                       glosses=_ROCK_CYCLE_GLOSSES, concept_name="THE ROCK CYCLE")


_ATMOSPHERE = {
    "true of the TROPOSPHERE": [
        "the lowest layer, where all weather happens",
        "temperature falls as you climb through it",
    ],
    "true of the STRATOSPHERE": [
        "home of the ozone layer that absorbs UV",
        "where airliners cruise, above the weather",
    ],
    "true of the GREENHOUSE effect": [
        "certain gases trapping outgoing heat and warming the surface",
        "without it Earth would average well below freezing",
    ],
}
_ATMOSPHERE_GLOSSES = {
    "true of the TROPOSPHERE": "the bottom ~12 km: clouds, rain, wind, us",
    "true of the STRATOSPHERE": "calm, dry, and UV-shielding",
    "true of the GREENHOUSE effect": "natural and necessary — the problem is its ENHANCEMENT",
}


def gen_atmosphere(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _ATMOSPHERE,
                       glosses=_ATMOSPHERE_GLOSSES, concept_name="THE ATMOSPHERE")


_HUMAN_IMPACT = {
    "an impact on the ATMOSPHERE": [
        "burning fossil fuels raising carbon dioxide levels",
        "CFCs thinning the ozone layer",
    ],
    "an impact on WATERWAYS": [
        "fertiliser runoff causing algal blooms",
        "plastic waste accumulating in the ocean",
    ],
    "an impact on LAND and habitats": [
        "clearing forest for farmland",
        "urban sprawl fragmenting habitats",
    ],
}
_HUMAN_IMPACT_GLOSSES = {
    "an impact on the ATMOSPHERE": "what goes up the chimney changes the whole air",
    "an impact on WATERWAYS": "what washes off the land ends up downstream",
    "an impact on LAND and habitats": "lost habitat is the biggest driver of extinction",
}


def gen_human_impact(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _HUMAN_IMPACT,
                       glosses=_HUMAN_IMPACT_GLOSSES, concept_name="HUMAN IMPACT")


_HAZARDS = {
    "true of EARTHQUAKES": [
        "most occur along plate boundaries",
        "their size is compared on the logarithmic magnitude scale",
    ],
    "true of VOLCANOES": [
        "they form where magma reaches the surface",
        "the Pacific Ring of Fire holds most of the active ones",
    ],
    "true of CYCLONES (hurricanes/typhoons)": [
        "they form over warm tropical oceans",
        "they spin around a calm central eye",
    ],
}
_HAZARDS_GLOSSES = {
    "true of EARTHQUAKES": "stored strain at plate edges released suddenly",
    "true of VOLCANOES": "molten rock finding a way up — often at plate boundaries too",
    "true of CYCLONES (hurricanes/typhoons)": "warm ocean water is the fuel tank",
}


def gen_hazards(rng: random.Random):
    return mc_which_is(rng, "Which statement is {label}?", _HAZARDS,
                       glosses=_HAZARDS_GLOSSES, concept_name="NATURAL HAZARDS")


_CLIMATE = {
    "a driver of the OCEAN's role in climate": [
        "currents carrying warmth from the equator toward the poles",
        "the sea absorbing most of the extra trapped heat",
    ],
    "part of the CARBON cycle": [
        "forests taking in carbon dioxide as they grow",
        "decay and burning returning carbon to the air",
    ],
    "evidence used to study PAST climate": [
        "air bubbles trapped in ancient ice cores",
        "tree rings recording good and bad growing years",
    ],
}
_CLIMATE_GLOSSES = {
    "a driver of the OCEAN's role in climate": "the ocean is the climate system's flywheel",
    "part of the CARBON cycle": "carbon moves between air, life, sea and rock",
    "evidence used to study PAST climate": "proxies: nature's own record books",
}


def gen_climate_systems(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _CLIMATE,
                       glosses=_CLIMATE_GLOSSES, concept_name="CLIMATE SYSTEMS")


_RESOURCES = {
    "a RENEWABLE resource": ["solar energy", "wind", "timber from managed forests"],
    "a NON-RENEWABLE resource": ["coal", "natural gas", "iron ore"],
    "a way to manage resources SUSTAINABLY": [
        "recycling metals instead of mining more",
        "quotas that keep fish stocks from collapsing",
    ],
}
_RESOURCES_GLOSSES = {
    "a RENEWABLE resource": "replenished on a human timescale",
    "a NON-RENEWABLE resource": "made over millions of years, used in decades",
    "a way to manage resources SUSTAINABLY": "use today without emptying tomorrow",
}


def gen_resource_management(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _RESOURCES,
                       glosses=_RESOURCES_GLOSSES, concept_name="MANAGING RESOURCES")


_SUSTAINABILITY = {
    "an example of REDUCING demand": [
        "insulating homes so they need less heating",
        "public transport replacing single-car trips",
    ],
    "an example of REUSING or RECYCLING": [
        "refilling water bottles instead of buying new ones",
        "composting food scraps into garden soil",
    ],
    "an example of RESTORING environments": [
        "replanting native trees along cleared river banks",
        "returning wetlands to filter water naturally",
    ],
}
_SUSTAINABILITY_GLOSSES = {
    "an example of REDUCING demand": "the cheapest resource is the one never used",
    "an example of REUSING or RECYCLING": "keep materials in the loop, out of landfill",
    "an example of RESTORING environments": "helping damaged systems heal and work again",
}


def gen_sustainability(rng: random.Random):
    return mc_which_is(rng, "Which of these is {label}?", _SUSTAINABILITY,
                       glosses=_SUSTAINABILITY_GLOSSES, concept_name="SUSTAINABILITY")


# ── Merge tables ─────────────────────────────────────────────────────────────
# senior_science_items.py merges DEPTH_STAGE_CONCEPTS into STAGE_CONCEPTS, so
# every country's senior packs can draw these; EARTH_ENV_STAGE_CONCEPTS is
# registered for AU only.

DEPTH_STAGE_CONCEPTS: dict[str, dict[int, dict[str, GenFn]]] = {
    "physics": {
        1: {
            "heating_processes": gen_heating_processes,
            "nuclear_radiation": gen_nuclear_radiation,
            "circuit_quantities": gen_circuit_quantities,
        },
        2: {
            "gravity_fields": gen_gravity_fields,
            "wave_properties": gen_wave_properties,
            "quantum_ideas": gen_quantum_ideas,
            "relativity_ideas": gen_relativity_ideas,
        },
    },
    "chemistry": {
        1: {
            "atomic_structure": gen_atomic_structure,
            "gas_laws": gen_gas_laws,
            "reaction_kinds": gen_reaction_kinds,
            "organic_basics": gen_organic_basics,
        },
        2: {
            "equilibrium": gen_equilibrium,
            "electrochemistry": gen_electrochemistry,
            "organic_synthesis": gen_organic_synthesis,
        },
    },
    "biology": {
        1: {
            "ecosystem_roles": gen_ecosystem_roles,
            "adaptation_types": gen_adaptation_types,
            "transport_systems": gen_transport_systems,
        },
        2: {
            "dna_protein": gen_dna_protein,
            "evolution_evidence": gen_evolution_evidence,
            "disease_types": gen_disease_types,
        },
    },
}

EARTH_ENV_STAGE_CONCEPTS: dict[int, dict[str, GenFn]] = {
    1: {
        "earth_structure": gen_earth_structure,
        "minerals": gen_minerals,
        "rock_cycle": gen_rock_cycle,
        "atmosphere": gen_atmosphere,
        "human_impact": gen_human_impact,
    },
    2: {
        "hazards": gen_hazards,
        "climate_systems": gen_climate_systems,
        "resource_management": gen_resource_management,
        "sustainability": gen_sustainability,
    },
}
