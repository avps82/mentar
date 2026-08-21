"""W6 (science half): the Y2-10 science strand fill — one disjoint fact table
per reference strand the auditor named MISSING after W7 tagging."""

from __future__ import annotations

import random

from mentar.engine.itemgen import GenFn, mc_which_is


def _mc(table, glosses, concept):
    def gen(rng: random.Random):
        return mc_which_is(rng, "Which of these is {label}?", table,
                           glosses=glosses, concept_name=concept)
    return gen


# ── Year 2 ───────────────────────────────────────────────────────────────────

# Framed by the ACTION, not the object (bug found 2026-08-21): a basketball
# both rolls AND bounces, so "a basketball on a court" was a defensible answer
# to "which ROLLS?" while filed under BOUNCES. Each option now describes motion
# that can only be one of the three.
gen_how_things_move = _mc({
    "something that ROLLS": ["an orange nudged across a table",
                             "a log rolling down a hill",
                             "a wheel turning along the road"],
    "something that SLIDES": ["a book pushed across a desk", "a sled on snow",
                              "a coin skidding across ice"],
    "something that BOUNCES": ["a ball dropped straight down onto concrete",
                               "a basketball dribbled on the spot"],
}, {
    "something that ROLLS": "round things turn over and over as they move",
    "something that SLIDES": "flat things skim along without turning",
    "something that BOUNCES": "springy things push back up when they hit the ground",
}, "HOW THINGS MOVE")

gen_life_cycle_young = _mc({
    "the young of a FROG": ["a tadpole swimming in a pond"],
    "the young of a BUTTERFLY": ["a caterpillar munching a leaf"],
    "the young of a CHICKEN": ["a chick hatching from its egg"],
    "the young of a KANGAROO": ["a joey in its mother's pouch"],
}, {
    "the young of a FROG": "tadpole → froglet → frog: it changes shape as it grows",
    "the young of a BUTTERFLY": "caterpillar → chrysalis → butterfly",
    "the young of a CHICKEN": "egg → chick → hen or rooster",
    "the young of a KANGAROO": "a joey grows up in the pouch",
}, "ANIMALS AND THEIR YOUNG")

gen_saving_water = _mc({
    "a way to SAVE water": ["turning the tap off while brushing your teeth",
                            "a short shower instead of a long one"],
    "a way water gets WASTED": ["a dripping tap left unfixed",
                                "hosing the path instead of sweeping it"],
    "something we USE water for": ["washing clothes", "watering the vegetable garden"],
}, {
    "a way to SAVE water": "using less does the same job with less water",
    "a way water gets WASTED": "water running with nobody using it",
    "something we USE water for": "homes use water for cleaning, drinking and growing",
}, "CARING FOR WATER")

# ── Year 3 ───────────────────────────────────────────────────────────────────

gen_landforms = _mc({
    "a MOUNTAIN": ["a high rocky peak with steep sides"],
    "a RIVER": ["fresh water flowing along a channel to the sea"],
    "a BEACH": ["a sandy shore where waves wash in"],
    "an ISLAND": ["land with water all the way around it"],
}, {
    "a MOUNTAIN": "high land pushed up over a very long time",
    "a RIVER": "flowing water that shapes the land as it goes",
    "a BEACH": "where the sea meets and moves the sand",
    "an ISLAND": "surrounded by water on every side",
}, "LANDFORMS")

gen_animal_groups = _mc({
    "an INSECT (six legs)": ["an ant", "a beetle", "a dragonfly"],
    "a BIRD (feathers)": ["a magpie", "an emu"],
    "a MAMMAL (fur, feeds milk)": ["a kangaroo", "a dog"],
}, {
    "an INSECT (six legs)": "six legs and a body in three parts",
    "a BIRD (feathers)": "feathers and a beak — most can fly, some cannot",
    "a MAMMAL (fur, feeds milk)": "fur or hair, and mothers feed milk",
}, "GROUPING ANIMALS")

gen_material_groups = _mc({
    "a NATURAL material": ["wool from sheep", "wood from trees", "beach sand"],
    "a MANUFACTURED material": ["plastic made in a factory", "concrete mixed for a path"],
    "something sorted for RECYCLING": ["paper in the recycling bin", "empty cans collected for melting down"],
}, {
    "a NATURAL material": "found in nature and used as it is",
    "a MANUFACTURED material": "people made it by changing natural things",
    "something sorted for RECYCLING": "used again instead of thrown away",
}, "GROUPING MATERIALS")

