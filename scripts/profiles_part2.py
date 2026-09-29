"""
Domain profiles Part 2: Medical, Steel, Pipes & Water, Transformers & Motors, Chemicals, Kitchen Appliances (26 standards).
"""

PART2_PROFILES = {
    # ==================== MEDICAL (3) ====================
    "IS 3055 (Part 1)": {
        "clean_product": "Clinical Thermometers - Solid Stem Type",
        "paraphrases": [
            "solid stem clinical mercury thermometers",
            "clinical thermometers - solid stem type with engraved scale",
            "solid glass stem medical thermometers for body temperature",
            "prismatic solid stem clinical mercury-in-glass thermometers"
        ],
        "indirect_descriptions": [
            "mercury-in-glass diagnostic fever measurement instruments constructed from a solid capillary glass stem with temperature scale etched directly on the exterior glass surface and constriction for maximum reading retention",
            "direct-reading solid glass medical diagnostic thermometric devices featuring constriction capillaries for oral and axillary body temperature measurement",
            "solid stem medical temperature indicators with maximum registering constriction"
        ],
        "key_features": ["direct-etched glass stem graduation", "constriction retention of maximum column", "measurement range (35.5C to 42.0C) with +/-0.1C accuracy"],
        "materials": ["lead-free borosilicate glass", "mercury", "ceramic enamel scale markings"],
        "parameters": {"range": "35.5 C to 42.0 C", "scale_type": "solid stem engraved", "accuracy": "+/- 0.1 C"},
        "application": "clinical body temperature measurement in hospitals and clinics",
        "near_match_candidates": ["IS 3055 (Part 1)", "IS 3055 (Part 2)"],
        "near_match_specs": [
            "Clinical thermometers of solid stem type having markings directly on stem glass (Part 1)",
            "solid stem mercury-in-glass thermometers with etched scale markings",
            "clinical solid stem instruments compliant with IS 3055 (Part 1)"
        ]
    },
    "IS 3055 (Part 2)": {
        "clean_product": "Clinical Thermometers - Enclosed Scale Type",
        "paraphrases": [
            "enclosed scale clinical mercury thermometers",
            "clinical thermometers - enclosed scale type with separate scale strip",
            "sheathed glass enclosed-scale medical thermometers",
            "twin-tube enclosed scale diagnostic thermometers"
        ],
        "indirect_descriptions": [
            "mercury-in-glass clinical fever measurement instruments featuring an internal capillary tube and a separate printed milk-glass scale strip hermetically enclosed within a protective outer glass sheath",
            "enclosed scale diagnostic temperature indicators where the graduated scale strip is mounted behind the capillary within a transparent outer glass casing",
            "hermetically sealed twin-tube medical thermometers with enclosed graduated scale plates"
        ],
        "key_features": ["internal enclosed scale strip protected against wear", "protective outer glass envelope", "maximum registering constriction"],
        "materials": ["borosilicate glass outer envelope", "opal/milk glass scale strip", "mercury"],
        "parameters": {"range": "35.5 C to 42.0 C", "scale_type": "enclosed scale strip", "accuracy": "+/- 0.1 C"},
        "application": "clinical body temperature measurement in healthcare facilities",
        "near_match_candidates": ["IS 3055 (Part 2)", "IS 3055 (Part 1)"],
        "near_match_specs": [
            "Clinical thermometers of enclosed scale type with separate internal scale strip (Part 2)",
            "enclosed scale clinical thermometers with outer protective glass tube",
            "enclosed-scale medical diagnostic thermometers conforming to IS 3055 (Part 2)"
        ]
    },
    "IS 7620 (Part 1)": {
        "clean_product": "Diagnostic Medical X-Ray Equipment",
        "paraphrases": [
            "diagnostic medical X-ray equipment and systems",
            "diagnostic radiological imaging apparatus",
            "medical diagnostic X-ray generators and tube housings",
            "fixed and mobile medical radiographic imaging units"
        ],
        "indirect_descriptions": [
            "radiological imaging medical devices comprising high-voltage generators, rotating anode X-ray tube assemblies, beam-limiting collimators, and exposure controls for clinical diagnostic radiography",
            "high-voltage ionizing radiation medical examination systems with stray radiation shielding and precision focal spot alignment",
            "diagnostic radiographic examination equipment with radiation leakage protection and reproducible dosage control"
        ],
        "key_features": ["radiation leakage shielding conformity", "high-voltage generator reproducibility and kVp accuracy", "timer accuracy and automatic exposure termination"],
        "materials": ["lead shielding", "tungsten anode", "heavy-gauge steel chassis", "high-voltage transformers"],
        "parameters": {"voltage_rating": "40 kV to 150 kV", "shielding": "radiation leakage < 1 mGy/h at 1m"},
        "application": "clinical diagnostic radiography in government hospitals and medical colleges",
        "near_match_candidates": ["IS 7620 (Part 1)"],
        "near_match_specs": [
            "Diagnostic medical X-ray equipment conforming to Part 1 electrical and radiation safety specifications",
            "medical radiographic X-ray imaging units meeting beam limitation and radiation containment criteria",
            "diagnostic X-ray apparatus complying with IS 7620 (Part 1)"
        ]
    },

    # ==================== STEEL (8) ====================
    "IS 15911:2010": {
        "clean_product": "Structural Steel (Ordinary Quality)",
        "paraphrases": [
            "structural steel of ordinary quality",
            "ordinary quality carbon steel sections and plates",
            "standard commercial carbon structural steel",
            "hot-rolled carbon structural steel for non-critical fabrication"
        ],
        "indirect_descriptions": [
            "hot-rolled carbon steel plates, sections, flats, and bars manufactured without guaranteed impact testing, intended for general non-critical civil and mechanical framing works",
            "commercial quality structural steel elements with specified minimum tensile strength and bend properties for non-fatigue load frameworks",
            "ordinary carbon steel structural profiles for secondary architectural and shed framing"
        ],
        "key_features": ["tensile strength range (380-540 MPa)", "bend test ductility", "chemical composition limits for sulfur and phosphorus"],
        "materials": ["carbon steel"],
        "parameters": {"tensile_strength": "380 - 540 MPa", "yield_strength_min": "230 MPa", "quality": "ordinary quality"},
        "application": "general structural framing, warehouse sheds, and secondary support fabrication",
        "near_match_candidates": ["IS 15911:2010", "IS 17404:2020", "IS 18384:2023", "IS 1161:2014"],
        "near_match_specs": [
            "Structural Steel of Ordinary Quality for non-critical engineering fabrication per IS 15911:2010",
            "ordinary quality hot-rolled carbon steel plates and profiles without low-temperature impact guarantee",
            "commercial grade structural carbon steel conforming to IS 15911"
        ]
    },
    "IS 16644:2018": {
        "clean_product": "Stress-Relieved Low Relaxation Steel Wire for Pre-stressed Concrete",
        "paraphrases": [
            "stress-relieved low relaxation steel wire for prestressed concrete (PSC)",
            "low-relaxation high tensile steel prestressing wires",
            "indented and plain prestressing steel wires for bridges",
            "stabilized low-relaxation high carbon steel PSC wire"
        ],
        "indirect_descriptions": [
            "cold-drawn high-carbon steel wires subjected to continuous thermo-mechanical tension stabilization (stress-relieving) to yield ultra-low isothermal stress relaxation under high sustained tensile loads",
            "high-tensile prestressing steel tendons engineered for pre-tensioned and post-tensioned concrete girders, railway sleepers, and flyovers",
            "thermo-mechanically stabilized prestressing high-strength wires displaying guaranteed 1000-hour low relaxation performance"
        ],
        "key_features": ["low isothermal relaxation (<2.5% at 1000 hours at 70% UTS)", "high 0.2% proof stress ratio", "reverse bend fatigue resistance"],
        "materials": ["high carbon steel"],
        "parameters": {"wire_diameter": "3 mm - 7 mm", "uts_min": "1570 - 1860 MPa", "relaxation_1000h_max": "2.5%"},
        "application": "pre-stressed concrete railway sleepers, viaduct girders, and bridge decks",
        "near_match_candidates": ["IS 16644:2018", "IS 15911:2010", "IS 18316:2023"],
        "near_match_specs": [
            "Stress-relieved, low relaxation steel wire specifically for pre-stressed concrete works",
            "high tensile low-relaxation PSC wire with maximum 2.5% relaxation at 1000 hours",
            "prestressing concrete steel wire meeting IS 16644:2018 specifications"
        ]
    },
    "IS 17404:2020": {
        "clean_product": "Electrogalvanized Carbon Steel Sheets and Strips",
        "paraphrases": [
            "electrogalvanized hot rolled and cold reduced carbon steel sheets and strips",
            "electrolytically zinc coated carbon steel sheets",
            "electro-zinc plated cold rolled steel strips",
            "electrolytic galvanized steel sheets for precision fabrication"
        ],
        "indirect_descriptions": [
            "carbon steel sheet and strip substrates electrochemically coated with uniform micro-thin zinc protective layers via continuous electrolytic deposition, providing superior surface smoothness and paint adhesion",
            "electrolytically zinc-plated cold reduced steel coils engineered for home appliance enclosures, switchgear cabinets, and automotive panels",
            "electro-coated zinc-layer carbon steel sheets with high formability and tight coating thickness tolerances"
        ],
        "key_features": ["uniform electrolytic zinc deposit without spangle", "superior spot weldability and phosphate/paint receptivity", "formability and drawing grades"],
        "materials": ["carbon steel substrate", "electrolytic zinc coating"],
        "parameters": {"coating_mass": "10 - 60 g/m2 per side", "substrate": "hot rolled / cold reduced"},
        "application": "appliance enclosures, electrical control panels, and automotive stampings",
        "near_match_candidates": ["IS 17404:2020", "IS 18385:2023", "IS 18513:2023", "IS 15911:2010"],
        "near_match_specs": [
            "Electrogalvanized hot rolled and cold reduced carbon steel sheets and strips per IS 17404:2020",
            "electrolytically zinc coated steel sheets displaying spangle-free uniform coating",
            "electro-zinc carbon steel sheets for precision bending and painting"
        ]
    },
    "IS 18316:2023": {
        "clean_product": "Steel Strips for Electrical Steel Processing",
        "paraphrases": [
            "hot-rolled and cold-rolled steel strips for electrical steel processing",
            "feedstock steel strips for CRGO and CRNGO electrical steels",
            "silicon steel processing precursor steel strips",
            "specialized strip steel for electrical lamination manufacture"
        ],
        "indirect_descriptions": [
            "specialized low-carbon silicon-alloyed flat steel feedstock coils intended for downstream rolling and annealing into grain-oriented (CRGO) or non-grain-oriented (CRNGO) core laminations",
            "high-purity intermediate steel strip products with tightly controlled magnetic inclusion levels, chemistry, and hot-band texture for transformer and motor core stamping",
            "flat rolled steel strip substrate intended for magnetic core electrical steel manufacturing"
        ],
        "key_features": ["strict chemistry control (carbon <0.005%, silicon 0.5-3.5%)", "controlled hot-band grain texture", "low non-metallic inclusion cleanliness"],
        "materials": ["silicon steel alloy", "low carbon steel"],
        "parameters": {"process_route": "semi/fully processed CRGO or CRNGO", "thickness": "1.5 mm - 3.0 mm"},
        "application": "raw material for manufacturing magnetic core laminations for transformers and motors",
        "near_match_candidates": ["IS 18316:2023", "IS 17404:2020", "IS 18384:2023", "IS 1180 (Part 1)"],
        "near_match_specs": [
            "Steel strips intended for processing of semi/fully processed non-grain oriented or grain oriented electrical steel",
            "feedstock steel strips for CRGO/CRNGO magnetic core lamination processing per IS 18316:2023",
            "specialized electrical steel strip raw material meeting magnetic chemistry standards"
        ]
    },
    "IS 18384:2023": {
        "clean_product": "Steel Strip, Sheet and Plates for Welded Steel Pipe for Pipelines",
        "paraphrases": [
            "hot-rolled steel strip, sheet and plates for welded steel pipe for pipeline transportation",
            "pipeline quality hot-rolled steel plates and coils",
            "API/pipeline grade steel sheets for oil, gas and water pipes",
            "high-toughness steel plates for welded pipeline fabrication"
        ],
        "indirect_descriptions": [
            "hot-rolled high-strength low-alloy (HSLA) steel plates and coils manufactured with thermo-mechanically controlled processing (TMCP) for fabrication into submerged arc welded (SAW) and high-frequency welded (HFW) line pipes",
            "heavy-gauge pipeline steel plates with high Charpy V-notch toughness and low carbon equivalent for cross-country hydrocarbon and water pipelines",
            "weldable pipeline plate steel resistant to hydrogen-induced cracking (HIC) for high-pressure line pipe transportation"
        ],
        "key_features": ["high low-temperature drop-weight tear and Charpy toughness", "weldability with low carbon equivalent (CEpcm)", "sour service / HIC resistance criteria"],
        "materials": ["micro-alloyed HSLA steel"],
        "parameters": {"grades": "e.g. X52, X60, X70 equivalents", "process": "TMCP hot-rolled"},
        "application": "fabrication of long-distance oil, gas, slurry, and water transportation line pipes",
        "near_match_candidates": ["IS 18384:2023", "IS 15911:2010", "IS 18385:2023", "IS 1239 (Part 1):2014"],
        "near_match_specs": [
            "Hot-rolled steel strip, sheet and plates specifically for welded steel pipe for pipeline transportation systems",
            "pipeline quality TMCP steel plates meeting Charpy impact and weldability specifications of IS 18384:2023",
            "plate steel engineered for cross-country line pipe manufacturing"
        ]
    },
    "IS 18385:2023": {
        "clean_product": "Hot-Dip Galvanized / Galvannealed Steel Sheet for Automotive Applications",
        "paraphrases": [
            "hot-dip galvanized and galvannealed steel sheet and strips for automotive applications",
            "automotive grade zinc-coated and iron-zinc alloyed steel sheets",
            "galvannealed (GA) high-formability automotive steel strips",
            "corrosion-resistant automotive body panel steel sheets"
        ],
        "indirect_descriptions": [
            "deep-drawing cold-reduced carbon steel sheets continuously coated with hot-dip zinc or heat-treated iron-zinc intermetallic alloys (galvannealed), formulated for automotive body-in-white (BIW) stamping and exterior skin panels",
            "automotive structural and aesthetic sheet steel providing exceptional resistance to perforation corrosion, high weldability, and crater-free automotive paint receptivity",
            "continuous hot-dip coated high-strength automotive steel sheet with tight zinc-iron alloy layer control"
        ],
        "key_features": ["iron-zinc alloy phase control (galvannealed 8-12% Fe)", "drawability and bake-hardening capability", "resistance to cyclic automotive corrosion tests"],
        "materials": ["extra-low carbon / IF steel substrate", "zinc-iron alloy coating"],
        "parameters": {"coating_type": "GI (galvanized) / GA (galvannealed)", "coating_mass": "30 - 120 g/m2"},
        "application": "automotive body stampings, chassis components, and anti-corrosive vehicle enclosures",
        "near_match_candidates": ["IS 18385:2023", "IS 17404:2020", "IS 18513:2023"],
        "near_match_specs": [
            "Hot-dip galvanized/galvannealed steel sheet and strips specifically for automotive applications",
            "automotive grade GA/GI sheets with controlled zinc-iron alloy layer per IS 18385:2023",
            "high formability zinc-coated automotive body panel steel"
        ]
    },
    "IS 18513:2023": {
        "clean_product": "Hot-Dip Zinc-Aluminium-Magnesium (ZAM) Alloy Coated Steel Sheets",
        "paraphrases": [
            "hot-dip zinc-aluminium-magnesium alloy coated steel sheets, plates and strips",
            "Zn-Al-Mg (ZAM) ternary alloy coated corrosion resistant steel sheets",
            "zinc-aluminum-magnesium coated steel for harsh outdoor exposure",
            "self-healing edge-corrosion resistant ZAM steel coils"
        ],
        "indirect_descriptions": [
            "high-durability flat steel products continuously coated via molten alloy bath containing zinc, aluminium, and magnesium, engineered for extraordinary atmospheric barrier protection and self-healing cut-edge passivation",
            "ternary alloy coated structural steel coils providing five to ten times higher corrosion resistance than traditional galvanizing in coastal and agricultural solar racking environments",
            "zinc-aluminium-magnesium metallic coated steel plates displaying superior resistance to red rust in severe industrial chloride atmospheres"
        ],
        "key_features": ["ternary alloy coating (Zn + Al + Mg)", "cut-edge self-healing hydroxide film formation", "extreme salt spray corrosion endurance"],
        "materials": ["steel substrate", "zinc-aluminium-magnesium alloy coating"],
        "parameters": {"coating_composition": "Zn with 1-11% Al and 1-3% Mg", "coating_mass": "90 - 450 g/m2"},
        "application": "solar mounting structures, coastal infrastructure, agricultural sheds, and highway crash barriers",
        "near_match_candidates": ["IS 18513:2023", "IS 17404:2020", "IS 18385:2023", "IS 15911:2010"],
        "near_match_specs": [
            "Hot-dip zinc - aluminium - magnesium alloy coated steel sheets, plates and strips",
            "ternary Zn-Al-Mg coated steel exhibiting cut-edge self-healing corrosion resistance per IS 18513:2023",
            "ZAM alloy coated steel sheets for aggressive environmental exposure"
        ]
    },
    "IS 8329:2000": {
        "clean_product": "Centrifugally Cast (Spun) Ductile Iron Pressure Pipes",
        "paraphrases": [
            "centrifugally cast (spun) ductile iron pressure pipes for water, gas and sewage",
            "ductile iron (DI) pressure pipes with socket and spigot joints",
            "centrifugal spun ductile iron piping for water supply mains",
            "cement mortar lined ductile iron pipeline conduits"
        ],
        "indirect_descriptions": [
            "spheroidal graphite (ductile) iron pipeline conduits produced through centrifugal spinning in metal moulds, featuring high tensile strength, elongation ductility, and internal cement mortar anti-corrosive linings",
            "heavy-duty pressurized fluid conveyance pipes engineered for underground potable water distribution, sewerage force mains, and gas delivery under high surge pressures",
            "centrifugally cast ductile iron pressure pipes with push-on flexible rubber gasket joints for civil water networks"
        ],
        "key_features": ["spheroidal graphite nodularity (>80%)", "internal sulphate-resisting cement mortar lining", "high burst and beam load resistance"],
        "materials": ["ductile iron (spheroidal graphite)", "cement mortar lining", "zinc/bitumen outer coating"],
        "parameters": {"pressure_classes": "Class K7 / K9 / K12 / C-class", "nominal_diameter": "DN 80 mm - DN 2000 mm", "joints": "push-on Tyton joint"},
        "application": "urban potable water distribution networks, raw water trunk mains, and sewerage force mains",
        "near_match_candidates": ["IS 8329:2000", "IS 9523:2000", "IS 1729:2002", "IS 1239 (Part 1):2014"],
        "near_match_specs": [
            "Centrifugally cast (spun) ductile iron pressure pipes for water, gas and sewage per IS 8329:2000",
            "ductile iron pressure pipes with internal cement mortar lining and flexible push-on socket joints",
            "spigot and socket spun DI pipes conforming to Class K7/K9 pressure ratings"
        ]
    },

    # ==================== PIPES & WATER (4) ====================
    "IS 9523:2000": {
        "clean_product": "Ductile Iron Fittings for Pressure Pipes",
        "paraphrases": [
            "ductile iron fittings for pressure pipes for water, gas and sewage",
            "ductile iron bends, tees, reducers and tapers for water pipelines",
            "sand-cast and molded ductile iron pipeline fittings",
            "socketed and flanged ductile iron pipe fittings"
        ],
        "indirect_descriptions": [
            "spheroidal graphite cast iron junction and flow-control pipeline components comprising tees, bends, flanged spigots, reducers, and duckfoot bends designed to connect ductile iron pressure lines",
            "molded ductile iron pipeline connector fittings equipped with rubber gasket socket chambers or drilled flange faces for pressurized municipal water works",
            "ductile iron plumbing fittings with internal protective coatings engineered to withstand hydraulic surge in potable water networks"
        ],
        "key_features": ["nodular graphite structure with minimum 10% elongation", "hydrostatic factory pressure testing without leakage", "flanged or push-on socket compatibility"],
        "materials": ["ductile iron", "fusion-bonded epoxy / cement mortar lining"],
        "parameters": {"diameters": "DN 80 mm - DN 2000 mm", "pressure_rating": "PN 10 / PN 16 / PN 25"},
        "application": "directional changes, branching, and valve connections in municipal water pipelines",
        "near_match_candidates": ["IS 9523:2000", "IS 8329:2000", "IS 1239 (Part 1):2014"],
        "near_match_specs": [
            "Ductile iron fittings for pressure pipes for water, gas and sewage per IS 9523:2000",
            "ductile iron pipe fittings (tees, bends, reducers) compatible with DI pressure piping",
            "flanged and socketed ductile iron fittings complying with IS 9523"
        ]
    },
    "IS 1161:2014": {
        "clean_product": "Steel Tubes for Structural Purposes",
        "paraphrases": [
            "steel tubes for structural purposes (circular hollow sections)",
            "circular hollow sections (CHS) for structural steel fabrication",
            "welded and seamless structural steel tubular profiles",
            "structural grade tubular steel sections for trusses and columns"
        ],
        "indirect_descriptions": [
            "circular hollow structural sections produced by high-frequency electric resistance welding or seamless extrusion, engineered for structural frameworks, columns, space trusses, and scaffolding",
            "structural steel circular pipes manufactured to specific yield stress grades (YSt 210, YSt 240, YSt 310) providing high torsional resistance and uniform section modulus",
            "tubular carbon steel load-bearing profiles for airport terminal trusses, stadium canopies, and transmission towers"
        ],
        "key_features": ["structural yield strength grades (YSt 210, YSt 240, YSt 310)", "flattening and bend test ductility", "dimensional tolerances on outside diameter and wall thickness"],
        "materials": ["carbon steel"],
        "parameters": {"grades": "YSt 210, YSt 240, YSt 310", "type": "circular hollow section (CHS)"},
        "application": "architectural space frames, industrial roof trusses, structural columns, and scaffolding",
        "near_match_candidates": ["IS 1161:2014", "IS 1239 (Part 1):2014", "IS 4270:2001", "IS 15911:2010"],
        "near_match_specs": [
            "Steel tubes specifically for structural purposes conforming to IS 1161:2014",
            "circular hollow structural steel tubes graded YSt 210/240/310 for load-bearing frameworks",
            "structural tubular steel sections excluding fluid conveyance specifications"
        ]
    },
    "IS 1239 (Part 1):2014": {
        "clean_product": "Mild Steel Tubes for Water, Gas and Steam",
        "paraphrases": [
            "steel tubes, tubulars and wrought steel fittings - Part 1: steel tubes",
            "mild steel ERW pipes for water, gas, steam and air lines",
            "galvanized and black mild steel conveyance tubes",
            "GI and MS pipes conforming to light, medium and heavy classes"
        ],
        "indirect_descriptions": [
            "electric resistance welded (ERW) and seamless mild steel tubular conduits in black or hot-dip galvanized finish, engineered for fluid transport of water, steam, compressed air, and non-corrosive gases",
            "commercial plumbing and fire-sprinkler steel conveyance pipes categorized into Light (Class A), Medium (Class B), and Heavy (Class C) pressure categories",
            "threaded and plain-end mild steel pipes for domestic plumbing, firefighting lines, and cooling loops"
        ],
        "key_features": ["pressure classification (Light/Medium/Heavy)", "hot-dip zinc galvanizing weight (>400 g/m2 for GI pipes)", "hydraulic test pressure (5 MPa) without leakage"],
        "materials": ["mild carbon steel", "hot-dip zinc galvanizing"],
        "parameters": {"nominal_bore": "15 mm to 150 mm", "classes": "Class Light / Medium / Heavy", "finish": "black / galvanized (GI)"},
        "application": "water distribution lines, steam conveyance, gas transmission, and fire-sprinkler piping",
        "near_match_candidates": ["IS 1239 (Part 1):2014", "IS 1161:2014", "IS 4270:2001", "IS 8329:2000"],
        "near_match_specs": [
            "Steel tubes, tubulars and other wrought steel fittings - Part 1: Steel tubes per IS 1239 (Part 1):2014",
            "mild steel fluid conveyance pipes categorized into Light, Medium, and Heavy classes",
            "black and galvanized (GI) mild steel pipes for water, gas and steam lines"
        ]
    },
    "IS 4270:2001": {
        "clean_product": "Steel Tubes for Water Wells (up to 200 mm dia)",
        "paraphrases": [
            "steel tubes used for water-wells (up to 200 mm diameter)",
            "water well casing pipes and slotted screen tubes",
            "seamless and ERW casing pipes for tubewell boring",
            "heavy-wall water-well casing steel tubes"
        ],
        "indirect_descriptions": [
            "seamless and electric resistance welded steel tubular casing conduits with threaded screwd-and-socket or bevelled-end joints, engineered for insertion into drilled water boreholes to prevent borehole wall collapse",
            "heavy-gauge cylindrical steel well-casing tubes with tight straightness tolerances and high collapse resistance for deep agricultural and municipal groundwater extraction wells",
            "drilled water-well lining tubes and screen pipes up to 200 mm nominal bore for groundwater development"
        ],
        "key_features": ["high resistance to external hydrostatic collapse pressure", "straightness tolerance for borehole plumbing alignment", "precision API/screwed-socket casing threads"],
        "materials": ["carbon steel"],
        "parameters": {"size_range": "up to 200 mm nominal bore", "joints": "screwed and socketed / flush jointed / bevelled", "application": "water wells"},
        "application": "deep tubewell casing and groundwater extraction infrastructure",
        "near_match_candidates": ["IS 4270:2001", "IS 1161:2014", "IS 1239 (Part 1):2014"],
        "near_match_specs": [
            "Steel tubes specifically used for water-wells up to 200 mm diameter per IS 4270:2001",
            "tubewell casing steel pipes with screwed socket joints for deep borehole insertion",
            "water-well steel casing conduits complying with IS 4270"
        ]
    },

    # ==================== TRANSFORMERS & MOTORS (4) ====================
    "IS 1180 (Part 1)": {
        "clean_product": "Outdoor Oil Immersed Distribution Transformers",
        "paraphrases": [
            "outdoor type oil immersed distribution transformers up to 2500 kVA, 33 kV",
            "mineral oil immersed electrical distribution transformers",
            "three-phase pad/pole mounted oil filled distribution transformers",
            "energy efficient mineral oil immersed distribution transformers"
        ],
        "indirect_descriptions": [
            "stationary electrical electromagnetic induction apparatus housed in hermetically sealed or conservator steel tanks with radiator fins, insulated with mineral oil for stepping down grid distribution voltages",
            "three-phase liquid-immersed power conversion units up to 2500 kVA with standard maximum total loss limits at 50% and 100% loading for DISCOM electrification",
            "outdoor oil-cooled distribution transformers rated up to 33 kV with off-circuit tap changers and conservator oil breather systems"
        ],
        "key_features": ["standard maximum total loss level limits (Energy Efficiency Levels 1, 2, 3)", "mineral insulating oil dielectric breakdown strength (>30 kV)", "short-circuit withstand capability"],
        "materials": ["copper/aluminium winding", "CRGO silicon steel core", "transformer mineral oil", "mild steel tank"],
        "parameters": {"capacity": "up to 2500 kVA", "primary_voltage": "11 kV / 22 kV / 33 kV", "cooling": "ONAN"},
        "application": "electrical power distribution networks, rural electrification, and substation substations",
        "near_match_candidates": ["IS 1180 (Part 1)", "IS 12615", "IS 13340"],
        "near_match_specs": [
            "Outdoor type oil immersed distribution transformers up to and including 2500 kVA, 33 kV (Part 1)",
            "mineral oil filled distribution transformers conforming to IS 1180 (Part 1) loss levels",
            "three-phase distribution transformers with guaranteed energy efficiency ratings per IS 1180"
        ]
    },
    "IS 12615": {
        "clean_product": "Energy Efficient Three-Phase Induction Motors",
        "paraphrases": [
            "energy efficient induction motors - three phase squirrel cage",
            "line operated three-phase squirrel cage induction motors (IE2/IE3)",
            "high efficiency industrial AC induction electric motors",
            "energy efficient totally enclosed fan cooled (TEFC) induction motors"
        ],
        "indirect_descriptions": [
            "rotary electromagnetic machines with squirrel-cage rotor construction designed for direct-on-line operation from three-phase AC supplies, delivering standardized mechanical power at IE2, IE3, or IE4 efficiency classes",
            "totally enclosed fan-cooled (TEFC) cast-iron framed electric drive motors engineered to minimize copper and iron core losses during continuous industrial driving duty",
            "industrial AC three-phase drive motors compliant with efficiency classification and temperature rise thresholds"
        ],
        "key_features": ["efficiency classes (IE2 - High Efficiency, IE3 - Premium Efficiency)", "full-load efficiency and power factor performance", "Class F insulation with Class B temperature rise limit"],
        "materials": ["copper rotor/stator conductors", "low-loss silicon steel laminations", "cast iron frame"],
        "parameters": {"phase": "three-phase AC", "efficiency_class": "IE2 / IE3", "enclosure": "TEFC IP55"},
        "application": "industrial water pumps, compressors, fans, machine tools, and conveyors",
        "near_match_candidates": ["IS 12615", "IS 1180 (Part 1)", "IS 2993"],
        "near_match_specs": [
            "Energy Efficient Induction Motors - Three Phase Squirrel Cage per IS 12615",
            "line-operated three-phase motors meeting IE2 or IE3 efficiency levels",
            "squirrel cage AC induction motors conforming to IS 12615 specifications"
        ]
    },
    "IS 2993": {
        "clean_product": "A.C. Motor Capacitors",
        "paraphrases": [
            "a.c. motor capacitors for single-phase induction motors",
            "motor start and motor run metallized polypropylene capacitors",
            "dielectric capacitors for single-phase electric motors",
            "self-healing motor run capacitors for household appliances"
        ],
        "indirect_descriptions": [
            "passive electrical energy storage components employing metallized polypropylene dielectric films wound into non-inductive cylinders with flame-retardant encapsulation, used to produce auxiliary phase displacement in single-phase induction motors",
            "continuous motor-run and intermittent motor-start AC capacitors featuring self-healing dielectric properties and overpressure disconnect safety mechanisms",
            "alternating current capacitors intended for starting and continuous running of single-phase fractional horsepower motors in fans, pumps, and refrigerators"
        ],
        "key_features": ["self-healing metallized film dielectric", "overpressure safety disconnector mechanism", "endurance testing at 1.25 times rated voltage"],
        "materials": ["metallized polypropylene film", "polyurethane resin", "aluminium/plastic can"],
        "parameters": {"voltage_rating": "250 V - 450 V AC", "frequency": "50 Hz", "type": "motor run / start"},
        "application": "phase split circuits for ceiling fans, washing machines, submersible pumps, and air conditioner compressors",
        "near_match_candidates": ["IS 2993", "IS 13340", "IS 12615"],
        "near_match_specs": [
            "A.C. motor capacitors intended specifically for single-phase motor start and run per IS 2993",
            "motor run capacitors with self-healing metallized film dielectric for appliance motors",
            "single-phase induction motor capacitors complying with IS 2993"
        ]
    },
    "IS 13340": {
        "clean_product": "Self-Healing Power Capacitors for AC Systems up to 650 V",
        "paraphrases": [
            "power capacitors of self-healing type for AC power systems up to 650 V",
            "low voltage shunt power factor correction capacitors",
            "self-healing LV power capacitors for APFC panels",
            "three-phase metal-enclosed power factor correction capacitors"
        ],
        "indirect_descriptions": [
            "three-phase reactive power compensation capacitor banks utilizing metallized dielectric polymer film with automatic self-healing breakdown clearing, designed for parallel shunt connection in low-voltage power distribution systems",
            "low-voltage electrical power factor correction modules equipped with internal discharge resistors and tear-off overpressure fuses to optimize industrial reactive power",
            "self-healing power factor capacitors rated up to 650V for reducing kVA demand and line losses in electrical sub-stations"
        ],
        "key_features": ["self-healing metallized dielectric clears micro-faults", "internal discharge resistor to reduce voltage below 50V in 60s", "overpressure internal tear-off disconnector"],
        "materials": ["metallized polypropylene film", "biodegradable insulating oil/resin", "extruded aluminium can"],
        "parameters": {"rated_voltage": "up to 650 V AC", "reactive_power": "5 kVAr to 50 kVAr", "frequency": "50 Hz"},
        "application": "power factor improvement panels (APFC) in industrial commercial substations",
        "near_match_candidates": ["IS 13340", "IS 2993", "IS 1180 (Part 1)"],
        "near_match_specs": [
            "Power Capacitors of Self-healing Type for AC power systems having rated voltage up to 650 V",
            "shunt power factor correction capacitors for LV electrical installations per IS 13340",
            "self-healing power capacitors for APFC panels meeting IS 13340 standards"
        ]
    },

    # ==================== CHEMICALS (4) ====================
    "IS 252:2013": {
        "clean_product": "Caustic Soda (Sodium Hydroxide)",
        "paraphrases": [
            "caustic soda (sodium hydroxide) flakes and lye",
            "sodium hydroxide technical and rayon grade",
            "industrial caustic soda solid, flakes and liquid solution",
            "high purity chemical caustic soda for industrial processing"
        ],
        "indirect_descriptions": [
            "strongly alkaline chemical compound (NaOH) manufactured via chlor-alkali electrolysis, supplied as white hygroscopic flakes, fused solid blocks, or concentrated liquid lye for industrial synthesis and neutralization",
            "alkaline inorganic process reagent meeting rigorous purity thresholds for sodium hydroxide content and strictly limited carbonate, chloride, and iron impurities",
            "chemical grade sodium hydroxide for pulp bleaching, soap manufacturing, textile scouring, and effluent water neutralization"
        ],
        "key_features": ["NaOH purity (minimum 99.5% for rayon grade, 98.0% for technical)", "low sodium carbonate and chloride impurities", "hygroscopic and corrosive chemical safety packaging"],
        "materials": ["sodium hydroxide (NaOH)"],
        "parameters": {"grades": "Rayon grade / Technical grade", "forms": "flakes / lye / solid", "assay_min": "98.0% - 99.5%"},
        "application": "water treatment neutralization, textile scouring, soap making, and paper manufacturing",
        "near_match_candidates": ["IS 252:2013", "IS 10116:2015", "IS 15573"],
        "near_match_specs": [
            "Caustic Soda (sodium hydroxide) conforming to specification IS 252:2013",
            "rayon and technical grade caustic soda flakes and lye with guaranteed NaOH purity",
            "industrial sodium hydroxide complying with chemical limits of IS 252"
        ]
    },
    "IS 10116:2015": {
        "clean_product": "Boric Acid",
        "paraphrases": [
            "boric acid (H3BO3) - specification",
            "industrial and technical grade boric acid powder",
            "orthoboric acid crystals and granules",
            "refined boric acid for glass and industrial chemical manufacture"
        ],
        "indirect_descriptions": [
            "monobasic Lewis acid of boron supplied as free-flowing white crystalline powder or translucent scales, utilized as a chemical raw material, fluxing agent, preservative, and glass batch constituent",
            "purified orthoboric acid (H3BO3) manufactured with controlled trace levels of heavy metals, sulphates, and chlorides for industrial and chemical synthesis",
            "technical grade boric acid powder for borosilicate glassware manufacturing, ceramics, and flame retardancy treatments"
        ],
        "key_features": ["assay of H3BO3 (minimum 99.5%)", "trace limits on sulphate, chloride, and iron content", "free-flowing crystalline white appearance"],
        "materials": ["boric acid (H3BO3)"],
        "parameters": {"grades": "Special / Technical / Explosive", "purity_min": "99.5%", "moisture_max": "0.5%"},
        "application": "borosilicate glass production, optical fibers, wood preservation, and metallurgy fluxing",
        "near_match_candidates": ["IS 10116:2015", "IS 252:2013", "IS 2833:2019"],
        "near_match_specs": [
            "Boric acid conforming to specification IS 10116:2015",
            "technical grade orthoboric acid powder with minimum 99.5% purity",
            "industrial boric acid crystals meeting IS 10116 chemical purity criteria"
        ]
    },
    "IS 15573": {
        "clean_product": "Poly Aluminium Chloride (PAC)",
        "paraphrases": [
            "poly aluminium chloride (PAC) for water treatment",
            "polymeric aluminium chlorohydrate flocculant coagulant",
            "poly aluminium chloride powder and liquid for municipal water",
            "inorganic polymeric coagulant for drinking water purification"
        ],
        "indirect_descriptions": [
            "pre-hydrolyzed polynuclear inorganic aluminium coagulant compound supplied as yellow powder or aqueous solution, engineered to accelerate turbidity coagulation, flock formation, and color removal in raw potable water",
            "high-basicity polymeric coagulating chemical for municipal drinking water filtration plants and wastewater treatment facilities",
            "chemical coagulant reagent for rapid settling of suspended colloidal particles in water purification works"
        ],
        "key_features": ["alumina content (Al2O3 min 10% for liquid, 30% for powder)", "basicity ratio (35% to 65%)", "low trace levels of arsenic, cadmium, and lead"],
        "materials": ["poly aluminium chloride"],
        "parameters": {"forms": "liquid / powder", "al2o3_content_min": "10% liquid / 30% powder", "basicity": "35 - 65%"},
        "application": "potable water purification, sewage effluent treatment, and industrial effluent clarification",
        "near_match_candidates": ["IS 15573", "IS 252:2013", "IS 16240:2023"],
        "near_match_specs": [
            "Poly Aluminium Chloride (PAC) for water purification conforming to IS 15573",
            "polymeric aluminium coagulant for municipal potable water treatment",
            "PAC flocculant meeting basicity and alumina content standards of IS 15573"
        ]
    },
    "IS 2833:2019": {
        "clean_product": "Aniline",
        "paraphrases": [
            "aniline (amino-benzene) technical grade",
            "aniline oil for industrial organic chemical synthesis",
            "pure chemical aniline liquid in sealed drums",
            "monomeric aromatic amine aniline for dye and rubber chemicals"
        ],
        "indirect_descriptions": [
            "primary aromatic amine organic liquid synthesized by catalytic hydrogenation of nitrobenzene, supplied as a pale yellow to brownish oily liquid for chemical manufacturing",
            "organic chemical intermediate compound meeting strict distillation range and assay criteria for the synthesis of methylene diphenyl diisocyanate (MDI), rubber vulcanization accelerators, and dyes",
            "technical grade aniline liquid with tightly restricted nitrobenzene and moisture fractions"
        ],
        "key_features": ["purity assay (minimum 99.5% by mass)", "distillation range (183C to 185C)", "water content not exceeding 0.2%"],
        "materials": ["aniline (C6H5NH2)"],
        "parameters": {"assay_min": "99.5%", "distillation_range": "183.0 C - 185.0 C", "water_max": "0.2%"},
        "application": "chemical synthesis of polyurethane intermediates, rubber processing chemicals, dyes, and pharmaceuticals",
        "near_match_candidates": ["IS 2833:2019", "IS 252:2013", "IS 10116:2015"],
        "near_match_specs": [
            "Aniline technical grade conforming to specification IS 2833:2019",
            "chemical grade aniline with minimum 99.5% assay and controlled distillation range",
            "industrial aromatic amine aniline compliant with IS 2833"
        ]
    },

    # ==================== KITCHEN APPLIANCES (3) ====================
    "IS 302 (Part 2/Section 14)": {
        "clean_product": "Safety of Hand-Held Blenders",
        "paraphrases": [
            "safety requirements for hand-held electric food blenders",
            "immersion hand blenders and puree sticks",
            "motorized hand-held culinary food immersion blenders",
            "hand-held electric kitchen blenders with detachable blending shafts"
        ],
        "indirect_descriptions": [
            "hand-supported motorized culinary food preparation appliances featuring a slender immersion shaft with rotating stainless steel chopping blades designed for blending liquids, puréeing soups, and emulsifying food within containers",
            "domestic handheld food processing immersion devices equipped with ergonomic handles, momentary power triggers, and splash-guard blade hoods",
            "handheld electro-mechanical kitchen immersion blenders meeting electrical and mechanical blade guarding safety thresholds"
        ],
        "key_features": ["blade guard safety barrier preventing accidental contact", "intermittent duty thermal protection", "double insulation (Class II) construction"],
        "materials": ["ABS plastic motor body", "stainless steel shaft and blade", "copper motor coil"],
        "parameters": {"voltage": "230 V AC", "rated_power": "200W - 400W", "insulation": "Class II double insulated"},
        "application": "domestic food preparation, hospital diet kitchens, and institutional pantries",
        "near_match_candidates": ["IS 302 (Part 2/Section 14)", "IS 4250", "IS 302 : Part 1 (2024)"],
        "near_match_specs": [
            "Safety of household electrical appliances specifically for hand-held blenders (Part 2/Section 14)",
            "hand-held immersion food blenders with blade guarding and Class II insulation",
            "electric hand-held blenders complying with IS 302-2-14"
        ]
    },
    "IS 4250": {
        "clean_product": "Domestic Electric Food Mixers, Liquidizers and Grinders",
        "paraphrases": [
            "domestic electric food mixer (liquidizers and grinders) and centrifugal juicer",
            "electric mixer grinder (mixie) with stainless steel jars",
            "multi-jar food processors, dry grinders and wet liquidizers",
            "motorized kitchen mixer grinders with overload protector"
        ],
        "indirect_descriptions": [
            "countertop domestic food processing machines powered by high-speed universal motors with detachable stainless steel liquidizing, dry grinding, and wet chutney jars equipped with cutting blades",
            "multi-purpose household electric kitchen food mixers featuring rotary speed switches and thermal bi-metallic overload trip protection",
            "electric food preparation machines combining liquidizing, wet and dry grinding, and centrifugal juicing functions"
        ],
        "key_features": ["universal motor with thermal overload circuit breaker", "jar interlocking safety mechanism", "continuous and pulse speed regulation"],
        "materials": ["ABS plastic main body", "stainless steel jars", "hardened stainless steel blades"],
        "parameters": {"motor_wattage": "500W / 750W / 1000W", "voltage": "230 V AC", "jars": "liquidizing / grinding / chutney"},
        "application": "domestic food preparation, hostel messes, and commercial pantries",
        "near_match_candidates": ["IS 4250", "IS 302 (Part 2/Section 14)", "IS 302 : Part 1 (2024)"],
        "near_match_specs": [
            "Domestic electric food mixer (liquidizers and grinders) and centrifugal juicer per IS 4250",
            "electric mixer grinders with stainless steel jars and thermal overload protection",
            "multi-jar domestic food mixing and grinding appliances conforming to IS 4250"
        ]
    },
    "IS 15558": {
        "clean_product": "Instantaneous Domestic Water Heaters for LPG",
        "paraphrases": [
            "instantaneous domestic water heaters for use with liquefied petroleum gas (gas geysers)",
            "gas-fired instantaneous tankless water heaters for LPG",
            "flue-type instantaneous domestic LPG water geysers",
            "continuous-flow gas water heaters with flame failure safety"
        ],
        "indirect_descriptions": [
            "wall-mounted tankless water heating appliances utilizing atmospheric gas burners fueled by LPG to instantly heat flowing domestic water through a copper finned-tube heat exchanger upon water tap demand",
            "instantaneous continuous-flow gas geysers equipped with automatic pulse ignition, water-gas interlock valves, and oxygen depletion safety sensors (ODS)",
            "domestic LPG gas-fired water heaters providing immediate hot water without storage tanks"
        ],
        "key_features": ["flame failure safety shutoff valve", "water-gas pressure interlocking control", "overheat thermal cutout and 20-minute safety timer"],
        "materials": ["copper heat exchanger", "stainless steel burners", "powder-coated steel casing"],
        "parameters": {"capacity": "5L/min - 10L/min", "fuel": "LPG", "type": "instantaneous gas geyser"},
        "application": "domestic hot water supply in residential quarters and guest houses",
        "near_match_candidates": ["IS 15558", "IS 4246:2025", "IS 302 (Part 2/Sec 201)"],
        "near_match_specs": [
            "Instantaneous domestic water heaters for use with Liquefied Petroleum Gas (LPG) per IS 15558",
            "gas geysers operating on LPG with automatic ignition and water-gas interlock",
            "instantaneous LPG water heating appliances conforming to IS 15558"
        ]
    }
}
