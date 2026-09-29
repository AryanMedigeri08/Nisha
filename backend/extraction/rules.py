"""
backend/extraction/rules.py

Deterministic rules, regex extraction routines, span locators,
and lexicon matching functions for Phase 3 Requirement Extraction (Stage 1 & 2).
All extracted fields retain exact textual provenance (evidence spans).
"""

import re
from typing import List, Optional, Tuple, Dict, Any, Set

from backend.extraction.schemas import (
    ExtractedField,
    ExtractedParameter,
    ExtractedCitedStandard,
)
from backend.extraction.patterns import (
    CITED_STANDARD_PATTERN,
    PARAMETER_PATTERNS,
    MATERIAL_LEXICON,
    PROCUREMENT_PREFIXES,
    APPLICATION_MARKERS,
    TRAILING_FLUFF,
    SECTOR_TAXONOMY,
)


def find_evidence_span(text: str, target: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Locate the exact character span of target within text (case-insensitive).
    Returns (matched_substring, start_index, end_index) or (None, None, None).
    """
    if not text or not target:
        return None, None, None
    escaped = re.escape(target.strip())
    match = re.search(escaped, text, flags=re.IGNORECASE)
    if match:
        start, end = match.span()
        return text[start:end], start, end
    return None, None, None


def extract_cited_standards(query: str) -> List[ExtractedCitedStandard]:
    """
    Stage 1: Detect explicitly cited Indian Standards (IS numbers) in the query text.
    Preserves exact standard number, confidence (1.0), and evidence span.
    """
    standards: List[ExtractedCitedStandard] = []
    seen = set()

    for match in CITED_STANDARD_PATTERN.finditer(query):
        std_raw = match.group(0).strip()
        num_part = match.group(1).strip()
        std_norm = f"IS {num_part}"
        if std_norm.lower() not in seen:
            seen.add(std_norm.lower())
            start, end = match.span()
            standards.append(
                ExtractedCitedStandard(
                    standard_number=std_norm,
                    confidence=1.0,
                    evidence=std_raw,
                    start_idx=start,
                    end_idx=end,
                )
            )
    return standards


def extract_parameters_deterministic(query: str) -> List[ExtractedParameter]:
    """
    Stage 1: Deterministic extraction of technical parameters (voltages, power,
    dimensions, weights, capacities, currents, pressures, frequencies, percentages).
    Preserves parameter name, value, unit, and exact evidence span.
    """
    extracted_params: List[ExtractedParameter] = []
    occupied_spans: List[Tuple[int, int]] = []

    for pattern_cfg in PARAMETER_PATTERNS:
        category = pattern_cfg["category"]
        regex = pattern_cfg["pattern"]
        default_unit = pattern_cfg["default_unit"]

        for match in regex.finditer(query):
            start, end = match.span()

            # Prevent duplicate or overlapping parameter spans
            overlaps = any(
                max(start, o_start) < min(end, o_end)
                for o_start, o_end in occupied_spans
            )
            if overlaps:
                continue

            groups = match.groupdict()
            evidence = groups.get("evidence", match.group(0)).strip()
            val = groups.get("val", "").strip()
            unit = groups.get("unit") or default_unit
            prefix = groups.get("prefix") or ""
            spec = groups.get("spec") or ""
            suffix = groups.get("suffix") or ""

            # Require digits in value
            if not re.search(r"\d", val):
                continue

            # Determine specific contextual parameter name
            prefix_lower = prefix.lower().strip()
            if "rated voltage" in prefix_lower:
                name = "rated_voltage"
            elif "working voltage" in prefix_lower:
                name = "working_voltage"
            elif "maximum voltage" in prefix_lower:
                name = "maximum_voltage_rating"
            elif "voltage" in prefix_lower:
                name = "voltage"
            elif "maximum power" in prefix_lower or "power rating" in prefix_lower:
                name = "maximum_power_rating"
            elif "power" in prefix_lower:
                name = "power_rating"
            elif "door weight" in prefix_lower:
                name = "door_weight_limit"
            elif "load capacity" in prefix_lower:
                name = "load_capacity"
            elif "weight" in prefix_lower or "weighing" in prefix_lower or "mass" in prefix_lower:
                name = "weight"
            elif "capacity threshold" in prefix_lower:
                name = "capacity_threshold"
            elif "capacity" in prefix_lower:
                name = "capacity"
            elif "diameter" in prefix_lower or "dia" in prefix_lower or "dia" in suffix.lower():
                name = "diameter"
            elif "thickness" in prefix_lower:
                name = "thickness"
            elif category == "dimension":
                name = "dimension"
            else:
                name = category

            # Construct clean value string including range qualifier if present
            range_qual = groups.get("range", "").strip()
            if range_qual and range_qual.lower() not in val.lower():
                full_val = f"{range_qual} {val}".strip()
            else:
                full_val = val

            # Append AC/DC specification to unit if applicable
            full_unit = unit
            if spec and spec not in full_unit:
                full_unit = f"{full_unit} {spec}".strip()

            occupied_spans.append((start, end))
            extracted_params.append(
                ExtractedParameter(
                    name=name,
                    value=full_val,
                    unit=full_unit,
                    confidence=0.95,
                    evidence=evidence,
                    start_idx=start,
                    end_idx=end,
                )
            )

    extracted_params.sort(key=lambda p: p.start_idx if p.start_idx is not None else 0)
    return extracted_params


def extract_materials_deterministic(query: str) -> List[ExtractedField]:
    """
    Stage 1: Extract only engineering materials explicitly present in the query.
    Avoids inferring materials not mentioned in the text.
    """
    materials: List[ExtractedField] = []
    seen = set()

    # Match longer/compound materials first (e.g., "cast iron" before "iron")
    for mat in MATERIAL_LEXICON:
        pattern = r"\b" + re.escape(mat) + r"\b"
        for match in re.finditer(pattern, query, flags=re.IGNORECASE):
            val = mat.lower()
            start, end = match.span()

            # Disambiguate "iron": do not extract if part of "cast iron" or "grey iron"
            if val == "iron":
                prefix = query[max(0, start - 6):start].lower()
                if "cast" in prefix or "grey" in prefix:
                    continue

            # Disambiguate "carbon": do not extract single "carbon" if part of "carbon steel"
            if val == "carbon":
                suffix = query[end:min(len(query), end + 8)].lower()
                if "steel" in suffix:
                    continue

            # Disambiguate "aluminium" in chemical compound "poly aluminium chloride"
            if val in ["aluminium", "aluminum"]:
                surrounding = query[max(0, start - 6):min(len(query), end + 10)].lower()
                if "poly" in surrounding and "chloride" in surrounding:
                    continue

            if val not in seen:
                seen.add(val)
                materials.append(
                    ExtractedField(
                        value=val,
                        confidence=0.95,
                        evidence=query[start:end],
                        start_idx=start,
                        end_idx=end,
                    )
                )

    materials.sort(key=lambda m: m.start_idx if m.start_idx is not None else 0)
    return materials


def extract_application_deterministic(query: str) -> List[ExtractedField]:
    """
    Stage 1: Extract intended application or operating context from prepositional markers.
    Strips procurement prefix first, then trailing boilerplate.
    """
    applications: List[ExtractedField] = []

    # 1. Strip trailing procurement framing boilerplate
    cleaned_query = query
    for fluff in TRAILING_FLUFF:
        cleaned_query = re.sub(fluff, "", cleaned_query, flags=re.IGNORECASE).strip()

    # 2. Strip procurement prefix first so words like 'specifically for' aren't confused as application
    body = cleaned_query
    for prefix in PROCUREMENT_PREFIXES:
        match = re.match(r"^\s*" + prefix + r"\s*", body, flags=re.IGNORECASE)
        if match:
            body = body[match.end():]
            break

    # Strip intermediate boilerplate clauses
    body = re.sub(r"\s+to\s+satisfy\s+(?:technical|project)\s+requirements\s*", " ", body, flags=re.IGNORECASE).strip()

    # 3. Look for application markers in the body
    marker_pattern = (
        r"\s+(?P<marker>specifically\s+for|intended\s+for|required\s+for|designed\s+for|"
        r"suitable\s+for|for\s+use\s+(?:for|in)|for\s+installation\s+(?:for|in)|"
        r"for\s+installation|used\s+in|used\s+for)\s+(?P<app>.*)$"
    )
    match = re.search(marker_pattern, body, flags=re.IGNORECASE)

    app_text = ""
    if match:
        app_text = match.group("app").strip(" .;")
    else:
        # Fallback to last occurrence of " for " in the latter half of the body
        last_for = body.rfind(" for ")
        if last_for != -1 and last_for >= 3:
            app_text = body[last_for + 5:].strip(" .;")

    if app_text and len(app_text.split()) >= 1:
        # Remove any lingering trailing fluff or periods
        for fluff in TRAILING_FLUFF:
            app_text = re.sub(fluff, "", app_text, flags=re.IGNORECASE).strip(" .;")

        ev, s_idx, e_idx = find_evidence_span(query, app_text)
        if app_text:
            applications.append(
                ExtractedField(
                    value=app_text,
                    confidence=0.88,
                    evidence=ev or app_text,
                    start_idx=s_idx,
                    end_idx=e_idx,
                )
            )

    return applications


def extract_product_deterministic(
    query: str,
    applications: List[ExtractedField]
) -> Optional[ExtractedField]:
    """
    Stage 2: Isolate the core product noun phrase from procurement language.
    Strips procurement prefixes, trailing clauses, and application prepositions.
    """
    # 1. Strip trailing fluff
    text = query
    for fluff in TRAILING_FLUFF:
        text = re.sub(fluff, "", text, flags=re.IGNORECASE).strip()

    # 2. Strip leading procurement prefix
    body = text
    for prefix in PROCUREMENT_PREFIXES:
        match = re.match(r"^\s*" + prefix + r"\s*", body, flags=re.IGNORECASE)
        if match:
            body = body[match.end():]
            break

    # Strip intermediate boilerplate clauses
    body = re.sub(r"\s+to\s+satisfy\s+(?:technical|project)\s+requirements\s*", " ", body, flags=re.IGNORECASE).strip()

    # 3. Strip application phrase if detected
    if applications and applications[0].value:
        app_val = applications[0].value
        # Find position of app_val in body
        app_pos = body.lower().rfind(app_val.lower())
        if app_pos != -1:
            body = body[:app_pos]
            # Strip trailing preposition (e.g. " for ", " intended for ")
            body = re.sub(
                r"\s+(?:specifically\s+for|intended\s+for|required\s+for|designed\s+for|"
                r"suitable\s+for|for\s+use\s+(?:for|in)|for\s+installation\s+(?:for|in)|"
                r"for\s+installation|used\s+in|used\s+for|for)\s*$",
                "",
                body,
                flags=re.IGNORECASE
            )

    # 4. Clean boundaries and punctuation
    product_str = body.strip(" .,-;:()")

    # Remove leading articles if cleanly separated
    product_str = re.sub(r"^(?:the|a|an)\s+", "", product_str, flags=re.IGNORECASE).strip()

    if not product_str or len(product_str) < 3:
        return ExtractedField(value=None, confidence=0.0, evidence=None)

    ev, s_idx, e_idx = find_evidence_span(query, product_str)
    confidence = 0.92 if len(product_str.split()) <= 10 else 0.80

    return ExtractedField(
        value=product_str,
        confidence=confidence,
        evidence=ev or product_str,
        start_idx=s_idx,
        end_idx=e_idx,
    )


def extract_sector_deterministic(
    product_field: Optional[ExtractedField],
    app_fields: List[ExtractedField],
    query: str
) -> Optional[ExtractedField]:
    """
    Stage 2: Deterministic classification into one of the 22 authoritative sectors
    based on product noun phrase, application context, and query vocabulary.
    """
    prod_text = (product_field.value or "").lower() if product_field else ""
    app_text = " ".join(f.value or "" for f in app_fields).lower()
    query_text = query.lower()

    sector_scores: Dict[str, float] = {sec: 0.0 for sec in SECTOR_TAXONOMY}
    sector_evidence: Dict[str, str] = {}

    for sec, keywords in SECTOR_TAXONOMY.items():
        for kw in keywords:
            kw_pattern = r"\b" + re.escape(kw) + r"\b"
            if prod_text and re.search(kw_pattern, prod_text, flags=re.IGNORECASE):
                sector_scores[sec] += 3.0
                if sec not in sector_evidence:
                    sector_evidence[sec] = kw
            elif app_text and re.search(kw_pattern, app_text, flags=re.IGNORECASE):
                sector_scores[sec] += 1.5
                if sec not in sector_evidence:
                    sector_evidence[sec] = kw
            elif re.search(kw_pattern, query_text, flags=re.IGNORECASE):
                sector_scores[sec] += 1.0
                if sec not in sector_evidence:
                    sector_evidence[sec] = kw

    best_sector = max(sector_scores, key=sector_scores.get)
    max_score = sector_scores[best_sector]

    if max_score > 0:
        trigger_word = sector_evidence.get(best_sector, "")
        ev, s_idx, e_idx = find_evidence_span(query, trigger_word)
        confidence = 0.95 if max_score >= 3.0 else (0.80 if max_score >= 1.5 else 0.65)
        return ExtractedField(
            value=best_sector,
            confidence=confidence,
            evidence=ev or trigger_word,
            start_idx=s_idx,
            end_idx=e_idx,
        )

    return ExtractedField(value=None, confidence=0.0, evidence=None)


def extract_domain_requirements(
    query: str,
    parameters: List[ExtractedParameter]
) -> Tuple[List[ExtractedField], List[ExtractedField], List[ExtractedField]]:
    """
    Stage 2: Segment specialized requirements into safety, electrical, and mechanical domains.
    """
    safety_reqs: List[ExtractedField] = []
    electrical_reqs: List[ExtractedField] = []
    mechanical_reqs: List[ExtractedField] = []

    # Safety patterns
    safety_markers = [
        "safety", "protective", "fire protection", "fire survival", "retention system",
        "insulating", "flame retardant", "shock protection", "earthing", "emergency"
    ]
    for marker in safety_markers:
        pattern = r"\b" + re.escape(marker) + r"\b"
        match = re.search(pattern, query, flags=re.IGNORECASE)
        if match:
            start, end = match.span()
            safety_reqs.append(
                ExtractedField(
                    value=marker,
                    confidence=0.85,
                    evidence=query[start:end],
                    start_idx=start,
                    end_idx=end,
                )
            )

    # Electrical patterns & parameters
    for p in parameters:
        if p.name in ["voltage", "rated_voltage", "working_voltage", "maximum_voltage_rating", "current", "power_rating", "maximum_power_rating", "frequency"]:
            electrical_reqs.append(
                ExtractedField(
                    value=f"{p.name}: {p.value} {p.unit or ''}".strip(),
                    confidence=p.confidence,
                    evidence=p.evidence,
                    start_idx=p.start_idx,
                    end_idx=p.end_idx,
                )
            )

    # Mechanical patterns & parameters
    for p in parameters:
        if p.name in ["dimension", "diameter", "thickness", "weight", "door_weight_limit", "load_capacity", "pressure", "capacity", "capacity_threshold"]:
            mechanical_reqs.append(
                ExtractedField(
                    value=f"{p.name}: {p.value} {p.unit or ''}".strip(),
                    confidence=p.confidence,
                    evidence=p.evidence,
                    start_idx=p.start_idx,
                    end_idx=p.end_idx,
                )
            )

    return safety_reqs, electrical_reqs, mechanical_reqs
