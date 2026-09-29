"""
backend/extraction/patterns.py

Regular expression patterns, lexical dictionaries, and markers for
deterministic and pattern-based requirement extraction (Stage 1 & 2).
"""

import re
from typing import Dict, List, Pattern, Any

# 1. Cited Standards (IS Numbers)
# Matches IS numbers like "IS 4151", "IS 1239 (Part 1):2014", "IS 302 : Part 1 (2024)", "Indian Standard 269"
CITED_STANDARD_PATTERN: Pattern = re.compile(
    r"\b(?:IS|Indian\s+Standard)\s*(\d{2,5}(?:\s*(?:\([^\)]+\)|:\s*\d{4}|Part\s*[\d\w\s\/\:\-]+))*)\b",
    re.IGNORECASE
)

# 2. Technical Parameter Patterns
# Specific regexes capturing name, value, unit, and textual evidence
PARAMETER_PATTERNS: List[Dict[str, Any]] = [
    # Electrical Power / Capacity (kVA, MVA, kW, MW, HP, W)
    {
        "category": "power_rating",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>maximum\s+power\s+rating|rated\s+power|power\s+capacity|power)?\s*(?:having\s+)?(?P<val>(?:up\s+to\s+and\s+including|up\s+to)?\s*\d+(?:\.\d+)?)\s*(?P<unit>kVA|MVA|kW|MW|HP|W|watts?|kilowatts?)\b)",
            re.IGNORECASE
        ),
        "default_unit": "kW",
    },
    # Voltage (kV, V, volts, kilovolts, AC/DC)
    {
        "category": "voltage",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>rated\s+voltage|working\s+voltage|maximum\s+voltage\s+rating|voltage)?\s*(?:having\s+)?(?P<val>(?:up\s+to\s+and\s+including|up\s+to|between\s+\d+\s+and)?\s*\d+(?:\.\d+)?)\s*(?P<unit>kV|V|volts?|kilovolts?)\b(?:\s*(?P<spec>AC|DC))?(?:\s*and\s*(?P<sec_val>\d+(?:\.\d+)?)\s*(?P<sec_unit>kV|V)\b(?:\s*(?P<sec_spec>AC|DC))?)?)",
            re.IGNORECASE
        ),
        "default_unit": "V",
    },
    # Current (kA, mA, A, amperes)
    {
        "category": "current",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>rated\s+current|operating\s+current|current)?\s*(?:having\s+)?(?P<val>(?:up\s+to\s+and\s+including|up\s+to)?\s*\d+(?:\.\d+)?)\s*(?P<unit>\b(?:kA|mA|A|amperes?|milliamperes?)\b))",
            re.IGNORECASE
        ),
        "default_unit": "A",
    },
    # Weight / Mass / Load (kg, g, tonnes, kN, Joules)
    {
        "category": "weight_capacity",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>door\s+weight\s+limit|minimum\s+load\s+capacity|load\s+capacity|weighing|weight|load|mass)?\s*(?:having\s+)?(?P<val>(?:up\s+to\s+and\s+including|up\s+to|minimum\s+of)?\s*\d+(?:\.\d+)?)\s*(?P<unit>\b(?:kg|g|tonnes?|kN|Joules?|J)\b))",
            re.IGNORECASE
        ),
        "default_unit": "kg",
    },
    # Volume / Fluid Capacity (litres, ml, m3)
    {
        "category": "capacity",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>capacity\s+threshold|water\s+capacity|storage\s+capacity|capacity)?\s*(?:having\s+)?(?P<val>(?:exceeding|up\s+to\s+and\s+including|up\s+to|minimum\s+of)?\s*\d+(?:\.\d+)?)\s*(?P<unit>\b(?:litres?|liters?|L|ml|cubic\s+meters?|m3)\b)(?:\s*(?P<suffix>water\s+capacity|capacity))?)",
            re.IGNORECASE
        ),
        "default_unit": "L",
    },
    # Dimensions (Diameter, Length, Width, Thickness in mm, cm, m, inches)
    {
        "category": "dimension",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>diameter|dia|thickness|length|width|height|dimensions?|outer\s+diameter|bore)?\s*(?:having\s+)?(?P<val>(?:up\s+to\s+and\s+including|up\s+to|minimum\s+of)?\s*\d+(?:\.\d+)?)\s*(?P<unit>mm|cm|m|meters?|inches?)(?:\s*(?P<suffix>dia|diameter))?)",
            re.IGNORECASE
        ),
        "default_unit": "mm",
    },
    # Frequency (Hz, kHz, MHz)
    {
        "category": "frequency",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>frequency|operating\s+frequency)?\s*(?:having\s+)?(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>Hz|kHz|MHz))",
            re.IGNORECASE
        ),
        "default_unit": "Hz",
    },
    # Pressure (bar, psi, kPa, MPa, kg/cm2)
    {
        "category": "pressure",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>pressure|operating\s+pressure|test\s+pressure)?\s*(?:having\s+)?(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>bar|psi|kPa|MPa|kg/cm2))",
            re.IGNORECASE
        ),
        "default_unit": "bar",
    },
    # Temperature (°C, deg C)
    {
        "category": "temperature",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>temperature|operating\s+temperature)?\s*(?:having\s+)?(?P<val>-?\d+(?:\.\d+)?)\s*(?P<unit>°C|deg\s*C|degrees?\s*Celsius))",
            re.IGNORECASE
        ),
        "default_unit": "°C",
    },
    # Percentage (%)
    {
        "category": "percentage",
        "pattern": re.compile(
            r"(?P<evidence>(?P<prefix>concentration|purity|percentage|content)?\s*(?:having\s+)?(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>%))",
            re.IGNORECASE
        ),
        "default_unit": "%",
    }
]

