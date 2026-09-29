"""
backend/retrieval/reranker.py
=============================

Cross-Encoder reranker for refining candidate orderings from Reciprocal Rank Fusion.
Uses cross-encoder/ms-marco-MiniLM-L-6-v2 to evaluate (query, standard) pairs.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sentence_transformers import CrossEncoder

from backend.retrieval.schemas import StandardDocument, RetrievalCandidate

logger = logging.getLogger(__name__)

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_FINAL_TOP_K = 10


def format_standard_for_reranking(doc: StandardDocument) -> str:
    """Deterministic, rich text representation of standard candidate for cross-encoder."""
    parts = [f"{doc.is_number}: {doc.title}"]
    if doc.sector:
        parts.append(f"Sector: {doc.sector}")
    if doc.application:
        parts.append(f"Applications: {', '.join(doc.application)}")
    if doc.materials:
        parts.append(f"Materials: {', '.join(doc.materials)}")
    if doc.technical_parameters:
        parts.append(f"Parameters: {', '.join(doc.technical_parameters)}")
    return ". ".join(parts).strip()


class CrossEncoderReranker:
    """Reranks candidates using a cross-encoder model."""

    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
        corpus_path: Optional[Path] = None,
        model: Optional[CrossEncoder] = None,
    ):
        self.model_name = model_name
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.corpus_path = corpus_path or (self.project_root / "data" / "index" / "standards_corpus.json")

        self.documents = self._load_corpus()
        self.doc_map: Dict[str, StandardDocument] = {d.standard_id: d for d in self.documents}

        if model is not None:
            self.model = model
        else:
            self.model = CrossEncoder(self.model_name)

    def _load_corpus(self) -> List[StandardDocument]:
        """Load canonical standards corpus."""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}. Run index builder first.")
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [StandardDocument(**item) for item in data]

    def rerank(
        self,
        query_text: str,
        candidates: List[RetrievalCandidate],
        top_k: int = DEFAULT_FINAL_TOP_K,
    ) -> List[RetrievalCandidate]:
        """
        Rerank candidates using cross-encoder score.
        query_text: query representation or procurement text.
        candidates: RRF candidates (up to top_k or 20).
        Returns top_k reranked candidates with final_rank assigned.
        """
        if not candidates:
            return []

        pairs: List[Tuple[str, str]] = []
        valid_candidates: List[RetrievalCandidate] = []

        for cand in candidates:
            doc = self.doc_map.get(cand.standard_id)
            if doc:
                std_text = format_standard_for_reranking(doc)
            else:
                std_text = f"{cand.is_number}: {cand.title}"
            pairs.append((query_text, std_text))
            valid_candidates.append(cand)

        if not pairs:
            return candidates[:top_k]

        scores = self.model.predict(pairs, batch_size=64, show_progress_bar=False)

        # Pair scores with candidate objects
        scored_candidates: List[Tuple[float, str, RetrievalCandidate]] = []
        for score, cand in zip(scores, valid_candidates):
            cand_copy = cand.model_copy()
            cand_copy.reranker_score = round(float(score), 4)
            scored_candidates.append((float(score), cand_copy.standard_id, cand_copy))

        # Deterministic sort: descending score, ascending standard_id
        scored_candidates.sort(key=lambda x: (-x[0], x[1]))

        final_list: List[RetrievalCandidate] = []
        for rank, (_, _, cand) in enumerate(scored_candidates[:top_k], start=1):
            cand.final_rank = rank
            final_list.append(cand)

        return final_list
