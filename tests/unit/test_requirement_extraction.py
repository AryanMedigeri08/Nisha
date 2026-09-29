"""
tests/unit/test_requirement_extraction.py

Unit tests for the Phase 3 Requirement Extraction Engine (backend/extraction/).
Validates the 12 required criteria from the Phase 3 specification:
1. Product extraction
2. Material extraction
3. Application extraction
4. Parameter extraction
5. Unit extraction
6. IS number extraction
7. Empty-field handling
8. Ambiguous-field handling
9. No hallucinated parameters
10. No label leakage
11. Pydantic schema validation
12. Evidence-span preservation
"""

import json
import pytest
from pathlib import Path

from backend.extraction.extractor import RequirementExtractor
from backend.extraction.schemas import ProcurementRequirements


@pytest.fixture(scope="module")
def extractor():
    """Instantiate the requirement extractor."""
    return RequirementExtractor(use_llm_fallback=False)


@pytest.fixture(scope="module")
def synthetic_records():
    """Load sample synthetic records for testing."""
    data_path = Path("data/synthetic/synthetic_queries_v1.jsonl")
    assert data_path.exists(), "Synthetic dataset not found"
    records = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


# 1. Product Extraction
def test_product_extraction(extractor):
    query = "Notice Inviting Tender for supply of Portland slag cement for durable construction."
    res = extractor.extract(query=query, query_id="test_prod_1")
    assert res.product is not None
    assert res.product.value is not None
    assert "portland slag cement" in res.product.value.lower()
    assert res.product.confidence >= 0.80
    assert res.product.evidence is not None


# 2. Material Extraction
def test_material_extraction(extractor):
    query = "Tender for supply of copper wire and carbon steel sheets for manufacturing."
    res = extractor.extract(query=query, query_id="test_mat_1")
    extracted_mats = {m.value.lower() for m in res.materials}
    assert "copper" in extracted_mats
    assert "carbon" in extracted_mats or "carbon steel" in extracted_mats or "steel" in extracted_mats
    for m in res.materials:
        assert m.confidence >= 0.90
        assert m.evidence.lower() in query.lower()

    # Empty material test
    no_mat_query = "Supply of electric ceiling fans for office rooms."
    no_mat_res = extractor.extract(query=no_mat_query, query_id="test_mat_2")
    assert no_mat_res.materials == []


# 3. Application Extraction
def test_application_extraction(extractor):
    query = "Requisition for supply of induction motors specifically for agricultural irrigation systems."
    res = extractor.extract(query=query, query_id="test_app_1")
    assert len(res.application) >= 1
    app_val = res.application[0].value.lower()
    assert "agricultural" in app_val or "irrigation" in app_val
    assert res.application[0].confidence >= 0.70
    assert res.application[0].evidence in query


# 4. Parameter Extraction
def test_parameter_extraction(extractor):
    query = "Procurement of electric cables for rated voltage 1500 V DC and power capacity up to 2500 kVA."
    res = extractor.extract(query=query, query_id="test_param_1")
    assert len(res.parameters) >= 2
    param_names = {p.name for p in res.parameters}
    assert "rated_voltage" in param_names or "voltage" in param_names
    assert "power_rating" in param_names or "maximum_power_rating" in param_names

    voltage_param = next(p for p in res.parameters if "voltage" in p.name)
    assert "1500" in voltage_param.value
    assert "V" in voltage_param.unit


# 5. Unit Extraction
def test_unit_extraction(extractor):
    query = (
        "Requisition for door closers weighing up to 40 kg, pipe diameter up to 200 mm, "
        "and water storage tank exceeding 5 litre capacity."
    )
    res = extractor.extract(query=query, query_id="test_unit_1")
    units = {p.unit.lower() for p in res.parameters if p.unit}
    assert any("kg" in u for u in units)
    assert any("mm" in u for u in units)
    assert any("litre" in u or "l" in u for u in units)


# 6. IS Number Extraction
def test_is_number_extraction(extractor):
    # Real tender mentioning explicit Indian Standards
    query = "Supply of ordinary Portland cement conforming to IS 269:2015 and safety standards of IS 455."
    res = extractor.extract(query=query, query_id="test_is_1")
    assert len(res.cited_standards) == 2
    std_nums = {cs.standard_number for cs in res.cited_standards}
    assert any("269" in s for s in std_nums)
    assert any("455" in s for s in std_nums)
    for cs in res.cited_standards:
        assert cs.confidence == 1.0
        assert cs.evidence in query

    # Synthetic query without IS numbers must return empty list
    syn_query = "Tender for supply of domestic electric food mixers for domestic kitchen appliances."
    syn_res = extractor.extract(query=syn_query, query_id="test_is_2")
    assert syn_res.cited_standards == []


