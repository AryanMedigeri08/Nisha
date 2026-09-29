"""
backend/retrieval
=================

Phase 4 Hybrid Retrieval Engine package for PS26108.
Provides sparse (BM25) and dense (SentenceTransformer) retrieval,
Reciprocal Rank Fusion (RRF), and Cross-Encoder reranking.
"""

from backend.retrieval.schemas import (
    StandardDocument,
    RetrievalCandidate,
    RetrievalResult,
    IndexMetadata,
)
from backend.retrieval.bm25_retriever import BM25Retriever
from backend.retrieval.dense_retriever import DenseRetriever
from backend.retrieval.rrf import fuse_rrf
from backend.retrieval.reranker import CrossEncoderReranker
from backend.retrieval.retrieval_engine import RetrievalEngine

__all__ = [
    "StandardDocument",
    "RetrievalCandidate",
    "RetrievalResult",
    "IndexMetadata",
    "BM25Retriever",
    "DenseRetriever",
    "fuse_rrf",
    "CrossEncoderReranker",
    "RetrievalEngine",
]
