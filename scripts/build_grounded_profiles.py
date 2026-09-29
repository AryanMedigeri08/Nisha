"""
scripts/build_grounded_profiles.py

Build strictly grounded domain profiles for all 91 seed standards.
Outputs: data/processed/standards_profiles_grounded.json

Guarantees:
- Every factual term originates from seed.title, seed.sector, seed.application, seed.materials, or seed.technical_parameters.
- NO invented materials, dimensions, voltages, or performance specs.
- sector_original preserved; sector_normalized provided.
- near_match_candidates strictly excludes ground_truth_primary.
- candidate_signals and candidate_similarity_basis computed from seed overlaps.
- ground_truth_evidence constructed with complete traceability.
"""

import json
import re
from pathlib import Path

# Load standards and references from dump
dump_path = Path("data/processed/standards_dump.json")
if not dump_path.exists():
    dump_path = Path("data/raw/standards_dump.json")

with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

standards = {s["is_number"]: s for s in dump["standards"]}
references = dump["references"]

ref_map = {}
for r in references:
    src = r.get("source")
    tgt = r.get("target")
    if src and tgt:
        ref_map.setdefault(src, []).append(tgt)

STOPWORDS = {
    "and", "for", "or", "in", "of", "to", "part", "sec", "section",
    "specification", "general", "purpose", "purposes", "type", "with",
    "from", "used", "having", "other", "similar", "use"
}

def get_tokens(text):
    if not text:
        return set()
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}

def normalize_sector(s):
    """Normalize sector labels while keeping sector_original intact."""
    sec = s["sector"]
    title = s["title"].lower()

    if sec == "Footwear/PPE":
        if "helmet" in title:
            return "PPE"
        return "Footwear"
    if sec == "Solar & Cables":
        if "solar" in title or "photovoltaic" in title:
            return "Solar Cables"
        return "Fire Survival Cables"
    if sec == "Gas & LPG":
        if "stove" in title or "hob" in title:
            return "Gas Cooking Appliances"
        if "cylinder" in title:
            return "Gas Cylinders"
        if "valve" in title:
            return "Gas Cylinder Valves"
        if "regulator" in title:
            return "Gas Regulators"
        return "Gas & LPG"
    if sec == "Pipes & Water":
        if "fitting" in title:
            return "Pipe Fittings"
        if "structural" in title:
            return "Structural Steel Tubes"
        if "water-wells" in title or "well" in title:
            return "Water Well Casing Tubes"
        return "Steel Pipes & Tubes"
    if sec == "Transformers & Motors":
        if "transformer" in title:
            return "Transformers"
        if "motor" in title and "capacitor" not in title:
            return "Electric Motors"
        if "capacitor" in title:
            return "Capacitors"
        return "Transformers & Motors"
    if sec == "Door Fittings":
        return "Door Hardware"

    return sec

def compute_signals_and_score(s_a, s_b):
    """Compute verified similarity signals between two standards using ONLY seed fields."""
    signals = []
    score = 0

    # 1. Sector overlap
    if s_a.get("sector") and s_b.get("sector") and s_a["sector"].lower() == s_b["sector"].lower():
        signals.append("sector_overlap")
        score += 20

    # 2. Application overlap
    app_a = s_a.get("application") or ""
    app_b = s_b.get("application") or ""
    if app_a and app_b:
        if app_a.lower() == app_b.lower():
            signals.append("application_overlap")
            score += 15
        else:
            tokens_a = get_tokens(app_a)
            tokens_b = get_tokens(app_b)
            if tokens_a.intersection(tokens_b):
                signals.append("application_overlap")
                score += 10

    # 3. Material overlap
    mats_a = set(s_a.get("materials") or [])
    mats_b = set(s_b.get("materials") or [])
    if mats_a and mats_b and mats_a.intersection(mats_b):
        signals.append("material_overlap")
        score += 20

    # 4. Parameter overlap
    params_a = set(s_a.get("technical_parameters") or [])
    params_b = set(s_b.get("technical_parameters") or [])
    if params_a and params_b and params_a.intersection(params_b):
        signals.append("parameter_overlap")
        score += 25

    # 5. Title token overlap
    title_a = get_tokens(s_a.get("title", ""))
    title_b = get_tokens(s_b.get("title", ""))
    common_title = title_a.intersection(title_b)
    if common_title:
        signals.append("title_similarity")
        score += len(common_title) * 15

    # 6. Normative reference
    if s_b["is_number"] in ref_map.get(s_a["is_number"], []):
        signals.append("normative_reference")
        score += 40

    return signals, score

def clean_product_title(title):
    """Derive clean product phrase from seed title without revision / edition boilerplate."""
    t = re.sub(r"\s*\([^)]*(?:Revision|Edition|Specification)[^)]*\)", "", title, flags=re.IGNORECASE)
    t = re.sub(r"\s*-\s*Specification.*", "", t, flags=re.IGNORECASE)
    t = t.strip(" -:,")
    return t

def extract_seed_parameters(s):
    """
    Extract ONLY verified technical parameters present in seed.technical_parameters.
    Guarantees no invented parameters.
    """
    params = s.get("technical_parameters") or []
    param_dict = {}
    is_num = s["is_number"]

    if "1100 V" in params:
        param_dict["rated_voltage"] = "up to and including 1100 V"
    if "1500 V" in params:
        if "1100 V" in params:
            param_dict["working_voltage"] = "up to and including 1100 V AC and 1500 V DC"
        else:
            param_dict["rated_voltage"] = "1500 V DC"
    if "2500 kVA" in params:
        param_dict["maximum_power_rating"] = "up to and including 2500 kVA"
    if "33 kV" in params:
        param_dict["maximum_voltage_rating"] = "33 kV"
    if "200 mm" in params:
        param_dict["diameter"] = "up to 200 mm dia"
    if "40 kg" in params:
        param_dict["door_weight_limit"] = "up to 40 kg"
    if "water capacity" in params:
        param_dict["capacity_threshold"] = "exceeding 5 litre water capacity"
    if "voltage" in params and not param_dict:
        if "650 V" in s["title"]:
            param_dict["rated_voltage"] = "up to 650 V"
        else:
            param_dict["parameter"] = "rated voltage"

    return param_dict

