"""
scripts/audit_phase3_1.py

Comprehensive Audit for Phase 3.1:
1. Audit all 111 OVER_EXTRACTION cases:
   - Verify presence in raw query text.
   - Categorize as:
     a) VALID_QUERY_SUPPORTED (textually present in query, absent from seed non-authoritative facet)
     b) GENUINE_EXTRACTION_DEFECT (false positive, incorrect semantic sense, sub-token error)
2. Audit all 117 sector classification failures:
   - true sector errors (classifier predicted wrong sector)
   - normalization errors (e.g. compound seed label like Footwear/PPE vs PPE, Capacitors vs Transformers & Motors)
   - ambiguity cases (multi-sector crossover, e.g. kitchen appliances with electrical specifications)
   - missing-sector cases (extractor could not assign a sector)
3. Separate text-grounding extraction fidelity metrics from seed-profile alignment metrics.
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# Load synthetic records
with open("data/synthetic/synthetic_queries_v1.jsonl", "r", encoding="utf-8") as f:
    queries_data = {r["id"]: r for r in (json.loads(line) for line in f)}

# Load extraction results
with open("data/evaluation/extraction_results.jsonl", "r", encoding="utf-8") as f:
    extraction_results = [json.loads(line) for line in f]

print(f"Loaded {len(extraction_results)} extraction records.")

# =============================================================================
# PART 1: AUDIT ALL 111 OVER_EXTRACTION CASES
# =============================================================================
over_extractions = []
for res in extraction_results:
    q_id = res["query_id"]
    record = queries_data[q_id]
    q_text = record["query"]
    gt_mats = set(m.lower() for m in record.get("materials", []))
    pred_mats = set(m["value"].lower() for m in res["extracted"]["materials"] if m.get("value"))
    
    # Material over-extractions
    for em in (pred_mats - gt_mats):
        # Check if em is physically present in the query
        in_query = bool(re.search(r"\b" + re.escape(em) + r"\b", q_text, re.IGNORECASE))
        over_extractions.append({
            "query_id": q_id,
            "field": "material",
            "value": em,
            "in_query": in_query,
            "query": q_text,
            "gt_materials": list(gt_mats),
            "difficulty": record["difficulty"],
            "seed_standard": record["source_seed_standard"],
            "sector": record["sector_original"],
        })

    # Parameter over-extractions
    gt_params = record.get("parameters", {})
    pred_params = res["extracted"]["parameters"]
    if not gt_params and pred_params:
        for p in pred_params:
            p_val = p["value"]
            in_query = bool(re.search(r"\b" + re.escape(p["evidence"]) + r"\b", q_text, re.IGNORECASE))
            over_extractions.append({
                "query_id": q_id,
                "field": "parameter",
                "value": f"{p['name']}: {p_val} {p.get('unit') or ''}".strip(),
                "in_query": in_query,
                "query": q_text,
                "gt_parameters": gt_params,
                "difficulty": record["difficulty"],
                "seed_standard": record["source_seed_standard"],
                "sector": record["sector_original"],
            })

print(f"\nTotal OVER_EXTRACTION cases identified: {len(over_extractions)}")

valid_query_supported = [c for c in over_extractions if c["in_query"]]
not_in_query = [c for c in over_extractions if not c["in_query"]]

print(f"  - Present in Query Text (Valid Query-Supported Extraction): {len(valid_query_supported)}")
print(f"  - NOT Present in Query Text (True Hallucinations): {len(not_in_query)}")

# Further inspect the valid_query_supported cases: are there any contextual false positives?
# (e.g., words matched in a non-material sense)
semantic_fp = []
valid_domain_materials = []

for c in valid_query_supported:
    val = c["value"]
    q = c["query"].lower()
    
    # Check if the word is used as a material or in another sense
    if val == "iron" and ("electric iron" in q or "steam iron" in q or "flat iron" in q):
        # "iron" extracted as material from an appliance name "Electric iron"
        semantic_fp.append((c, "appliance_name_collision (Electric iron)"))
    elif val == "glass" and ("glassware" in q and "glass" not in q.replace("glassware", "")):
        semantic_fp.append((c, "subword_collision (glass in glassware)"))
    elif val == "carbon" and ("carbon steel" in q and val == "carbon"):
        # extracted both "carbon" and "carbon steel"
        semantic_fp.append((c, "compound_subcomponent (carbon from carbon steel)"))
    elif val == "slag" and "portland slag cement" in q:
        # slag is a constituent of slag cement
        valid_domain_materials.append((c, "constituent_in_seed_title"))
    elif val == "steel" and ("structural steel" in q or "steel tubes" in q or "carbon steel" in q):
        valid_domain_materials.append((c, "material_in_seed_title"))
    else:
        valid_domain_materials.append((c, "explicit_specification_in_query"))

print(f"\nBreakdown of Valid Query-Supported Extractions ({len(valid_query_supported)}):")
print(f"  1. Legitimate Engineering Materials / Specs in Query Text: {len(valid_domain_materials)}")
print(f"  2. Contextual / Subword Overlaps (Defects to Refine): {len(semantic_fp)}")

print("\nSample Contextual False Positives:")
for item, reason in semantic_fp[:5]:
    print(f"  [{reason}] Query ID: {item['query_id']} | Value: '{item['value']}' | Query: '{item['query']}'")

# Value distribution of valid materials absent from seed facet:
val_counter = Counter(c["value"] for c, _ in valid_domain_materials)
print("\nTop materials present in query but absent from non-authoritative seed facets:")
for val, count in val_counter.most_common(10):
    print(f"  - {val}: {count} occurrences")

# =============================================================================
# PART 2: AUDIT ALL 117 SECTOR CLASSIFICATION FAILURES
# =============================================================================
sector_failures = []
for res in extraction_results:
    q_id = res["query_id"]
    record = queries_data[q_id]
    q_text = record["query"]
    
    gt_sec_orig = record.get("sector_original", "")
    gt_sec_norm = record.get("sector_normalized", "")
    pred_sec = res["extracted"]["sector"]["value"] if res["extracted"].get("sector") else None
    
    matched = (pred_sec == gt_sec_orig or pred_sec == gt_sec_norm) if pred_sec else False
    if not matched:
        sector_failures.append({
            "query_id": q_id,
            "query": q_text,
            "gt_sector_original": gt_sec_orig,
            "gt_sector_normalized": gt_sec_norm,
            "predicted_sector": pred_sec,
            "difficulty": record["difficulty"],
            "product": record["product"],
        })

print(f"\n=============================================================================")
print(f"Total Sector Failures: {len(sector_failures)} (Target 117: {len(sector_failures) == 117})")

# Classify sector failures into:
# 1. missing-sector cases (pred_sec is None)
# 2. normalization errors (pred_sec is a valid normalized/sub-sector concept or compound variant)
# 3. ambiguity cases (query has terminology spanning multiple sectors, e.g. Electrical vs Kitchen Appliances)
# 4. true sector errors (classifier clearly predicted the wrong sector)

missing_sector = []
normalization_errors = []
ambiguity_cases = []
true_sector_errors = []

for sf in sector_failures:
    pred = sf["predicted_sector"]
    orig = sf["gt_sector_original"]
    norm = sf["gt_sector_normalized"]
    prod = sf["product"].lower()
    q = sf["query"].lower()

    if pred is None:
        missing_sector.append(sf)
    # Check normalization: e.g. "Footwear/PPE" vs "PPE" if not caught, or "Transformers & Motors" vs "Electrical"
    elif (orig == "Footwear/PPE" and pred in ["PPE", "Footwear"]) or \
         (orig == "Solar & Cables" and pred == "Electrical") or \
         (orig == "Transformers & Motors" and pred == "Capacitors"):
        normalization_errors.append(sf)
    # Check ambiguity: e.g. kitchen appliance with electrical spec, or pipes vs steel
    elif (orig == "Electrical" and pred in ["Kitchen Appliances", "HVAC"]) or \
         (orig == "Kitchen Appliances" and pred == "Electrical") or \
         (orig == "Refrigeration" and pred in ["HVAC", "Kitchen Appliances"]) or \
         (orig == "HVAC" and pred in ["Refrigeration", "Electrical"]) or \
         (orig == "Steel" and pred in ["Pipes & Water", "Cast Iron"]) or \
         (orig == "Pipes & Water" and pred in ["Steel", "Cast Iron"]) or \
         (orig == "Door Fittings" and pred in ["Cast Iron", "Steel"]) or \
         (orig == "Electrical Accessories" and pred == "Electrical") or \
         (orig == "Electrical" and pred == "Electrical Accessories") or \
         (orig == "Cast Iron" and pred in ["Pipes & Water", "Steel"]):
        ambiguity_cases.append(sf)
    else:
        true_sector_errors.append(sf)

print(f"\nSector Failure Breakdown:")
print(f"  1. Missing-sector cases (no sector predicted): {len(missing_sector)}")
print(f"  2. Normalization errors (normalized/sub-sector taxonomy mismatch): {len(normalization_errors)}")
print(f"  3. Ambiguity cases (multi-domain crossover, e.g. Electrical vs Kitchen): {len(ambiguity_cases)}")
print(f"  4. True sector errors (misclassification): {len(true_sector_errors)}")
print(f"  Total accounted for: {len(missing_sector) + len(normalization_errors) + len(ambiguity_cases) + len(true_sector_errors)}")

# Show samples of each
print("\n--- Sample Missing-Sector Cases ---")
for s in missing_sector[:3]:
    print(f"  Query ID: {s['query_id']} | GT: {s['gt_sector_original']} | Query: '{s['query']}'")

print("\n--- Sample Ambiguity Cases ---")
for s in ambiguity_cases[:4]:
    print(f"  Query ID: {s['query_id']} | GT: {s['gt_sector_original']} | Predicted: {s['predicted_sector']} | Product: '{s['product']}'")

print("\n--- Sample True Sector Errors ---")
for s in true_sector_errors[:4]:
    print(f"  Query ID: {s['query_id']} | GT: {s['gt_sector_original']} | Predicted: {s['predicted_sector']} | Product: '{s['product']}'")
