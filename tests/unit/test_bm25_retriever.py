"""
tests/unit/test_bm25_retriever.py
=================================

Unit tests for BM25 lexical sparse retriever:
- Deterministic rankings
- Top-K adherence
- Handling of empty / sparse requirements
- No duplicate candidates
- Technical parameter preservation in queries
"""

import pytest
from backend.extraction.schemas import (
    ProcurementRequirements,
    ExtractedField,
    ExtractedParameter,
)
from backend.retrieval.bm25_retriever import (
    BM25Retriever,
    build_bm25_query,
    tokenize_text,
)
from backend.retrieval.schemas import StandardDocument


@pytest.fixture(scope="module")
def bm25_retriever():
    return BM25Retriever()


def test_bm25_indexes_all_91_standards(bm25_retriever):
    """Ensure exactly 91 standards are loaded and indexed."""
    assert len(bm25_retriever.documents) == 91
    assert len(bm25_retriever.tokenized_corpus) == 91


def test_bm25_deterministic_ranking(bm25_retriever):
    """BM25 retrieval must produce identical rankings across multiple runs."""
    req = ProcurementRequirements(
        query_id="test_det",
        product=ExtractedField(value="Ordinary Portland Cement"),
        sector=ExtractedField(value="Cement"),
    )
    run1 = bm25_retriever.retrieve(req, top_k=10)
    run2 = bm25_retriever.retrieve(req, top_k=10)

    assert len(run1) == 10
    assert [c.standard_id for c in run1] == [c.standard_id for c in run2]
    assert [c.bm25_score for c in run1] == [c.bm25_score for c in run2]


def test_bm25_respects_top_k(bm25_retriever):
    """Retriever must return exactly top_k results."""
    req = ProcurementRequirements(
        query_id="test_k",
        product=ExtractedField(value="gas cylinder"),
    )
    for k in [1, 5, 15, 20]:
        cands = bm25_retriever.retrieve(req, top_k=k)
        assert len(cands) == k


def test_bm25_no_duplicate_candidates(bm25_retriever):
    """Returned candidate list must contain unique standard_ids."""
    req = ProcurementRequirements(
        query_id="test_dup",
        product=ExtractedField(value="steel tubes for structural piping"),
        materials=[ExtractedField(value="steel")],
    )
    cands = bm25_retriever.retrieve(req, top_k=20)
    ids = [c.standard_id for c in cands]
    assert len(ids) == len(set(ids))


def test_bm25_empty_requirements_handling(bm25_retriever):
    """Retriever must handle empty requirements safely without raising exceptions."""
    empty_req = ProcurementRequirements(query_id="empty_req")
    cands = bm25_retriever.retrieve(empty_req, top_k=10)
    assert len(cands) == 10
    assert all(c.bm25_rank == i + 1 for i, c in enumerate(cands))


def test_bm25_query_construction_preserves_parameters():
    """Verify parameters, values, and units are properly integrated in BM25 query."""
    req = ProcurementRequirements(
        query_id="test_param",
        product=ExtractedField(value="Distribution Transformer"),
        sector=ExtractedField(value="Electrical"),
        parameters=[
            ExtractedParameter(name="voltage", value="11", unit="kV", evidence="11 kV"),
            ExtractedParameter(name="power", value="250", unit="kVA", evidence="250 kVA"),
        ],
    )
    q_str = build_bm25_query(req)
    assert "Distribution Transformer" in q_str
    assert "Electrical" in q_str
    assert "voltage 11 kV" in q_str
    assert "power 250 kVA" in q_str