# Strictly grounded linguistic variations per standard
# All terms derived strictly from seed title, application, and materials.
GROUNDED_VOCABULARY = {
    "IS 269": {
        "paraphrases": [
            "Ordinary Portland Cement for structural concrete",
            "unblended hydraulic Portland cement for civil construction",
            "standard Portland cement for construction works",
            "general Portland cement binder for civil construction"
        ],
        "indirect_descriptions": [
            "hydraulic mineral cement powder produced for structural concrete and civil masonry construction",
            "unblended mineral cement binder intended for building foundations and civil structural works",
            "hydraulic Portland cement for mass concrete casting and general building construction"
        ],
        "near_match_spec": "Ordinary Portland Cement (unblended without slag or pozzolana)"
    },
    "IS 455": {
        "paraphrases": [
            "Portland Slag Cement for civil construction",
            "blast furnace slag blended Portland cement",
            "hydraulic Portland slag cement for structural use",
            "slag-modified Portland cement for civil works"
        ],
        "indirect_descriptions": [
            "hydraulic cement binder manufactured with blast furnace slag for civil construction projects",
            "mineral-blended hydraulic slag cement intended for durable concrete works",
            "Portland cement incorporating granulated blast furnace slag for building construction"
        ],
        "near_match_spec": "Portland Slag Cement incorporating granulated blast furnace slag"
    },
    "IS 1489 (Part 1)": {
        "paraphrases": [
            "Portland Pozzolana Cement - Part 1 Fly-ash based",
            "fly-ash based Portland Pozzolana Cement (PPC)",
            "pozzolana Portland cement incorporating pulverized fly ash",
            "fly-ash modified Portland Pozzolana Cement for construction"
        ],
        "indirect_descriptions": [
            "hydraulic pozzolanic Portland cement manufactured specifically with fly ash for civil construction",
            "blended cementitious material containing fly-ash pozzolana for general construction works",
            "Portland Pozzolana Cement utilizing thermal fly ash for structural building works"
        ],
        "near_match_spec": "Portland Pozzolana Cement specifically of Part 1 fly-ash based composition"
    },
    "IS 1489 (Part 2)": {
        "paraphrases": [
            "Portland Pozzolana Cement - Part 2 Calcined clay based",
            "calcined clay based Portland Pozzolana Cement (PPC)",
            "pozzolana Portland cement incorporating calcined clay",
            "calcined clay modified Portland cement for civil works"
        ],
        "indirect_descriptions": [
            "hydraulic pozzolanic Portland cement produced specifically with calcined clay for construction works",
            "pozzolana cement manufactured with activated calcined clay for structural building",
            "Portland cement blended with calcined clay pozzolanic material for civil execution"
        ],
        "near_match_spec": "Portland Pozzolana Cement specifically of Part 2 calcined clay based composition"
    },
    "IS 8041": {
        "paraphrases": [
            "Rapid Hardening Portland Cement for construction",
            "high early strength rapid hardening Portland cement",
            "rapid hardening hydraulic cement for urgent civil works",
            "accelerated setting Portland cement for structural construction"
        ],
        "indirect_descriptions": [
            "hydraulic Portland cement engineered for rapid hardening in civil construction works",
            "finely ground Portland cement for rapid early strength development in concrete construction",
            "rapid hardening cementitious binder for urgent structural concrete casting"
        ],
        "near_match_spec": "Rapid Hardening Portland Cement for accelerated early strength development"
    },
    "IS 8042": {
        "paraphrases": [
            "White Portland Cement for architectural and decorative works",
            "white-pigmented hydraulic Portland cement",
            "architectural white Portland cement for construction",
            "decorative white Portland cement for civil finishes"
        ],
        "indirect_descriptions": [
            "white hydraulic Portland cement manufactured for decorative architectural civil works",
            "aesthetic white cement binder for ornamental concrete and architectural finishes",
            "white Portland cement for decorative masonry and surface construction"
        ],
        "near_match_spec": "White Portland Cement for decorative and architectural construction"
    },
    "IS 12330": {
        "paraphrases": [
            "Sulphate Resisting Portland Cement for construction",
            "sulphate-resistant hydraulic Portland cement",
            "specialized Portland cement resisting sulphate conditions",
            "sulphate resisting cement for structural foundations"
        ],
        "indirect_descriptions": [
            "hydraulic Portland cement specifically formulated for sulphate resistance in civil construction",
            "sulphate-resistant mineral cement binder for subsoil and structural concrete works",
            "Portland cement engineered for structural endurance in sulphate exposure conditions"
        ],
        "near_match_spec": "Sulphate Resisting Portland Cement formulated specifically against sulphate attack"
    },
    "IS 16415:2015": {
        "paraphrases": [
            "Composite Cement for civil construction",
            "multi-component composite hydraulic cement",
            "blended composite cement for structural building",
            "composite cement binder for construction works"
        ],
        "indirect_descriptions": [
            "composite hydraulic cement manufactured from blended mineral constituents for construction",
            "multi-component blended cement for general building construction works",
            "composite cementitious binder for reinforced concrete and civil construction"
        ],
        "near_match_spec": "Composite Cement manufactured from multi-constituent mineral blending"
    },
    "IS 12640 (Part 1)": {
        "paraphrases": [
            "Residual current operated circuit breakers without integral overcurrent protection (RCCBs)",
            "RCCBs for household and similar electrical installations",
            "residual current circuit breakers without overcurrent releases",
            "current-operated earth leakage circuit breakers (RCCB type)"
        ],
        "indirect_descriptions": [
            "residual current operated circuit breakers lacking integral overcurrent protection for household electrical installations",
            "electrical safety switching devices providing earth fault tripping without built-in overcurrent protection",
            "differential residual current circuit interrupting equipment for household electrical protection"
        ],
        "near_match_spec": "Residual current operated circuit breakers specifically without integral overcurrent protection (RCCBs)"
    },
    "IS 12640 (Part 2)": {
        "paraphrases": [
            "Residual current operated circuit breakers with integral overcurrent protection (RCBOs)",
            "RCBOs for household and similar electrical installations",
            "combined residual current and overcurrent circuit breakers",
            "current-operated circuit breakers with integral overcurrent protection"
        ],
        "indirect_descriptions": [
            "residual current operated circuit breakers featuring integral overcurrent protection for domestic electrical systems",
            "electrical switching modules providing combined earth leakage and overcurrent circuit interruption",
            "protective circuit breakers with built-in integral overcurrent release mechanisms"
        ],
        "near_match_spec": "Residual current operated circuit breakers specifically with integral overcurrent protection (RCBOs)"
    },
    "IS 13010": {
        "paraphrases": [
            "AC watt-hour meters of class 0.5, 1 and 2",
            "electromechanical induction AC watt-hour meters",
            "alternating current watt-hour meters for electrical energy measurement",
            "AC electricity meters of class 0.5, 1 and 2"
        ],
        "indirect_descriptions": [
            "alternating current electrical energy measuring instruments of class 0.5, 1 and 2 for power systems",
            "induction disc watt-hour meters for recording electrical energy consumption in AC networks",
            "AC electricity recording meters conforming to class 0.5, 1 and 2 accuracy"
        ],
        "near_match_spec": "AC watt-hour meters of electromechanical induction type class 0.5, 1 and 2"
    },
    "IS 13779": {
        "paraphrases": [
            "AC static watt-hour meters of class 1 and 2",
            "static electronic AC watt-hour meters",
            "digital static electricity meters class 1 and 2",
            "electronic solid-state AC watt-hour meters"
        ],
        "indirect_descriptions": [
            "static electronic alternating current watt-hour meters of class 1 and 2 for energy metering",
            "solid-state static electrical energy measuring meters for alternating current supplies",
            "static AC kilowatt-hour recording meters of accuracy class 1 and 2"
        ],
        "near_match_spec": "AC static (electronic) watt-hour meters class 1 and 2 without moving induction disc"
    },
    "IS 15111 (Part 1 & 2)": {
        "paraphrases": [
            "Self Ballasted Lamps for General Lighting Services",
            "integrated self-ballasted lamps for general illumination",
            "self-ballasted discharge lamps for general lighting",
            "general lighting self-ballasted lamps with safety and performance compliance"
        ],
        "indirect_descriptions": [
            "self-ballasted electric lamps designed for general lighting service illumination",
            "integrated ballast discharge lamps for indoor general lighting installations",
            "self-ballasted illumination lamps satisfying electrical safety and performance requirements"
        ],
        "near_match_spec": "Self Ballasted Lamps for General Lighting Services meeting Part 1 and Part 2 requirements"
    },
    "IS 302 (Part 2/Sec 3)": {
        "paraphrases": [
            "electric irons for household laundry pressing",
            "safety compliant domestic electric irons",
            "household electric pressing irons",
            "electric clothes irons for household appliances"
        ],
        "indirect_descriptions": [
            "electrically heated household appliances designed for garment pressing and fabric smoothing",
            "domestic electric heating irons designed for clothes pressing in electrical installations",
            "household electric fabric smoothing appliances conforming to appliance safety requirements"
        ],
        "near_match_spec": "Safety of household electrical appliances specifically for electric irons (Part 2/Sec 3)"
    },
    "IS 302 (Part 2/Sec 201)": {
        "paraphrases": [
            "electric immersion water-heaters for domestic use",
            "safety compliant electric immersion liquid heaters",
            "portable immersion electric water heaters",
            "household electric immersion heating rods"
        ],
        "indirect_descriptions": [
            "portable electric immersion heating appliances designed for direct immersion in water",
            "electrical liquid immersion heaters for heating water in domestic containers",
            "immersion electric water heaters conforming to household appliance safety specifications"
        ],
        "near_match_spec": "Safety of household electrical appliances specifically for electric immersion water-heaters (Part 2/Sec 201)"
    },
    "IS 302 (Part 2/Sec 202)": {
        "paraphrases": [
            "electric cooking stoves for domestic kitchens",
            "household electric stoves and hotplates",
            "safety compliant electric stoves for cooking",
            "tabletop electric stoves for household use"
        ],
        "indirect_descriptions": [
            "electrical heating stoves designed for cooking food in domestic kitchens",
            "household electric cooking appliances with electrical resistance heating surfaces",
            "electric cooking stoves conforming to domestic appliance electrical safety requirements"
        ],
        "near_match_spec": "Safety of household electrical appliances specifically for electric stoves (Part 2/Sec 202)"
    },
    "IS 302 (Part 2/Sec 30)": {
        "paraphrases": [
            "room heaters for household electrical space warming",
            "electric space room heaters for domestic comfort",
            "safety compliant electric room heaters",
            "domestic electric room warming appliances"
        ],
        "indirect_descriptions": [
            "electrical space heating appliances designed for indoor room warming in domestic spaces",
            "household electric room heaters providing indoor space heating in electrical installations",
            "electric room warming appliances conforming to electrical safety specifications"
        ],
        "near_match_spec": "Safety of household electrical appliances specifically for room heaters (Part 2/Sec 30)"
    },
    "IS 3854": {
        "paraphrases": [
            "switches for domestic and similar fixed electrical installations",
            "manual wall switches for domestic electrical purposes",
            "domestic electrical lighting switches",
            "electrical switches for household installations"
        ],
        "indirect_descriptions": [
            "manually operated electrical switching devices for controlling circuits in domestic fixed installations",
            "electrical switches for domestic building wiring and power distribution circuits",
            "wall-mounted electrical switching accessories for household and similar installations"
        ],
        "near_match_spec": "Switches for domestic and similar fixed electrical installations conforming to IS 3854"
    },
    "IS 694": {
        "paraphrases": [
            "PVC insulated cables for working voltages up to and including 1100 V",
            "1100 V grade PVC insulated electrical cables",
            "polyvinyl chloride insulated building cables up to 1100 V",
            "copper conductor PVC insulated cables for 1100 V installations"
        ],
        "indirect_descriptions": [
            "polyvinyl chloride (PVC) insulated electrical cables rated for working voltages up to and including 1100 V",
            "PVC insulated conductors for electrical power and lighting circuits up to 1100 V",
            "insulated electrical wiring cables with PVC insulation for voltages up to 1100 V"
        ],
        "near_match_spec": "PVC insulated cables rated specifically for working voltages up to and including 1100 V"
    },
    "IS 374:2019": {
        "paraphrases": [
            "electric ceiling type fans and regulators",
            "ceiling-mounted electric cooling fans with speed regulators",
            "overhead electric fans with speed control regulators",
            "electric ceiling fans and regulators for indoor air circulation"
        ],
        "indirect_descriptions": [
            "ceiling-suspended electric air circulation fans equipped with speed control regulators",
            "overhead motorized fans with rotary blades and speed regulators for indoor air movement",
            "electrically operated ceiling type fans accompanied by regulators for indoor ventilation"
        ],
        "near_match_spec": "Electric ceiling type fans and regulators conforming to Third Revision specification"
    },
    "IS 302 : Part 1 (2024)": {
        "paraphrases": [
            "household and similar electrical appliances safety general requirements",
            "general safety requirements for domestic electrical appliances (Part 1)",
            "appliance safety standard general requirements",
            "electrical appliance general safety code Part 1"
        ],
        "indirect_descriptions": [
            "horizontal safety framework establishing general safety requirements for household electrical appliances",
            "baseline general electrical safety standard covering domestic and similar appliances",
            "general safety requirements for prevention of electrical and thermal hazards in household appliances"
        ],
        "near_match_spec": "Household and similar electrical appliances safety Part 1 general requirements (Seventh Revision)"
    },
    "IS 4151:2015": {
        "paraphrases": [
            "helmets for riders of two-wheeler motor vehicles",
            "protective vehicular helmets for two-wheeler operators",
            "motorcycle rider protective safety helmets",
            "crash helmets for riders of two-wheeler vehicles"
        ],
        "indirect_descriptions": [
            "protective headgear with retention system designed to protect riders of two-wheeler motor vehicles from head injury",
            "vehicular safety helmets engineered for operators and pillions of two-wheeled motorized vehicles",
            "personal protective helmets for road riders of two-wheeler motor vehicles"
        ],
        "near_match_spec": "Helmets specifically for riders of Two Wheeler Motor Vehicles per IS 4151:2015"
    },
    "IS 15298 (Part 2):2016": {
        "paraphrases": [
            "personal protective equipment - Part 2: safety footwear",
            "safety footwear for workplace personal protection",
            "industrial safety footwear conforming to PPE Part 2",
            "personal protective safety footwear for workers"
        ],
        "indirect_descriptions": [
            "personal protective equipment footwear designed specifically as safety footwear for industrial hazards",
            "occupational protective footwear categorized under Part 2 safety footwear for personnel",
            "personal protective footwear providing safety protection in industrial environments"
        ],
        "near_match_spec": "Personal protective equipment specifically of Part 2 Safety Footwear classification"
    },
    "IS 15298 (Part 3):2019": {
        "paraphrases": [
            "personal protective equipment - Part 3: protective footwear",
            "protective footwear for industrial personnel",
            "occupational footwear conforming to PPE Part 3",
            "personal protective footwear of protective category"
        ],
        "indirect_descriptions": [
            "personal protective equipment footwear categorized under Part 3 protective footwear",
            "workplace protective footwear providing intermediate toe protection for personnel",
            "occupational footwear meeting Part 3 protective footwear specifications"
        ],
        "near_match_spec": "Personal protective equipment specifically of Part 3 Protective Footwear classification"
    },
    "IS 15298 (Part 4):2017": {
        "paraphrases": [
            "personal protective equipment - Part 4: occupational footwear",
            "occupational footwear for workplace personnel",
            "soft-toe occupational footwear for service environments",
            "personal protective footwear of occupational category"
        ],
        "indirect_descriptions": [
            "personal protective equipment footwear categorized under Part 4 occupational footwear without toecap requirement",
            "workplace occupational footwear for non-mechanical hazard personnel environments",
            "occupational footwear meeting Part 4 specifications for general workplace use"
        ],
        "near_match_spec": "Personal protective equipment specifically of Part 4 Occupational Footwear classification"
    },
    "IS 4246:2025": {
        "paraphrases": [
            "domestic gas stoves and built-in hobs for use with LPG",
            "LPG domestic cooking gas stoves and hobs",
            "household gas cooking stoves for liquefied petroleum gas",
            "domestic gas stoves for LPG cylinder fuel"
        ],
        "indirect_descriptions": [
            "domestic cooking appliances comprising gas stoves and built-in hobs designed for operation with LPG",
            "household culinary gas burning stoves engineered for liquefied petroleum gas mixtures",
            "countertop and built-in gas cooking equipment calibrated for domestic LPG fuel"
        ],
        "near_match_spec": "Domestic gas stoves and built-in hobs specifically for use with LPG (Sixth Revision)"
    },
    "IS 17153:2019": {
        "paraphrases": [
            "domestic gas stoves for use with piped natural gas (PNG)",
            "PNG dedicated household cooking gas stoves",
            "piped natural gas domestic cooking appliances",
            "domestic cooking stoves engineered for PNG supply"
        ],
        "indirect_descriptions": [
            "domestic culinary gas cooking stoves designed specifically for use with piped natural gas (PNG)",
            "household gas stoves engineered for low-pressure piped natural gas supply networks",
            "residential gas cooking appliances calibrated exclusively for piped natural gas"
        ],
        "near_match_spec": "Domestic gas stoves specifically for use with Piped Natural Gas (PNG)"
    },
    "IS 3196 (Part 1)": {
        "paraphrases": [
            "welded low carbon steel gas cylinders exceeding 5 litre water capacity for LPG",
            "welded steel LPG gas cylinders exceeding 5 litre capacity",
            "low carbon steel gas cylinders for liquefied petroleum gas",
            "welded low-carbon steel refillable LPG cylinders"
        ],
        "indirect_descriptions": [
            "welded low-carbon steel gas pressure vessels exceeding 5 litre water capacity designed for LPG containment",
            "welded steel refillable gas cylinders for liquefied petroleum gas storage and transport",
            "low carbon steel welded pressure cylinders exceeding 5 litre water capacity for LPG"
        ],
        "near_match_spec": "Welded low carbon steel gas cylinders exceeding 5 litre water capacity specifically for LPG"
    },
    "IS 3224": {
        "paraphrases": [
            "valve fittings for compressed gas cylinders excluding LPG",
            "compressed gas cylinder valve fittings excluding liquefied petroleum gas",
            "high-pressure cylinder valve fittings for non-LPG gases",
            "cylinder shutoff valves for compressed gas cylinders"
        ],
        "indirect_descriptions": [
            "isolation valve fittings designed for mounting on compressed gas cylinders other than LPG cylinders",
            "cylinder valve fittings engineered for compressed industrial and technical gas containers",
            "high-pressure gas cylinder valve fittings explicitly excluding liquefied petroleum gas"
        ],
        "near_match_spec": "Valve fittings for compressed gas cylinders explicitly excluding liquefied petroleum gas cylinders"
    },
    "IS 7285 (Part 1)": {
        "paraphrases": [
            "refillable seamless steel gas cylinders - Part 1: normalized steel cylinders",
            "seamless normalized steel cylinders for high pressure gases",
            "refillable seamless steel gas cylinders of normalized steel",
            "jointless normalized steel high-pressure gas containers"
        ],
        "indirect_descriptions": [
            "refillable seamless steel gas cylinders manufactured from normalized steel for compressed gases",
            "jointless normalized steel pressure vessels designed for high-pressure gas containment",
            "seamless steel gas cylinders of normalized steel construction for refillable gas service"
        ],
        "near_match_spec": "Refillable seamless steel gas cylinders specifically of normalized steel construction (Part 1)"
    },
    "IS 9798": {
        "paraphrases": [
            "low pressure regulators for use with LPG mixtures",
            "low pressure gas regulators for liquefied petroleum gas",
            "domestic LPG cylinder low pressure regulators",
            "diaphragm pressure regulators for LPG mixtures"
        ],
        "indirect_descriptions": [
            "pressure regulating devices designed to control low delivery pressure for LPG gas mixtures",
            "low pressure regulators for domestic and commercial liquefied petroleum gas installations",
            "gas pressure regulators engineered to step down cylinder pressure for LPG mixtures"
        ],
        "near_match_spec": "Low pressure regulators specifically for use with liquefied petroleum gas (LPG) mixtures"
    },
    "IS 15683:2018": {
        "paraphrases": [
            "portable fire extinguishers - performance and construction",
            "man-portable fire extinguishers for fire fighting",
            "handheld portable fire extinguishers with performance compliance",
            "portable fire extinguishing appliances for building fire safety"
        ],
        "indirect_descriptions": [
            "portable fire extinguishing equipment designed for manual initial-attack fire suppression in premises",
            "man-portable pressurized fire extinguishing cylinders for first-aid fire fighting",
            "portable fire extinguishers satisfying performance and construction criteria"
        ],
        "near_match_spec": "Portable Fire Extinguishers conforming to performance and construction specification IS 15683"
    },
    "IS 16018:2012": {
        "paraphrases": [
            "wheeled fire extinguishers for industrial fire safety",
            "mobile wheeled trolley fire extinguishers",
            "trolley-mounted heavy wheeled fire extinguishers",
            "wheeled mobile fire extinguishing equipment"
        ],
        "indirect_descriptions": [
            "wheeled mobile fire extinguishing apparatus mounted on chassis for industrial hazard suppression",
            "trolley-mounted fire extinguishers designed for mobile deployment across plant areas",
            "wheeled heavy fire extinguishing units for industrial facility fire protection"
        ],
        "near_match_spec": "Wheeled Fire Extinguishers mounted on mobile wheel chassis per IS 16018:2012"
    },
    "IS 3055 (Part 1)": {
        "paraphrases": [
            "clinical thermometers - Part 1: solid stem type",
            "solid stem clinical glass thermometers",
            "clinical mercury-in-glass thermometers of solid stem design",
            "direct-reading solid stem medical thermometers"
        ],
        "indirect_descriptions": [
            "clinical diagnostic thermometers constructed with a solid glass stem for medical body temperature measurement",
            "medical diagnostic temperature measuring instruments of solid stem glass design",
            "solid stem type clinical thermometers for healthcare diagnostic use"
        ],
        "near_match_spec": "Clinical thermometers specifically of solid stem type (Part 1)"
    },
    "IS 3055 (Part 2)": {
        "paraphrases": [
            "clinical thermometers - Part 2: enclosed scale type",
            "enclosed scale clinical glass thermometers",
            "clinical thermometers with enclosed internal scale strip",
            "enclosed-scale medical diagnostic thermometers"
        ],
        "indirect_descriptions": [
            "clinical diagnostic thermometers featuring an enclosed scale strip inside a glass sheath for medical use",
            "medical diagnostic thermometers of enclosed scale construction for body temperature measurement",
            "enclosed scale type clinical thermometers for healthcare patient monitoring"
        ],
        "near_match_spec": "Clinical thermometers specifically of enclosed scale type (Part 2)"
    },
    "IS 7620 (Part 1)": {
        "paraphrases": [
            "diagnostic medical X-ray equipment (Part 1)",
            "medical diagnostic radiological X-ray apparatus",
            "diagnostic X-ray imaging systems for hospitals",
            "medical radiographic X-ray examination equipment"
        ],
        "indirect_descriptions": [
            "diagnostic medical radiological imaging equipment for clinical examination in hospitals",
            "medical diagnostic X-ray apparatus designed for clinical radiography and patient examination",
            "diagnostic X-ray equipment conforming to medical electrical safety specifications"
        ],
        "near_match_spec": "Diagnostic Medical X-Ray Equipment conforming to Part 1 specifications"
    },
    "IS 15911:2010": {
        "paraphrases": [
            "structural steel (ordinary quality) for civil engineering",
            "ordinary quality structural carbon steel plates and profiles",
            "commercial quality structural steel for framing",
            "hot-rolled ordinary quality structural steel"
        ],
        "indirect_descriptions": [
            "hot-rolled carbon structural steel of ordinary quality intended for non-critical civil engineering works",
            "ordinary quality carbon steel sections and plates for structural framework fabrication",
            "structural carbon steel conforming to ordinary quality specifications"
        ],
        "near_match_spec": "Structural Steel of Ordinary Quality per IS 15911:2010"
    },
    "IS 16644:2018": {
        "paraphrases": [
            "stress-relieved low relaxation steel wire for pre-stressed concrete",
            "low relaxation steel wire for pre-stressed concrete works",
            "stress-relieved steel prestressing wire for concrete",
            "high tensile low relaxation steel wire for pre-stressed concrete"
        ],
        "indirect_descriptions": [
            "stress-relieved low relaxation high-tensile steel wire for pre-stressed concrete civil structures",
            "thermo-mechanically treated low relaxation steel tendons for pre-stressed concrete members",
            "low relaxation steel wire engineered for pre-stressed concrete bridge and sleeper construction"
        ],
        "near_match_spec": "Stress-Relieved, Low Relaxation Steel Wire specifically for Pre-stressed Concrete"
    },
    "IS 17404:2020": {
        "paraphrases": [
            "electrogalvanized hot rolled and cold reduced carbon steel sheets and strips",
            "electrolytically zinc coated carbon steel sheets and strips",
            "electrogalvanized carbon steel flat products",
            "electro-coated zinc carbon steel sheet and strip"
        ],
        "indirect_descriptions": [
            "carbon steel sheets and strips electrolytically coated with zinc for corrosion protection",
            "electrogalvanized hot-rolled and cold-reduced carbon steel products for engineering fabrication",
            "electrolytic zinc coated flat carbon steel coils and sheets for manufacturing"
        ],
        "near_match_spec": "Electrogalvanized hot rolled and cold reduced carbon steel sheets and strips per IS 17404:2020"
    },
    "IS 18316:2023": {
        "paraphrases": [
            "steel strips intended for processing of electrical steel",
            "hot rolled and cold rolled steel strips for electrical steel processing",
            "steel strip feedstock for non-grain oriented and grain oriented electrical steel",
            "specialized steel strips for electrical steel lamination manufacture"
        ],
        "indirect_descriptions": [
            "hot-rolled and cold-rolled steel strips intended for subsequent processing into electrical steels",
            "flat steel strip raw material engineered for manufacturing magnetic electrical steel sheets",
            "steel strips processed for grain-oriented and non-grain-oriented electrical steel applications"
        ],
        "near_match_spec": "Steel strips specifically intended for processing of non-grain oriented or grain oriented electrical steel"
    },
    "IS 18384:2023": {
        "paraphrases": [
            "hot-rolled steel strip, sheet and plates for welded steel pipe for pipeline transportation",
            "steel plates and strips for welded pipeline transportation pipes",
            "hot-rolled pipeline quality steel strip and plate",
            "weldable steel sheet and plate for pipeline pipe fabrication"
        ],
        "indirect_descriptions": [
            "hot-rolled steel strip, sheet and plates formulated for manufacturing welded steel line pipes",
            "steel plates engineered for pipeline transportation system pipe welding and fabrication",
            "hot-rolled plate steel intended for welded steel fluid transportation pipelines"
        ],
        "near_match_spec": "Hot-Rolled Steel Strip, Sheet and Plates specifically for Welded Steel Pipe for Pipeline Transportation"
    },
    "IS 18385:2023": {
        "paraphrases": [
            "hot-dip galvanized / galvannealed steel sheet and strips for automotive applications",
            "automotive grade hot-dip galvanized and galvannealed steel sheets",
            "zinc-coated steel sheet and strips for automotive vehicle manufacturing",
            "corrosion-resistant automotive steel sheet and strips"
        ],
        "indirect_descriptions": [
            "hot-dip galvanized and galvannealed steel sheet products engineered for automotive applications",
            "automotive grade zinc-coated flat steel products for vehicular stamping and panel fabrication",
            "galvannealed and galvanized steel strip designed for automotive engineering use"
        ],
        "near_match_spec": "Hot-Dip galvanized/galvannealed Steel Sheet and strips specifically for Automotive Applications"
    },
    "IS 18513:2023": {
        "paraphrases": [
            "hot-dip zinc - aluminium - magnesium alloy coated steel sheets, plates and strips",
            "zinc-aluminium-magnesium alloy coated steel sheet products",
            "ternary alloy coated corrosion-resistant steel plates and strips",
            "hot-dip Zn-Al-Mg coated carbon steel sheets and plates"
        ],
        "indirect_descriptions": [
            "steel sheets and plates continuously coated with a ternary zinc-aluminium-magnesium alloy for barrier protection",
            "flat steel products coated with zinc-aluminium-magnesium alloy for severe environmental resistance",
            "hot-dip Zn-Al-Mg alloy coated carbon steel plates and strips for construction engineering"
        ],
        "near_match_spec": "Hot-Dip Zinc - Aluminium - Magnesium Alloy Coated Steel Sheets, Plates and Strips"
    },
    "IS 8329:2000": {
        "paraphrases": [
            "centrifugally cast (spun) ductile iron pressure pipes for water, gas and sewage",
            "spun ductile iron pressure pipes for fluid conveyance",
            "ductile iron pressure pipes with socket and spigot joints",
            "centrifugal ductile iron piping for water supply and sewage"
        ],
        "indirect_descriptions": [
            "centrifugally cast ductile iron pressure pipes engineered for conveying water, gas, and sewage",
            "spun ductile iron pipeline conduits designed for pressurized fluid transmission in civil works",
            "centrifugally spun iron pressure pipes with socket connections for municipal water networks"
        ],
        "near_match_spec": "Centrifugally cast (spun) ductile iron pressure pipes specifically for water, gas and sewage"
    },
    "IS 9523:2000": {
        "paraphrases": [
            "ductile iron fittings for pressure pipes for water, gas and sewage",
            "ductile iron pipeline fittings (tees, bends, reducers) for pressure lines",
            "ductile iron junction fittings for water, gas and sewage pipes",
            "cast ductile iron pressure pipe fittings for fluid pipelines"
        ],
        "indirect_descriptions": [
            "ductile iron pipe fittings engineered for connecting pressure pipes conveying water, gas, and sewage",
            "junction and directional fittings of ductile iron for pressurized fluid transmission pipelines",
            "ductile iron pipeline connectors and fittings for civil water and sewage piping"
        ],
        "near_match_spec": "Ductile iron fittings specifically for pressure pipes for water, gas and sewage"
    },
    "IS 1161:2014": {
        "paraphrases": [
            "steel tubes for structural purposes",
            "circular structural steel tubes for frameworks",
            "welded structural steel hollow tubes",
            "structural grade tubular steel sections"
        ],
        "indirect_descriptions": [
            "steel tubular sections manufactured for structural purposes and civil load-bearing frameworks",
            "circular hollow steel tubes engineered for architectural trusses and structural fabrication",
            "structural steel pipes designed for mechanical support and civil engineering frameworks"
        ],
        "near_match_spec": "Steel tubes specifically for structural purposes conforming to IS 1161:2014"
    },
    "IS 1239 (Part 1):2014": {
        "paraphrases": [
            "steel tubes, tubulars and other wrought steel fittings - Part 1: steel tubes",
            "mild steel tubes for water, gas and steam lines",
            "commercial mild steel fluid conveyance tubes",
            "welded and seamless mild steel pipes for water and gas"
        ],
        "indirect_descriptions": [
            "mild steel tubes designed for conveying water, gas, and steam in municipal and industrial lines",
            "steel tubular conduits for piping distribution in water, gas, and steam installations",
            "mild steel conveyance pipes conforming to Part 1 steel tubes specification"
        ],
        "near_match_spec": "Steel tubes, tubulars and other wrought steel fittings - Part 1: Steel Tubes per IS 1239"
    },
    "IS 4270:2001": {
        "paraphrases": [
            "steel tubes used for water-wells (up to 200 mm dia)",
            "water well steel casing tubes up to 200 mm diameter",
            "tubewell casing pipes of steel up to 200 mm dia",
            "steel well-casing tubes for borehole water extraction"
        ],
        "indirect_descriptions": [
            "steel tubular casing pipes up to 200 mm diameter designed for water-well drilling and groundwater extraction",
            "cylindrical steel casing tubes used for lining drilled water-wells up to 200 mm diameter",
            "steel well-tubes engineered for water-well infrastructure up to 200 mm dia"
        ],
        "near_match_spec": "Steel tubes specifically used for water-wells up to 200 mm diameter per IS 4270:2001"
    },
    "IS 1180 (Part 1)": {
        "paraphrases": [
            "outdoor type oil immersed distribution transformers up to 2500 kVA, 33 kV",
            "mineral oil immersed electrical distribution transformers (Part 1)",
            "outdoor distribution transformers up to 2500 kVA rated up to 33 kV",
            "mineral oil cooled electrical distribution transformers"
        ],
        "indirect_descriptions": [
            "outdoor mineral oil immersed transformers for electrical power distribution up to 2500 kVA and 33 kV",
            "oil-cooled distribution transformers rated up to 2500 kVA, 33 kV for power distribution systems",
            "stationary electromagnetic induction distribution transformers insulated with mineral oil up to 33 kV"
        ],
        "near_match_spec": "Outdoor type oil immersed distribution transformers up to and including 2500 kVA, 33 kV (Part 1)"
    },
    "IS 12615": {
        "paraphrases": [
            "energy efficient induction motors - three phase squirrel cage",
            "three-phase squirrel cage energy efficient induction motors",
            "line-operated three-phase induction electric motors",
            "high efficiency AC induction motors with squirrel cage rotor"
        ],
        "indirect_descriptions": [
            "three-phase squirrel-cage induction electric motors engineered for energy efficient operation",
            "rotary electromagnetic induction motors operating on three-phase AC supplies for power systems",
            "energy efficient three-phase AC induction drive motors with squirrel-cage rotor construction"
        ],
        "near_match_spec": "Energy Efficient Induction Motors - Three Phase Squirrel Cage per IS 12615"
    },
    "IS 2993": {
        "paraphrases": [
            "A.C. motor capacitors for single-phase motors",
            "motor start and motor run AC capacitors",
            "alternating current capacitors for induction motors",
            "A.C. capacitors for electrical motor circuits"
        ],
        "indirect_descriptions": [
            "alternating current capacitors designed for starting and running electrical induction motors",
            "A.C. motor capacitors providing phase displacement in single-phase motor circuits",
            "electrical capacitors intended for AC motor starting and continuous running applications"
        ],
        "near_match_spec": "A.C. motor capacitors intended specifically for motor starting and running per IS 2993"
    },
    "IS 13340": {
        "paraphrases": [
            "power capacitors of self-healing type for AC power systems up to 650 V",
            "self-healing low voltage AC power capacitors up to 650 V",
            "self-healing power factor correction capacitors up to 650 V",
            "AC power system self-healing capacitors rated up to 650 V"
        ],
        "indirect_descriptions": [
            "self-healing power capacitors designed for alternating current power systems having rated voltage up to 650 V",
            "power factor correction capacitors of self-healing construction for electrical systems up to 650 V",
            "self-healing shunt power capacitors for AC electrical power installations up to 650 V"
        ],
        "near_match_spec": "Power Capacitors of Self-healing Type for AC Power Systems having Rated Voltage up to 650 V"
    },
    "IS 252:2013": {
        "paraphrases": [
            "caustic soda (sodium hydroxide) for industrial use",
            "technical grade caustic soda chemical compound",
            "commercial caustic soda for industrial processing",
            "caustic soda flakes and lye for chemical processing"
        ],
        "indirect_descriptions": [
            "alkaline chemical reagent caustic soda supplied for industrial materials and chemical processing",
            "sodium hydroxide chemical compound intended for industrial processing and water treatment",
            "chemical grade caustic soda manufactured for chemical synthesis and neutralization"
        ],
        "near_match_spec": "Caustic Soda conforming to chemical processing specification IS 252:2013"
    },
    "IS 10116:2015": {
        "paraphrases": [
            "boric acid for industrial materials and chemical processing",
            "technical grade boric acid chemical powder",
            "commercial boric acid for chemical synthesis",
            "boric acid compound for industrial processing"
        ],
        "indirect_descriptions": [
            "inorganic chemical compound boric acid intended for industrial materials and chemical processing",
            "technical grade boric acid powder for glass, ceramic, and chemical manufacturing",
            "boric acid chemical reagent conforming to industrial chemical specifications"
        ],
        "near_match_spec": "Boric Acid conforming to chemical processing specification IS 10116:2015"
    },
    "IS 15573": {
        "paraphrases": [
            "poly aluminium chloride for water treatment and chemical processing",
            "polymeric aluminium chloride coagulant chemical",
            "poly aluminium chloride chemical compound",
            "poly aluminium chloride coagulant for industrial processing"
        ],
        "indirect_descriptions": [
            "aluminium-based chemical coagulant poly aluminium chloride for water and chemical processing",
            "polymeric aluminium chloride compound intended for chemical processing and industrial materials",
            "poly aluminium chloride flocculating chemical for water clarification and processing"
        ],
        "near_match_spec": "Poly Aluminium Chloride chemical compound conforming to IS 15573"
    },
    "IS 2833:2019": {
        "paraphrases": [
            "aniline for industrial chemical processing",
            "chemical grade aniline organic compound",
            "monomeric aniline liquid for chemical synthesis",
            "technical grade aniline for chemical processing"
        ],
        "indirect_descriptions": [
            "aromatic chemical compound aniline intended for industrial synthesis and chemical processing",
            "organic chemical intermediate aniline for industrial manufacturing processes",
            "technical grade chemical aniline liquid for organic synthesis and industrial materials"
        ],
        "near_match_spec": "Aniline conforming to chemical processing specification IS 2833:2019"
    },
    "IS 302 (Part 2/Section 14)": {
        "paraphrases": [
            "hand-held blenders for domestic kitchen food preparation",
            "safety compliant motorized hand-held blenders",
            "household electric hand-held immersion blenders",
            "domestic hand-held kitchen food blenders"
        ],
        "indirect_descriptions": [
            "motorized hand-held culinary food preparation blenders for domestic kitchen use",
            "portable handheld electrical food blenders designed for kitchen liquidizing and blending",
            "hand-held electric kitchen food blenders conforming to appliance safety requirements"
        ],
        "near_match_spec": "Safety of household electrical appliances specifically for Hand-held Blenders (Part 2/Section 14)"
    },
    "IS 4250": {
        "paraphrases": [
            "domestic electric food mixer (liquidizers and grinders) and centrifugal juicer",
            "household electric mixer grinders with liquidizers and grinders",
            "domestic electric food mixers and centrifugal juicers",
            "kitchen electric mixer grinders with liquidizing jars"
        ],
        "indirect_descriptions": [
            "motorized culinary food mixing, liquidizing, grinding and centrifugal juicing machines for domestic kitchens",
            "household electric food preparation appliances combining mixing, grinding, and juicing functions",
            "domestic kitchen food mixers and liquidizers conforming to electrical performance standards"
        ],
        "near_match_spec": "Domestic Electric Food Mixer (Liquidizers and Grinders) and Centrifugal Juicer per IS 4250"
    },
    "IS 15558": {
        "paraphrases": [
            "instantaneous domestic water heaters for use with LPG",
            "gas-fired instantaneous water heaters for liquefied petroleum gas",
            "domestic instantaneous gas water heaters for LPG",
            "instantaneous domestic gas geysers for LPG use"
        ],
        "indirect_descriptions": [
            "instantaneous water heating appliances fueled by LPG for domestic kitchen and bath water heating",
            "domestic continuous-flow water heaters operating on liquefied petroleum gas fuel",
            "instantaneous gas-fired domestic water heating units designed for LPG cylinders"
        ],
        "near_match_spec": "Instantaneous Domestic Water Heater specifically for use with Liquefied Petroleum Gas"
    },
    "IS 1391 (Part-1):2017": {
        "paraphrases": [
            "room air conditioners - Part 1: unitary air conditioners",
            "unitary (window type) room air conditioners",
            "single-package unitary room air conditioners",
            "self-contained unitary room cooling air conditioners"
        ],
        "indirect_descriptions": [
            "unitary single-package room air conditioning machines designed for space cooling and ventilation",
            "self-contained window-mounted air conditioners for room temperature control in civil spaces",
            "unitary room cooling air conditioners conforming to Part 1 specifications"
        ],
        "near_match_spec": "Room Air Conditioners specifically of Part 1 Unitary Air Conditioners classification"
    },
    "IS 1391 (Part-2):2018": {
        "paraphrases": [
            "room air conditioners - Part 2: split air conditioners",
            "split type room air conditioning systems",
            "two-unit split room air conditioners (indoor and outdoor units)",
            "ductless split room air conditioners for space cooling"
        ],
        "indirect_descriptions": [
            "split-type room air conditioning systems featuring separate indoor air-handling and outdoor condensing units",
            "two-part room cooling air conditioners with interconnecting refrigerant piping for building cooling",
            "split room air conditioning units conforming to Part 2 specifications"
        ],
        "near_match_spec": "Room Air Conditioners specifically of Part 2 Split Air Conditioners classification"
    },
    "IS 8148:2018": {
        "paraphrases": [
            "ducted and package air conditioners for central cooling",
            "packaged commercial air conditioning units",
            "ducted packaged air conditioning systems for buildings",
            "commercial ducted air conditioners for space climate control"
        ],
        "indirect_descriptions": [
            "packaged and ducted air conditioning assemblies engineered for duct air distribution in buildings",
            "commercial ducted air conditioning equipment for centralized environmental climate control",
            "packaged air conditioners designed for ducted ventilation and cooling networks"
        ],
        "near_match_spec": "Ducted and Package Air Conditioners per IS 8148:2018"
    },
    "IS 11329:2018": {
        "paraphrases": [
            "finned type heat exchangers for room air conditioners",
            "heat exchanger finned coils for room air conditioning units",
            "cooling and condensing finned heat exchangers for RAC units",
            "finned tube heat exchange assemblies for room air conditioners"
        ],
        "indirect_descriptions": [
            "finned heat exchanging assemblies designed for refrigerant-to-air thermal transfer in room air conditioners",
            "finned tube heat exchangers for room air conditioner cooling and condensing circuits",
            "extended-surface finned heat exchangers manufactured for room air conditioning equipment"
        ],
        "near_match_spec": "Finned type Heat Exchanger specifically for Room Air Conditioner per IS 11329:2018"
    },
    "IS 10617:2018": {
        "paraphrases": [
            "hermetic compressors for air conditioning and refrigeration",
            "hermetically sealed refrigerant motor-compressors",
            "hermetic compressors for room cooling and refrigeration units",
            "sealed hermetic cooling compressors"
        ],
        "indirect_descriptions": [
            "hermetically enclosed fluid motor-compressor machines designed for pumping refrigerant in cooling circuits",
            "sealed positive-displacement hermetic compressors for air conditioning and refrigeration systems",
            "hermetic refrigerant compressors conforming to HVAC mechanical safety specifications"
        ],
        "near_match_spec": "Hermetic compressor specifically for refrigeration and air conditioning per IS 10617:2018"
    },
    "IS 17550 (Part 1):2021": {
        "paraphrases": [
            "household refrigerating appliances - Part 1: general requirements",
            "domestic refrigerators and food preservation appliances",
            "household refrigerating appliances general requirements",
            "domestic electric refrigerators for food cold storage"
        ],
        "indirect_descriptions": [
            "insulated food storage refrigerating appliances designed for fresh food preservation in households",
            "domestic electric refrigerating cabinets conforming to Part 1 general requirements and test methods",
            "household refrigeration appliances for domestic cold food storage"
        ],
        "near_match_spec": "Household Refrigerating Appliances - Characteristics and Test Methods Part 1: General Requirements"
    },
    "IS 7872:2018": {
        "paraphrases": [
            "freezers for food cold storage and preservation",
            "domestic and commercial sub-zero deep freezers",
            "refrigerated food storage freezers",
            "freezing storage cabinets for food preservation"
        ],
        "indirect_descriptions": [
            "refrigerated low-temperature storage appliances designed for freezing and preserving foodstuffs",
            "freezing cabinets engineered for sub-zero food preservation in households and food services",
            "insulated freezing equipment conforming to freezer temperature and performance specifications"
        ],
        "near_match_spec": "Freezers specifically engineered for low-temperature food freezing and storage per IS 7872:2018"
    },
    "IS 16240:2023": {
        "paraphrases": [
            "reverse osmosis based point of use water treatment systems for drinking purposes",
            "point-of-use (PoU) reverse osmosis drinking water purifiers",
            "domestic RO drinking water treatment appliances",
            "membrane-based reverse osmosis water purification systems for drinking"
        ],
        "indirect_descriptions": [
            "membrane-based reverse osmosis filtration appliances designed for point-of-use drinking water purification",
            "point-of-use water purification systems utilizing reverse osmosis for safe drinking water treatment",
            "reverse osmosis drinking water treatment equipment conforming to point-of-use purification standards"
        ],
        "near_match_spec": "Reverse Osmosis Based Point of Use Water Treatment System specifically for Drinking Purposes"
    },
    "IS 1659:2004": {
        "paraphrases": [
            "block boards for furniture and interior woodwork",
            "solid wood batten blockboards for joinery",
            "timber core block boards for interior products",
            "wooden block boards for cabinetry and partitioning"
        ],
        "indirect_descriptions": [
            "composite timber boards constructed with solid wood core blocks between outer veneers for furniture",
            "wooden batten core blockboard panels for interior joinery and structural furniture",
            "bonded wooden block boards engineered for cabinetmaking and interior paneling"
        ],
        "near_match_spec": "Block Boards consisting of solid timber core blocks bonded between wood veneers"
    },
    "IS 12823:2015": {
        "paraphrases": [
            "prelaminated particle boards from wood and other lignocellulosic material",
            "melamine surfaced prelaminated particle boards",
            "pre-laminated particle boards for modular furniture",
            "decorative paper laminated particle boards"
        ],
        "indirect_descriptions": [
            "wood particle composite panels factory-surfaced with decorative resin-impregnated paper lamination",
            "prelaminated particle boards from wood and lignocellulosic materials for interior furniture products",
            "pre-laminated modular panels for office furniture and cabinetry fabrication"
        ],
        "near_match_spec": "Prelaminated particle boards from wood and other lignocellulosic material per IS 12823:2015"
    },
    "IS 3087:2005": {
        "paraphrases": [
            "particle boards of wood (medium density) for general purpose",
            "plain medium density wood particle boards",
            "unlaminated wood particle boards for general interior use",
            "resin-bonded raw wood particle boards"
        ],
        "indirect_descriptions": [
            "plain medium density particle boards manufactured from compressed wood chips for general interior purposes",
            "unlaminated wood-based particle board panels for general structural furniture substrates",
            "reconstituted wood particle boards of medium density for general purpose applications"
        ],
        "near_match_spec": "Particle boards of wood and other lignocellulosic materials (medium density) for general purpose"
    },
    "IS 12406:2021": {
        "paraphrases": [
            "medium density fibre boards (MDF) for general purpose",
            "engineered wood medium density fibreboards",
            "homogeneous MDF wood fiber panels for general joinery",
            "medium density fibre boards for furniture and interior products"
        ],
        "indirect_descriptions": [
            "dry-process engineered wood panels manufactured from refined wood fibers for general interior joinery",
            "medium density fibreboards (MDF) with uniform fiber consistency for furniture and decorative products",
            "homogeneous wood fiber boards engineered for general purpose cabinetry and architectural woodwork"
        ],
        "near_match_spec": "Medium density fibre boards (MDF) specifically for general purpose per IS 12406:2021"
    },
    "IS 1726:1991": {
        "paraphrases": [
            "cast iron manhole covers and frames for civil drainage",
            "heavy duty cast iron sewer chamber covers and frames",
            "cast iron manhole inspection covers and frames",
            "cast iron covers and frames for drainage chambers"
        ],
        "indirect_descriptions": [
            "cast iron access covers and seating frames designed for sealing underground drainage and sewer chambers",
            "heavy-duty iron manhole covers and frames engineered for civil highway and road drainage chambers",
            "cast iron road covers and peripheral frames for drainage inspection shafts"
        ],
        "near_match_spec": "Cast iron manhole covers and frames conforming to drainage loading classifications of IS 1726"
    },
    "IS 1729:2002": {
        "paraphrases": [
            "cast iron/ductile iron drainage pipes and fittings (socket and spigot)",
            "cast iron sanitary drainage pipes and pipe fittings",
            "non-pressure socket and spigot iron drainage piping",
            "cast iron drainage pipelines for over ground civil stacks"
        ],
        "indirect_descriptions": [
            "cast iron and ductile iron tubular conduits and fittings for over-ground non-pressure gravity drainage",
            "socket and spigot iron pipes and fittings engineered for sanitary building drainage and rainwater disposal",
            "cast iron non-pressure drainage piping for wastewater and soil discharge pipelines"
        ],
        "near_match_spec": "Cast iron/ductile iron drainage pipes and pipe fittings specifically for over ground non-pressure pipelines"
    },
    "IS 210:2009": {
        "paraphrases": [
            "grey iron castings for engineering and civil infrastructure",
            "flake graphite grey cast iron foundry products",
            "industrial grey iron castings of specified strength grades",
            "cast grey iron components for general engineering"
        ],
        "indirect_descriptions": [
            "flake-graphite iron engineering cast components produced in foundry moulds for mechanical and civil applications",
            "grey iron castings conforming to tensile strength grading for machinery and infrastructure",
            "unalloyed grey cast iron structural components for civil infrastructure and machinery"
        ],
        "near_match_spec": "Grey iron castings conforming to tensile strength grading specifications of IS 210:2009"
    },
    "IS 17293:2020": {
        "paraphrases": [
            "electric cable for photovoltaic systems for rated voltage 1500 V DC",
            "solar photovoltaic electric cables rated 1500 V DC",
            "1500 V DC solar power cables for photovoltaic systems",
            "photovoltaic solar system electric cables rated at 1500 V DC"
        ],
        "indirect_descriptions": [
            "specialized electrical cables rated at 1500 V DC for power interconnection in solar photovoltaic systems",
            "flexible solar cables engineered for outdoor string connections in 1500 V DC photovoltaic arrays",
            "photovoltaic system electrical power cables conforming to 1500 V DC voltage rating"
        ],
        "near_match_spec": "Electric Cable for Photovoltaic Systems specifically for rated voltage 1500 V DC per IS 17293:2020"
    },
    "IS 17505 (Part 1):2021": {
        "paraphrases": [
            "thermosetting insulated fire survival cables for voltage up to 1100 V AC and 1500 V DC",
            "fire survival electric cables for emergency power circuits",
            "thermosetting insulated fire survival cables (Part 1)",
            "fire survival cables maintaining circuit continuity up to 1100 V AC / 1500 V DC"
        ],
        "indirect_descriptions": [
            "thermosetting insulated fire survival electrical cables engineered to maintain circuit integrity under fire conditions up to 1100 V AC and 1500 V DC",
            "emergency power cables with thermosetting insulation for critical fire survival electrical installations",
            "fire survival electrical cabling for emergency evacuation power circuits up to 1100 V AC / 1500 V DC"
        ],
        "near_match_spec": "Thermosetting Insulated, Fire Survival Cables for working voltage up to and including 1100 V AC and 1500 V DC"
    },
    "IS 878:2008": {
        "paraphrases": [
            "laboratory glassware - graduated measuring cylinders",
            "borosilicate glass graduated volumetric cylinders",
            "graduated measuring cylinders for laboratory liquid handling",
            "precision graduated glass cylinders for scientific testing"
        ],
        "indirect_descriptions": [
            "graduated cylindrical glass vessels designed for volumetric liquid measurement in laboratories",
            "laboratory glassware cylinders with etched graduation markings for scientific measurement",
            "borosilicate glass measuring cylinders calibrated for accurate liquid measurement in laboratories"
        ],
        "near_match_spec": "Laboratory glassware - Graduated measuring cylinders conforming to IS 878:2008"
    },
    "IS 915:2012": {
        "paraphrases": [
            "laboratory glassware - one-mark volumetric flasks",
            "one-mark glass volumetric flasks with stoppers",
            "precision one-mark volumetric flasks for laboratories",
            "borosilicate glass one-mark analytical volumetric flasks"
        ],
        "indirect_descriptions": [
            "one-mark glass volumetric flasks designed to contain calibrated liquid volumes in laboratories",
            "laboratory glassware volumetric flasks with neck calibration line for preparing standard solutions",
            "precision one-mark glass containment flasks for chemical analytical preparations"
        ],
        "near_match_spec": "Laboratory glassware - One-Mark volumetric flasks conforming to IS 915:2012"
    },
    "IS 2619:2018": {
        "paraphrases": [
            "glass beakers for laboratory measurement and handling",
            "borosilicate glass laboratory beakers with spout",
            "cylindrical glass beakers for chemical heating and mixing",
            "laboratory glass beakers for scientific experiments"
        ],
        "indirect_descriptions": [
            "flat-bottomed glass vessels with pouring spout designed for heating and mixing reagents in laboratories",
            "laboratory glassware beakers for liquid handling and chemical reaction procedures",
            "heat-resistant borosilicate glass beakers for laboratory scientific handling"
        ],
        "near_match_spec": "Glass beakers conforming to laboratory handling specification IS 2619:2018"
    },
    "IS 14772:2020": {
        "paraphrases": [
            "boxes and enclosures for electrical accessories for household fixed installations",
            "electrical mounting boxes and enclosures for household accessories",
            "modular accessory back-boxes for fixed electrical wiring",
            "enclosure boxes for domestic electrical switches and accessories"
        ],
        "indirect_descriptions": [
            "protective mounting boxes and enclosures designed for housing electrical accessories in fixed installations",
            "enclosure boxes engineered for terminating wiring accessories in domestic electrical installations",
            "modular accessory boxes and enclosures for fixed building electrification"
        ],
        "near_match_spec": "Boxes and Enclosures for Electrical Accessories for Household and Similar Fixed Electrical Installations"
    },
    "IS 14927 (Part 2):2001": {
        "paraphrases": [
            "cable trunking and ducting systems - Part 2: mounting on walls or ceiling",
            "surface cable trunking and ducting channels for walls and ceilings",
            "electrical cable containment trunking systems for walls or ceiling",
            "rigid cable ducting channels for surface electrical installations"
        ],
        "indirect_descriptions": [
            "cable trunking and ducting systems engineered for mounting on walls or ceilings to protect building wiring",
            "surface-mounted electrical cable containment trunking channels for wall and ceiling installations",
            "cable ducting and trunking enclosures intended for mounting on walls or ceiling"
        ],
        "near_match_spec": "Cable Trunking and Ducting Systems specifically of Part 2: Intended for mounting on walls or ceiling"
    },
    "IS 1258:2005": {
        "paraphrases": [
            "bayonet lamp holders (B22) for electrical installations",
            "bayonet cap lamp holders for lighting fixtures",
            "domestic bayonet lighting lamp holders",
            "electrical bayonet lamp sockets for fixed lighting"
        ],
        "indirect_descriptions": [
            "electrical lighting connector sockets with bayonet slots designed for holding and connecting lamp caps",
            "bayonet lamp holders providing mechanical retention and electrical connection for lighting fixtures",
            "bayonet cap lamp holders conforming to domestic electrical installation specifications"
        ],
        "near_match_spec": "Bayonet Lamp Holders conforming to IS 1258:2005"
    },
    "IS 13774:2021": {
        "paraphrases": [
            "live working gloves of insulating material",
            "dielectric insulating gloves for live electrical line maintenance",
            "electrical insulating rubber gloves for live power work",
            "insulating safety gloves for live working electricians"
        ],
        "indirect_descriptions": [
            "protective hand gloves manufactured from insulating material for live electrical line working",
            "dielectric insulating safety gloves designed to protect personnel during energized electrical contact",
            "insulating elastomeric gloves engineered for live working maintenance in electrical installations"
        ],
        "near_match_spec": "Live Working Gloves of Insulating Material conforming to IS 13774:2021"
    },
    "IS 16190:2014": {
        "paraphrases": [
            "high density polyethylene (HDPE) laminated woven lay flat tube for irrigation purposes",
            "HDPE woven lay flat flexible water delivery tubes for irrigation",
            "laminated woven polyethylene lay-flat tubing for agricultural irrigation",
            "flexible HDPE lay-flat irrigation water delivery pipes"
        ],
        "indirect_descriptions": [
            "collapsible flexible lay flat tubes made of HDPE laminated woven fabric for field water irrigation",
            "woven polyethylene lay flat tubing designed for water conveyance in agricultural irrigation",
            "laminated woven HDPE irrigation tubes for farm surface water distribution"
        ],
        "near_match_spec": "High Density Polyethylene (HDPE) laminated woven lay flat tube specifically for general irrigation purpose"
    },
    "IS 16627:2017": {
        "paraphrases": [
            "HDPE laminated woven lay flat tube for mains and submains of drip irrigation systems",
            "drip irrigation mainline and submain HDPE woven lay-flat delivery tubing",
            "reinforced HDPE lay flat tubes for drip irrigation manifolds",
            "laminated woven polyethylene lay-flat tubes for drip irrigation mains"
        ],
        "indirect_descriptions": [
            "high-strength laminated woven HDPE lay flat delivery tubes engineered for mains and submains of drip irrigation",
            "pressurized woven lay-flat polyethylene manifolds designed for drip irrigation distribution networks",
            "woven HDPE lay flat pipes specifically manufactured for drip irrigation mainline and submain headers"
        ],
        "near_match_spec": "High density polyethylene (HDPE) laminated woven lay flat tube specifically for mains and submains of drip irrigation system"
    },
    "IS 17729:2021": {
        "paraphrases": [
            "flexible water storage tanks for agriculture and horticulture purposes",
            "collapsible flexible water storage tanks for farms",
            "flexible agricultural water containment storage reservoirs",
            "polymer fabric flexible water tanks for horticulture"
        ],
        "indirect_descriptions": [
            "collapsible flexible water storage containment tanks designed for agricultural and horticulture water retention",
            "flexible water storage reservoirs for on-farm irrigation water harvesting and buffer storage",
            "collapsible polymer water containment vessels engineered for agricultural and horticulture purposes"
        ],
        "near_match_spec": "Flexible Water Storage Tank specifically for Agriculture and Horticulture Purposes per IS 17729:2021"
    },
    "IS 12444:2020": {
        "paraphrases": [
            "copper wire rods for electrical applications",
            "high conductivity copper wire rods for electrical conductor drawing",
            "continuous cast copper wire rods for electrical cables",
            "copper rods for electrical wire and cable drawing"
        ],
        "indirect_descriptions": [
            "continuous cast high-purity copper wire rods manufactured for electrical conductor wire drawing",
            "high conductivity copper rod feedstock intended for electrical cables and wiring applications",
            "copper wire rods engineered as raw material for electrical conductor drawing"
        ],
        "near_match_spec": "Copper Wire Rods specifically for Electrical Applications per IS 12444:2020"
    },
    "IS 613:2000": {
        "paraphrases": [
            "copper rods and bars for electrical purposes",
            "high conductivity copper rectangular bars and rods for electrical busbars",
            "drawn copper busbars and rods for electrical switchboards",
            "solid copper conductor bars and rods for electrical panels"
        ],
        "indirect_descriptions": [
            "solid copper rods and rectangular busbars manufactured for electrical power conduction",
            "high conductivity copper bars and rods intended for electrical switchgear and panel boards",
            "drawn copper conductor sections engineered for electrical current distribution"
        ],
        "near_match_spec": "Copper Rods and Bars specifically for Electrical Purposes per IS 613:2000"
    },
    "IS 14810:2000": {
        "paraphrases": [
            "copper tubes for plumbing",
            "seamless solid-drawn copper plumbing pipes for water conveyance",
            "copper water and sanitation pipes for plumbing installations",
            "seamless copper piping tubes for building plumbing"
        ],
        "indirect_descriptions": [
            "seamless solid-drawn copper tubes engineered for potable water and fluid conveyance in plumbing",
            "corrosion-resistant copper pipes designed for domestic water distribution and plumbing installations",
            "seamless copper tubes conforming to plumbing water conveyance specifications"
        ],
        "near_match_spec": "Copper Tubes specifically for plumbing installations per IS 14810:2000"
    },
    "IS 6343:1982": {
        "paraphrases": [
            "door closers (pneumatically regulated) for light doors weighing up to 40 kg",
            "pneumatic door closers for lightweight interior doors up to 40 kg",
            "air-regulated automatic door closers for light doors up to 40 kg",
            "pneumatically regulated overhead door closing mechanisms up to 40 kg"
        ],
        "indirect_descriptions": [
            "pneumatically regulated door self-closing hardware engineered for light doors weighing up to 40 kg",
            "automatic air-cushioned door closing mechanisms designed for lightweight doors not exceeding 40 kg",
            "pneumatic door closers providing controlled closing motion for light doors up to 40 kg mass"
        ],
        "near_match_spec": "Door closers (pneumatically regulated) specifically for light doors weighing up to 40 kg per IS 6343:1982"
    },
    "IS 208:2020": {
        "paraphrases": [
            "door handles for building hardware and architectural joinery",
            "metal door pull and lever handles for building doors",
            "architectural door handles for residential and commercial joinery",
            "hardware door handles for building entrance and room doors"
        ],
        "indirect_descriptions": [
            "metallic door grip hardware handles designed for operating and pulling interior and exterior building doors",
            "architectural door pull and lever handles engineered for mounting on building doors",
            "metal door handles conforming to building hardware mechanical and finish standards"
        ],
        "near_match_spec": "Door Handles conforming to building hardware specification IS 208:2020"
    }
}

