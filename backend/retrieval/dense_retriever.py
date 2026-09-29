"""
backend/retrieval/dense_retriever.py
====================================

Dense semantic retriever for Indian Standards.
Uses sentence-transformers/all-MiniLM-L6-v2 to embed extracted requirements
and compute cosine similarity over pre-computed standard profile embeddings.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.extraction.schemas import ProcurementRequirements
from backend.retrieval.schemas import StandardDocument, RetrievalCandidate

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_dense_query(req: ProcurementRequirements) -> str:
    """
    Construct semantic query representation from Phase 3 extraction output.
    Formats extracted fields into natural semantic text for embedding.
    """
    parts: List[str] = []

    if req.product and req.product.value:
        parts.append(f"Product: {req.product.value}")

    if req.sector and req.sector.value:
        parts.append(f"Sector: {req.sector.value}")

    apps = [a.value for a in req.application if a.value]
    if apps:
        parts.append(f"Application: {', '.join(apps)}")

    mats = [m.value for m in req.materials if m.value]
    if mats:
        parts.append(f"Materials: {', '.join(mats)}")

    params: List[str] = []
    for p in req.parameters:
        p_str = f"{p.name}: {p.value}"
        if p.unit:
            p_str += f" {p.unit}"
        params.append(p_str)
    if params:
        parts.append(f"Technical parameters: {', '.join(params)}")

    if not parts:
        return "Indian Standard procurement specification"

    return ". ".join(parts).strip()


class DenseRetriever:
    """Dense vector retriever using SentenceTransformer embeddings."""

    def __init__(
        self,
        corpus_path: Optional[Path] = None,
        embeddings_path: Optional[Path] = None,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        model: Optional[SentenceTransformer] = None,
    ):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.corpus_path = corpus_path or (self.project_root / "data" / "index" / "standards_corpus.json")
        self.embeddings_path = embeddings_path or (self.project_root / "data" / "index" / "standard_embeddings.npy")
        self.model_name = model_name

        self.documents = self._load_corpus()
        self.embeddings = self._load_embeddings()

        if len(self.documents) != len(self.embeddings):
            raise ValueError(
                f"Mismatch between documents count ({len(self.documents)}) and embeddings count ({len(self.embeddings)})"
            )

        if model is not None:
            self.model = model
        else:
            self.model = SentenceTransformer(self.model_name)

    def _load_corpus(self) -> List[StandardDocument]:
        """Load canonical standards corpus."""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}. Run index builder first.")
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [StandardDocument(**item) for item in data]

    def _load_embeddings(self) -> np.ndarray:
        """Load pre-computed numpy embeddings."""
        if not self.embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {self.embeddings_path}. Run index builder first.")
        embs = np.load(self.embeddings_path)
        # Ensure unit normalization for cosine similarity via dot product
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (embs / norms).astype(np.float32)

    def retrieve(
        self,
        requirements: ProcurementRequirements,
        top_k: int = 20,
    ) -> List[RetrievalCandidate]:
        """
        Retrieve top_k candidates using dense semantic similarity.
        Ties are broken deterministically by standard_id.
        """
        query_str = build_dense_query(requirements)
        query_emb = self.model.encode(
            [query_str],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].astype(np.float32)

        # Cosine similarity via dot product
        scores = np.dot(self.embeddings, query_emb)

        scored_docs: List[Tuple[float, str, StandardDocument]] = []
        for score, doc in zip(scores, self.documents):
            scored_docs.append((float(score), doc.standard_id, doc))

        # Deterministic sort: descending score, ascending standard_id
        scored_docs.sort(key=lambda x: (-x[0], x[1]))

        candidates: List[RetrievalCandidate] = []
        for rank, (score, std_id, doc) in enumerate(scored_docs[:top_k], start=1):
            candidates.append(
                RetrievalCandidate(
                    standard_id=doc.standard_id,
                    is_number=doc.is_number,
                    title=doc.title,
                    sector=doc.sector,
                    dense_rank=rank,
                    dense_score=round(score, 4),
                    final_rank=rank,
                )
            )

        return candidates