# ── Year 4 ───────────────────────────────────────────────────────────────────

# No "true of ALL THREE" category (bug found 2026-08-21): it was a SUPERSET of
# the other three, so "each one is shaped like a ball" was true of the Moon
# while being the wrong answer to "which is true of the MOON?".
gen_sun_moon_earth = _mc({
    "true of the SUN": ["it is a star that makes its own light and heat",
                        "it is far bigger than the other two"],
    "true of the MOON": ["it circles the Earth about once a month",
                         "it shines only by reflecting sunlight"],
    "true of the EARTH": ["it spins around once every day, giving us day and night",
                          "it is the only one of the three with life on it"],
}, {
    "true of the SUN": "our nearest star — never look straight at it",
    "true of the MOON": "it makes no light of its own",
    "true of the EARTH": "its spin gives us day and night",
}, "SUN, EARTH AND MOON")

# ── Year 5 ───────────────────────────────────────────────────────────────────

gen_solar_system = _mc({
    "a PLANET": ["Mars", "Jupiter", "Venus"],
    "a STAR": ["the Sun", "a point of light burning its own fuel"],
    "a MOON (natural satellite)": ["the object that orbits Earth each month",
                                   "one of Jupiter's many orbiting companions"],
}, {
    "a PLANET": "orbits a star and shines only by reflected light",
    "a STAR": "makes its own light and heat",
    "a MOON (natural satellite)": "orbits a planet, not the Sun directly",
}, "THE SOLAR SYSTEM")

# ── Year 6 ───────────────────────────────────────────────────────────────────

gen_extreme_environments = _mc({
    "an adaptation for the DESERT": ["storing water in a thick stem",
                                     "being active only in the cool night"],
    "an adaptation for the ANTARCTIC": ["a thick layer of blubber",
                                        "huddling in groups to keep warm"],
    "an adaptation for the DEEP SEA": ["making your own light in the darkness",
                                       "coping with crushing water pressure"],
}, {
    "an adaptation for the DESERT": "the problems are heat and almost no water",
    "an adaptation for the ANTARCTIC": "the problem is extreme cold",
    "an adaptation for the DEEP SEA": "the problems are darkness and pressure",
}, "LIFE IN EXTREME PLACES")

gen_geological_change = _mc({
    "a SUDDEN change to the land": ["an earthquake cracking the ground",
                                    "a landslide after heavy rain"],
    "a SLOW change to the land": ["a river carving its valley deeper",
                                  "wind wearing away a rock arch"],
    "a change to the land made by PEOPLE": ["digging a quarry for stone",
                                            "clearing a hillside of trees"],
}, {
    "a SUDDEN change to the land": "over in minutes, remembered for centuries",
    "a SLOW change to the land": "too slow to watch, huge over thousands of years",
    "a change to the land made by PEOPLE": "machines change land faster than nature",
}, "CHANGING LANDSCAPES")

# ── Year 7 ───────────────────────────────────────────────────────────────────

gen_vertebrate_groups = _mc({
    "a FISH": ["it breathes through gills its whole life"],
    "an AMPHIBIAN": ["it starts life in water and moves onto land as an adult"],
    "a REPTILE": ["it has dry scales and lays leathery eggs on land"],
    "a special case: it lays eggs but feeds MILK": ["the platypus"],
}, {
    "a FISH": "gills, fins, lives in water start to finish",
    "an AMPHIBIAN": "two lives: water first, land later",
    "a REPTILE": "scaly skin; eggs out of water",
    "a special case: it lays eggs but feeds MILK": "monotremes break the neat rules — classification has edge cases",
}, "VERTEBRATE GROUPS")

gen_earth_moon_sun_patterns = _mc({
    "caused by Earth SPINNING once a day": ["day turning into night", "the stars seeming to wheel across the night sky"],
    "caused by Earth ORBITING the Sun with a tilt": ["summer changing to winter", "longer days in summer and shorter days in winter"],
    "a PHASE of the Moon": ["a thin crescent growing to a full moon over two weeks", "a half-lit Moon a week after new moon"],
}, {
    "caused by Earth SPINNING once a day": "rotation: your side of Earth turns away from the Sun",
    "caused by Earth ORBITING the Sun with a tilt": "the tilt points your half toward or away from the Sun",
    "a PHASE of the Moon": "we see different amounts of the Moon's sunlit half",
}, "PATTERNS IN THE SKY")

