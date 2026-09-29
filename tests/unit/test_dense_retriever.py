"""
tests/unit/test_dense_retriever.py
==================================

Unit tests for Dense semantic retriever:
- 91 standards indexed
- Embedding dimension consistency (384)
- Deterministic inference
- Top-K adherence
- Unique candidate outputs
- Safe handling of sparse queries
"""

import pytest
import numpy as np
from backend.extraction.schemas import ProcurementRequirements, ExtractedField
from backend.retrieval.dense_retriever import DenseRetriever, build_dense_query


@pytest.fixture(scope="module")
def dense_retriever():
    return DenseRetriever()


def test_dense_indexes_all_91_standards(dense_retriever):
    """Ensure exactly 91 standards are loaded and indexed."""
    assert len(dense_retriever.documents) == 91
    assert dense_retriever.embeddings.shape[0] == 91


def test_dense_embedding_dimension_is_384(dense_retriever):
    """Sentence-transformers all-MiniLM-L6-v2 dimension must be exactly 384."""
    assert dense_retriever.embeddings.shape[1] == 384


def test_dense_deterministic_ranking(dense_retriever):
    """Dense retrieval must yield deterministic rankings on identical inputs."""
    req = ProcurementRequirements(
        query_id="test_det",
        product=ExtractedField(value="Submersible pump"),
        sector=ExtractedField(value="Pumps"),
    )
    run1 = dense_retriever.retrieve(req, top_k=10)
    run2 = dense_retriever.retrieve(req, top_k=10)

    assert len(run1) == 10
    assert [c.standard_id for c in run1] == [c.standard_id for c in run2]
    assert np.allclose([c.dense_score for c in run1], [c.dense_score for c in run2], atol=1e-4)


def test_dense_respects_top_k(dense_retriever):
    """Retriever must return exactly top_k results."""
    req = ProcurementRequirements(
        query_id="test_k",
        product=ExtractedField(value="fire safety helmet"),
    )
    for k in [1, 5, 10, 20]:
        cands = dense_retriever.retrieve(req, top_k=k)
        assert len(cands) == k


def test_dense_no_duplicate_candidates(dense_retriever):
    """Candidate standard IDs must be unique."""
    req = ProcurementRequirements(
        query_id="test_dup",
        product=ExtractedField(value="plywood and composite panels"),
    )
    cands = dense_retriever.retrieve(req, top_k=20)
    ids = [c.standard_id for c in cands]
    assert len(ids) == len(set(ids))


def test_dense_empty_requirements_handling(dense_retriever):
    """Empty requirements must return valid candidates without crashing."""
    req = ProcurementRequirements(query_id="empty_req")
    cands = dense_retriever.retrieve(req, top_k=5)
    assert len(cands) == 5
    assert all(c.dense_score is not None for c in cands)
