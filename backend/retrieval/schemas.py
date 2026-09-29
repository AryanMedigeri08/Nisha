"""
backend/retrieval/schemas.py
============================

Pydantic schemas for the Phase 4 Hybrid Retrieval Engine.
Defines data structures for standard documents, retrieval candidates,
fused results, and index metadata.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class StandardDocument(BaseModel):
    """Canonical searchable representation for an Indian Standard."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    title: str
    sector: Optional[str] = None
    application: List[str] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    technical_parameters: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    status: Optional[str] = None
    qco_or_regulatory_order: Optional[str] = None
    searchable_text: str = ""

    def build_searchable_text(self) -> str:
        """Deterministic searchable text representation."""
        lines = [
            f"IS NUMBER:\n{self.is_number}",
            f"\nTITLE:\n{self.title}",
            f"\nSECTOR:\n{self.sector or 'None'}",
        ]
        
        app_str = ", ".join(self.application) if self.application else "None"
        lines.append(f"\nAPPLICATION:\n{app_str}")

        mat_str = ", ".join(self.materials) if self.materials else "None"
        lines.append(f"\nMATERIALS:\n{mat_str}")

        param_str = ", ".join(self.technical_parameters) if self.technical_parameters else "None"
        lines.append(f"\nTECHNICAL PARAMETERS:\n{param_str}")

        if self.references:
            lines.append(f"\nREFERENCES:\n{', '.join(self.references)}")
            
        return "\n".join(lines).strip()


class RetrievalCandidate(BaseModel):
    """Ranked standard candidate with multi-stage ranking details."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    title: str
    sector: Optional[str] = None
    bm25_rank: Optional[int] = None
    bm25_score: Optional[float] = None
    dense_rank: Optional[int] = None
    dense_score: Optional[float] = None
    rrf_rank: Optional[int] = None
    rrf_score: Optional[float] = None
    reranker_score: Optional[float] = None
    final_rank: int = 1


class RetrievalResult(BaseModel):
    """Complete retrieval result containing final candidates and intermediate candidate sets."""
    model_config = ConfigDict(extra="ignore")

    query_id: str
    query_text: Optional[str] = None
    candidates: List[RetrievalCandidate] = Field(default_factory=list)
    bm25_candidates: List[RetrievalCandidate] = Field(default_factory=list)
    dense_candidates: List[RetrievalCandidate] = Field(default_factory=list)
    rrf_candidates: List[RetrievalCandidate] = Field(default_factory=list)


class IndexMetadata(BaseModel):
    """Metadata detailing the search index configuration, models, and dimensions."""
    model_config = ConfigDict(extra="ignore")

    index_version: str
    created_at: str
    standard_count: int
    embedding_model: str
    embedding_dimension: int
    reranker_model: str
    bm25_top_k: int = 20
    dense_top_k: int = 20
    rrf_k: int = 60
    rrf_top_k: int = 20
    final_top_k: int = 10
