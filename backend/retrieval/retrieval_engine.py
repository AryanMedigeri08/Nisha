"""
backend/retrieval/retrieval_engine.py
=====================================

Integrated Hybrid Retrieval Engine for PS26108.
Coordinates BM25 sparse retrieval, dense semantic retrieval,
Reciprocal Rank Fusion (RRF), and Cross-Encoder reranking.

Strict Rule Enforcement:
- NO access to ground-truth labels during inference.
- Purely consumes extracted requirements and unlabelled query text.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from backend.extraction.schemas import ProcurementRequirements
from backend.retrieval.bm25_retriever import BM25Retriever
from backend.retrieval.dense_retriever import DenseRetriever, build_dense_query
from backend.retrieval.reranker import CrossEncoderReranker
from backend.retrieval.rrf import fuse_rrf
from backend.retrieval.schemas import (
    RetrievalCandidate,
    RetrievalResult,
    StandardDocument,
)

logger = logging.getLogger(__name__)

DEFAULT_BM25_TOP_K = 20
DEFAULT_DENSE_TOP_K = 20
DEFAULT_RRF_K = 60
DEFAULT_RRF_TOP_K = 20
DEFAULT_FINAL_TOP_K = 10


class RetrievalEngine:
    """Unified hybrid retrieval and reranking engine."""

    def __init__(
        self,
        corpus_path: Optional[Path] = None,
        embeddings_path: Optional[Path] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        dense_retriever: Optional[DenseRetriever] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        bm25_top_k: int = DEFAULT_BM25_TOP_K,
        dense_top_k: int = DEFAULT_DENSE_TOP_K,
        rrf_k: int = DEFAULT_RRF_K,
        rrf_top_k: int = DEFAULT_RRF_TOP_K,
        final_top_k: int = DEFAULT_FINAL_TOP_K,
    ):
        self.bm25_retriever = bm25_retriever or BM25Retriever(corpus_path=corpus_path)
        self.dense_retriever = dense_retriever or DenseRetriever(
            corpus_path=corpus_path, embeddings_path=embeddings_path
        )
        self.reranker = reranker or CrossEncoderReranker(corpus_path=corpus_path)

        self.bm25_top_k = bm25_top_k
        self.dense_top_k = dense_top_k
        self.rrf_k = rrf_k
        self.rrf_top_k = rrf_top_k
        self.final_top_k = final_top_k

    def retrieve_bm25(
        self,
        requirements: ProcurementRequirements,
        top_k: Optional[int] = None,
    ) -> List[RetrievalCandidate]:
        """Sparse lexical retrieval."""
        k = top_k if top_k is not None else self.bm25_top_k
        return self.bm25_retriever.retrieve(requirements, top_k=k)

    def retrieve_dense(
        self,
        requirements: ProcurementRequirements,
        top_k: Optional[int] = None,
    ) -> List[RetrievalCandidate]:
        """Dense semantic retrieval."""
        k = top_k if top_k is not None else self.dense_top_k
        return self.dense_retriever.retrieve(requirements, top_k=k)

    def fuse_rrf(
        self,
        bm25_candidates: List[RetrievalCandidate],
        dense_candidates: List[RetrievalCandidate],
        k: Optional[int] = None,
        top_k: Optional[int] = None,
    ) -> List[RetrievalCandidate]:
        """Reciprocal Rank Fusion of sparse and dense candidates."""
        rrf_k = k if k is not None else self.rrf_k
        target_top_k = top_k if top_k is not None else self.rrf_top_k
        return fuse_rrf(bm25_candidates, dense_candidates, k=rrf_k, top_k=target_top_k)

    def rerank_cross_encoder(
        self,
        query_text: str,
        candidates: List[RetrievalCandidate],
        top_k: Optional[int] = None,
    ) -> List[RetrievalCandidate]:
        """Cross-Encoder reranking of top candidate pool."""
        target_top_k = top_k if top_k is not None else self.final_top_k
        return self.reranker.rerank(query_text, candidates, top_k=target_top_k)

    def retrieve(
        self,
        requirements: ProcurementRequirements,
        query_text: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RetrievalResult:
        """
        Execute full end-to-end hybrid retrieval:
        1. BM25 sparse retrieval (top 20)
        2. Dense vector retrieval (top 20)
        3. Reciprocal Rank Fusion (top 20)
        4. Cross-Encoder reranking (top 10)
        """
        target_final_k = top_k if top_k is not None else self.final_top_k

        # 1. BM25
        bm25_cands = self.retrieve_bm25(requirements, top_k=self.bm25_top_k)

        # 2. Dense
        dense_cands = self.retrieve_dense(requirements, top_k=self.dense_top_k)

        # 3. RRF Fusion
        rrf_cands = self.fuse_rrf(
            bm25_cands, dense_cands, k=self.rrf_k, top_k=self.rrf_top_k
        )

        # 4. Cross-Encoder Reranking
        rerank_query = query_text or build_dense_query(requirements)
        final_candidates = self.rerank_cross_encoder(
            rerank_query, rrf_cands, top_k=target_final_k
        )

        return RetrievalResult(
            query_id=requirements.query_id,
            query_text=query_text,
            candidates=final_candidates,
            bm25_candidates=bm25_cands,
            dense_candidates=dense_cands,
            rrf_candidates=rrf_cands,
        )
