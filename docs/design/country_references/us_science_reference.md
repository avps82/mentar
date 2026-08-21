# US Science (NGSS) — full reference (maintainer-supplied, 2026-08-21)

Status: **RECEIVED, not yet wired.** W8 precondition for US science
(docs/design/curriculum_depth_program.md). Do not build against this until
the maintainer says go.

**⚠ CONTRADICTS AN EXISTING DECISION — flagged, not resolved:**
`senior_science_items.py`'s `NO_SCIENCE_LEVELS = {"us_g12"}` records that
Grade 12 US science ships NOTHING "by decision (electives, no single shape
to model)" (docs/PHASE0_STATUS.md, 2026-08-15 entry). This reference
DOES supply Grade 12 content: "Advanced Electives / AP Sciences" — Earth &
Environmental Science topics (biogeochemical cycles, soil mechanics,
alternative energy tech, pollution modeling) plus a named AP menu (AP
Biology/Chemistry/Physics/Environmental Science). Whether this is enough to
overturn NO_SCIENCE_LEVELS is a maintainer call, not something to decide by
building it — the original reasoning ("no single shape") may still hold even
with a topic list in hand, since AP is an elective menu, not one syllabus.
Do not silently wire Grade 12 content without that decision being revisited
explicitly.

Aligned to NGSS (Next Generation Science Standards), used by most US states.
Three pillars every grade: Physical Science, Life Science, Earth & Space
Science. Middle school (6-8) is commonly taught as **Integrated Science**
(all three pillars each year) rather than one pillar per year — the topics
below are the NGSS mastery blocks required BY END OF GRADE 8, not per-grade
splits; that shape needs a content-authoring decision of its own, separate
from the existing US_SEQUENCE (Biology G9 → Chemistry G10 → Physics G11,
G12 contested above) which already models high school correctly.

---

## Elementary School (Grades 1 to 5)

### Grade 1
- Physical Science: Light and shadows (how light passes through different materials); sound and vibrations (how sound is made and how it communicates).
- Life Science: Plant and animal parts (roots, stems, fur, eyes) used for survival; how parents and offspring behave to help the young survive.
- Earth & Space Science: Observing patterns of the sun, moon, and stars in the sky; tracking daylight hours across different seasons.

### Grade 2
- Physical Science: Matter and its properties (solids, liquids, heating, cooling); classifying materials by strength, flexibility, and purpose.
- Life Science: What plants need to grow (water, light); how animals help disperse seeds and pollinate plants; diversity of life in different habitats.
- Earth & Space Science: Earth's landforms (mountains, valleys) and water bodies; slow changes to Earth (erosion, weathering) vs. fast changes (volcanoes, earthquakes).

### Grade 3
- Physical Science: Balanced and unbalanced forces; tracking patterns of motion to predict future movement; magnetic and electric interactions.
- Life Science: Plant and animal life cycles; traits inherited from parents vs. traits influenced by the environment; fossils and ancient environments.
- Earth & Space Science: Weather patterns across different seasons; climate zones around the world; evaluating solutions to reduce weather-related hazards.

### Grade 4
- Physical Science: Conservation of energy; speed and energy transfer; wave properties (wavelength, amplitude) and how waves transfer information.
- Life Science: Internal and external structures of plants and animals (e.g., bones, leaves) that support survival, growth, and behavior; animal sensory processing.
- Earth & Space Science: Rock layers and fossil evidence over time; mapping Earth's features; renewable vs. non-renewable energy sources and engineering footprints.

### Grade 5
- Physical Science: Matter is made of particles too small to be seen; conservation of matter during mixing or chemical reactions; gravitational force.
- Life Science: Energy transfer in ecosystems (the sun, producers, consumers, decomposers); movement of matter through plants, animals, and decomposers.
- Earth & Space Science: Interaction of Earth's four major spheres (geosphere, biosphere, hydrosphere, atmosphere); distribution of fresh vs. salt water; distances of stars and solar system scales.

## Middle School (Grades 6 to 8)

