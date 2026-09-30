"""
backend/review/comparison.py
============================

Candidate Comparison Engine for PS26108 Phase 7.
Builds factual, side-by-side comparative matrices for 2-3 candidate standards
without creating arbitrary composite scores.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.models import ReviewCandidate, Review
from backend.review.schemas import (
    CandidateComparisonResponse,
    CandidateDTO,
    VerificationItemDTO,
    VerificationState,
)


class CandidateComparisonEngine:
    """Builds side-by-side factual comparisons of retrieved standards."""

    @classmethod
    def compare(
        cls,
        db: Session,
        review: Review,
        candidate_ids: List[int],
    ) -> CandidateComparisonResponse:
        """
        Produce a structured side-by-side comparison for selected candidates.
        """
        candidates: List[ReviewCandidate] = (
            db.query(ReviewCandidate)
            .filter(
                ReviewCandidate.review_id == review.id,
                ReviewCandidate.id.in_(candidate_ids),
            )
            .order_by(ReviewCandidate.retrieval_rank.asc())
            .all()
        )

        candidate_dtos: List[CandidateDTO] = []
        for c in candidates:
            # Map verification items for this candidate
            v_items = [
                VerificationItemDTO(
                    id=v.id,
                    review_id=v.review_id,
                    candidate_id=v.candidate_id,
                    standard_id=v.standard_id,
                    item_key=v.item_key,
                    title=v.title,
                    category=v.category,
                    system_state=v.system_state,
                    officer_state=VerificationState(v.officer_state),
                    is_regulatory=v.is_regulatory,
                    system_evidence=v.system_evidence,
                    officer_evidence_reference=v.officer_evidence_reference,
                    officer_note=v.officer_note,
                    verified_at=v.verified_at,
                    verified_by=v.verified_by,
                    created_at=v.created_at,
                )
                for v in review.verification_items
                if v.candidate_id == c.id or v.standard_id == c.standard_id
            ]

            candidate_dtos.append(
                CandidateDTO(
                    id=c.id,
                    review_id=c.review_id,
                    standard_id=c.standard_id,
                    is_number=c.is_number,
                    title=c.title,
                    sector=c.sector,
                    application=c.application,
                    materials=c.materials or [],
                    technical_parameters=c.technical_parameters or [],
                    retrieval_rank=c.retrieval_rank,
                    reranker_score=c.reranker_score,
                    rrf_score=c.rrf_score,
                    retrieval_method=c.retrieval_method or "hybrid_cross_encoder",
                    requirement_coverage=c.requirement_coverage,
                    gaps=c.gaps,
                    standard_status=c.standard_status,
                    qco_status=c.qco_status,
                    qco_ids=c.qco_ids or [],
                    order_names=c.order_names or [],
                    effective_date=c.effective_date,
                    authority=c.authority,
                    ai_recommendation_state=c.ai_recommendation_state,
                    notes=c.notes,
                    evidence=c.evidence,
                    normative_references=c.normative_references or [],
                    verification_items=v_items,
                )
            )

        # 1. Facet Comparison Matrix
        facet_comparison = cls._build_facet_matrix(candidate_dtos)

        # 2. Regulatory Comparison Matrix
        regulatory_comparison = cls._build_regulatory_matrix(candidate_dtos)

        # 3. Gaps Comparison Matrix
        gaps_comparison = cls._build_gaps_matrix(candidate_dtos)

        return CandidateComparisonResponse(
            review_id=review.review_id,
            candidates=candidate_dtos,
            facet_comparison=facet_comparison,
            regulatory_comparison=regulatory_comparison,
            gaps_comparison=gaps_comparison,
        )

    @classmethod
    def _build_facet_matrix(cls, candidates: List[CandidateDTO]) -> List[Dict[str, Any]]:
        """Construct dimension-by-dimension comparison table."""
        rows = [
            {"dimension": "IS Number", "values": {c.is_number: c.is_number for c in candidates}},
            {"dimension": "Standard Title", "values": {c.is_number: c.title for c in candidates}},
            {"dimension": "Sector", "values": {c.is_number: c.sector or "Unspecified" for c in candidates}},
            {"dimension": "Application Scope", "values": {c.is_number: c.application or "Unspecified" for c in candidates}},
            {
                "dimension": "Product Match Status",
                "values": {
                    c.is_number: (c.requirement_coverage.get("product", {}).get("status", "UNKNOWN") if c.requirement_coverage else "UNKNOWN")
                    for c in candidates
                },
            },
            {
                "dimension": "Direct Matches Count",
                "values": {
                    c.is_number: (c.requirement_coverage.get("direct_matches", 0) if c.requirement_coverage else 0)
                    for c in candidates
                },
            },
            {
                "dimension": "Partial Matches Count",
                "values": {
                    c.is_number: (c.requirement_coverage.get("partial_matches", 0) if c.requirement_coverage else 0)
                    for c in candidates
                },
            },
            {
                "dimension": "Unknown Facets Count",
                "values": {
                    c.is_number: (c.requirement_coverage.get("unknown_count", 0) if c.requirement_coverage else 0)
                    for c in candidates
                },
            },
            {
                "dimension": "Conflicts Count",
                "values": {
                    c.is_number: (c.requirement_coverage.get("conflicts_count", 0) if c.requirement_coverage else 0)
                    for c in candidates
                },
            },
            {
                "dimension": "Retrieval Rank",
                "values": {c.is_number: f"#{c.retrieval_rank}" for c in candidates},
            },
            {
                "dimension": "AI Recommendation",
                "values": {c.is_number: c.ai_recommendation_state for c in candidates},
            },
        ]
        return rows

    @classmethod
    def _build_regulatory_matrix(cls, candidates: List[CandidateDTO]) -> List[Dict[str, Any]]:
        """Construct regulatory and currency comparison table."""
        rows = [
            {"dimension": "Standard Currency Status", "values": {c.is_number: c.standard_status or "NEEDS_VERIFICATION" for c in candidates}},
            {"dimension": "QCO Seed Association", "values": {c.is_number: c.qco_status or "NOT_FOUND_IN_SEED" for c in candidates}},
            {"dimension": "Associated QCO Orders", "values": {c.is_number: ", ".join(c.order_names) if c.order_names else "None" for c in candidates}},
            {"dimension": "Gazette Effective Date", "values": {c.is_number: c.effective_date or "NOT_AVAILABLE" for c in candidates}},
            {"dimension": "Notifying Authority", "values": {c.is_number: c.authority or "NOT_AVAILABLE" for c in candidates}},
        ]
        return rows

    @classmethod
    def _build_gaps_matrix(cls, candidates: List[CandidateDTO]) -> List[Dict[str, Any]]:
        """Construct gap profile comparison table."""
        rows = [
            {"dimension": "Total Gaps Identified", "values": {c.is_number: len(c.gaps or []) for c in candidates}},
            {
                "dimension": "High Severity Gaps",
                "values": {
                    c.is_number: sum(1 for g in (c.gaps or []) if g.get("severity") == "HIGH")
                    for c in candidates
                },
            },
            {
                "dimension": "Medium Severity Gaps",
                "values": {
                    c.is_number: sum(1 for g in (c.gaps or []) if g.get("severity") == "MEDIUM")
                    for c in candidates
                },
            },
            {
                "dimension": "Verification Items Required",
                "values": {c.is_number: len(c.verification_items) for c in candidates},
            },
        ]
        return rows
