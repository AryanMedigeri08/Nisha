"""
backend/retrieval/index_builder.py
==================================

Builds the canonical searchable representation and embeddings for all 91 seed Indian Standards.
Saves canonical document corpora, dense embedding matrices, and index metadata.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, Reference
from backend.retrieval.schemas import StandardDocument, IndexMetadata

logger = logging.getLogger(__name__)

DEFAULT_INDEX_VERSION = "v1.0.0"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_BM25_TOP_K = 20
DEFAULT_DENSE_TOP_K = 20
DEFAULT_RRF_K = 60
DEFAULT_RRF_TOP_K = 20
DEFAULT_FINAL_TOP_K = 10


def tokenize_text(text: str) -> List[str]:
    """Deterministic tokenization for lexical search (lowercase alphanumeric words)."""
    return re.findall(r"\b[a-zA-Z0-9_\-\./]+\b", text.lower())


class SearchIndexBuilder:
    """Builds and serializes canonical search documents and dense embeddings."""

    def __init__(
        self,
        index_dir: Optional[Path] = None,
        embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
        reranker_model_name: str = DEFAULT_RERANKER_MODEL,
        index_version: str = DEFAULT_INDEX_VERSION,
    ):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.index_dir = index_dir or (self.project_root / "data" / "index")
        self.embedding_model_name = embedding_model_name
        self.reranker_model_name = reranker_model_name
        self.index_version = index_version
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def load_standards_from_db(self) -> List[StandardDocument]:
        """Load all 91 standards and verified references from the authoritative database."""
        session = SessionLocal()
        try:
            standards = session.query(Standard).order_by(Standard.id).all()
            references = session.query(Reference).all()

            # Map references by source standard id
            ref_map: Dict[int, List[str]] = {}
            for ref in references:
                source_id = ref.source_standard_id
                target_std = ref.target_standard
                ref_str = f"{target_std.is_number} ({ref.reference_type})" if target_std else ""
                if ref_str:
                    ref_map.setdefault(source_id, []).append(ref_str)

            docs: List[StandardDocument] = []
            for std in standards:
                # Application list
                app_list = [std.application] if std.application else []
                # Materials list
                mat_list = std.materials if isinstance(std.materials, list) else []
                # Technical parameters
                param_list = std.technical_parameters if isinstance(std.technical_parameters, list) else []
                # Verified references
                refs = ref_map.get(std.id, [])

                doc = StandardDocument(
                    standard_id=std.standard_id,
                    is_number=std.is_number,
                    title=std.title,
                    sector=std.sector,
                    application=app_list,
                    materials=mat_list,
                    technical_parameters=param_list,
                    references=refs,
                    year=std.year,
                    status=std.status,
                    qco_or_regulatory_order=std.qco_or_regulatory_order,
                )
                doc.searchable_text = doc.build_searchable_text()
                docs.append(doc)

            return docs
        finally:
            session.close()

    def build_and_save_index(self) -> Tuple[IndexMetadata, float]:
        """
        Build and persist:
          - data/index/standards_corpus.json
          - data/index/standard_embeddings.npy
          - data/index/retrieval_index_metadata.json
        Returns (IndexMetadata, build_time_seconds).
        """
        start_time = time.perf_counter()

        logger.info("Loading standards from database...")
        docs = self.load_standards_from_db()
        if len(docs) != 91:
            raise ValueError(f"Expected 91 seed standards, found {len(docs)}")

        # Check uniqueness of standard_ids
        std_ids = [d.standard_id for d in docs]
        if len(std_ids) != len(set(std_ids)):
            raise ValueError("Duplicate standard_id detected in seed standards")

        # Save canonical corpus
        corpus_path = self.index_dir / "standards_corpus.json"
        with open(corpus_path, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in docs], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d standard documents to %s", len(docs), corpus_path)

        # Generate dense embeddings
        logger.info("Loading embedding model %s...", self.embedding_model_name)
        embed_model = SentenceTransformer(self.embedding_model_name)
        texts_to_embed = [d.searchable_text for d in docs]

        logger.info("Generating embeddings for 91 standards...")
        embeddings = embed_model.encode(
            texts_to_embed,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        embeddings = embeddings.astype(np.float32)

        # Save embeddings
        embeddings_path = self.index_dir / "standard_embeddings.npy"
        np.save(embeddings_path, embeddings)
        logger.info("Saved embeddings shape %s to %s", embeddings.shape, embeddings_path)

        build_time = time.perf_counter() - start_time

        # Metadata
        metadata = IndexMetadata(
            index_version=self.index_version,
            created_at=datetime.now(timezone.utc).isoformat(),
            standard_count=len(docs),
            embedding_model=self.embedding_model_name,
            embedding_dimension=int(embeddings.shape[1]),
            reranker_model=self.reranker_model_name,
            bm25_top_k=DEFAULT_BM25_TOP_K,
            dense_top_k=DEFAULT_DENSE_TOP_K,
            rrf_k=DEFAULT_RRF_K,
            rrf_top_k=DEFAULT_RRF_TOP_K,
            final_top_k=DEFAULT_FINAL_TOP_K,
        )

        metadata_path = self.index_dir / "retrieval_index_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(), f, indent=2)
        logger.info("Saved index metadata to %s in %.2fs", metadata_path, build_time)

        return metadata, build_time