gen_ecosystem_relationships = _mc({
    "a PREDATOR-and-prey relationship": ["an eagle hunting a rabbit", "a spider trapping flies in its web"],
    "COMPETITION between organisms": ["two seedlings racing each other for light", "two magpies squabbling over the same territory"],
    "a relationship where BOTH benefit": ["a bee feeding while pollinating the flower", "a cleaner fish eating parasites off a larger fish"],
}, {
    "a PREDATOR-and-prey relationship": "one eats; the other is eaten",
    "COMPETITION between organisms": "both need the same scarce thing",
    "a relationship where BOTH benefit": "each side gains — mutualism",
}, "ECOSYSTEM RELATIONSHIPS")

gen_water_cycle = _mc({
    "part of the WATER CYCLE": ["water evaporating from the sea",
                                "rain falling from cooling clouds"],
    "a way people STORE water": ["a dam across a river valley", "a rainwater tank by a shed"],
    "a way to use water WISELY": ["watering gardens at dusk so less evaporates"],
}, {
    "part of the WATER CYCLE": "the same water goes round and round: sea, sky, land",
    "a way people STORE water": "saved in wet times for the dry ones",
    "a way to use water WISELY": "same benefit, less water lost",
}, "WATER ON THE MOVE")

# ── Year 8 ───────────────────────────────────────────────────────────────────

gen_organ_systems = _mc({
    "the job of the RESPIRATORY system": ["getting oxygen in and carbon dioxide out"],
    "the job of the SKELETAL system": ["holding the body up and protecting organs"],
    "the job of the MUSCULAR system": ["pulling on bones so the body can move"],
    "the job of the DIGESTIVE system": ["breaking food down so it can be absorbed"],
}, {
    "the job of the RESPIRATORY system": "lungs swap gases with the blood",
    "the job of the SKELETAL system": "the frame: support plus protection",
    "the job of the MUSCULAR system": "muscles only pull — they work in pairs",
    "the job of the DIGESTIVE system": "a long tube that turns meals into fuel",
}, "ORGAN SYSTEMS AND THEIR JOBS")

gen_reaction_signs = _mc({
    "a SIGN a chemical reaction happened": ["gas bubbles forming in the mixture",
                                            "an unexpected colour change",
                                            "the mixture getting hot by itself"],
    "a PHYSICAL change, not a reaction": ["ice melting into water",
                                          "sugar disappearing into tea"],
    "an everyday CHEMICAL reaction": ["a cake rising as it bakes", "iron slowly rusting"],
}, {
    "a SIGN a chemical reaction happened": "a NEW substance appeared",
    "a PHYSICAL change, not a reaction": "same substance, different form — reversible",
    "an everyday CHEMICAL reaction": "kitchens and garages run on chemistry",
}, "SIGNS OF CHEMICAL REACTIONS")

gen_rock_types_junior = _mc({
    "how IGNEOUS rock forms": ["molten rock cooling and hardening", "lava from an eruption setting solid"],
    "how SEDIMENTARY rock forms": ["layers of sediment squashed together over ages", "mud and sand on a sea floor slowly cementing"],
    "how METAMORPHIC rock forms": ["an existing rock changed by heat and pressure underground", "limestone baked deep underground until it becomes marble"],
}, {
    "how IGNEOUS rock forms": "from fire: cooled lava or magma",
    "how SEDIMENTARY rock forms": "from layers: often holds fossils",
    "how METAMORPHIC rock forms": "from change: cooked and squeezed, not melted",
}, "HOW ROCKS FORM")

# ── Year 9 ───────────────────────────────────────────────────────────────────

gen_body_control = _mc({
    "controlled by NERVES (fast messages)": ["pulling your hand off a hot pan",
                                             "blinking as something flies at your eye"],
    "controlled by HORMONES (slow messages)": ["a growth spurt through the teenage years",
                                               "adrenaline keeping you alert after a fright"],
    "true of a REFLEX": ["it happens before you have time to think"],
}, {
    "controlled by NERVES (fast messages)": "electrical signals — milliseconds",
    "controlled by HORMONES (slow messages)": "chemicals in the blood — minutes to years",
    "true of a REFLEX": "the shortcut skips the thinking brain for speed",
}, "NERVES AND HORMONES")