# 7. Empty-Field Handling
def test_empty_field_handling(extractor):
    # Query with product only, no parameters and no materials
    query = "Procurement of office tables and chairs for administrative facilities."
    res = extractor.extract(query=query, query_id="test_empty_1")
    assert res.product is not None
    assert res.materials == []
    assert res.parameters == []
    assert res.cited_standards == []

    # Empty string query
    empty_res = extractor.extract(query="   ", query_id="test_empty_2")
    assert empty_res.product.value is None
    assert empty_res.overall_confidence == 0.0


# 8. Ambiguous-Field Handling
def test_ambiguous_field_handling(extractor):
    query = "Requisition for supply of general miscellaneous hardware."
    res = extractor.extract(query=query, query_id="test_ambig_1")
    # Must not hallucinate parameters or materials
    assert res.materials == []
    assert res.parameters == []
    assert res.cited_standards == []
    # Overall confidence reflects ambiguity
    assert res.overall_confidence < 0.90


# 9. No Hallucinated Parameters
def test_no_hallucinated_parameters(extractor, synthetic_records):
    # Test across 50 records: every extracted parameter's numeric value must exist in query
    for r in synthetic_records[:50]:
        res = extractor.extract(query=r["query"], query_id=r["id"])
        for p in res.parameters:
            assert p.evidence in r["query"], (
                f"Parameter evidence '{p.evidence}' not in query '{r['query']}'"
            )
            # Numeric value must be present in query
            import re
            p_nums = re.findall(r"\b\d+(?:\.\d+)?\b", p.value)
            for num in p_nums:
                assert num in r["query"], (
                    f"Hallucinated number {num} in parameter {p.name} for query: '{r['query']}'"
                )


# 10. No Label Leakage
def test_no_label_leakage(extractor):
    forbidden_calls = [
        {"ground_truth_primary": ["IS 455"]},
        {"ground_truth_related": ["IS 269"]},
        {"near_match_candidates": ["IS 1239"]},
        {"source_seed_standard": "IS 4151:2015"},
        {"ground_truth_evidence": [{"field": "product", "value": "test"}]},
    ]
    for leak_kwargs in forbidden_calls:
        with pytest.raises(ValueError, match="LABEL LEAKAGE VIOLATION"):
            extractor.extract(query="Valid query text", query_id="test_leak", **leak_kwargs)


# 11. Pydantic Schema Validation
def test_pydantic_schema_validation(extractor):
    query = "Notice Inviting Tender for supply of A.C. motor capacitors for electrical power systems."
    res = extractor.extract(query=query, query_id="test_schema_1")
    assert isinstance(res, ProcurementRequirements)

    dumped = res.model_dump()
    assert "query_id" in dumped
    assert "product" in dumped
    assert "sector" in dumped
    assert "application" in dumped
    assert "materials" in dumped
    assert "parameters" in dumped
    assert "safety_requirements" in dumped
    assert "electrical_requirements" in dumped
    assert "mechanical_requirements" in dumped
    assert "cited_standards" in dumped
    assert "language" in dumped
    assert "overall_confidence" in dumped

    # Re-parse into model
    reparsed = ProcurementRequirements.model_validate(dumped)
    assert reparsed.query_id == res.query_id
    assert reparsed.overall_confidence == res.overall_confidence


# 12. Evidence-Span Preservation
def test_evidence_span_preservation(extractor):
    query = (
        "Notice Inviting Tender for supply of Electric Cable for Photovoltaic Systems "
        "for rated voltage 1500 V DC for solar and electrical cabling."
    )
    res = extractor.extract(query=query, query_id="test_span_1")

    # Check product span
    if res.product and res.product.start_idx is not None and res.product.end_idx is not None:
        slice_text = query[res.product.start_idx:res.product.end_idx]
        assert slice_text == res.product.evidence

    # Check application span
    for app in res.application:
        if app.start_idx is not None and app.end_idx is not None:
            slice_text = query[app.start_idx:app.end_idx]
            assert slice_text == app.evidence

    # Check parameter span
    for param in res.parameters:
        if param.start_idx is not None and param.end_idx is not None:
            slice_text = query[param.start_idx:param.end_idx]
            assert slice_text == param.evidence