# 3. Explicit Materials Lexicon
# Materials supported by engineering standards and seed dataset
MATERIAL_LEXICON: List[str] = [
    # Multi-word materials first (for greedy regex matching)
    "cast iron",
    "grey iron",
    "carbon steel",
    "structural steel",
    "particle board",
    "poly aluminium chloride",
    "polyethylene",
    # Single-word materials
    "cement",
    "clinker",
    "slag",
    "gypsum",
    "steel",
    "carbon",
    "iron",
    "copper",
    "pvc",
    "hdpe",
    "glass",
    "aluminium",
    "aluminum",
    "lpg",
    "brass",
    "bronze",
    "zinc",
    "lead",
    "tin",
    "clay",
    "rubber",
    "wood",
    "mdf",
    "polymer",
    "silicon",
    "polyurethane",
    "leather",
    "textile",
    "ceramic",
]

# 4. Procurement Framing Prefixes (sorted by specificity/length descending)
PROCUREMENT_PREFIXES: List[str] = [
    r"Notice\s+Inviting\s+Tender\s+for\s+(?:the\s+)?supply\s+and\s+inspection\s+of",
    r"Notice\s+Inviting\s+Tender\s+for\s+specialized\s+supply\s+of",
    r"Notice\s+Inviting\s+Tender\s+for\s+(?:the\s+)?supply\s+and\s+commissioning\s+of",
    r"Notice\s+Inviting\s+Tender\s+for\s+supply\s+(?:and\s+inspection\s+)?of",
    r"Notice\s+Inviting\s+Tender\s+for\s+procurement\s+of",
    r"Notice\s+Inviting\s+Tender\s+for\s+delivery\s+of",
    r"Notice\s+Inviting\s+Tender\s+for",
    r"Notice\s+Inviting\s+Bids\s+for\s+(?:the\s+)?delivery\s+of",
    r"Notice\s+Inviting\s+Bids\s+for",
    r"Requisition\s+for\s+procurement\s+conforming\s+specifically\s+to",
    r"Requisition\s+for\s+the\s+supply\s+and\s+delivery\s+of",
    r"Requisition\s+for\s+supply\s+and\s+commissioning\s+of",
    r"Requisition\s+for\s+procurement\s+and\s+delivery\s+of",
    r"Requisition\s+for\s+procurement\s+of",
    r"Requisition\s+for\s+delivery\s+of",
    r"Requisition\s+for\s+supply\s+of",
    r"Competitive\s+bids\s+invited\s+specifically\s+for",
    r"Competitive\s+bids\s+invited\s+for\s+supply\s+of",
    r"Competitive\s+bids\s+invited\s+for",
    r"Tender\s+for\s+supply\s+and\s+delivery\s+specifically\s+of",
    r"Tender\s+for\s+(?:the\s+)?supply\s+and\s+commissioning\s+of",
    r"Tender\s+for\s+supply\s+and\s+delivery\s+of",
    r"Tender\s+for\s+procurement\s+of",
    r"Tender\s+for\s+(?:the\s+)?supply\s+of",
    r"Tender\s+enquiry\s+for\s+procurement\s+specifically\s+of",
    r"Tender\s+enquiry\s+for\s+supply\s+of",
    r"Tender\s+inquiry\s+for\s+procurement\s+of",
    r"Tender\s+inquiry\s+for\s+supply\s+of",
    r"Annual\s+rate\s+contract\s+for\s+(?:the\s+)?supply\s+of",
    r"Invitation\s+of\s+bids\s+specifically\s+for\s+supply\s+of",
    r"Invitation\s+of\s+bids\s+for\s+supply\s+of",
    r"Official\s+procurement\s+tender\s+for\s+supply\s+of",
    r"Official\s+procurement\s+tender\s+for",
    r"Specialized\s+procurement\s+tender\s+for",
    r"Procurement\s+specification\s+for\s+supply\s+of",
    r"Procurement\s+tender\s+for\s+delivery\s+of",
    r"Procurement\s+tender\s+for\s+supply\s+of",
    r"Procurement\s+and\s+supply\s+of",
    r"Public\s+tender\s+for\s+supply\s+of",
    r"Bids\s+invited\s+for\s+procurement\s+of",
    r"Bids\s+invited\s+for\s+supply\s+of",
    r"Supply\s+and\s+delivery\s+of",
    r"Supply\s+and\s+procurement\s+of",
    r"Supply\s+of",
    r"Procurement\s+of",
]

