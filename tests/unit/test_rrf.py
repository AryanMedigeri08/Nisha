"""
tests/unit/test_rrf.py
======================

Unit tests for Reciprocal Rank Fusion (RRF):
- Mathematical correctness of RRF scoring: 1 / (k + rank)
- Fusing intersecting and disjoint candidate lists
- Handling candidates appearing in only one retriever
- Deterministic tie-breaking
- Preservation of intermediate rank metadata
- Top-K truncation
"""

import pytest
from backend.retrieval.rrf import fuse_rrf, DEFAULT_RRF_K
from backend.retrieval.schemas import RetrievalCandidate


def make_cand(std_id: str, title: str = "Test", rank: int = 1, score: float = 1.0) -> RetrievalCandidate:
    return RetrievalCandidate(
        standard_id=std_id,
        is_number=f"IS {std_id.upper()}",
        title=title,
        bm25_rank=rank,
        bm25_score=score,
        dense_rank=rank,
        dense_score=score,
        final_rank=rank,
    )


def test_rrf_mathematical_formula():
    """Verify RRF score matches 1 / (k + r1) + 1 / (k + r2)."""
    k = 60
    # Candidate appearing at rank 1 in both BM25 and Dense
    c1_bm25 = make_cand("std_1", rank=1)
    c1_dense = make_cand("std_1", rank=1)

    # Candidate appearing at rank 2 in BM25, not in Dense
    c2_bm25 = make_cand("std_2", rank=2)

    fused = fuse_rrf([c1_bm25, c2_bm25], [c1_dense], k=k, top_k=2)

    expected_score_1 = (1.0 / (60 + 1)) + (1.0 / (60 + 1))  # 2 / 61 = 0.032787
    expected_score_2 = 1.0 / (60 + 2)                        # 1 / 62 = 0.016129

    assert len(fused) == 2
    assert fused[0].standard_id == "std_1"
    assert pytest.approx(fused[0].rrf_score, abs=1e-5) == round(expected_score_1, 6)
    assert fused[1].standard_id == "std_2"
    assert pytest.approx(fused[1].rrf_score, abs=1e-5) == round(expected_score_2, 6)


def test_rrf_handles_disjoint_retrievers():
    """Candidates appearing only in one retriever must be fused cleanly."""
    bm25_cands = [make_cand("bm_only_1", rank=1), make_cand("bm_only_2", rank=2)]
    dense_cands = [make_cand("dense_only_1", rank=1), make_cand("dense_only_2", rank=2)]

    fused = fuse_rrf(bm25_cands, dense_cands, k=60, top_k=4)

    assert len(fused) == 4
    # rank 1 for both gives score 1/61; tie broken alphabetically: "bm_only_1" vs "dense_only_1"
    assert fused[0].standard_id == "bm_only_1"
    assert fused[1].standard_id == "dense_only_1"
    assert fused[0].rrf_score == fused[1].rrf_score


def test_rrf_deterministic_tie_breaking():
    """Ties in score must be broken deterministically by standard_id."""
    c_b = make_cand("std_b", rank=1)
    c_a = make_cand("std_a", rank=1)

    # c_b is rank 1 in bm25, c_a is rank 1 in dense -> both have score 1/(60+1)
    fused = fuse_rrf([c_b], [c_a], k=60, top_k=2)
    # Both have identical score 1/61; tie broken alphabetically: std_a should precede std_b
    assert fused[0].standard_id == "std_a"
    assert fused[1].standard_id == "std_b"
    assert fused[0].rrf_score == fused[1].rrf_score


def test_rrf_preserves_retrieval_metadata():
    """Fused candidates must retain their original BM25 and dense ranks."""
    bm25 = [make_cand("std_x", rank=3, score=12.5)]
    dense = [make_cand("std_x", rank=5, score=0.88)]

    fused = fuse_rrf(bm25, dense, k=60, top_k=1)
    assert len(fused) == 1
    assert fused[0].bm25_rank == 1  # 1st in bm25 list
    assert fused[0].dense_rank == 1  # 1st in dense list
    assert fused[0].bm25_score == 12.5
    assert fused[0].dense_score == 0.88
    assert fused[0].rrf_rank == 1


def test_rrf_respects_top_k():
    """RRF must truncate output strictly to requested top_k."""
    bm25 = [make_cand(f"std_{i}", rank=i) for i in range(1, 15)]
    dense = [make_cand(f"std_{i+10}", rank=i) for i in range(1, 15)]

    fused = fuse_rrf(bm25, dense, top_k=5)
    assert len(fused) == 5
