"""
tests/unit/test_reranker.py
===========================

Unit tests for Cross-Encoder reranker:
- Deterministic score calculation and ranking
- Handles empty candidate lists
- Preserves candidate metadata while setting final_rank
- Top-K adherence
"""

import pytest
from backend.retrieval.reranker import CrossEncoderReranker
from backend.retrieval.schemas import RetrievalCandidate


@pytest.fixture(scope="module")
def reranker():
    return CrossEncoderReranker()


def test_reranker_deterministic_scoring(reranker):
    """Reranker must output identical scores and ranks on identical input."""
    query = "Supply of ordinary portland cement for structural construction"
    cands = [
        RetrievalCandidate(
            standard_id="is_269",
            is_number="IS 269",
            title="Ordinary Portland Cement",
            rrf_rank=1,
            final_rank=1,
        ),
        RetrievalCandidate(
            standard_id="is_455",
            is_number="IS 455",
            title="Portland Slag Cement",
            rrf_rank=2,
            final_rank=2,
        ),
    ]

    run1 = reranker.rerank(query, cands, top_k=2)
    run2 = reranker.rerank(query, cands, top_k=2)

    assert [c.standard_id for c in run1] == [c.standard_id for c in run2]
    assert [c.reranker_score for c in run1] == [c.reranker_score for c in run2]
    assert [c.final_rank for c in run1] == [1, 2]


def test_reranker_respects_top_k(reranker):
    """Reranker must return exactly top_k results."""
    query = "Electrical cables for domestic wiring"
    cands = [
        RetrievalCandidate(
            standard_id="is_694",
            is_number="IS 694",
            title="PVC Insulated Cables",
            rrf_rank=1,
            final_rank=1,
        ),
        RetrievalCandidate(
            standard_id="is_17293_2020",
            is_number="IS 17293:2020",
            title="Electric Cable for Photovoltaic Systems",
            rrf_rank=2,
            final_rank=2,
        ),
        RetrievalCandidate(
            standard_id="is_17505_part_1_2021",
            is_number="IS 17505 (Part 1):2021",
            title="Thermosetting Insulated, Fire Survival Cables",
            rrf_rank=3,
            final_rank=3,
        ),
    ]

    reranked = reranker.rerank(query, cands, top_k=2)
    assert len(reranked) == 2
    assert reranked[0].final_rank == 1
    assert reranked[1].final_rank == 2


def test_reranker_empty_candidates_handling(reranker):
    """Reranker handles empty list safely."""
    reranked = reranker.rerank("Some query", [], top_k=5)
    assert reranked == []