gen_energy_in_reactions = _mc({
    "an EXOTHERMIC reaction (gives out heat)": ["a campfire burning",
                                                "hand-warmers heating up when activated"],
    "an ENDOTHERMIC reaction (takes in heat)": ["an instant cold pack turning icy",
                                                "photosynthesis storing the Sun's energy"],
    "evidence a NEW substance formed": ["a solid appearing when two clear liquids mix"],
}, {
    "an EXOTHERMIC reaction (gives out heat)": "energy leaves — surroundings warm up",
    "an ENDOTHERMIC reaction (takes in heat)": "energy is absorbed — surroundings cool down",
    "evidence a NEW substance formed": "chemistry means new substances, not new shapes",
}, "ENERGY IN REACTIONS")

gen_ecosystem_flows = _mc({
    "how ENERGY moves in an ecosystem": ["flowing one way: sun → plants → animals",
                                         "about 90% lost as heat at each step"],
    "how NUTRIENTS move in an ecosystem": ["cycling round and round via decomposers", "a fallen log rotting back into the soil that feeds new trees"],
    "a reason a POPULATION might crash": ["its food source failing in a drought", "a new predator arriving with no natural enemies"],
}, {
    "how ENERGY moves in an ecosystem": "one-way street — that is why food chains are short",
    "how NUTRIENTS move in an ecosystem": "a loop — atoms are reused forever",
    "a reason a POPULATION might crash": "populations track their resources",
}, "ENERGY AND NUTRIENT FLOWS")

# ── Year 10 ──────────────────────────────────────────────────────────────────

gen_bond_kinds_y10 = _mc({
    "where IONIC bonding happens": ["between a metal and a non-metal, swapping electrons", "in table salt, where sodium hands chlorine an electron"],
    "where COVALENT bonding happens": ["between non-metals, sharing electron pairs", "in a water molecule, where hydrogen and oxygen share"],
    "where METALLIC bonding happens": ["in a metal: a lattice in a sea of free electrons", "in copper wire, where drifting electrons carry the current"],
}, {
    "where IONIC bonding happens": "give and take: charged ions attract",
    "where COVALENT bonding happens": "share and hold: molecules form",
    "where METALLIC bonding happens": "the free electrons make metals conduct",
}, "KINDS OF CHEMICAL BOND")

gen_global_systems = _mc({
    "part of the global CARBON cycle": ["forests absorbing carbon dioxide as they grow", "burning coal returning ancient carbon to the air"],
    "how the OCEAN shapes climate": ["currents carrying heat from the tropics toward the poles", "the sea soaking up most of the trapped extra heat"],
    "the ENHANCED greenhouse effect": ["extra fossil-fuel gases trapping extra heat", "rising carbon dioxide thickening the natural heat blanket"],
}, {
    "part of the global CARBON cycle": "carbon moves between air, life, sea and rock",
    "how the OCEAN shapes climate": "the ocean stores and ships most of the heat",
    "the ENHANCED greenhouse effect": "the natural blanket, thickened by us",
}, "GLOBAL SYSTEMS")

# "SPEEDING UP" / "SLOWING DOWN", not "ACCELERATING" / "DECELERATING"
# (tightened 2026-08-21): by Year 10 a student has learned that deceleration IS
# acceleration with a negative sign, so a braking train was a defensible answer
# to "which is ACCELERATING?" while being marked wrong. The physics vocabulary
# is kept in the labels; the question no longer turns on it.
gen_motion_y10 = _mc({
    "an object at CONSTANT speed": ["a car cruising with the speedo needle steady", "a walker covering the same distance every minute"],
    "an object SPEEDING UP": ["a sprinter pulling away from the blocks",
                              "a dropped stone falling faster and faster"],
    "an object SLOWING DOWN": ["a train braking smoothly into a station", "a rolling ball slowed by grass until it stops"],
}, {
    "an object at CONSTANT speed": "no change per second — zero acceleration",
    "an object SPEEDING UP": "positive acceleration: velocity grows each second",
    "an object SLOWING DOWN": "negative acceleration — still acceleration, pointing backwards",
}, "DESCRIBING MOTION")