# 5. Application Prepositional Markers
APPLICATION_MARKERS: List[str] = [
    r"\bspecifically\s+for\b",
    r"\bintended\s+for\b",
    r"\brequired\s+for\b",
    r"\bdesigned\s+for\b",
    r"\bsuitable\s+for\b",
    r"\bused\s+in\b",
    r"\bused\s+for\b",
    r"\bfor\s+use\s+in\b",
    r"\bfor\s+use\s+for\b",
    r"\bfor\s+installation\s+in\b",
    r"\bfor\s+installation\b",
    r"\bfor\s+project\s+execution\b",
    r"\bfor\b",
]

# 6. Trailing Procurement Framing Fluff (to exclude from application)
TRAILING_FLUFF: List[str] = [
    r"\bto\s+satisfy\s+project\s+requirements\.?$",
    r"\bfor\s+immediate\s+deployment\.?$",
    r"\bfor\s+site\s+utilization\.?$",
    r"\bfor\s+departmental\s+infrastructure\.?$",
    r"\bas\s+per\s+project\s+specifications\.?$",
    r"\bas\s+per\s+tender\s+specifications\.?$",
    r"\bto\s+satisfy\s+technical\s+requirements\.?$",
    r"\bfor\s+project\s+requirements\.?$",
]

# 7. Sector Keyword Ontologies (all 22 Authoritative Sectors)
SECTOR_TAXONOMY: Dict[str, List[str]] = {
    "Cement": [
        "cement", "portland", "pozzolana", "clinker", "masonry cement", "supersulphated",
        "hydrophobic", "rapid hardening", "low heat", "high alumina", "calcined clay",
        "slag cement", "hydraulic cement", "hydraulic structures"
    ],
    "Transformers & Motors": [
        "transformer", "distribution transformer", "induction motor", "squirrel cage",
        "motor capacitor", "ac motor capacitor", "power capacitor", "kva", "mineral oil",
        "power systems", "substation", "high voltage"
    ],
    "Solar & Cables": [
        "photovoltaic", "solar cable", "fire survival cable", "thermosetting insulated",
        "electric cable", "cross-linked", "pv cable", "solar power", "1500 v dc",
        "solar panels"
    ],
    "HVAC": [
        "air conditioner", "room air conditioner", "split room air conditioner",
        "package air conditioner", "heat exchanger", "compressor", "hermetic compressor",
        "hvac", "ducted", "ventilation", "cooling"
    ],
    "Gas & LPG": [
        "lpg", "gas cylinder", "cylinder valve", "gas stove", "gas cooking", "methane",
        "natural gas", "refillable seamless", "shutoff valve", "liquefied petroleum",
        "gas container"
    ],
    "Medical": [
        "x-ray", "diagnostic medical", "medical equipment", "clinical thermometer",
        "medical electrical", "radiation", "healthcare", "radiology", "patient"
    ],
    "Footwear/PPE": [
        "helmet", "headgear", "safety footwear", "occupational footwear", "protective boot",
        "safety shoe", "insulating glove", "live working glove", "ppe", "toecap",
        "personal protective"
    ],
    "Steel": [
        "structural steel", "carbon steel", "steel sheet", "steel plate", "steel strip",
        "electrogalvanized", "hot rolled", "cold reduced", "hot-dip zinc", "welded steel pipe",
        "steel coils", "flat steel"
    ],
    "Agriculture": [
        "water storage tank", "flexible water storage", "agricultural irrigation",
        "drip irrigation", "micro irrigation", "horticulture", "farms", "polyethylene pipeline"
    ],
    "Wood Products": [
        "particle board", "prelaminated", "medium density fibre", "mdf", "wood board",
        "block board", "plywood", "flush door", "lignocellulosic", "timber", "interior products"
    ],
    "Electrical": [
        "residual current", "circuit breaker", "rcbo", "rccb", "ceiling fan", "electric fan",
        "switches", "fixed electrical", "electric fence", "fuse", "electricity meter",
        "watt-hour meter", "static watt-hour", "electrical installations", "appliances",
        "immersion water-heater", "room heater", "electric iron", "food mixer"
    ],
    "Electrical Accessories": [
        "bayonet", "lamp holder", "trunking", "ducting", "enclosure", "conduit",
        "plug", "socket-outlet", "junction box", "cable trunking", "fixed lighting"
    ],
    "Laboratory Glassware": [
        "measuring cylinder", "volumetric flask", "beaker", "laboratory glassware",
        "graduated cylinder", "borosilicate", "laboratory handling", "volumetric"
    ],
    "Kitchen Appliances": [
        "food mixer", "liquidizer", "grinder", "blender", "juicer", "centrifugal juicer",
        "electric iron", "immersion water-heater", "storage water heater", "kitchen appliance",
        "domestic electric"
    ],
    "Fire Safety": [
        "fire extinguisher", "portable fire extinguisher", "wheeled fire extinguisher",
        "fire protection", "extinguishing agent", "fire fighting"
    ],
    "Copper": [
        "copper rod", "copper bar", "copper wire", "copper tube", "copper conductor",
        "high conductivity copper", "drawn copper", "continuous cast copper"
    ],
    "Chemicals": [
        "caustic soda", "boric acid", "poly aluminium chloride", "aniline",
        "chemical compound", "chemical reagent", "industrial chemicals"
    ],
    "Cast Iron": [
        "cast iron", "grey iron", "manhole cover", "manhole frame", "iron casting",
        "drainage cover", "gully tops", "castings"
    ],
    "Pipes & Water": [
        "steel tube", "tubular section", "wrought steel", "water-well", "ductile iron pipe",
        "pvc pipe", "polyethylene pipe", "drainage pipe", "water piping", "gas piping"
    ],
    "Refrigeration": [
        "freezer", "refrigerating appliance", "refrigerator", "deep freezer",
        "food freezer", "food freezing", "frost-free"
    ],
    "Door Fittings": [
        "door closer", "door handle", "pneumatically regulated", "building hardware",
        "door lock", "hinge", "light doors", "pull handle"
    ],
    "Water Treatment": [
        "reverse osmosis", "point of use", "water treatment system", "drinking water",
        "water purifier", "membrane filtration"
    ],
}