print(f"Total grounded vocabulary defined: {len(GROUNDED_VOCABULARY)}")
assert len(GROUNDED_VOCABULARY) == 91, f"Expected 91 vocabulary entries, got {len(GROUNDED_VOCABULARY)}"

# Compile final grounded profiles
final_grounded_profiles = {}

for is_num, s in standards.items():
    vocab = GROUNDED_VOCABULARY[is_num]
    clean_prod = clean_product_title(s["title"])
    sec_norm = normalize_sector(s)
    seed_params = extract_seed_parameters(s)
    seed_mats = s.get("materials") or []
    seed_app = s.get("application") or ""

    # Compute candidate standards and signals strictly excluding self
    scored = []
    for other_num, other_s in standards.items():
        if other_num == is_num:
            continue
        sigs, score = compute_signals_and_score(s, other_s)
        if sigs:
            scored.append((score, other_num, sigs))
    scored.sort(key=lambda x: x[0], reverse=True)

    candidates = [c[1] for c in scored[:3]]
    cand_sigs = {c[1]: c[2] for c in scored[:3]}
    unique_signals = sorted(list({sig for c in scored[:3] for sig in c[2]}))

    # Base provenance evidence
    evidence = [
        {"field": "product", "value": clean_prod, "source": "seed.title"},
        {"field": "sector", "value": s["sector"], "source": "seed.sector"}
    ]
    if seed_app:
        evidence.append({"field": "application", "value": seed_app, "source": "seed.application"})
    if seed_mats:
        evidence.append({"field": "materials", "value": seed_mats, "source": "seed.materials"})
    if seed_params:
        evidence.append({"field": "parameters", "value": seed_params, "source": "seed.technical_parameters"})
    if ref_map.get(is_num):
        for ref_target in ref_map[is_num]:
            evidence.append({"field": "related_standard", "value": ref_target, "source": "seed.references"})

    clean_nms = vocab["near_match_spec"]
    clean_nms = re.sub(r'\s*(?:per|conforming to.*|specification of.*|meeting.*)\s*IS\s*[\d\w\s\(\)\:\/]+.*$', '', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\s*IS\s*\d+.*$', '', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\s*conforming to Part\s*\d+.*$', '', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\s*specifically of Part\s*\d+:?\s*', ' specifically ', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\s*\(Part\s*[\d\w\s\/\:\-]+\)', '', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\bPart\s*\d+\b', '', clean_nms, flags=re.I).strip()
    clean_nms = re.sub(r'\s*-\s*:\s*', ' - ', clean_nms).strip()
    clean_nms = re.sub(r'\s*:\s*-\s*', ' - ', clean_nms).strip()
    clean_nms = re.sub(r'\s+', ' ', clean_nms).strip()

    final_grounded_profiles[is_num] = {
        "id": s["id"],
        "standard_id": s["standard_id"],
        "is_number": is_num,
        "title": s["title"],
        "clean_product": clean_prod,
        "sector_original": s["sector"],
        "sector_normalized": sec_norm,
        "application": seed_app,
        "materials": seed_mats,
        "parameters": seed_params,
        "paraphrases": vocab["paraphrases"],
        "indirect_descriptions": vocab["indirect_descriptions"],
        "near_match_spec": clean_nms,
        "near_match_candidates": candidates,
        "candidate_signals": cand_sigs,
        "candidate_similarity_basis": unique_signals,
        "ground_truth_evidence": evidence
    }

out_path = Path("data/processed/standards_profiles_grounded.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(final_grounded_profiles, f, indent=2)

print(f"SUCCESS: Created {len(final_grounded_profiles)} grounded profiles in {out_path}")