gen_periodic_table_y10 = _mc({
    "true of a GROUP (column)": ["its elements share similar chemical behaviour", "lithium, sodium and potassium all sit in it together"],
    "true of a PERIOD (row)": ["across it, elements shift from metal to non-metal", "each step along it adds one proton"],
    "true of the NOBLE gases": ["they barely react with anything at all", "helium and neon are among them"],
}, {
    "true of a GROUP (column)": "same outer electrons → same chemistry",
    "true of a PERIOD (row)": "one more proton and electron at every step",
    "true of the NOBLE gases": "full outer shells — nothing to gain or lose",
}, "READING THE PERIODIC TABLE")

gen_universe_y10 = _mc({
    "true of a GALAXY": ["billions of stars held together by gravity",
                         "our Sun sits in one called the Milky Way"],
    "evidence for the BIG BANG": ["distant galaxies all rushing away from us",
                                  "faint leftover heat filling the whole sky"],
    "true of a LIGHT-YEAR": ["it measures distance — how far light travels in a year", "the nearest star beyond the Sun is about four of them away"],
}, {
    "true of a GALAXY": "stars come in cities of billions",
    "evidence for the BIG BANG": "expansion plus afterglow: the universe had a beginning",
    "true of a LIGHT-YEAR": "a ruler, not a clock",
}, "THE UNIVERSE")


AU_JUNIOR_SCIENCE_FILL: dict[int, dict[str, tuple[GenFn, str, str]]] = {
    2: {
        "au2_science_how_things_move": (gen_how_things_move, "Forces and motion", "How things move"),
        "au2_science_young_animals": (gen_life_cycle_young, "Life cycles", "Animals and their young"),
        "au2_science_saving_water": (gen_saving_water, "Resources", "Caring for water"),
    },
    3: {
        "au3_science_landforms": (gen_landforms, "Earth's surface", "Landforms"),
        "au3_science_animal_groups": (gen_animal_groups, "Grouping living things", "Grouping animals"),
        "au3_science_material_groups": (gen_material_groups, "Grouping materials", "Grouping materials"),
    },
    4: {
        "au4_science_sun_moon_earth": (gen_sun_moon_earth, "Earth and space", "Sun, Earth and Moon"),
    },
    5: {
        "au5_science_solar_system": (gen_solar_system, "Earth's place", "The solar system"),
    },
    6: {
        "au6_science_extreme_environments": (gen_extreme_environments, "Extreme environments", "Life in extreme places"),
        "au6_science_geological_change": (gen_geological_change, "Geological changes", "Changing landscapes"),
    },
    7: {
        "au7_science_vertebrate_groups": (gen_vertebrate_groups, "Classification", "Vertebrate groups"),
        "au7_science_sky_patterns": (gen_earth_moon_sun_patterns, "Earth Moon and Sun", "Patterns in the sky"),
        "au7_science_ecosystem_relationships": (gen_ecosystem_relationships, "Ecosystems", "Ecosystem relationships"),
        "au7_science_water_cycle": (gen_water_cycle, "Water and resources", "Water on the move"),
    },
    8: {
        "au8_science_organ_systems": (gen_organ_systems, "Body systems", "Organ systems and their jobs"),
        "au8_science_reaction_signs": (gen_reaction_signs, "Chemical reactions", "Signs of chemical reactions"),
        "au8_science_rock_types": (gen_rock_types_junior, "Rock cycle", "How rocks form"),
    },
    9: {
        "au9_science_body_control": (gen_body_control, "Body control", "Nerves and hormones"),
        "au9_science_energy_in_reactions": (gen_energy_in_reactions, "Chemical reactions", "Energy in reactions"),
        "au9_science_ecosystem_flows": (gen_ecosystem_flows, "Ecosystems", "Energy and nutrient flows"),
    },
    10: {
        "au10_science_bond_kinds": (gen_bond_kinds_y10, "Chemical bonding", "Kinds of chemical bond"),
        "au10_science_global_systems": (gen_global_systems, "Global systems", "Global systems"),
        "au10_science_motion": (gen_motion_y10, "Motion", "Describing motion"),
        "au10_science_periodic_table": (gen_periodic_table_y10, "Periodic table", "Reading the periodic table"),
        "au10_science_universe": (gen_universe_y10, "Universe", "The universe"),
    },
}