Supplied as ONE combined block covering the three pillars' required mastery
"by end of Grade 8" — not split per grade. Do not invent a Grade 6/7/8 split
this reference doesn't make.

### Physical Science (Chemistry & Physics)
- Structure of Matter: Atomic structures, molecules, and chemical formulas; periodic table organization; synthetic vs. natural materials.
- Chemical Reactions: Conservation of mass in closed vs. open systems; chemical reactions that release or absorb thermal energy (exothermic/endothermic).
- Forces & Motion: Newton's Three Laws of Motion; calculating mass, speed, and acceleration; electric, magnetic, and gravitational field forces.
- Energy & Waves: Kinetic vs. potential energy systems; thermal energy transfer (conduction, convection, radiation); mechanical vs. electromagnetic waves.

### Life Science (Biology & Ecology)
- Cells & Organisms: Cell theory; structures and functions of plant/animal cells (organelles); body systems working together to maintain homeostasis.
- Ecosystem Dynamics: Photosynthesis and cellular respiration formulas; competitive, predatory, and mutually beneficial interactions in food webs; ecosystem disruptions.
- Heredity & Evolution: DNA, genes, chromosomes, and mutations; sexual vs. asexual reproduction; fossil records, natural selection, and adaptation over time.

### Earth & Space Science (Geology, Meteorology, Astronomy)
- Earth's Systems: The rock cycle, plate tectonics, and sea-floor spreading; geoscience processes causing natural hazards (prediction and mitigation).
- Weather & Climate: Air masses, pressure systems, and ocean currents; factors driving global climate change (greenhouse effect, human impacts).
- Space Systems: Earth-sun-moon system (seasons, lunar phases, eclipses); gravitational forces in the solar system, galaxies, and the universe.

## High School (Grades 9 to 12)

Standard college-prep sequence — matches the existing `US_SEQUENCE`
(Biology G9 → Chemistry G10 → Physics G11) exactly for grades 9-11.

### Grade 9: Biology (Life Science)
- Biochemistry & Cells: Structure of carbon-based biomolecules (proteins, lipids, carbs, nucleic acids); cellular division (mitosis/meiosis); cellular transport systems.
- Genetics & Heredity: DNA replication, transcription, and translation (protein synthesis); predicting traits using Punnett squares; genetic engineering.
- Evolution & Ecology: Evidence for evolution (homologous structures, embryology); mathematical models of population growth; carrying capacities of ecosystems.

### Grade 10: Chemistry (Physical Science)
- Atomic Structure & Bonding: Electron configurations and valence shells; periodic table trends (electronegativity, atomic radius); ionic, covalent, and metallic bonds.
- Stoichiometry & Reactions: Balancing chemical equations; the mole concept and mass-to-mole conversions; limiting reactants and percent yield.
- Thermodynamics & Kinetics: Collision theory and activation energy; Le Chatelier's principle (chemical equilibrium); enthalpy and entropy changes.

### Grade 11: Physics (Physical Science)
- Mechanics: Kinematics (one-dimensional and two-dimensional motion vectors); dynamics (forces, torque, friction); conservation of momentum and impulse; work, power, and mechanical energy.
- Electricity & Magnetism: Coulomb's law and electric fields; Ohm's law, voltage, current, and series/parallel DC circuits; electromagnetic induction.
- Modern Physics: Quantum mechanics foundations; dual nature of light and matter; nuclear physics (fission, fusion, radioactive half-life decay).

### Grade 12: Advanced Electives / AP Sciences — SEE THE CONTRADICTION FLAG ABOVE
- Earth & Environmental Science: Biogeochemical cycles; soil mechanics and agriculture; alternative energy tech; air/water pollution modeling.
- Advanced Placement (AP/IB) Courses: College-level courses such as AP Biology, AP Chemistry, AP Physics (Algebra- or Calculus-based), or AP Environmental Science, culminating in a national exam for university credit.

Licence note (same posture as us_english_reference.md): NGSS content is
US-state-adopted but the existing US_GENERIC packs claim no alignment;
anything built from this reference inherits that "none claimed" posture.
