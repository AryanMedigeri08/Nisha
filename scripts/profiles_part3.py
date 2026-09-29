"""
Domain profiles Part 3: HVAC, PPE, Refrigeration, Water Treatment, Wood, Cast Iron, Solar & Cables, Glassware, Accessories, Agriculture, Copper, Door Fittings (36 standards).
"""

PART3_PROFILES = {
    # ==================== HVAC (5) ====================
    "IS 1391 (Part-1):2017": {
        "clean_product": "Room Air Conditioners - Unitary Air Conditioners",
        "paraphrases": [
            "room air conditioners - Part 1: unitary (window) air conditioners",
            "unitary window type room air conditioners",
            "self-contained window mounted room air conditioners",
            "single-package window air conditioning units"
        ],
        "indirect_descriptions": [
            "self-contained factory-assembled refrigeration air conditioning machines housed within a single cabinet, engineered for mounting through a wall sleeve or window opening to deliver filtered and dehumidified air",
            "unitary window-mounted vapor compression cooling systems with hermetic rotary compressors and capillary tube expansion for residential or office cooling",
            "single-package electro-mechanical room cooling appliances providing sensible and latent thermal capacity without external interconnecting refrigerant piping"
        ],
        "key_features": ["cooling capacity rating test", "cooling seasonal performance factor (CSPF)", "maximum operating conditions test (no trip at 46C)"],
        "materials": ["galvanized sheet metal casing", "copper piping", "aluminium finned coils", "R32/R410A refrigerant"],
        "parameters": {"capacity": "0.75 TR - 2.0 TR", "type": "unitary / window", "voltage": "230 V single-phase"},
        "application": "climate control in government offices, staff quarters, and conference rooms",
        "near_match_candidates": ["IS 1391 (Part-1):2017", "IS 1391 (Part-2):2018", "IS 8148:2018"],
        "near_match_specs": [
            "Room Air Conditioners - Part 1: Unitary (window type) Air Conditioners per IS 1391 (Part-1):2017",
            "unitary single-chassis window air conditioners excluding split-type systems",
            "self-contained window air cooling units conforming to IS 1391-1"
        ]
    },
    "IS 1391 (Part-2):2018": {
        "clean_product": "Room Air Conditioners - Split Air Conditioners",
        "paraphrases": [
            "room air conditioners - Part 2: split air conditioners",
            "high-wall ductless split air conditioning systems",
            "inverter and fixed-speed split room air conditioners",
            "two-unit split type room cooling systems"
        ],
        "indirect_descriptions": [
            "two-part vapor-compression air conditioning systems comprising an indoor fan-coil air-handling unit and a separate outdoor condensing unit connected via field-installed refrigerant copper tubing",
            "ductless wall-mounted split cooling units incorporating variable-frequency inverter motor drives, low-noise crossflow fans, and wireless remote control",
            "split-type electro-mechanical comfort cooling appliances with separate indoor cooling and outdoor heat dissipation modules"
        ],
        "key_features": ["seasonal energy efficiency ratio (ISEER)", "sound pressure level of indoor unit (<45 dB)", "interconnecting flare/brazed refrigerant line integrity"],
        "materials": ["ABS plastic indoor casing", "galvanized powder coated outdoor unit", "copper tubes", "hydrophilic aluminium fins"],
        "parameters": {"capacity": "1.0 TR / 1.5 TR / 2.0 TR", "type": "split unit (indoor + outdoor)", "refrigerant": "R32 / R410A"},
        "application": "comfort cooling in executive offices, meeting rooms, hospitals, and guest houses",
        "near_match_candidates": ["IS 1391 (Part-2):2018", "IS 1391 (Part-1):2017", "IS 8148:2018"],
        "near_match_specs": [
            "Room Air Conditioners - Part 2: Split Air Conditioners per IS 1391 (Part-2):2018",
            "split-type room air conditioners featuring separate indoor high-wall and outdoor condensing units",
            "ductless split AC units meeting ISEER efficiency standards of IS 1391-2"
        ]
    },
    "IS 8148:2018": {
        "clean_product": "Ducted and Packaged Air Conditioners",
        "paraphrases": [
            "ducted and package air conditioners",
            "commercial packaged air conditioning units",
            "ducted split and rooftop packaged AC systems",
            "centralized ducted packaged climate control systems"
        ],
        "indirect_descriptions": [
            "medium-to-large capacity factory-engineered comfort cooling assemblies designed for connection to ductwork air distribution networks, featuring high-static blower fans and scroll compressors",
            "commercial ducted central cooling systems serving large open-plan office zones, server halls, and auditorium spaces through supply air duct distribution",
            "high-capacity packaged environmental cooling plants with water-cooled or air-cooled condenser configurations"
        ],
        "key_features": ["external static pressure capability for duct distribution", "energy efficiency ratio (EER) under full and part load", "multi-circuit scroll compressor staging"],
        "materials": ["heavy-gauge galvanized steel frame", "copper coils", "scroll compressors", "acoustic insulation"],
        "parameters": {"capacity": "3.0 TR to 25.0 TR", "type": "ducted / packaged unit", "phase": "three-phase 415 V"},
        "application": "central cooling for banquet halls, office floors, server rooms, and healthcare departments",
        "near_match_candidates": ["IS 8148:2018", "IS 1391 (Part-2):2018", "IS 1391 (Part-1):2017"],
        "near_match_specs": [
            "Ducted and Package Air Conditioners per IS 8148:2018",
            "packaged commercial air conditioners designed for ductwork distribution",
            "high-capacity ducted air conditioning equipment conforming to IS 8148"
        ]
    },
    "IS 11329:2018": {
        "clean_product": "Finned Type Heat Exchangers for Room Air Conditioners",
        "paraphrases": [
            "finned type heat exchangers for room air conditioners",
            "copper tube aluminium fin cooling and condensing coils",
            "extended surface finned heat exchangers for RAC units",
            "evaporator and condenser finned tube coil assemblies"
        ],
        "indirect_descriptions": [
            "extended-surface thermal transfer assemblies manufactured by mechanically expanding seamless round copper tubes into corrugated or louvered aluminium foil fins for refrigerant-to-air heat exchange",
            "high-efficiency evaporator and condenser heat exchanging coils treated with hydrophilic or anti-corrosive epoxy coatings for air conditioning refrigeration circuits",
            "finned tubular heat exchangers engineered to withstand cyclic refrigerant pressures and environmental airborne salinity"
        ],
        "key_features": ["burst pressure and pneumatic leak test (helium/nitrogen at >2.5 MPa)", "tube-to-fin mechanical bond tightness", "fin surface corrosion resistance"],
        "materials": ["seamless deoxidized high-phosphorus copper tubes", "hydrophilic aluminium foil fins"],
        "parameters": {"fin_type": "louvered / corrugated aluminium", "tube_od": "7 mm / 9.52 mm", "test_pressure": "> 2.5 MPa"},
        "application": "cooling coils and condensing coils for room air conditioning manufacturing",
        "near_match_candidates": ["IS 11329:2018", "IS 10617:2018", "IS 1391 (Part-2):2018"],
        "near_match_specs": [
            "Finned type heat exchangers specifically for room air conditioners per IS 11329:2018",
            "copper tube aluminium fin heat exchanger coils meeting pneumatic pressure integrity",
            "evaporator and condenser finned heat exchangers conforming to IS 11329"
        ]
    },
    "IS 10617:2018": {
        "clean_product": "Hermetic Compressors for Refrigeration and Air Conditioning",
        "paraphrases": [
            "hermetic compressors for air conditioning and refrigeration",
            "hermetically sealed rotary and reciprocating refrigerant compressors",
            "welded steel shell hermetic motor-compressor units",
            "hermetic vapor compression cooling pump units"
        ],
        "indirect_descriptions": [
            "welded leak-tight steel-cased fluid compression assemblies enclosing both an electric motor and a rotary or reciprocating compressor mechanism within a continuous refrigerant-oil atmosphere",
            "positive displacement hermetic refrigerant compressors engineered to pump eco-friendly refrigerants with high volumetric efficiency and low acoustic vibration",
            "hermetically enclosed refrigeration compressors with internal motor overload protectors and suction gas cooling"
        ],
        "key_features": ["hermetic shell weld tightness and burst pressure safety", "locked rotor current and motor winding insulation endurance", "isentropic and volumetric compression efficiency"],
        "materials": ["drawn carbon steel casing", "copper stator windings", "hardened alloy steel rotor/shaft"],
        "parameters": {"refrigerants": "R32 / R410A / R134a", "type": "rotary / reciprocating hermetic", "voltage": "230 V / 415 V"},
        "application": "refrigerant circulation in domestic air conditioners, commercial chillers, and refrigerators",
        "near_match_candidates": ["IS 10617:2018", "IS 11329:2018", "IS 17550 (Part 1):2021"],
        "near_match_specs": [
            "Hermetic compressors for air conditioning and refrigeration per IS 10617:2018",
            "hermetically sealed welded motor-compressor assemblies meeting pressure and electrical safety",
            "refrigeration hermetic compressors conforming to IS 10617"
        ]
    },

    # ==================== FOOTWEAR / PPE (4) ====================
    "IS 15298 (Part 2):2016": {
        "clean_product": "Personal Protective Equipment - Safety Footwear (200J Toecap)",
        "paraphrases": [
            "personal protective equipment - Part 2: safety footwear (200 Joules toecap)",
            "industrial safety footwear with 200J steel or composite toecap",
            "heavy-duty safety boots with impact and compression resistant toecaps",
            "protective leather safety shoes for heavy construction and industrial hazards"
        ],
        "indirect_descriptions": [
            "specialized industrial protective occupational footwear fitted with internal metallic or composite safety toecaps tested to withstand an impact energy of 200 Joules and compression load of 15 kN",
            "full-grain leather industrial boots featuring puncture-resistant midsole inserts, oil/acid resistant anti-static polyurethane outsoles, and 200J crush-proof toe protection",
            "safety grade personal protective footwear engineered for heavy construction sites and metal foundry environments"
        ],
        "key_features": ["toecap impact resistance minimum 200 Joules", "toecap compression resistance minimum 15 kN", "antistatic and slip-resistant outsole performance"],
        "materials": ["full grain breathable leather", "steel / composite toecap", "dual-density PU outsole"],
        "parameters": {"impact_resistance": "200 Joules", "compression_resistance": "15 kN", "category": "Safety Footwear (Part 2)"},
        "application": "personal protection in construction sites, heavy engineering factories, and mining works",
        "near_match_candidates": ["IS 15298 (Part 2):2016", "IS 15298 (Part 3):2019", "IS 15298 (Part 4):2017"],
        "near_match_specs": [
            "Personal protective equipment - Part 2: Safety Footwear incorporating 200 Joules impact toecap",
            "safety footwear with certified 200J toe protection and 15 kN compression resistance per IS 15298 (Part 2)",
            "heavy-duty safety shoes meeting Part 2 specifications"
        ]
    },
    "IS 15298 (Part 3):2019": {
        "clean_product": "Personal Protective Equipment - Protective Footwear (100J Toecap)",
        "paraphrases": [
            "personal protective equipment - Part 3: protective footwear (100 Joules toecap)",
            "protective industrial footwear with 100J toecap protection",
            "medium-duty protective shoes for warehouse and logistical handling",
            "protective boots with 100 Joule impact resistant safety toe"
        ],
        "indirect_descriptions": [
            "occupational protective footwear incorporating internal protective toecaps engineered to withstand an intermediate impact energy of 100 Joules and compression of 10 kN",
            "medium-hazard industrial work shoes with slip-resistant soles, energy absorption in the heel area, and 100J mechanical toe protection",
            "protective footwear providing moderate impact protection for logistical, warehouse, and light manufacturing operations"
        ],
        "key_features": ["toecap impact resistance minimum 100 Joules", "toecap compression resistance minimum 10 kN", "slip resistance on ceramic and steel floor surfaces"],
        "materials": ["leather upper", "lightweight protective toecap", "polyurethane sole"],
        "parameters": {"impact_resistance": "100 Joules", "compression_resistance": "10 kN", "category": "Protective Footwear (Part 3)"},
        "application": "logistics centers, warehousing operations, light assembly plants, and maintenance workshops",
        "near_match_candidates": ["IS 15298 (Part 3):2019", "IS 15298 (Part 2):2016", "IS 15298 (Part 4):2017"],
        "near_match_specs": [
            "Personal protective equipment - Part 3: Protective Footwear incorporating 100 Joules impact toecap",
            "protective footwear with certified 100J toe impact protection per IS 15298 (Part 3)",
            "medium-hazard protective shoes meeting Part 3 specifications"
        ]
    },
    "IS 15298 (Part 4):2017": {
        "clean_product": "Personal Protective Equipment - Occupational Footwear (No Toecap)",
        "paraphrases": [
            "personal protective equipment - Part 4: occupational footwear (without toecap)",
            "occupational work shoes without toe impact protection",
            "soft-toe anti-slip occupational shoes for hospital and catering staff",
            "workplace occupational footwear for non-mechanical hazards"
        ],
        "indirect_descriptions": [
            "workplace occupational footwear manufactured without protective toecaps, designed for personnel exposed to non-mechanical hazards like slip and fall, static electricity, and water ingress",
            "lightweight ergonomic occupational shoes featuring slip-resistant profiled soles, heel energy absorption, and antistatic properties for healthcare, kitchen, and laboratory staff",
            "comfortable work footwear providing ergonomic support and skid resistance without impact-resistant toecap reinforcements"
        ],
        "key_features": ["no toecap required", "slip resistance compliance (SRA / SRB / SRC)", "antistatic and energy absorption of seat region"],
        "materials": ["leather or microfibre upper", "cushioned EVA / PU outsole"],
        "parameters": {"toecap": "none (occupational)", "slip_resistance": "tested on ceramic / steel", "category": "Occupational Footwear (Part 4)"},
        "application": "healthcare staff, commercial kitchen workers, pharmaceutical cleanrooms, and hospitality staff",
        "near_match_candidates": ["IS 15298 (Part 4):2017", "IS 15298 (Part 2):2016", "IS 15298 (Part 3):2019"],
        "near_match_specs": [
            "Personal protective equipment - Part 4: Occupational Footwear without impact toecap requirements",
            "occupational soft-toe work shoes with certified slip resistance and antistatic soles per IS 15298 (Part 4)",
            "occupational footwear meeting Part 4 specifications for non-mechanical hazard environments"
        ]
    },
    "IS 4151:2015": {
        "clean_product": "Helmets for Riders of Two-Wheeler Motor Vehicles",
        "paraphrases": [
            "protective helmets for riders of two-wheeler motor vehicles",
            "motorcycle rider safety helmets (full-face and open-face)",
            "two-wheeler vehicular protective crash helmets",
            "motorcyclist headgear with impact attenuation and retention system"
        ],
        "indirect_descriptions": [
            "protective headgear assemblies comprising a rigid shock-deflecting thermoplastic or composite outer shell, impact-absorbing expanded polystyrene (EPS) liner, retention chinstrap, and shatter-resistant visor",
            "motor vehicle protective crash helmets subjected to rigorous drop-tower impact attenuation, penetration resistance, and chinstrap retention dynamic load tests",
            "safety head protection equipment engineered to protect motorcycle operators from traumatic brain injuries during vehicular collisions"
        ],
        "key_features": ["peak impact deceleration (<300 g)", "penetration test resistance against sharp striker", "retention chin-strap dynamic displacement and release mechanism"],
        "materials": ["ABS / polycarbonate shell", "high-density EPS protective liner", "scratch-resistant polycarbonate visor"],
        "parameters": {"head_sizes": "540 mm to 600 mm", "mass_max": "1500 grams", "retention": "quick-release chinstrap"},
        "application": "personal head protection for police riders, dispatch couriers, and motorists",
        "near_match_candidates": ["IS 4151:2015", "IS 15298 (Part 2):2016"],
        "near_match_specs": [
            "Helmets for riders of two-wheeler motor vehicles conforming to IS 4151:2015",
            "motorcycle protective helmets with certified impact attenuation and penetration resistance",
            "two-wheeler safety headgear satisfying dynamic retention and visor clarity standards of IS 4151"
        ]
    },

    # ==================== REFRIGERATION & WATER (3) ====================
    "IS 17550 (Part 1):2021": {
        "clean_product": "Household Refrigerating Appliances - General Requirements",
        "paraphrases": [
            "household refrigerating appliances - characteristics and test methods Part 1: general requirements",
            "domestic refrigerators and frost-free refrigerating appliances",
            "household electric refrigerators and food storage chillers",
            "vapor-compression domestic food preservation refrigerators"
        ],
        "indirect_descriptions": [
            "thermally insulated food storage cabinets cooled by integral vapor compression refrigeration circuits, engineered to maintain internal compartment temperatures between 0C and +8C for food preservation",
            "domestic cold storage appliances subjected to rigorous pull-down, storage temperature, energy consumption, and thermal insulation airtightness test methods",
            "residential electric refrigerators with hermetic cooling systems and cyclopentane blown polyurethane foam thermal insulation"
        ],
        "key_features": ["storage compartment temperature performance", "energy consumption and annual kilowatt-hour efficiency", "safety against electrical and refrigerant flammability hazards"],
        "materials": ["pre-painted galvanized steel cabinet", "HIPS food-grade inner liner", "polyurethane (PUF) insulation", "R600a isobutane"],
        "parameters": {"storage_volume": "180 L to 500 L", "climate_class": "Tropical (T)", "refrigerant": "isobutane (R600a)"},
        "application": "food preservation in residential quarters, hospital wards, and guest house kitchens",
        "near_match_candidates": ["IS 17550 (Part 1):2021", "IS 7872:2018", "IS 10617:2018"],
        "near_match_specs": [
            "Household refrigerating appliances - Part 1: General requirements and test methods per IS 17550 (Part 1):2021",
            "domestic electric refrigerators for fresh food storage with tropical climate rating",
            "household food preservation refrigerators conforming to IS 17550-1"
        ]
    },
    "IS 7872:2018": {
        "clean_product": "Freezers",
        "paraphrases": [
            "domestic and commercial deep freezers",
            "chest freezers and upright deep storage freezing cabinets",
            "sub-zero food storage deep freezers (-18C)",
            "commercial and domestic deep freezing storage units"
        ],
        "indirect_descriptions": [
            "heavy-insulated low-temperature food preservation cabinets capable of cooling and freezing fresh foodstuffs and maintaining internal temperatures at or below -18C in all storage baskets",
            "commercial and household chest-type or upright deep-freezing appliances with high freezing capacity, skin-condenser systems, and low-temperature sealing gaskets",
            "sub-zero thermodynamic storage equipment engineered for continuous preservation of frozen foods and medical samples"
        ],
        "key_features": ["freezing capacity (cooling food from ambient to -18C within 24h)", "temperature rise time during power interruption (>12 hours)", "sub-zero storage uniformity (-18C)"],
        "materials": ["embossed aluminium / pre-coated steel tank", "high-density PUF insulation", "spring-assisted insulated lid"],
        "parameters": {"storage_temperature": "<= -18 C", "capacity": "100 L to 600 L", "lid_type": "top-opening chest / upright door"},
        "application": "bulk food preservation, commercial kitchens, dairy distribution, and medical vaccine depots",
        "near_match_candidates": ["IS 7872:2018", "IS 17550 (Part 1):2021"],
        "near_match_specs": [
            "Freezers conforming to low-temperature specification IS 7872:2018",
            "deep freezers maintaining <= -18C internal storage temperature",
            "chest and upright deep freezing cabinets meeting freezing capacity criteria of IS 7872"
        ]
    },
    "IS 16240:2023": {
        "clean_product": "Reverse Osmosis (RO) Based Point-of-Use Water Treatment Systems",
        "paraphrases": [
            "reverse osmosis based point of use (PoU) water treatment systems for drinking purposes",
            "domestic RO drinking water purifiers with multi-stage filtration",
            "point-of-use reverse osmosis water purification plants",
            "membrane-based drinking water purification appliances"
        ],
        "indirect_descriptions": [
            "pressurized multi-stage drinking water purification systems employing semi-permeable thin-film composite reverse osmosis membranes alongside sediment pre-filters, activated carbon blocks, and post-mineralizers",
            "point-of-use domestic and institutional water filtration devices designed to reduce total dissolved solids (TDS), heavy metal ions, cysts, and chemical contaminants from raw tap water",
            "water treatment appliances providing guaranteed recovery ratio, microbial reduction, and purified water output meeting drinking thresholds"
        ],
        "key_features": ["TDS reduction percentage (>90% rejection)", "recovery ratio (minimum 40% water recovery)", "microbial and chemical contaminant reduction validation"],
        "materials": ["food-grade polypropylene filter housings", "polyamide thin-film composite RO membrane", "activated carbon block"],
        "parameters": {"flow_rate": "10 L/h - 50 L/h", "tds_reduction_min": "90%", "recovery_rate_min": "40%"},
        "application": "safe drinking water generation in offices, residential schools, clinics, and government buildings",
        "near_match_candidates": ["IS 16240:2023", "IS 15573"],
        "near_match_specs": [
            "Reverse Osmosis based point of use water treatment system for drinking purposes per IS 16240:2023",
            "point-of-use RO drinking water purifiers with certified TDS rejection and minimum 40% water recovery",
            "membrane-based water purification appliances conforming to IS 16240"
        ]
    },

    # ==================== WOOD PRODUCTS (4) ====================
    "IS 1659:2004": {
        "clean_product": "Block Boards",
        "paraphrases": [
            "block boards for furniture and interior joinery",
            "commercial and decorative solid wood blockboards",
            "bonded timber blockboards with face veneers",
            "grade I and grade II block boards for woodworking"
        ],
        "indirect_descriptions": [
            "composite timber building panels manufactured with a core of solid wood blocks or strips not exceeding 25 mm width, laid edge-to-edge between crossbands and commercial face veneers bonded under heat and pressure",
            "rigid warp-resistant wood panels constructed from seasoned softwood batten cores surfaced on both faces with timber veneers for cabinetry and modular paneling",
            "solid wooden batten core structural boards complying with moisture content and screw holding tests"
        ],
        "key_features": ["solid wood core strips without voids", "water resistance bonding (BWP / MR grades)", "high modulus of rupture and screw holding power"],
        "materials": ["seasoned timber core blocks", "commercial / decorative veneers", "phenolic / amino resin adhesive"],
        "parameters": {"grades": "Grade I (BWP) / Grade II (MR)", "thickness": "19 mm / 25 mm", "core_block_width_max": "25 mm"},
        "application": "office partitions, wooden doors, shelves, cabinetry, and structural interior furniture",
        "near_match_candidates": ["IS 1659:2004", "IS 12823:2015", "IS 3087:2005", "IS 12406:2021"],
        "near_match_specs": [
            "Block Boards consisting of solid timber core blocks bonded between wood veneers per IS 1659:2004",
            "solid wooden batten core blockboards conforming to Grade I (BWP) or Grade II (MR)",
            "blockboards meeting screw holding and adhesion criteria of IS 1659"
        ]
    },
    "IS 12823:2015": {
        "clean_product": "Prelaminated Particle Boards",
        "paraphrases": [
            "prelaminated particle boards from wood and other lignocellulosic materials",
            "melamine faced prelaminated particle boards",
            "pre-laminated particle boards with decorative surface lamination",
            "decorative resin-impregnated paper laminated particle boards"
        ],
        "indirect_descriptions": [
            "wood-based composite panels produced by bonding decorative melamine-impregnated paper foils under thermal pressure directly onto both surfaces of plain particle boards without secondary wet adhesives",
            "factory-surfaced modular furniture panels featuring scratch-resistant, cigarette burn resistant, and stain-proof decorative melamine overlays on lignocellulosic core boards",
            "pre-laminated modular panels for office workstations and institutional storage units with matching edge-banded surfaces"
        ],
        "key_features": ["direct melamine paper thermal lamination (Grade I / Grade II)", "surface abrasion and stain resistance", "internal bond strength and moisture swelling limits"],
        "materials": ["wood particles / agro-residues", "melamine impregnated decorative paper", "synthetic resin"],
        "parameters": {"grades": "Grade I (exterior) / Grade II (interior)", "surface_types": "suede / matt / glossy finish", "thickness": "9 mm - 25 mm"},
        "application": "modular office workstations, computer desks, filing cabinets, and wall paneling",
        "near_match_candidates": ["IS 12823:2015", "IS 3087:2005", "IS 12406:2021", "IS 1659:2004"],
        "near_match_specs": [
            "Prelaminated particle boards from wood and other lignocellulosic materials per IS 12823:2015",
            "melamine faced prelaminated particle boards with factory-fused decorative surfaces",
            "pre-laminated panels satisfying surface abrasion and moisture resistance of IS 12823"
        ]
    },
    "IS 3087:2005": {
        "clean_product": "Particle Boards of Wood (Medium Density) for General Purpose",
        "paraphrases": [
            "particle boards of wood and other lignocellulosic materials (medium density) for general purpose",
            "plain medium density wood particle boards",
            "unlaminated three-layer flat-pressed particle boards",
            "resin-bonded raw chipboards for interior fabrication"
        ],
        "indirect_descriptions": [
            "unlaminated reconstituted wood panels fabricated by compressing wood chips, flakes, or shavings bound together with thermosetting synthetic resins under heat in a flat platen press",
            "plain three-layer or graduated density structural chipboards exhibiting uniform core density and fine surface particle distribution for veneer or laminate substrate use",
            "raw medium density particle board panels satisfying mechanical bending and internal bond strength thresholds"
        ],
        "key_features": ["medium density range (500 to 900 kg/m3)", "internal bond tensile strength perpendicular to surface", "bending modulus of rupture (MOR)"],
        "materials": ["wood chips / flakes", "urea formaldehyde / phenol formaldehyde resin"],
        "parameters": {"grades": "Grade I (exterior) / Grade II (interior)", "density": "500 - 900 kg/m3", "surface": "plain unlaminated"},
        "application": "core substrate for laminating, false ceilings, partition framing, and acoustic paneling",
        "near_match_candidates": ["IS 3087:2005", "IS 12823:2015", "IS 12406:2021", "IS 1659:2004"],
        "near_match_specs": [
            "Particle boards of wood and other lignocellulosic materials (medium density) for general purpose per IS 3087:2005",
            "plain unlaminated medium density particle boards for structural furniture substrates",
            "raw chipboards conforming to mechanical strength limits of IS 3087"
        ]
    },
    "IS 12406:2021": {
        "clean_product": "Medium Density Fibreboards (MDF) for General Purpose",
        "paraphrases": [
            "medium density fibre boards (MDF) for general purpose",
            "engineered wood medium density fibreboards (MDF)",
            "homogeneous dry-process MDF boards for routing and joinery",
            "interior and exterior grade MDF panels"
        ],
        "indirect_descriptions": [
            "dry-process engineered wood panels manufactured by reducing wood into individual lignocellulosic fibers, combining them with synthetic resin adhesive, and hot-pressing into dense panels with smooth machinable surfaces",
            "homogeneous structural wood fibre panels having uniform internal density suitable for intricate CNC edge routing, profiling, carving, and direct polyurethane paint finishing",
            "defect-free engineered wood fiberboards with high tensile strength perpendicular to the face and low edge swelling"
        ],
        "key_features": ["uniform fiber consistency throughout thickness without knots or grain voids", "exceptional edge-routing and paint-receptivity characteristics", "screw withdrawal resistance on face and edge"],
        "materials": ["refined wood fibers", "synthetic polymer resin"],
        "parameters": {"density": "650 - 900 kg/m3", "grades": "Grade I (exterior) / Grade II (interior)", "thickness": "6 mm - 35 mm"},
        "application": "CNC profiled cabinet shutters, decorative jaali screens, door cores, and architectural moldings",
        "near_match_candidates": ["IS 12406:2021", "IS 3087:2005", "IS 12823:2015", "IS 1659:2004"],
        "near_match_specs": [
            "Medium density fibre boards (MDF) for general purpose per IS 12406:2021",
            "engineered wood fiberboards with uniform machinable density for precision CNC routing",
            "MDF panels conforming to mechanical and moisture resistance criteria of IS 12406"
        ]
    },

    # ==================== CAST IRON (3) ====================
    "IS 1726:1991": {
        "clean_product": "Cast Iron Manhole Covers and Frames",
        "paraphrases": [
            "cast iron manhole covers and frames for drainage and sewerage",
            "heavy duty cast iron sewer chamber covers and frames",
            "circular and rectangular cast iron manhole access covers",
            "road traffic cast iron manhole frame assemblies"
        ],
        "indirect_descriptions": [
            "heavy-duty gray or ductile cast iron access chamber closures and supporting peripheral frames engineered to seal underground municipal drainage, sewerage, and stormwater inspection chambers against surface water and wheel loads",
            "cast iron roadway inspection chamber access sets graded for Light, Medium, Heavy, and Extra-Heavy wheel traffic with non-rocking seating geometry",
            "sand-cast iron road covers with patterned non-slip surfaces and lifting key slots designed for heavy vehicular axle loading"
        ],
        "key_features": ["load test classification (LD, MD, HD, EHD up to 350 kN / 400 kN)", "non-rocking concentric seating", "corrosion-resistant black bituminous dipping"],
        "materials": ["grey cast iron (grade FG 150 / FG 200)", "bituminous coating"],
        "parameters": {"grades": "LD-2.5 / MD-10 / HD-20 / EHD-35", "clear_opening": "450 mm / 560 mm / 600 mm", "shape": "circular / rectangular"},
        "application": "municipal highways, city sewerage networks, stormwater culverts, and airport runways",
        "near_match_candidates": ["IS 1726:1991", "IS 1729:2002", "IS 210:2009"],
        "near_match_specs": [
            "Cast iron manhole covers and frames conforming to loading classes of IS 1726:1991",
            "heavy-duty cast iron sewer inspection covers with certified non-rocking frames",
            "cast iron roadway access covers meeting load testing criteria of IS 1726"
        ]
    },
    "IS 1729:2002": {
        "clean_product": "Cast Iron / Ductile Iron Drainage Pipes and Fittings",
        "paraphrases": [
            "cast iron/ductile iron drainage pipes and pipe fittings (socket and spigot)",
            "cast iron soil, waste and rainwater drainage pipes",
            "socket and spigot cast iron soil pipes for building drainage",
            "spun cast iron non-pressure sanitary drainage pipes"
        ],
        "indirect_descriptions": [
            "cast iron and ductile iron tubular gravity drainage conduits and junction fittings manufactured with socket and spigot ends for above-ground soil, waste, and rainwater drainage systems in buildings",
            "sand-cast and centrifugally spun iron sanitary drainage pipes coated with anti-corrosive bitumen for non-pressure plumbing stacks and roof rainwater disposal",
            "rigid acoustic-dampening iron drainage pipelines designed for non-pressurized wastewater transit in institutional building stacks"
        ],
        "key_features": ["acoustic sound damping of wastewater flow", "socket and spigot lead/rubber gasket jointing", "hydraulic leak test for gravity flow"],
        "materials": ["grey cast iron / ductile iron", "protective bituminous lacquer"],
        "parameters": {"diameters": "50 mm / 75 mm / 100 mm / 150 mm", "type": "socket and spigot non-pressure", "finish": "bitumen dipped"},
        "application": "vertical sanitary soil and waste stacks, vent pipes, and rainwater downspouts in multi-story buildings",
        "near_match_candidates": ["IS 1729:2002", "IS 1726:1991", "IS 8329:2000"],
        "near_match_specs": [
            "Cast iron/ductile iron drainage pipes and fittings for overground non-pressure pipelines per IS 1729:2002",
            "socket and spigot cast iron soil and rainwater drainage pipes for building stacks",
            "non-pressure iron drainage piping conforming to IS 1729"
        ]
    },
    "IS 210:2009": {
        "clean_product": "Grey Iron Castings",
        "paraphrases": [
            "grey iron castings - specification",
            "flake graphite grey cast iron engineering components",
            "industrial grey iron castings grades FG 150 to FG 400",
            "cast iron machine bodies, housings and general engineering castings"
        ],
        "indirect_descriptions": [
            "flake-graphite iron engineering cast components produced in foundry sand moulds with specified carbon equivalent, displaying superior compressive strength, machinability, and vibration damping capacity",
            "unalloyed and low-alloy grey cast iron structural pieces categorized into strength grades (FG 150, FG 200, FG 260, FG 300) for mechanical engineering and municipal infrastructure",
            "foundry-cast grey iron machine beds, valve bodies, motor casings, and counterweights compliant with tensile strength benchmarks"
        ],
        "key_features": ["tensile strength grades (150 MPa to 400 MPa)", "high compressive strength and thermal conductivity", "excellent vibration damping and dry sliding wear resistance"],
        "materials": ["grey cast iron (lamellar flake graphite)"],
        "parameters": {"grades": "FG 150, FG 200, FG 260, FG 300, FG 350, FG 400", "microstructure": "pearlitic matrix with flake graphite"},
        "application": "machine bases, pump casings, gearbox housings, counterweights, and municipal castings",
        "near_match_candidates": ["IS 210:2009", "IS 1726:1991", "IS 1729:2002"],
        "near_match_specs": [
            "Grey iron castings conforming to tensile strength grades of IS 210:2009",
            "flake graphite cast iron components graded FG 200 / FG 260 for engineering applications",
            "grey cast iron foundry products conforming to IS 210 specifications"
        ]
    },

    # ==================== SOLAR & CABLES (2) ====================
    "IS 17293:2020": {
        "clean_product": "Electric Cables for Photovoltaic Systems (1500 V DC)",
        "paraphrases": [
            "electric cables for photovoltaic systems for rated voltage 1500 V DC",
            "solar DC cables for photovoltaic string connections",
            "cross-linked halogen-free solar PV power cables 1.5 kV DC",
            "UV and ozone resistant solar photovoltaic electric cables"
        ],
        "indirect_descriptions": [
            "specialized flexible single-core electrical cables comprising tinned copper stranded conductors with cross-linked polymer insulation and outer sheath, engineered to withstand outdoor solar UV radiation, ozone, and temperatures up to 90C",
            "halogen-free low-smoke electric cables rated at 1500 V DC for outdoor string interconnection between solar PV modules, combiner boxes, and grid inverters",
            "solar photovoltaic DC cables subjected to 25-year thermal endurance and severe weatherability validation tests"
        ],
        "key_features": ["rated voltage 1.5 kV DC (conductor to ground and conductor to conductor)", "UV, ozone, and weather resistance for 25-year design life", "halogen-free flame retardant (HFFR) compound"],
        "materials": ["tinned electrolytic copper conductor (Class 5)", "cross-linked polyolefin (XLPO) insulation and sheath"],
        "parameters": {"voltage_rating": "1500 V DC", "conductor": "tinned annealed copper Class 5", "temperature_rating": "-40 C to +90 C"},
        "application": "interconnection of photovoltaic solar panels, array strings, and solar power plants",
        "near_match_candidates": ["IS 17293:2020", "IS 694", "IS 17505 (Part 1):2021"],
        "near_match_specs": [
            "Electric Cable for Photovoltaic Systems for rated voltage 1500 V DC per IS 17293:2020",
            "solar PV cables with cross-linked halogen-free insulation and tinned copper conductors",
            "1.5 kV DC solar cables meeting UV and weather resistance of IS 17293"
        ]
    },
    "IS 17505 (Part 1):2021": {
        "clean_product": "Thermosetting Insulated Fire Survival Cables",
        "paraphrases": [
            "thermosetting insulated, fire survival cables for voltage up to 1100 V AC and 1500 V DC",
            "fire survival circuit integrity electric cables",
            "fire resistant mineral-tape wrapped emergency electrical cables",
            "fire survival power and control cables for emergency evacuation circuits"
        ],
        "indirect_descriptions": [
            "high-performance electrical cables engineered to maintain circuit integrity and electrical continuity for at least 120 minutes during direct exposure to flame temperatures exceeding 750C to 950C",
            "fire-survival power cables wrapped with mica glass tapes and cross-linked thermosetting insulation, delivering zero halogen and low smoke toxicity in high-occupancy buildings",
            "emergency circuit survival cables designed for continuous power supply to fire smoke extraction fans, emergency lighting, and fire lifts during a blaze"
        ],
        "key_features": ["circuit integrity under fire conditions (minimum 950C for 180 min)", "low smoke emission and zero halogen acidic gas generation", "high dielectric withstand post-flame exposure"],
        "materials": ["annealed copper conductor", "mica glass tape fire barrier", "cross-linked thermoset insulation (XLPE/silicone)", "LSZH sheath"],
        "parameters": {"voltage_rating": "up to 1100 V AC / 1500 V DC", "fire_rating": "circuit integrity at 950 C", "smoke": "low smoke zero halogen"},
        "application": "emergency power feeds for smoke evacuation fans, fire alarm systems, emergency lighting, and hospital life-support",
        "near_match_candidates": ["IS 17505 (Part 1):2021", "IS 694", "IS 17293:2020"],
        "near_match_specs": [
            "Thermosetting Insulated, Fire Survival Cables up to and including 1100 V AC and 1500 V DC per IS 17505 (Part 1):2021",
            "fire survival cables maintaining circuit continuity under direct flame exposure for critical safety systems",
            "fire resistant LSZH cables meeting circuit integrity criteria of IS 17505-1"
        ]
    },

    # ==================== LABORATORY GLASSWARE (3) ====================
    "IS 878:2008": {
        "clean_product": "Laboratory Glassware - Graduated Measuring Cylinders",
        "paraphrases": [
            "laboratory glassware - graduated measuring cylinders",
            "borosilicate glass graduated volumetric cylinders",
            "Class A and Class B graduated glass measuring cylinders",
            "precision graduated laboratory liquid measuring cylinders"
        ],
        "indirect_descriptions": [
            "cylindrical volumetric liquid measurement vessels fabricated from thermally shock-resistant borosilicate glass, featuring heavy hexagonal base supports, pouring spouts, and durable etched metric graduation lines",
            "laboratory analytical measuring cylinders calibrated to deliver (Ex) liquids at 20C within strict volumetric error limits for Class A and Class B precision",
            "graduated glass cylinders with permanent ceramic enamel markings and thermal expansion resistance for scientific testing"
        ],
        "key_features": ["Class A and Class B volumetric tolerance compliance", "hydrolytic resistance Class 1 borosilicate glass", "permanent acid/alkali resistant enamel graduations"],
        "materials": ["Type 1 borosilicate 3.3 glass", "ceramic enamel marking"],
        "parameters": {"capacities": "5 ml to 2000 ml", "calibration": "Ex (to deliver) at 20 C", "accuracy_classes": "Class A / Class B"},
        "application": "chemical analytical measurement in university laboratories, pharmaceutical QC, and soil testing centers",
        "near_match_candidates": ["IS 878:2008", "IS 915:2012", "IS 2619:2018"],
        "near_match_specs": [
            "Laboratory glassware - Graduated measuring cylinders conforming to IS 878:2008",
            "borosilicate glass measuring cylinders calibrated to deliver (Ex) Class A and B tolerances",
            "graduated laboratory cylinders meeting volumetric capacity limits of IS 878"
        ]
    },
    "IS 915:2012": {
        "clean_product": "Laboratory Glassware - One-Mark Volumetric Flasks",
        "paraphrases": [
            "laboratory glassware - one-mark volumetric flasks",
            "Class A and Class B one-mark glass volumetric flasks with ground stoppers",
            "borosilicate glass volumetric measuring flasks with interchangeable glass/polyethylene stoppers",
            "precision standard solution preparation volumetric flasks"
        ],
        "indirect_descriptions": [
            "pear-shaped flat-bottomed volumetric glass vessels having long narrow necks with a single circular calibration mark etched around the circumference and interchangeable ground-glass or plastic stoppers",
            "high-precision laboratory volumetric containment flasks calibrated to contain (In) precise liquid volumes at 20C for standard analytical reagent preparation",
            "analytical one-mark flasks manufactured from low-expansion borosilicate glass with verified meniscus visibility and capacity tolerances"
        ],
        "key_features": ["Class A volumetric accuracy with calibration certificate", "calibrated to contain (In) nominal volume at 20C", "interchangeable standard taper ground neck and stopper fit"],
        "materials": ["Type 1 borosilicate 3.3 glass", "ground glass / PE stopper"],
        "parameters": {"capacities": "5 ml to 5000 ml", "calibration": "In (to contain) at 20 C", "accuracy_classes": "Class A / Class B"},
        "application": "preparation of standard volumetric solutions and accurate chemical dilutions in testing laboratories",
        "near_match_candidates": ["IS 915:2012", "IS 878:2008", "IS 2619:2018"],
        "near_match_specs": [
            "Laboratory glassware - One-Mark volumetric flasks per IS 915:2012",
            "precision volumetric flasks with interchangeable ground joint stoppers calibrated to contain (In)",
            "one-mark glass flasks conforming to Class A tolerances of IS 915"
        ]
    },
    "IS 2619:2018": {
        "clean_product": "Glass Beakers",
        "paraphrases": [
            "laboratory glass beakers (low form and tall form)",
            "borosilicate glass beakers with pouring spout and graduation",
            "laboratory Griffin low-form glass beakers",
            "heat-resistant chemical glass beakers for laboratories"
        ],
        "indirect_descriptions": [
            "cylindrical flat-bottomed laboratory containers fabricated from chemical and thermal shock resistant borosilicate 3.3 glass, featuring a reinforced beaded rim, pouring spout, and approximate volume graduations",
            "general laboratory chemical vessels designed for heating, dissolving, mixing, and temporary containment of aggressive reagents on hotplates and water baths",
            "borosilicate glass beakers with uniform wall thickness and high hydrolytic resistance for scientific experiments"
        ],
        "key_features": ["thermal shock endurance (minimum 150C temperature difference)", "chemical resistance to acids, neutral and alkaline solutions", "beaded rim with non-drip pouring spout"],
        "materials": ["Type 1 borosilicate 3.3 glass"],
        "parameters": {"capacities": "25 ml to 5000 ml", "form": "low form (Griffin) / tall form (Berzelius)", "thermal_shock": "tested to 150 C delta T"},
        "application": "chemical reagent mixing, heating, titrations, and crystallization in science laboratories",
        "near_match_candidates": ["IS 2619:2018", "IS 878:2008", "IS 915:2012"],
        "near_match_specs": [
            "Glass beakers conforming to laboratory specification IS 2619:2018",
            "borosilicate 3.3 glass beakers with spout and beaded rim for chemical heating",
            "laboratory glass beakers meeting thermal shock and dimensional criteria of IS 2619"
        ]
    },

    # ==================== ELECTRICAL ACCESSORIES (4) ====================
    "IS 14772:2020": {
        "clean_product": "Boxes and Enclosures for Electrical Accessories",
        "paraphrases": [
            "boxes and enclosures for electrical accessories for household and similar fixed electrical installations",
            "flush and surface mounted electrical accessory junction and modular switch boxes",
            "metallic and non-metallic modular mounting boxes for electrical fittings",
            "concealed conduit and surface electrical back boxes"
        ],
        "indirect_descriptions": [
            "sheet steel or molded thermoplastic mounting enclosures engineered to house and secure flush-mounted wall switches, sockets, and wire terminations inside masonry or dry-lining walls",
            "rigid electrical terminal back-boxes featuring knock-out conduit entries, earthing screws, and brass threaded fixing inserts for modular wiring accessories",
            "protective mounting enclosures shielding building wiring connections from mechanical damage and providing fire containment"
        ],
        "key_features": ["impact resistance and mechanical strength of box walls", "resistance to abnormal heat and fire (glow wire test 650C/850C)", "earthing continuity across metal conduit entries"],
        "materials": ["galvanized sheet steel (1.0 - 1.6 mm)", "flame-retardant polycarbonate / ABS"],
        "parameters": {"modules": "1, 2, 3, 4, 6, 8, 12 modules", "mounting": "flush / surface", "conduit_entry": "metric knockouts"},
        "application": "concealed and surface electrical wiring in residential and commercial building electrification",
        "near_match_candidates": ["IS 14772:2020", "IS 14927 (Part 2):2001", "IS 3854"],
        "near_match_specs": [
            "Boxes and enclosures for electrical accessories for household and similar fixed installations per IS 14772:2020",
            "modular electrical back-boxes and junction enclosures for flush wall mounting",
            "enclosure boxes for electrical accessories meeting glow wire and impact criteria of IS 14772"
        ]
    },
    "IS 14927 (Part 2):2001": {
        "clean_product": "Cable Trunking and Ducting Systems for Walls and Ceilings",
        "paraphrases": [
            "cable trunking and ducting systems for electrical installations - Part 2: mounting on walls or ceiling",
            "PVC surface cable trunking and wiring raceways",
            "non-flame propagating electrical cable casing and capping channels",
            "rigid thermoplastic cable containment trunking with snap-on lids"
        ],
        "indirect_descriptions": [
            "rigid insulating thermoplastic or metallic channel assemblies with detachable snap-on covers, designed for mounting on walls or ceilings to accommodate, route, and protect insulated building wires",
            "surface wiring raceways and ducting profiles equipped with compartment dividers, internal corners, and flat angles for commercial cable management",
            "non-flame propagating cable containment channels shielding power and communication wiring along building corridors"
        ],
        "key_features": ["non-flame propagating fire safety", "impact resistance at low and high temperatures (-5C to +60C)", "cover retention security under internal cable pressure"],
        "materials": ["rigid unplasticized polyvinyl chloride (uPVC)", "galvanized sheet steel"],
        "parameters": {"cross_section": "20x12 mm to 100x50 mm", "mounting": "surface wall / ceiling", "flammability": "non-flame propagating"},
        "application": "surface wiring and cable management in offices, schools, and retrofitted buildings",
        "near_match_candidates": ["IS 14927 (Part 2):2001", "IS 14772:2020", "IS 694"],
        "near_match_specs": [
            "Cable trunking and ducting systems for electrical installations - Part 2: Intended for mounting on walls or ceiling",
            "rigid PVC cable trunking with snap-on lid for surface cable containment per IS 14927 (Part 2)",
            "wall-mounted wiring channels conforming to flame retardancy of IS 14927-2"
        ]
    },
    "IS 1258:2005": {
        "clean_product": "Bayonet Lamp Holders",
        "paraphrases": [
            "bayonet lamp holders (B22)",
            "B22d bayonet cap lamp holders for lighting fixtures",
            "pendant and batten type brass/polycarbonate bayonet lamp holders",
            "brass and phenolic bayonet lighting lamp holders"
        ],
        "indirect_descriptions": [
            "electrical lighting connector accessories featuring a cylindrical socket with J-shaped bayonet slots, spring-loaded electrical contact plungers, and screw terminals for connecting B22 lamp caps to AC power",
            "batten-mounted, pendant, and threaded entry bayonet lamp holders designed to hold incandescent, CFL, and LED lamps securely while maintaining contact pressure without overheating",
            "lamp holder accessories providing mechanical retention and electric shock protection up to 250V"
        ],
        "key_features": ["endurance test with electric load (2500 insertions and 200 hours at rated current)", "contact spring pressure retention", "insulation resistance and creepage distance compliance"],
        "materials": ["brass contacts and liner", "flame retardant phenolic / PBT body", "phosphor bronze springs"],
        "parameters": {"rated_current": "2A", "rated_voltage": "250 V AC", "size": "B22d", "types": "batten / pendant / bracket"},
        "application": "indoor and outdoor general illumination fixtures and residential lighting circuits",
        "near_match_candidates": ["IS 1258:2005", "IS 3854", "IS 15111 (Part 1 & 2)"],
        "near_match_specs": [
            "Bayonet lamp holders conforming to B22 specification IS 1258:2005",
            "batten and pendant B22d bayonet lamp holders with spring-loaded brass plungers",
            "bayonet lighting lamp holders meeting endurance and thermal criteria of IS 1258"
        ]
    },
    "IS 13774:2021": {
        "clean_product": "Live Working Gloves of Insulating Material",
        "paraphrases": [
            "live working gloves of insulating material",
            "electrical insulating rubber gloves for live line power maintenance",
            "high-voltage electrician insulating safety gloves (Class 00 to Class 4)",
            "dielectric protective gloves for live electrical line maintenance"
        ],
        "indirect_descriptions": [
            "elastomeric natural or synthetic rubber hand protection gear fabricated without seams, designed to protect electrical utility technicians from electrical shock during contact with energized conductors",
            "dielectric proof-tested insulating gloves categorized into voltage protection classes (Class 00 to Class 4) for power grid operations up to 36 kV AC",
            "insulating safety gloves subjected to individual proof voltage tests, tensile stretch verification, and mechanical puncture resistance"
        ],
        "key_features": ["dielectric proof voltage and withstand testing for every individual glove", "mechanical puncture, tear, and tensile strength", "resistance to acid, oil, ozone, and extreme cold"],
        "materials": ["high-purity natural latex rubber / synthetic elastomer"],
        "parameters": {"classes": "Class 00 (500V) to Class 4 (36kV)", "test_voltage": "up to 40 kV AC", "category": "electrical insulating gloves"},
        "application": "live-line electrical substation maintenance, line worker protection, and switchgear servicing",
        "near_match_candidates": ["IS 13774:2021", "IS 15298 (Part 2):2016"],
        "near_match_specs": [
            "Live working gloves of insulating material conforming to IS 13774:2021",
            "dielectric electrical insulating gloves proof tested for live line work up to specified voltage class",
            "insulating rubber electrician gloves meeting proof voltage and puncture resistance of IS 13774"
        ]
    },

    # ==================== AGRICULTURE (3) ====================
    "IS 16190:2014": {
        "clean_product": "HDPE Laminated Woven Lay Flat Tubes for Irrigation",
        "paraphrases": [
            "high density polyethylene (HDPE) laminated woven lay flat tube for irrigation purposes",
            "woven HDPE lay flat flexible irrigation delivery pipes",
            "agricultural flexible woven layflat hose for flood and furrow irrigation",
            "laminated woven polyethylene lay-flat water conveyance tubing"
        ],
        "indirect_descriptions": [
            "flexible water conveyance conduits constructed from circular woven high-density polyethylene tape fabrics coated on both sides with low-density polyethylene films, designed to collapse flat when not pressurized",
            "portable agricultural water discharge hoses providing high burst pressure resistance, puncture endurance, and easy roll-up storage for seasonal field flood irrigation",
            "UV-stabilized collapsible woven irrigation tubing engineered for surface water transport across rough agricultural soils"
        ],
        "key_features": ["burst pressure and working pressure safety ratio", "lamination adhesion peel strength between woven fabric and film", "carbon black UV stabilization"],
        "materials": ["high density polyethylene (HDPE) tapes", "LDPE lamination coating", "carbon black UV stabilizer"],
        "parameters": {"diameters": "50 mm to 200 mm", "working_pressure": "2 to 6 kg/cm2", "burst_pressure_min": "10 kg/cm2"},
        "application": "surface water delivery from tubewells to agricultural crops, flood and furrow irrigation",
        "near_match_candidates": ["IS 16190:2014", "IS 16627:2017", "IS 17729:2021"],
        "near_match_specs": [
            "High Density Polyethylene (HDPE) laminated woven lay flat tube for general irrigation purposes per IS 16190:2014",
            "woven HDPE lay flat pipes for open furrow and field water conveyance",
            "flexible lay-flat irrigation tubing conforming to burst and adhesion limits of IS 16190"
        ]
    },
    "IS 16627:2017": {
        "clean_product": "HDPE Lay Flat Tubes for Mains and Submains of Drip Irrigation",
        "paraphrases": [
            "HDPE laminated woven lay flat tube for mains and submains of drip irrigation systems",
            "drip irrigation mainline and submain woven lay-flat delivery tubing",
            "pressurized layflat manifolds for micro-irrigation header systems",
            "reinforced HDPE layflat pipes with take-off connectors for drip laterals"
        ],
        "indirect_descriptions": [
            "specialized high-strength reinforced lay-flat polyethylene pipeline conduits engineered specifically to serve as pressurized main and submain manifolds in pressurized micro and drip irrigation systems",
            "tear-resistant multi-layered woven lay-flat hoses formulated to support mechanical punching of lateral connector fittings without edge propagation or water leakage under continuous operating pressure",
            "pressurized water distribution manifolds for automated drip irrigation networks providing structural rigidity against cyclic pressure pulses"
        ],
        "key_features": ["tear resistance around lateral take-off hole punching", "cyclic pressure surge endurance without delamination", "UV resistance for multi-season outdoor exposure"],
        "materials": ["woven high tenacity HDPE fabric", "virgin PE film lamination"],
        "parameters": {"nominal_sizes": "50 mm - 150 mm", "working_pressure": "up to 4.0 kg/cm2", "application": "drip irrigation mains/submains"},
        "application": "mains and submain manifolds in pressurized drip irrigation and micro-sprinkler networks",
        "near_match_candidates": ["IS 16627:2017", "IS 16190:2014", "IS 17729:2021"],
        "near_match_specs": [
            "HDPE laminated woven lay flat tube specifically for use in mains and submains of drip irrigation systems per IS 16627:2017",
            "drip irrigation lay-flat pipes designed for lateral take-off punching without tearing",
            "pressurized micro-irrigation submain layflat tubing complying with IS 16627"
        ]
    },
    "IS 17729:2021": {
        "clean_product": "Flexible Water Storage Tanks for Agriculture and Horticulture",
        "paraphrases": [
            "flexible water storage tanks for agriculture and horticulture purposes",
            "collapsible polymer bladder tanks for agricultural rainwater harvesting",
            "pillow-type flexible water storage reservoirs for farms",
            "geomembrane coated fabric flexible water storage bladders"
        ],
        "indirect_descriptions": [
            "collapsible pillow-shaped fluid containment vessels fabricated from high-strength polyester or polyamide woven fabrics coated with waterproof elastomeric polymers, equipped with inlet/outlet ball valves and vent pipes",
            "portable enclosed agricultural water storage reservoirs designed for rapid deployment on unprepared farm soil to harvest rainwater and store micro-irrigation water",
            "UV-resistant enclosed water containment bladders preventing evaporation, algae growth, and seepage in rural horticulture farms"
        ],
        "key_features": ["tensile and tear strength of coated fabric seams", "potable water non-toxicity and algae inhibition", "weld seam peel adhesion and hydraulic hydrostatic pressure integrity"],
        "materials": ["PVC/TPU coated woven polyester fabric", "brass/polypropylene valves and fittings"],
        "parameters": {"storage_capacity": "5,000 L to 100,000 L", "fabric_weight": "> 900 g/m2", "temperature_range": "-10 C to +60 C"},
        "application": "on-farm emergency water storage, rainwater harvesting, and seasonal irrigation buffers",
        "near_match_candidates": ["IS 17729:2021", "IS 16190:2014", "IS 16627:2017"],
        "near_match_specs": [
            "Flexible water storage tanks for agriculture and horticulture purposes per IS 17729:2021",
            "collapsible polymer bladder tanks for on-farm water storage and irrigation",
            "flexible water containment reservoirs conforming to seam strength and UV criteria of IS 17729"
        ]
    },

    # ==================== COPPER (3) ====================
    "IS 12444:2020": {
        "clean_product": "Copper Wire Rods for Electrical Applications",
        "paraphrases": [
            "copper wire rods for electrical applications (continuous cast)",
            "electrolytic tough pitch (ETP) and oxygen-free (OFE) continuous cast copper wire rods",
            "high-conductivity copper redraw rods for cable wire drawing",
            "8 mm continuous cast copper wire rods for electrical conductors"
        ],
        "indirect_descriptions": [
            "continuously cast and hot-rolled high-purity copper rod coils produced via Southwire or Contirod processes, engineered for cold-drawing into fine electrical conductor wires and telecom cables",
            "high-conductivity copper feedstock rods possessing minimum 100% IACS electrical conductivity, smooth surface finish, and high elongation for wire-drawing dies",
            "continuous cast copper wire rods with tightly controlled oxygen content (100-400 ppm for ETP) ensuring freedom from surface inclusions and slivers"
        ],
        "key_features": ["electrical conductivity minimum 100% IACS (0.017241 ohm.mm2/m at 20C)", "high drawability elongation (>35%)", "torsion and spiral elongation test performance"],
        "materials": ["high-purity electrolytic copper (Cu min 99.90%)"],
        "parameters": {"nominal_diameter": "8 mm (6.35 mm to 18 mm)", "conductivity_min": "100% IACS", "grades": "ETP (Electrolytic Tough Pitch) / OFE"},
        "application": "raw material for manufacturing electric cables, winding wires, and electrical busbars",
        "near_match_candidates": ["IS 12444:2020", "IS 613:2000", "IS 14810:2000"],
        "near_match_specs": [
            "Copper wire rods specifically for electrical applications per IS 12444:2020",
            "continuous cast copper rods with minimum 100% IACS conductivity for wire drawing",
            "electrolytic redraw copper rods complying with IS 12444"
        ]
    },
    "IS 613:2000": {
        "clean_product": "Copper Rods and Bars for Electrical Purposes",
        "paraphrases": [
            "copper rods and bars for electrical purposes (busbars and flats)",
            "high conductivity copper rectangular busbars and round rods",
            "drawn electrolytic copper flats and sections for switchgear panels",
            "hard and half-hard copper busbars for power substations"
        ],
        "indirect_descriptions": [
            "solid round, rectangular, and square copper bar sections manufactured by extrusion and drawing, intended for conducting high electrical currents in switchgear busbars, transformers, and earthing conductors",
            "high-purity electrolytic copper electrical busbars supplied in annealed, half-hard, or hard temper, offering low contact resistance and high short-circuit mechanical rigidity",
            "electrical conductor copper flats and rods displaying guaranteed electrical resistivity and bend ductility around small radii"
        ],
        "key_features": ["electrical resistivity max 0.01777 ohm.mm2/m for hard temper", "sharp 90-degree transverse and longitudinal bend ductility without cracking", "dimensional tolerances on flat busbar edges and camber"],
        "materials": ["electrolytic tough pitch copper (Cu min 99.90%)"],
        "parameters": {"cross_sections": "flats (width up to 250 mm, thick up to 25 mm) / rounds", "tempers": "annealed (O) / half-hard (HB) / hard (HD)"},
        "application": "electrical switchboard busbars, panel boards, generator terminals, and substation grounding",
        "near_match_candidates": ["IS 613:2000", "IS 12444:2020", "IS 14810:2000"],
        "near_match_specs": [
            "Copper rods and bars for electrical purposes per IS 613:2000",
            "rectangular high-conductivity copper busbars and rods for switchgear panels",
            "copper busbar flats complying with electrical conductivity and bend criteria of IS 613"
        ]
    },
    "IS 14810:2000": {
        "clean_product": "Copper Tubes for Plumbing",
        "paraphrases": [
            "copper tubes for plumbing - specification",
            "seamless solid-drawn copper water and sanitation pipes",
            "deoxidized high phosphorus copper plumbing pipes",
            "hard, half-hard and annealed copper tubes for domestic potable water"
        ],
        "indirect_descriptions": [
            "seamless solid-drawn phosphorus-deoxidized copper tubes engineered for conveying hot and cold potable water, sanitation lines, central heating systems, and medical gases in buildings",
            "corrosion-resistant seamless plumbing copper tubing supplied in straight lengths or coils, suitable for soldered capillary fittings, compression joints, and brazing",
            "smooth-bore copper water tubes designed to resist pitting corrosion and withstand high internal water hammer pressures"
        ],
        "key_features": ["phosphorus-deoxidized non-arsenical copper (DHP-Cu min 99.90%, P 0.015-0.040%)", "pneumatic / eddy current non-destructive flaw detection", "hydraulic pressure proof testing (up to 5 MPa)"],
        "materials": ["DHP copper (Cu-DHP)"],
        "parameters": {"outer_diameter": "6 mm to 108 mm", "tempers": "half-hard (straight) / soft annealed (coils)", "carbon_film_max": "passivation tested"},
        "application": "potable water distribution, domestic hot water lines, medical gas piping, and refrigeration",
        "near_match_candidates": ["IS 14810:2000", "IS 613:2000", "IS 12444:2020"],
        "near_match_specs": [
            "Copper tubes specifically for plumbing applications per IS 14810:2000",
            "seamless phosphorus-deoxidized copper water tubes for potable plumbing installations",
            "copper plumbing pipes conforming to pressure testing and temper of IS 14810"
        ]
    },

    # ==================== DOOR FITTINGS (2) ====================
    "IS 6343:1982": {
        "clean_product": "Pneumatically Regulated Door Closers (up to 40 kg)",
        "paraphrases": [
            "door closers (pneumatically regulated) for light doors weighing up to 40 kg",
            "pneumatic overhead door closers for interior lightweight doors",
            "air-cushioned pneumatic door closing devices",
            "automatic pneumatic door closers for light office doors"
        ],
        "indirect_descriptions": [
            "mechanical door self-closing hardware comprising a compression spring cylinder paired with an adjustable pneumatic air-dashpot piston to softly close lightweight interior doors without slamming",
            "pneumatically regulated overhead door control mechanisms featuring adjustable air bleed valves for controlling closing speed on doors weighing up to 40 kg",
            "light-duty pneumatic automatic door closing hardware for institutional interior partitions and screen doors"
        ],
        "key_features": ["endurance cycle testing (100,000 opening/closing operations)", "pneumatic air-bleed valve regulating closing velocity", "door mass rating strictly limited up to 40 kg"],
        "materials": ["die-cast aluminium / brass cylinder", "hardened steel piston and spring", "rubber piston cup seal"],
        "parameters": {"max_door_weight": "up to 40 kg", "regulation": "pneumatic air dashpot", "endurance": "100,000 cycles"},
        "application": "automatic soft-closing of light office interior doors, screen doors, and hospital partition doors",
        "near_match_candidates": ["IS 6343:1982", "IS 208:2020"],
        "near_match_specs": [
            "Door closers (pneumatically regulated) specifically for light doors weighing up to 40 kg per IS 6343:1982",
            "pneumatic air-regulated door closers for interior doors up to 40 kg mass",
            "light door closers conforming to 100,000 cycle endurance of IS 6343"
        ]
    },
    "IS 208:2020": {
        "clean_product": "Door Handles",
        "paraphrases": [
            "door handles for architectural and building hardware",
            "die-cast and extruded metal door pull and lever handles",
            "brass, aluminium and stainless steel architectural door handles",
            "mortise and surface mounted door handles for building doors"
        ],
        "indirect_descriptions": [
            "architectural hardware grip accessories manufactured from extruded brass, die-cast zinc, aluminium alloy, or fabricated stainless steel, designed for operating or manually pulling open interior and exterior building doors",
            "surface-mounted pull handles and mortise lever handles on backplates subjected to mechanical pull load tests, salt spray corrosion verification, and finish durability checks",
            "door operating grip hardware with ergonomic contouring and concealed screw fixing for residential and commercial joinery doors"
        ],
        "key_features": ["axial pull and cantilever load strength (withstanding >1500 N force)", "corrosion resistance finish (neutral salt spray testing)", "freedom from sharp burrs and casting flaws"],
        "materials": ["extruded brass", "die-cast zinc alloy", "stainless steel (SS 304)", "aluminium alloy"],
        "parameters": {"types": "lever handle / pull handle", "sizes": "75 mm to 300 mm", "finishes": "satin / polished / anodized / powder coated"},
        "application": "interior and exterior doors in administrative complexes, hospitals, hotels, and residential buildings",
        "near_match_candidates": ["IS 208:2020", "IS 6343:1982"],
        "near_match_specs": [
            "Door handles conforming to architectural hardware specification IS 208:2020",
            "metal door lever and pull handles satisfying mechanical load and finish criteria",
            "architectural door handles complying with IS 208"
        ]
    }
}
