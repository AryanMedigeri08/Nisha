"""
Domain profiles Part 1: Cement, Electrical, Gas & LPG, Fire Safety (29 standards).
"""

PART1_PROFILES = {
    # ==================== CEMENT (8) ====================
    "IS 269": {
        "clean_product": "Ordinary Portland Cement",
        "paraphrases": [
            "ordinary Portland cement 33, 43 and 53 grades",
            "standard hydraulic Portland cement for civil structural casting",
            "unblended general-purpose Portland cement",
            "pure clinker-gypsum Portland hydraulic cement"
        ],
        "indirect_descriptions": [
            "finely pulverized hydraulic mineral binder produced by pulverizing clinker consisting of hydraulic calcium silicates with dry gypsum addition, intended for mass concrete foundations and structural casting",
            "standard grade mineral adhesive binder for load-bearing civil frameworks and cast-in-situ reinforced concrete elements with 28-day characteristic strength compliance",
            "calcined limestone-based structural hydraulic binder for conventional masonry, beam casting, and superstructure civil execution"
        ],
        "key_features": ["28-day compressive strength conformity", "soundness and standard setting time", "clinker gypsum composition without supplementary pozzolans"],
        "materials": ["cement", "clinker", "gypsum"],
        "parameters": {"grades": "33/43/53", "setting_time_initial_min": "30 mins", "soundness_max": "10 mm"},
        "application": "civil construction and reinforced concrete works",
        "near_match_candidates": ["IS 269", "IS 455", "IS 1489 (Part 1)", "IS 1489 (Part 2)", "IS 16415:2015"],
        "near_match_specs": [
            "Ordinary Portland Cement without any slag or pozzolanic mineral admixture",
            "general purpose OPC cement with specified 33/43/53 grade compressive strength",
            "unblended hydraulic cement meeting standard fineness and soundness criteria for structural RCC"
        ]
    },
    "IS 455": {
        "clean_product": "Portland Slag Cement",
        "paraphrases": [
            "Portland blast furnace slag cement",
            "granulated slag blended Portland cement",
            "slag-modified hydraulic cement for marine and aggressive exposure",
            "hydraulic Portland slag cement for durable substructures"
        ],
        "indirect_descriptions": [
            "composite hydraulic binding material formulated by intimately grinding Portland cement clinker with granulated blast furnace slag and gypsum, providing low heat of hydration and sulphate resistance",
            "slag-enriched inorganic binder for marine piling, coastal foundations, and sewerage-exposed civil concrete structures",
            "mineral-blended hydraulic cementing agent utilizing industrial blast furnace byproducts to achieve reduced chemical permeability"
        ],
        "key_features": ["low heat of hydration", "high resistance to chemical attack and marine salts", "granulated blast furnace slag content 25-70%"],
        "materials": ["cement", "clinker", "blast furnace slag", "gypsum"],
        "parameters": {"slag_percentage": "25-70%", "heat_of_hydration": "low"},
        "application": "coastal, marine and underground civil infrastructure",
        "near_match_candidates": ["IS 455", "IS 269", "IS 12330", "IS 1489 (Part 1)"],
        "near_match_specs": [
            "Portland Slag Cement (PSC) incorporating intimate blend of granulated blast furnace slag",
            "slag cement formulated specifically for chemical resistance in coastal piling works",
            "hydraulic cement containing 25% to 70% granulated iron blast furnace slag"
        ]
    },
    "IS 1489 (Part 1)": {
        "clean_product": "Portland Pozzolana Cement - Fly-ash based",
        "paraphrases": [
            "fly-ash based Portland Pozzolana Cement (PPC)",
            "calcined coal fly-ash blended hydraulic cement",
            "pulverized fuel ash based pozzolanic Portland cement",
            "fly-ash modified Portland cement for mass concreting"
        ],
        "indirect_descriptions": [
            "hydraulic pozzolanic binder manufactured by blending Portland clinker with pulverized fuel fly ash from thermal power plants, providing long-term strength gain and low thermal cracking risk",
            "fly-ash pozzolan blended cementitious material intended for hydro-electric dams, retaining walls, and mass concrete placements",
            "siliceous pulverized mineral binder utilizing classified thermal fly-ash to enhance pore refinement and reduce bleeding in concrete"
        ],
        "key_features": ["fly-ash pozzolana proportion 15-35%", "improved workability and reduced heat of hydration", "long-term compressive strength progression"],
        "materials": ["cement", "clinker", "fly ash", "gypsum"],
        "parameters": {"pozzolana_type": "fly ash", "pozzolana_percentage": "15-35%"},
        "application": "mass concrete works, general building and plastering",
        "near_match_candidates": ["IS 1489 (Part 1)", "IS 1489 (Part 2)", "IS 269", "IS 455", "IS 16415:2015"],
        "near_match_specs": [
            "Portland Pozzolana Cement specifically incorporating pulverized thermal fly-ash as the pozzolanic component",
            "Part 1 fly-ash based PPC cement for crack-resistant mass concrete construction",
            "blended cement meeting Part 1 requirements with classified fly-ash addition between 15% and 35%"
        ]
    },
    "IS 1489 (Part 2)": {
        "clean_product": "Portland Pozzolana Cement - Calcined clay based",
        "paraphrases": [
            "calcined clay based Portland Pozzolana Cement",
            "calcined pozzolana clay blended Portland cement",
            "calcined clay pozzolanic hydraulic cement for civil structures",
            "Part 2 clay-pozzolana modified Portland cement"
        ],
        "indirect_descriptions": [
            "hydraulic binder synthesized by blending Portland clinker with calcined clay pozzolana and gypsum, exhibiting high early density and reduced permeability",
            "calcined clay-incorporated inorganic cementing medium for specialized hydraulic structures and water-retaining reservoirs",
            "thermally activated clay-blended hydraulic cement for aggressive weathering resistance without coal fly-ash incorporation"
        ],
        "key_features": ["calcined clay pozzolana 15-35%", "high chemical durability", "homogeneous clay calcination control"],
        "materials": ["cement", "clinker", "calcined clay", "gypsum"],
        "parameters": {"pozzolana_type": "calcined clay", "pozzolana_percentage": "15-35%"},
        "application": "water-retaining structures, marine works and masonry",
        "near_match_candidates": ["IS 1489 (Part 2)", "IS 1489 (Part 1)", "IS 269", "IS 455"],
        "near_match_specs": [
            "Portland Pozzolana Cement Part 2 specifically manufactured using calcined clay as the pozzolanic constituent",
            "calcined clay based pozzolanic cement without fly-ash admixture",
            "Part 2 specification compliant pozzolanic binder formulated with activated thermally calcined clay"
        ]
    },
    "IS 8041": {
        "clean_product": "Rapid Hardening Portland Cement",
        "paraphrases": [
            "high early strength Portland cement",
            "rapid setting high-early-strength Portland cement",
            "fast-curing structural Portland hydraulic cement",
            "rapid hardening hydraulic binder for emergency repair works"
        ],
        "indirect_descriptions": [
            "ultra-finely ground hydraulic clinker formulation engineered for accelerated hydration kinetics and rapid early compressive strength development within 24 to 72 hours",
            "specialized high-early-strength binder designed for pre-cast concrete fabrication, cold weather concreting, and urgent pavement repair",
            "accelerated strength mineral matrix allowing early formwork stripping and fast operational commissioning of civil structures"
        ],
        "key_features": ["high fineness specific surface (>3250 cm2/g)", "1-day and 3-day rapid compressive strength achievement", "quick formwork turnaround capability"],
        "materials": ["cement", "clinker", "gypsum"],
        "parameters": {"early_strength_1day_min": "16 MPa", "fineness_min": "3250 cm2/g"},
        "application": "rapid road repairs, precast manufacturing, cold weather concreting",
        "near_match_candidates": ["IS 8041", "IS 269", "IS 12330", "IS 1489 (Part 1)"],
        "near_match_specs": [
            "Rapid Hardening Portland Cement characterized by elevated fineness and 1-day early compressive strength development",
            "high early strength cement specifically designed for emergency road repair and early deshuttering",
            "rapid hardening cement achieving minimum 16 MPa compressive strength at 24 hours"
        ]
    },
    "IS 8042": {
        "clean_product": "White Portland Cement",
        "paraphrases": [
            "architectural white Portland cement",
            "iron-free white hydraulic Portland cement",
            "decorative white Portland cement for terrazzo and facade",
            "high whiteness grade Portland cement"
        ],
        "indirect_descriptions": [
            "calcined hydraulic mineral binder prepared from iron-free raw clays and pure limestone, displaying minimum 70% reflectance whiteness index for decorative applications",
            "decorative architectural cementing compound formulated for terrazzo flooring, ornamental cast stone, and aesthetic wall finishes",
            "non-staining aesthetic white binder for architectural plastering, grouting, and colored mortar formulations"
        ],
        "key_features": ["whiteness index min 70%", "iron oxide content strictly limited below 1%", "architectural finishing stability"],
        "materials": ["cement", "white clinker", "gypsum", "pure limestone"],
        "parameters": {"whiteness_index_min": "70%", "iron_oxide_max": "1.0%"},
        "application": "architectural finishes, terrazzo tiles, decorative pointing, ornamental casting",
        "near_match_candidates": ["IS 8042", "IS 269", "IS 16415:2015"],
        "near_match_specs": [
            "White Portland Cement having minimum 70% whiteness reflectance index",
            "iron-free white architectural cement for decorative terrazzo and facade works",
            "white Portland cement compliant with whiteness and chemical purity specifications"
        ]
    },
    "IS 12330": {
        "clean_product": "Sulphate Resisting Portland Cement",
        "paraphrases": [
            "sulphate-resistant Portland cement (SRPC)",
            "low-tricalcium-aluminate Portland cement",
            "sulphate-immune hydraulic Portland cement for foundations",
            "chemical resistant Portland cement for saline soils"
        ],
        "indirect_descriptions": [
            "specialized hydraulic cement clinker with tricalcium aluminate (C3A) strictly controlled below 5%, eliminating destructive ettringite expansion in sulphate-rich groundwaters",
            "chemically stabilized hydraulic binder for marshland foundations, sewage treatment tanks, and high-sulphate subsoil conditions",
            "anti-sulphate mineral binder designed to withstand aggressive underground chemical and brackish water environments"
        ],
        "key_features": ["C3A content maximum 5%", "immunity against sulphate attack and expansion", "soundness and prolonged structural durability in saline environments"],
        "materials": ["cement", "clinker", "gypsum"],
        "parameters": {"c3a_max": "5%", "soundness_max": "10 mm"},
        "application": "subsoil foundations, marine piles, sewage treatment plants, saline regions",
        "near_match_candidates": ["IS 12330", "IS 269", "IS 455", "IS 8041"],
        "near_match_specs": [
            "Sulphate Resisting Portland Cement (SRPC) with tricalcium aluminate content not exceeding 5%",
            "sulphate-resistant cement specifically intended for structures in high-sulphate ground conditions",
            "cement satisfying chemical composition requirements for sulphate attack mitigation in saline soils"
        ]
    },
    "IS 16415:2015": {
        "clean_product": "Composite Cement",
        "paraphrases": [
            "ternary blended composite hydraulic cement",
            "clinker-slag-flyash composite cement",
            "multi-component eco-friendly Portland composite cement",
            "three-part composite cement for sustainable infrastructure"
        ],
        "indirect_descriptions": [
            "ternary blended inorganic binder produced by intergrinding Portland clinker with both granulated blast furnace slag and siliceous fly ash along with gypsum",
            "multi-constituent ecological hydraulic cement combining supplementary cementitious minerals to achieve enhanced durability and reduced carbon footprint",
            "three-phase composite hydraulic matrix for general building construction and environmental civil projects"
        ],
        "key_features": ["ternary blend of clinker, granulated slag (15-35%), and fly ash (15-35%)", "high impermeability", "enhanced late-age strength"],
        "materials": ["cement", "clinker", "blast furnace slag", "fly ash", "gypsum"],
        "parameters": {"slag_pct": "15-35%", "fly_ash_pct": "15-35%"},
        "application": "green building construction, mass concrete, hydraulic engineering",
        "near_match_candidates": ["IS 16415:2015", "IS 269", "IS 455", "IS 1489 (Part 1)"],
        "near_match_specs": [
            "Composite Cement manufactured by simultaneously blending clinker with both granulated slag and fly ash",
            "ternary composite cement satisfying combined slag and fly ash percentage requirements",
            "composite cement specification for multi-mineral blended hydraulic binder"
        ]
    },

    # ==================== ELECTRICAL (13) ====================
    "IS 12640 (Part 1)": {
        "clean_product": "Residual Current Circuit Breakers without Overcurrent Protection (RCCBs)",
        "paraphrases": [
            "residual current operated circuit breakers (RCCB)",
            "earth leakage circuit breakers without integral overcurrent protection",
            "current-operated differential protection devices for household installations",
            "RCCB protective switchgear for domestic distribution boards"
        ],
        "indirect_descriptions": [
            "electromechanical safety protective switching device designed to detect residual earth leakage currents and rapidly disconnect circuits to prevent electrocution, lacking built-in thermal or magnetic overload trips",
            "differential current sensing breaker module for sub-distribution panels intended solely for earth fault trip protection without overcurrent elements",
            "core-balance transformer operated isolating breaker for preventing electric shock and fire hazards caused by earth fault leakage"
        ],
        "key_features": ["residual tripping current sensitivity (30mA / 100mA)", "pure residual current protection without overcurrent mechanism", "rapid fault disconnection time"],
        "materials": ["copper", "silver alloy contacts", "polycarbonate enclosure", "iron core"],
        "parameters": {"rated_residual_current": "30mA/100mA", "type": "RCCB (no integral overcurrent)"},
        "application": "residential and commercial electrical sub-distribution boards",
        "near_match_candidates": ["IS 12640 (Part 1)", "IS 12640 (Part 2)", "IS 3854"],
        "near_match_specs": [
            "Residual Current Circuit Breakers (RCCBs) specifically without integral overcurrent protection mechanism",
            "RCCB device providing earth leakage tripping only, requiring upstream MCB coordination",
            "Part 1 compliant residual current breaker for fault current protection without overload release"
        ]
    },
    "IS 12640 (Part 2)": {
        "clean_product": "Residual Current Circuit Breakers with Integral Overcurrent Protection (RCBOs)",
        "paraphrases": [
            "residual current breakers with overcurrent protection (RCBO)",
            "integrated earth leakage and overload circuit breakers",
            "combined residual current and short-circuit protective switchgear",
            "compact RCBO modules for comprehensive circuit protection"
        ],
        "indirect_descriptions": [
            "integrated electrical protective switching device combining residual earth leakage tripping with built-in thermal bimetal and magnetic solenoid overcurrent releases in a single modular frame",
            "dual-function circuit interruption module providing simultaneous protection against shock hazards, prolonged thermal overload, and short-circuit currents",
            "compact multi-protection circuit breaker incorporating both differential core balance sensing and integral overload tripping elements"
        ],
        "key_features": ["combined residual current and overcurrent protection", "short circuit breaking capacity", "single unit space-saving modular design"],
        "materials": ["copper", "silver alloy contacts", "polycarbonate enclosure", "bimetallic strip"],
        "parameters": {"rated_residual_current": "30mA", "short_circuit_capacity": "6kA/10kA", "type": "RCBO (integral overcurrent)"},
        "application": "distribution boards requiring integrated earth fault and overload protection",
        "near_match_candidates": ["IS 12640 (Part 2)", "IS 12640 (Part 1)", "IS 3854"],
        "near_match_specs": [
            "Residual Current Circuit Breakers with integral overcurrent protection (RCBOs)",
            "RCBO device providing combined earth leakage, thermal overload, and short circuit protection in a single pole/frame",
            "Part 2 compliant circuit breaker featuring integral overcurrent tripping mechanisms"
        ]
    },
    "IS 13010": {
        "clean_product": "AC Watt-Hour Meters (Electromechanical)",
        "paraphrases": [
            "alternating current induction-type watt-hour meters",
            "electromechanical AC energy meters class 0.5, 1 and 2",
            "induction disc electricity meters for energy measurement",
            "analogue electro-mechanical kilowatt-hour meters"
        ],
        "indirect_descriptions": [
            "electromechanical induction-disc electrical energy measuring instrument utilizing rotating aluminum disc and gear train registers for recording active energy consumption in alternating current systems",
            "magnetic induction type energy metering apparatus of accuracy classes 0.5, 1, and 2 for tariff recording in AC power networks",
            "disc-driven cumulative active electrical power metering units with cyclometer counter mechanisms"
        ],
        "key_features": ["electromechanical induction disc mechanism", "accuracy classes 0.5, 1 and 2", "rotor magnetic suspension and register gear ratio stability"],
        "materials": ["copper coils", "aluminium disc", "steel laminations", "bakelite housing"],
        "parameters": {"accuracy_class": "0.5, 1, 2", "frequency": "50 Hz", "meter_type": "electromechanical induction"},
        "application": "electrical energy consumption metering in utility and industrial installations",
        "near_match_candidates": ["IS 13010", "IS 13779"],
        "near_match_specs": [
            "AC watt-hour meters of electromechanical induction disc type",
            "analogue disc-driven kilowatt-hour meters class 0.5, 1 and 2",
            "electromechanical energy measuring units compliant with IS 13010"
        ]
    },
    "IS 13779": {
        "clean_product": "AC Static Watt-Hour Meters",
        "paraphrases": [
            "electronic AC static watt-hour meters",
            "static solid-state electricity energy meters class 1 and 2",
            "digital static kilowatt-hour meters for residential billing",
            "microcontroller based static electronic energy meters"
        ],
        "indirect_descriptions": [
            "solid-state digital electronic energy metering instrument employing current transducers and integrated measurement circuits for recording active electrical power without moving mechanical parts",
            "static microprocessor-controlled electrical consumption recorder with non-volatile memory and LCD register display for utility revenue metering",
            "tamper-resistant solid-state watt-hour metering apparatus conforming to class 1 and 2 accuracy thresholds for single and three-phase supplies"
        ],
        "key_features": ["static electronic solid-state operation (no moving parts)", "accuracy class 1.0 and 2.0", "anti-tamper sensing and digital LCD readout"],
        "materials": ["semiconductor circuitry", "copper shunt / CT", "fire-retardant polycarbonate"],
        "parameters": {"accuracy_class": "1 and 2", "meter_type": "static electronic", "display": "LCD"},
        "application": "consumer electricity tariff metering and sub-metering in power distribution",
        "near_match_candidates": ["IS 13779", "IS 13010"],
        "near_match_specs": [
            "AC static (electronic solid-state) watt-hour meters class 1 and 2",
            "digital static energy meters without moving mechanical induction discs",
            "electronic kilowatt-hour meters conforming to static meter specification IS 13779"
        ]
    },
    "IS 15111 (Part 1 & 2)": {
        "clean_product": "Self-Ballasted Lamps for General Lighting Services",
        "paraphrases": [
            "integrated compact fluorescent lamps (CFL)",
            "self-ballasted lamps for general illumination",
            "energy-saving integrated ballast fluorescent lamps",
            "self-ballasted discharge lamps with safety and performance compliance"
        ],
        "indirect_descriptions": [
            "integral discharge lighting units comprising a low-pressure mercury discharge tube coupled with an electronic ballast and cap, designed for retrofit into standard domestic lamp holders",
            "self-contained energy efficient fluorescent lighting sources incorporating internal driving circuitry for direct connection to AC mains",
            "compact integrated ballast illumination assemblies meeting dual safety and photometric efficacy thresholds"
        ],
        "key_features": ["integrated internal electronic ballast", "luminous efficacy and color rendering index", "electrical safety against shock and fire hazards"],
        "materials": ["glass tube", "phosphor coating", "electronic PCB", "PBT housing", "brass/aluminium cap"],
        "parameters": {"voltage": "230 V", "base_type": "B22 / E27", "frequency": "50 Hz"},
        "application": "indoor general lighting and energy-efficient building illumination",
        "near_match_candidates": ["IS 15111 (Part 1 & 2)", "IS 1258:2005", "IS 3854"],
        "near_match_specs": [
            "Self-Ballasted Lamps for general lighting services combining Part 1 safety and Part 2 performance",
            "integrated ballast discharge lamps with internal starting and operating ballasts",
            "compact self-ballasted lamps satisfying comprehensive safety and efficacy criteria"
        ]
    },
    "IS 302 (Part 2/Sec 3)": {
        "clean_product": "Safety of Electric Irons",
        "paraphrases": [
            "safety requirements for domestic electric irons",
            "electric dry and steam iron safety specifications",
            "thermostatically controlled electric clothes pressing irons",
            "household electric iron safety and heating compliance"
        ],
        "indirect_descriptions": [
            "electrically heated fabric pressing appliances equipped with soleplates, heating elements, and adjustable thermostatic cutouts, intended for household garment smoothing",
            "domestic electric heating irons incorporating thermal insulation, grounding continuity, and overheat safety controls",
            "household soleplate heating equipment designed for dry and steam pressing with thermostatic temperature regulation"
        ],
        "key_features": ["soleplate temperature regulation", "thermal cutout safety protection", "dielectric strength and earth bonding integrity"],
        "materials": ["aluminium / stainless steel soleplate", "nichrome heating element", "phenolic plastic handle"],
        "parameters": {"voltage": "230 V AC", "rated_power": "750W - 1200W", "soleplate_type": "non-stick / polished"},
        "application": "domestic laundry pressing and garment care in hostels/hotels",
        "near_match_candidates": ["IS 302 (Part 2/Sec 3)", "IS 302 : Part 1 (2024)", "IS 302 (Part 2/Sec 202)"],
        "near_match_specs": [
            "Safety of household electrical appliances specifically for electric irons (Part 2/Sec 3)",
            "electric irons with adjustable thermostat and soleplate thermal protection",
            "household electric garment pressing irons compliant with IS 302-2-3"
        ]
    },
    "IS 302 (Part 2/Sec 201)": {
        "clean_product": "Safety of Electric Immersion Water Heaters",
        "paraphrases": [
            "safety requirements for electric immersion water heaters",
            "portable bucket electric immersion rod heaters",
            "sheathed immersion heating elements for liquids",
            "domestic liquid immersion electric heaters"
        ],
        "indirect_descriptions": [
            "portable liquid heating devices consisting of tubular metallic sheathed resistance elements with waterproof terminal heads and hanging hooks for heating water in buckets or open containers",
            "direct immersion electrical heating apparatus equipped with insulation resistance safeguards and water level immersion indicators",
            "sheathed portable liquid immersion heating rods for domestic and institutional water heating"
        ],
        "key_features": ["tubular sheathed heating element", "water-tight sealed terminal enclosure", "protective earthing and earthing resistance"],
        "materials": ["copper / nickel-plated brass tube", "magnesium oxide insulation", "nichrome wire", "bakelite handle"],
        "parameters": {"rated_input": "1000W - 2000W", "voltage": "230 V AC", "immersion_depth_marked": "yes"},
        "application": "domestic water heating and institutional liquid heating",
        "near_match_candidates": ["IS 302 (Part 2/Sec 201)", "IS 302 : Part 1 (2024)", "IS 15558", "IS 302 (Part 2/Sec 30)"],
        "near_match_specs": [
            "Safety requirements specifically for portable electric immersion water heaters (Part 2/Sec 201)",
            "electric immersion rod heaters with sealed waterproof handle and liquid immersion level marking",
            "immersion water heaters complying with IS 302-2-201"
        ]
    },
    "IS 302 (Part 2/Sec 202)": {
        "clean_product": "Safety of Electric Stoves",
        "paraphrases": [
            "safety requirements for domestic electric cooking stoves",
            "electric cooking plates and electric stoves",
            "solid hotplate electric cooking appliances",
            "household electric tabletop cooking ranges"
        ],
        "indirect_descriptions": [
            "tabletop electrical cooking apparatus equipped with cast iron hotplates or open coiled radiant heating elements and step-energy regulators for culinary food preparation",
            "domestic food cooking appliances powered by electrical resistance heaters with heat shields and fire-resistant bases",
            "stationary electric tabletop stoves designed for domestic culinary heating with multi-position heat switches"
        ],
        "key_features": ["hotplate surface temperature stability", "spillage protection against liquid ingress", "electrical insulation and thermal enclosure protection"],
        "materials": ["cast iron hotplate", "enameled mild steel body", "ceramic terminal block"],
        "parameters": {"voltage": "230 V AC", "hotplate_power": "1000W - 2000W", "switch_type": "rotary step switch"},
        "application": "domestic cooking, institutional pantries and hostel kitchens",
        "near_match_candidates": ["IS 302 (Part 2/Sec 202)", "IS 302 : Part 1 (2024)", "IS 4246:2025", "IS 302 (Part 2/Sec 3)"],
        "near_match_specs": [
            "Safety of household electrical appliances specifically for electric stoves (Part 2/Sec 202)",
            "electric stoves and solid hotplate cooking units with spillage protection",
            "tabletop electric cooking stoves compliant with IS 302-2-202"
        ]
    },
    "IS 302 (Part 2/Sec 30)": {
        "clean_product": "Safety of Room Heaters",
        "paraphrases": [
            "safety requirements for domestic electric room heaters",
            "electric space heaters and radiant room warmers",
            "convection and fan-assisted electric room heaters",
            "space warming electric radiant heaters for cold climates"
        ],
        "indirect_descriptions": [
            "electrical space heating appliances comprising radiant quartz or rod heating elements, parabolic reflectors, and protective mesh guards, intended for residential space warming",
            "convective and radiant electric room warming equipment equipped with tip-over safety switches and overheat limiters",
            "domestic space heating appliances with thermal cutoff and touch-safe protective grilles for indoor thermal comfort"
        ],
        "key_features": ["tilt/tip-over safety cutoff switch", "finger-proof protective mesh grille", "thermal overheat fuse protection"],
        "materials": ["quartz tube / carbon rods", "stainless steel reflector", "steel sheet body"],
        "parameters": {"rated_wattage": "1000W / 2000W", "voltage": "230 V AC", "heating_modes": "dual heat settings"},
        "application": "residential space heating and government office winter warming",
        "near_match_candidates": ["IS 302 (Part 2/Sec 30)", "IS 302 : Part 1 (2024)", "IS 374:2019"],
        "near_match_specs": [
            "Safety of household electrical appliances specifically for room heaters (Part 2/Sec 30)",
            "electric space heaters with tilt-safety shutoff mechanism and protective grille",
            "room heating appliances compliant with IS 302-2-30"
        ]
    },
    "IS 3854": {
        "clean_product": "Switches for Domestic and Similar Purposes",
        "paraphrases": [
            "switches for domestic and similar fixed electrical installations",
            "flush and surface mounted electrical wall switches",
            "modular and piano type electrical lighting switches",
            "manual electrical switches for household installations"
        ],
        "indirect_descriptions": [
            "manually operated electrical switching devices designed for controlling fixed lighting and small appliance branch circuits in residential and commercial buildings",
            "modular snap-action electrical switches with silver-inlaid contact tips and flame-retardant enclosures for 6A and 16A wall installations",
            "wall-mounted mechanical contact switches for AC electrical distribution systems up to 250V"
        ],
        "key_features": ["making and breaking endurance (40,000 operations)", "temperature rise limits on terminals", "fire-resistant insulating body material"],
        "materials": ["polycarbonate", "phosphor bronze terminals", "silver alloy contacts"],
        "parameters": {"rated_current": "6A / 16A", "rated_voltage": "250 V AC", "mounting": "flush / surface"},
        "application": "residential and commercial building electrification",
        "near_match_candidates": ["IS 3854", "IS 14772:2020", "IS 1258:2005"],
        "near_match_specs": [
            "Switches for domestic and similar purposes for fixed electrical installations",
            "modular AC electrical switches of 6A and 16A rating meeting endurance and temperature rise criteria",
            "wall switches compliant with IS 3854"
        ]
    },
    "IS 694": {
        "clean_product": "PVC Insulated Cables for Voltages up to 1100 V",
        "paraphrases": [
            "PVC insulated electric cables up to and including 1100 V",
            "single-core and multi-core copper PVC building wiring cables",
            "flexible PVC insulated copper cables for domestic wiring",
            "1100V grade PVC insulated power and lighting cables"
        ],
        "indirect_descriptions": [
            "insulated electrical conductors made of annealed high-conductivity copper wires covered with polyvinyl chloride (PVC) insulation and sheath, designed for internal wiring up to 1.1 kV",
            "flame retardant PVC insulated electrical building wires for conduit and casing-capping installations in building electrification",
            "low-voltage insulated flexible copper cables for fixed power and lighting circuits up to 1100 volts"
        ],
        "key_features": ["high-conductivity electrolytic copper conductors", "flame retardant PVC insulation compound", "voltage rating up to 1100 V AC"],
        "materials": ["copper conductor", "PVC insulation", "PVC outer sheath"],
        "parameters": {"voltage_rating": "up to 1100 V", "conductor_type": "solid / stranded copper", "insulation": "PVC type A"},
        "application": "internal building wiring, conduit installations, and electrical distribution",
        "near_match_candidates": ["IS 694", "IS 17293:2020", "IS 17505 (Part 1):2021"],
        "near_match_specs": [
            "PVC insulated cables for working voltages up to and including 1100 V",
            "building wiring cables with PVC insulation and annealed copper conductor per IS 694",
            "1100V grade PVC flexible electrical cables for fixed wiring"
        ]
    },
    "IS 374:2019": {
        "clean_product": "Electric Ceiling Type Fans and Regulators",
        "paraphrases": [
            "electric ceiling fans and electronic speed regulators",
            "overhead electric circulation fans with step regulators",
            "ceiling-mounted electric cooling fans with suspension system",
            "energy-efficient electric ceiling fans for office and domestic use"
        ],
        "indirect_descriptions": [
            "ceiling-suspended electro-mechanical air circulation machines consisting of an electric motor rotor driving balanced metallic or plastic blades, accompanied by an electronic step regulator for room air movement",
            "overhead rotary air moving appliances equipped with safety suspension rods, downrods, and multi-position speed controllers for indoor continuous ventilation",
            "electrically powered ceiling mounted air movement equipment featuring balanced aerodynamic blades and step-type speed controllers"
        ],
        "key_features": ["service value (air delivery per watt)", "suspension safety secondary wire mechanism", "temperature rise limits on motor windings"],
        "materials": ["copper motor windings", "aluminium blades", "mild steel downrod", "electronic regulator"],
        "parameters": {"sweep_size": "1200 mm / 1400 mm", "voltage": "230 V AC", "speed_steps": "5 steps"},
        "application": "air circulation in government offices, schools, and institutional quarters",
        "near_match_candidates": ["IS 374:2019", "IS 302 : Part 1 (2024)", "IS 3854"],
        "near_match_specs": [
            "Electric ceiling type fans and speed regulators conforming to third revision energy and safety requirements",
            "ceiling fans with 1200 mm sweep, high service value, and electronic step regulators",
            "overhead electric fans meeting IS 374:2019 specifications"
        ]
    },
    "IS 302 : Part 1 (2024)": {
        "clean_product": "Safety of Household and Similar Electrical Appliances - General Requirements",
        "paraphrases": [
            "general safety requirements for household and similar electrical appliances",
            "baseline electrical appliance safety standard (Part 1)",
            "comprehensive safety guidelines against electrical and thermal hazards in appliances",
            "general electrical safety code for domestic appliances"
        ],
        "indirect_descriptions": [
            "overarching safety criteria and testing framework establishing fundamental requirements for preventing electrical shock, thermal burns, mechanical injury, radiation, and fire in household electrical appliances",
            "horizontal electrical equipment safety benchmark specifying creepage distances, dielectric insulation strength, earthing continuity, and mechanical robustness across consumer electro-mechanical goods",
            "baseline general safety specification governing design, insulation, construction, and testing of domestic electro-thermal and electro-mechanical equipment"
        ],
        "key_features": ["dielectric insulation and leakage current limits", "flame retardancy and glow-wire resistance of polymers", "protection against access to live electrical parts"],
        "materials": ["electrical insulation materials", "flame-retardant polymers", "conductive metal terminals"],
        "parameters": {"supply_voltage_max": "250 V single-phase / 480 V other", "revision": "Seventh Revision (2024)"},
        "application": "universal electrical appliance manufacturing and type testing",
        "near_match_candidates": ["IS 302 : Part 1 (2024)", "IS 302 (Part 2/Sec 3)", "IS 302 (Part 2/Sec 30)", "IS 302 (Part 2/Sec 201)", "IS 302 (Part 2/Sec 202)", "IS 374:2019"],
        "near_match_specs": [
            "Safety of household and similar electrical appliances - Part 1 General Requirements (Seventh Revision)",
            "horizontal general safety framework covering insulation, earthing, and fire resistance for all electrical appliances",
            "general appliance safety baseline under IS 302 : Part 1 (2024)"
        ]
    },

    # ==================== GAS & LPG (6) ====================
    "IS 4246:2025": {
        "clean_product": "Domestic Gas Stoves and Built-in Hobs for LPG",
        "paraphrases": [
            "domestic gas stoves and built-in hobs for liquefied petroleum gas",
            "LPG cooking stoves and countertop burners for domestic use",
            "household gas cooking appliances for LPG cylinders",
            "multi-burner domestic LPG gas stoves with flame failure safety"
        ],
        "indirect_descriptions": [
            "countertop and drop-in culinary cooking apparatus equipped with atmospheric aerated burners, brass control valves, and pan supports engineered for liquefied petroleum gas mixtures",
            "domestic culinary gas heating appliances operating on bottled hydrocarbon gas with thermal efficiency benchmarks and combustion safety",
            "tabletop and built-in cooking stoves calibrated for pressurized LPG fuel combustion in residential kitchens"
        ],
        "key_features": ["thermal efficiency minimum 68%", "carbon monoxide emission limits (<0.02%)", "gas-tight brass valve integrity"],
        "materials": ["stainless steel / toughened glass body", "brass burners", "cast iron pan supports"],
        "parameters": {"fuel_type": "LPG", "burners": "2 / 3 / 4 burners", "thermal_efficiency_min": "68%"},
        "application": "domestic cooking and institutional food preparation using LPG",
        "near_match_candidates": ["IS 4246:2025", "IS 17153:2019", "IS 9798", "IS 302 (Part 2/Sec 202)"],
        "near_match_specs": [
            "Domestic gas stoves and built-in hobs specifically for use with Liquefied Petroleum Gas (LPG)",
            "LPG gas stoves satisfying Sixth Revision thermal efficiency and combustion emission standards",
            "gas cooking stoves calibrated for cylinder LPG mixtures conforming to IS 4246:2025"
        ]
    },
    "IS 17153:2019": {
        "clean_product": "Domestic Gas Stoves for Piped Natural Gas (PNG)",
        "paraphrases": [
            "domestic gas stoves for use with piped natural gas (PNG)",
            "PNG dedicated household cooking stoves and hobs",
            "piped methane gas domestic cooking stoves",
            "natural gas domestic cooking appliances for city gas networks"
        ],
        "indirect_descriptions": [
            "culinary gas cooking apparatus featuring specialized burner jets and manifold assemblies calibrated strictly for low-pressure piped methane-rich natural gas networks",
            "residential cooking appliances designed for piped utility natural gas supply with specific injector sizing and combustion air ratio",
            "household gas burning cooking appliances designed exclusively for piped natural gas infrastructure"
        ],
        "key_features": ["optimized PNG injector nozzle orifice", "thermal efficiency conformity for methane fuel", "low combustion emissions of CO and NOx"],
        "materials": ["stainless steel", "brass burner heads", "powder coated mild steel frame"],
        "parameters": {"fuel_type": "PNG (Piped Natural Gas)", "supply_pressure": "21 mbar", "burners": "2 / 3 / 4"},
        "application": "residential cooking in urban areas serviced by city gas distribution (CGD) networks",
        "near_match_candidates": ["IS 17153:2019", "IS 4246:2025", "IS 9798"],
        "near_match_specs": [
            "Domestic gas stoves specifically engineered for use with Piped Natural Gas (PNG)",
            "gas cooking stoves calibrated for 21 mbar piped methane supply rather than bottled LPG",
            "PNG domestic gas stoves conforming to IS 17153:2019"
        ]
    },
    "IS 3196 (Part 1)": {
        "clean_product": "Welded Low Carbon Steel Gas Cylinders for LPG",
        "paraphrases": [
            "welded low carbon steel gas cylinders exceeding 5 litre capacity for LPG",
            "welded steel LPG storage cylinders for domestic and commercial fuel",
            "two-piece or three-piece welded steel cylinders for liquefied petroleum gas",
            "low-carbon steel refillable LPG fuel cylinders"
        ],
        "indirect_descriptions": [
            "welded pressure vessels fabricated from deep-drawing low-carbon micro-alloyed steel sheets, designed to contain pressurized liquefied petroleum gas mixtures with minimum burst pressure safety factors",
            "circumferentially and longitudinally welded steel pressure containers for safe transport and distribution of pressurized bottled hydrocarbon cooking gases",
            "refillable welded steel vessels exceeding 5-litre water capacity for domestic and commercial LPG storage"
        ],
        "key_features": ["hydrostatic stretch test compliance", "circumferential weld radiographic examination", "normalized or stress-relieved post-weld heat treatment"],
        "materials": ["low carbon micro-alloyed steel", "welding consumables"],
        "parameters": {"water_capacity": "> 5 litres (e.g. 33.3L / 47.5L)", "test_pressure": "2.5 MPa", "working_fluid": "LPG"},
        "application": "bottled LPG distribution for household, commercial and industrial heating",
        "near_match_candidates": ["IS 3196 (Part 1)", "IS 7285 (Part 1)", "IS 3224"],
        "near_match_specs": [
            "Welded low carbon steel gas cylinders exceeding 5 litre water capacity specifically for LPG",
            "welded steel refillable cylinders for LPG distribution per Part 1 specifications",
            "welded LPG cylinders meeting hydrostatic test pressure and weld integrity of IS 3196 (Part 1)"
        ]
    },
    "IS 3224": {
        "clean_product": "Valve Fittings for Compressed Gas Cylinders (Excluding LPG)",
        "paraphrases": [
            "valve fittings for compressed gas cylinders excluding LPG",
            "high-pressure cylinder shutoff valves for industrial and medical gases",
            "cylinder valves for oxygen, nitrogen, argon and air cylinders",
            "brass shutoff valves for compressed high-pressure gas containers"
        ],
        "indirect_descriptions": [
            "precision-machined forged brass fluid isolation valves with standardized inlet taper threads and gas-specific outlet connections, intended for mounting on industrial compressed gas cylinders other than LPG",
            "high-pressure cylinder head valve assemblies featuring safety burst discs and spindle seals for non-liquefied compressed gas cylinders",
            "containment shutoff valves for refillable seamless steel gas cylinders handling atmospheric and specialized gases"
        ],
        "key_features": ["gas-specific outlet connection threading", "burst disc / pressure relief device integration", "leak-tightness at 200 bar operating pressure"],
        "materials": ["forged brass", "stainless steel spindle", "PTFE / nylon packing"],
        "parameters": {"working_pressure": "150 - 250 bar", "fluid_scope": "compressed gases excluding LPG", "thread": "taper thread to cylinder"},
        "application": "industrial, medical, and laboratory gas cylinders (oxygen, nitrogen, hydrogen, argon)",
        "near_match_candidates": ["IS 3224", "IS 9798", "IS 7285 (Part 1)", "IS 3196 (Part 1)"],
        "near_match_specs": [
            "Valve fittings for compressed gas cylinders explicitly excluding liquefied petroleum gas",
            "forged brass cylinder valves for industrial compressed gas cylinders per IS 3224",
            "shutoff valve fittings with gas-specific threads for compressed oxygen, nitrogen, and argon"
        ]
    },
    "IS 7285 (Part 1)": {
        "clean_product": "Refillable Seamless Steel Gas Cylinders - Normalized Steel",
        "paraphrases": [
            "refillable seamless steel gas cylinders (normalized steel)",
            "seamless normalized steel cylinders for high pressure industrial gases",
            "seamless steel high-pressure vessels for industrial gases",
            "jointless seamless forged steel gas containers"
        ],
        "indirect_descriptions": [
            "seamless cylindrical pressure vessels manufactured from forged or hot-extruded billets of alloy or carbon manganese steel subjected to normalizing heat treatment, designed for high-pressure storage without welds",
            "jointless high-strength steel pressure containers intended for containing permanent gases at working pressures exceeding 150 bar",
            "seamless normalized high-pressure gas storage cylinders for industrial and technical gases"
        ],
        "key_features": ["seamless weld-free body construction", "normalizing heat treatment for uniform grain structure", "hydraulic burst test and ultrasonic flaw detection"],
        "materials": ["carbon manganese steel", "chromium molybdenum alloy steel"],
        "parameters": {"working_pressure": "150 - 200 bar", "heat_treatment": "normalized", "construction": "seamless jointless"},
        "application": "high-pressure containment of industrial, medical and calibration gases",
        "near_match_candidates": ["IS 7285 (Part 1)", "IS 3196 (Part 1)", "IS 3224"],
        "near_match_specs": [
            "Refillable seamless steel gas cylinders manufactured from normalized steel (Part 1)",
            "jointless seamless high-pressure gas cylinders for industrial gases excluding welded construction",
            "seamless normalized steel pressure vessels conforming to IS 7285 (Part 1)"
        ]
    },
    "IS 9798": {
        "clean_product": "Low Pressure Regulators for LPG Mixtures",
        "paraphrases": [
            "low pressure regulators for liquefied petroleum gas (LPG)",
            "domestic LPG cylinder pressure regulators",
            "diaphragm-operated low pressure LPG pressure reducers",
            "compact click-on LPG cylinder regulators"
        ],
        "indirect_descriptions": [
            "spring-loaded flexible diaphragm pressure reducing devices designed for snap-on mounting on domestic LPG cylinder valves to step down cylinder pressure to a safe operating level for burners",
            "fluid pressure control devices incorporating excess flow check mechanisms and calibrated relief valves for residential LPG installations",
            "diaphragm-actuated gas pressure regulators maintaining nominal 29 mbar outlet pressure from high-pressure bottled LPG"
        ],
        "key_features": ["regulated outlet pressure (nominally 29 mbar / 2.94 kPa)", "excess flow shutoff safety mechanism", "leak-tight rubber diaphragm and valve pad"],
        "materials": ["die-cast zinc alloy / aluminium", "nitrile rubber diaphragm", "brass valve seat", "stainless steel spring"],
        "parameters": {"inlet_pressure": "0.3 - 17 bar", "outlet_pressure": "29 mbar (2.94 kPa)", "flow_rate": "0.5 kg/h - 1.5 kg/h"},
        "application": "domestic and commercial LPG cylinder gas distribution to cooking appliances",
        "near_match_candidates": ["IS 9798", "IS 3224", "IS 4246:2025"],
        "near_match_specs": [
            "Low pressure regulators specifically for use with liquefied petroleum gas (LPG) mixtures",
            "diaphragm-operated domestic LPG cylinder pressure regulators delivering 29 mbar outlet pressure",
            "LPG regulators meeting safety, shutoff and flow requirements of IS 9798"
        ]
    },

    # ==================== FIRE SAFETY (2) ====================
    "IS 15683:2018": {
        "clean_product": "Portable Fire Extinguishers",
        "paraphrases": [
            "portable fire extinguishers - performance and construction",
            "man-portable fire extinguishers (water, foam, powder, CO2, clean agent)",
            "handheld first-aid fire fighting extinguishers",
            "portable pressurized fire extinguisher units"
        ],
        "indirect_descriptions": [
            "first-aid manual fire extinguishing apparatus of portable mass (< 20 kg) containing pressurized extinguishing agents like ABC dry chemical powder, aqueous foam, or carbon dioxide with discharge horn and trigger valve",
            "handheld pressurized firefighting cylinders fitted with pressure gauges, safety pins, and discharge hoses for rapid fire knock-down across classes A, B, and C",
            "portable fire suppressing equipment for building corridors and server rooms with specific fire rating performance"
        ],
        "key_features": ["fire rating test validation (e.g. 2A, 21B, 55B)", "hydraulic proof test of vessel", "operating temperature range (-30C to +60C)"],
        "materials": ["mild steel deep drawn body", "brass discharge valve", "ABC dry powder / AFFF / CO2"],
        "parameters": {"capacity": "1kg - 9kg / 2L - 9L", "operating_pressure": "15 bar", "mounting": "wall bracket"},
        "application": "first-aid firefighting in offices, hospitals, industrial workshops, and residential complexes",
        "near_match_candidates": ["IS 15683:2018", "IS 16018:2012"],
        "near_match_specs": [
            "Portable Fire Extinguishers conforming to performance and construction specification IS 15683:2018",
            "man-portable handheld fire extinguishers below 20 kg total mass",
            "portable firefighting appliances satisfying Class A/B fire ratings and hydraulic proof testing"
        ]
    },
    "IS 16018:2012": {
        "clean_product": "Wheeled Fire Extinguishers",
        "paraphrases": [
            "wheeled mobile fire extinguishers",
            "trolley-mounted heavy-duty fire extinguishers",
            "large capacity mobile firefighting extinguisher units",
            "wheeled mobile dry chemical and foam fire extinguishers"
        ],
        "indirect_descriptions": [
            "heavy-capacity mobile firefighting apparatus exceeding 20 kg total mass mounted on a wheeled trolley chassis with tow handle and extended discharge hose for industrial hazard suppression",
            "high-volume mobile extinguishing agent dispensers designed for rapid deployment across large fuel storage farms, aviation aprons, and industrial refineries",
            "trolley-transported heavy chemical firefighting units with nitrogen propellant cartridges and high-flow delivery nozzles"
        ],
        "key_features": ["chassis wheel mobility and balance", "large agent capacity (25kg - 150kg / 25L - 100L)", "extended discharge hose and high discharge throw"],
        "materials": ["welded carbon steel pressure vessel", "pneumatic or solid rubber wheels", "heavy duty steel frame"],
        "parameters": {"capacity": "25kg / 50kg / 75kg / 150kg", "mobility": "wheeled trolley chassis", "discharge_range": "> 8 meters"},
        "application": "high-hazard industrial plants, oil refineries, power stations, and airport hangars",
        "near_match_candidates": ["IS 16018:2012", "IS 15683:2018"],
        "near_match_specs": [
            "Wheeled (trolley-mounted) Fire Extinguishers designed for high-capacity mobility",
            "large-scale mobile fire extinguishers on wheel frames exceeding 25 kg agent capacity",
            "wheeled firefighting appliances conforming to IS 16018:2012"
        ]
    }
}
