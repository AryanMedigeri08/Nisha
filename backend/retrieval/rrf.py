"""
backend/retrieval/rrf.py
========================

Reciprocal Rank Fusion (RRF) for combining sparse lexical (BM25) and dense semantic rankings.
Implements RRF(d) = sum(1 / (k + rank(d))) with configurable k and deterministic tie-breaking.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from backend.retrieval.schemas import RetrievalCandidate

logger = logging.getLogger(__name__)

DEFAULT_RRF_K = 60
DEFAULT_RRF_TOP_K = 20


def fuse_rrf(
    bm25_candidates: List[RetrievalCandidate],
    dense_candidates: List[RetrievalCandidate],
    k: int = DEFAULT_RRF_K,
    top_k: int = DEFAULT_RRF_TOP_K,
) -> List[RetrievalCandidate]:
    """
    Fuse BM25 and Dense candidate lists using Reciprocal Rank Fusion.
    
    Formula:
        RRF_score(d) = sum_{system} 1 / (k + rank_{system}(d))

    Handles documents appearing in only one retriever list.
    Ties are broken deterministically by standard_id.
    """
    # Track accumulated scores and metadata per standard_id
    scores: Dict[str, float] = {}
    candidate_meta: Dict[str, Dict] = {}

    # Process BM25 candidates
    for rank, cand in enumerate(bm25_candidates, start=1):
        std_id = cand.standard_id
        scores[std_id] = scores.get(std_id, 0.0) + (1.0 / (k + rank))
        if std_id not in candidate_meta:
            candidate_meta[std_id] = {
                "standard_id": std_id,
                "is_number": cand.is_number,
                "title": cand.title,
                "sector": cand.sector,
                "bm25_rank": rank,
                "bm25_score": cand.bm25_score,
                "dense_rank": None,
                "dense_score": None,
            }
        else:
            candidate_meta[std_id]["bm25_rank"] = rank
            candidate_meta[std_id]["bm25_score"] = cand.bm25_score

    # Process Dense candidates
    for rank, cand in enumerate(dense_candidates, start=1):
        std_id = cand.standard_id
        scores[std_id] = scores.get(std_id, 0.0) + (1.0 / (k + rank))
        if std_id not in candidate_meta:
            candidate_meta[std_id] = {
                "standard_id": std_id,
                "is_number": cand.is_number,
                "title": cand.title,
                "sector": cand.sector,
                "bm25_rank": None,
                "bm25_score": None,
                "dense_rank": rank,
                "dense_score": cand.dense_score,
            }
        else:
            candidate_meta[std_id]["dense_rank"] = rank
            candidate_meta[std_id]["dense_score"] = cand.dense_score

    # Deterministic sort: descending by rrf_score, ascending by standard_id
    sorted_std_ids = sorted(scores.keys(), key=lambda sid: (-scores[sid], sid))

    fused_candidates: List[RetrievalCandidate] = []
    for rank, std_id in enumerate(sorted_std_ids[:top_k], start=1):
        meta = candidate_meta[std_id]
        fused_candidates.append(
            RetrievalCandidate(
                standard_id=meta["standard_id"],
                is_number=meta["is_number"],
                title=meta["title"],
                sector=meta["sector"],
                bm25_rank=meta["bm25_rank"],
                bm25_score=meta["bm25_score"],
                dense_rank=meta["dense_rank"],
                dense_score=meta["dense_score"],
                rrf_rank=rank,
                rrf_score=round(scores[std_id], 6),
                final_rank=rank,
            )
        )

    return fused_candidates
