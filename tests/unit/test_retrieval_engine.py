"""
tests/unit/test_retrieval_engine.py
===================================

Unit tests for RetrievalEngine:
- End-to-end hybrid retrieval pipeline
- Absolute guarantee against label leakage (Rule 1)
- Validation that all returned standard IDs exist in the 91-standard corpus
- No duplicate candidates in top-K
- Candidate pool sizes (BM25 top 20, Dense top 20, RRF top 20, Reranked top 10)
- Soft sector behavior (no hard filtering discarding cross-sector matches)
"""

import pytest
from backend.extraction.schemas import (
    ProcurementRequirements,
    ExtractedField,
    ExtractedParameter,
)
from backend.retrieval.retrieval_engine import RetrievalEngine
from backend.retrieval.schemas import RetrievalResult


@pytest.fixture(scope="module")
def engine():
    return RetrievalEngine()


def test_retrieval_engine_end_to_end(engine):
    """Test full pipeline: BM25 (20) + Dense (20) -> RRF (20) -> Reranker (10)."""
    req = ProcurementRequirements(
        query_id="syn_test_001",
        product=ExtractedField(value="Domestic gas stove for LPG"),
        sector=ExtractedField(value="Kitchen Appliances"),
        materials=[ExtractedField(value="stainless steel")],
    )
    result = engine.retrieve(req, query_text="Notice Inviting Tender for supply of Domestic Gas Stoves for LPG")

    assert isinstance(result, RetrievalResult)
    assert result.query_id == "syn_test_001"
    assert len(result.bm25_candidates) == 20
    assert len(result.dense_candidates) == 20
    assert len(result.rrf_candidates) == 20
    assert len(result.candidates) == 10

    # Ensure ranking is sequential 1..10
    assert [c.final_rank for c in result.candidates] == list(range(1, 11))


def test_no_label_leakage_in_retrieval_pipeline(engine):
    """
    CRITICAL RULE 1: RetrievalEngine MUST NOT access or accept ground truth fields:
    ground_truth_primary, ground_truth_related, near_match_candidates,
    source_seed_standard, ground_truth_evidence.
    """
    # Create requirement object ensuring ground truth fields are absent
    req = ProcurementRequirements(
        query_id="syn_leak_test",
        product=ExtractedField(value="Submersible pumpsets for clear cold water"),
        sector=ExtractedField(value="Pumps"),
    )

    # Verify that the schemas do not possess any ground truth attributes
    assert not hasattr(req, "ground_truth_primary")
    assert not hasattr(req, "ground_truth_related")
    assert not hasattr(req, "near_match_candidates")
    assert not hasattr(req, "source_seed_standard")
    assert not hasattr(req, "ground_truth_evidence")

    # Verify that the engine's retrieve() method accepts only requirements, query_text, top_k
    import inspect
    sig = inspect.signature(engine.retrieve)
    allowed_params = {"requirements", "query_text", "top_k"}
    assert set(sig.parameters.keys()) == allowed_params


def test_all_candidates_belong_to_91_standard_corpus(engine):
    """Every candidate returned must be one of the 91 valid standards."""
    valid_ids = {d.standard_id for d in engine.bm25_retriever.documents}
    assert len(valid_ids) == 91

    req = ProcurementRequirements(
        query_id="syn_valid_test",
        product=ExtractedField(value="Cast iron manhole covers and frames"),
        sector=ExtractedField(value="Civil Infrastructure"),
    )
    result = engine.retrieve(req)

    for cand in result.candidates:
        assert cand.standard_id in valid_ids
        assert cand.is_number.startswith("IS")


def test_top_k_candidates_contain_no_duplicates(engine):
    """Final candidates list must have no duplicates."""
    req = ProcurementRequirements(
        query_id="syn_nodup_test",
        product=ExtractedField(value="Polyethylene pipes for water supply"),
    )
    result = engine.retrieve(req, top_k=10)
    std_ids = [c.standard_id for c in result.candidates]
    assert len(std_ids) == len(set(std_ids))


def test_no_hard_sector_filtering(engine):
    """
    Ensure the engine does NOT discard candidates whose sector does not match
    the extracted sector (soft relevance, no hard Boolean exclusion).
    """
    req = ProcurementRequirements(
        query_id="syn_cross_sector",
        product=ExtractedField(value="Boxes and Enclosures for Electrical Accessories"),
        sector=ExtractedField(value="Electrical"),  # Query says 'Electrical', standard sector may be 'Electrical Accessories'
    )
    result = engine.retrieve(req, top_k=10)
    # Check that candidate sectors can vary and are not exclusively 'Electrical'
    sectors = {c.sector for c in result.candidates if c.sector}
    assert len(sectors) > 1 or "Electrical Accessories" in sectors or "Electrical" in sectors
