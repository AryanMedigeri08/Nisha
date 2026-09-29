"""
backend/retrieval/bm25_retriever.py
===================================

BM25 lexical sparse retriever for Indian Standards.
Uses rank_bm25.BM25Okapi with deterministic query construction from
Phase 3 extracted procurement requirements.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rank_bm25 import BM25Okapi

from backend.extraction.schemas import ProcurementRequirements
from backend.retrieval.schemas import StandardDocument, RetrievalCandidate

logger = logging.getLogger(__name__)


def tokenize_text(text: str) -> List[str]:
    """Deterministic tokenization for BM25 (lowercase alphanumeric words)."""
    if not text:
        return []
    return re.findall(r"\b[a-zA-Z0-9_\-\./]+\b", text.lower())


def build_bm25_query(req: ProcurementRequirements) -> str:
    """
    Construct sparse retrieval query from Phase 3 extraction output.
    Format: product + sector + applications + materials + parameters + safety/elec/mech.
    Preserves technical values and units.
    """
    parts: List[str] = []

    if req.product and req.product.value:
        parts.append(req.product.value)

    if req.sector and req.sector.value:
        parts.append(req.sector.value)

    for app in req.application:
        if app.value:
            parts.append(app.value)

    for mat in req.materials:
        if mat.value:
            parts.append(mat.value)

    for param in req.parameters:
        param_str = f"{param.name} {param.value}"
        if param.unit:
            param_str += f" {param.unit}"
        parts.append(param_str)

    for s in req.safety_requirements:
        if s.value:
            parts.append(s.value)

    for e in req.electrical_requirements:
        if e.value:
            parts.append(e.value)

    for m in req.mechanical_requirements:
        if m.value:
            parts.append(m.value)

    return " ".join(parts).strip()


class BM25Retriever:
    """Sparse lexical retriever using BM25Okapi over the Indian Standards corpus."""

    def __init__(
        self,
        corpus_path: Optional[Path] = None,
        documents: Optional[List[StandardDocument]] = None,
    ):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.corpus_path = corpus_path or (self.project_root / "data" / "index" / "standards_corpus.json")

        if documents is not None:
            self.documents = documents
        else:
            self.documents = self._load_corpus()

        self.doc_map: Dict[str, StandardDocument] = {doc.standard_id: doc for doc in self.documents}
        self.tokenized_corpus = [tokenize_text(doc.searchable_text) for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def _load_corpus(self) -> List[StandardDocument]:
        """Load canonical standards corpus from JSON."""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}. Run index builder first.")
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [StandardDocument(**item) for item in data]

    def retrieve(
        self,
        requirements: ProcurementRequirements,
        top_k: int = 20,
    ) -> List[RetrievalCandidate]:
        """
        Retrieve top_k candidates for the given structured requirements.
        Ties are broken deterministically by standard_id.
        """
        query_str = build_bm25_query(requirements)
        tokenized_query = tokenize_text(query_str)

        if not tokenized_query:
            # Fallback if query extraction was completely empty
            tokenized_query = ["is", "standard"]

        scores = self.bm25.get_scores(tokenized_query)

        # Pair with standard_ids
        scored_docs: List[Tuple[float, str, StandardDocument]] = []
        for score, doc in zip(scores, self.documents):
            scored_docs.append((float(score), doc.standard_id, doc))

        # Deterministic sort: descending by score, ascending by standard_id
        scored_docs.sort(key=lambda x: (-x[0], x[1]))

        candidates: List[RetrievalCandidate] = []
        for rank, (score, std_id, doc) in enumerate(scored_docs[:top_k], start=1):
            candidates.append(
                RetrievalCandidate(
                    standard_id=doc.standard_id,
                    is_number=doc.is_number,
                    title=doc.title,
                    sector=doc.sector,
                    bm25_rank=rank,
                    bm25_score=round(score, 4),
                    final_rank=rank,
                )
            )

        return candidates
