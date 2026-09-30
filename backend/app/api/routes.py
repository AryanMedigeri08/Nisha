"""
backend/app/api/routes.py
=========================

FastAPI REST API routes for PS26108 Phase 7.
Provides endpoints for procurement query submission, candidate review,
verification checklists, officer decision recording, audit trails, and standards browsing.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query as FastQuery, status
from sqlalchemy.orm import Session

from backend.app.core.config import PROJECT_ROOT
from backend.app.core.database import get_db
from backend.app.models.models import Standard, ReviewCandidate, AuditEvent
from backend.review.schemas import (
    AuditEventDTO,
    CandidateComparisonResponse,
    CandidateDTO,
    CompareCandidatesRequest,
    CreateReviewRequest,
    DashboardStatsResponse,
    OfficerDecisionDTO,
    ReopenReviewRequest,
    ReviewDetailDTO,
    ReviewListResponse,
    SubmitDecisionRequest,
    UpdateVerificationRequest,
    VerificationItemDTO,
)
from backend.review.review_service import ReviewService, PipelineContext
from backend.review.comparison import CandidateComparisonEngine
from backend.review.state_machine import InvalidStateTransitionError, VerificationConstraintError

router = APIRouter(prefix="/api", tags=["Procurement Review & Decision Support"])


# -----------------------------------------------------------------------------
# Reviews & Queries
# -----------------------------------------------------------------------------

@router.post(
    "/reviews",
    response_model=ReviewDetailDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Procurement Query & Generate Decision-Support Review",
)
def create_review(
    request: CreateReviewRequest,
    db: Session = Depends(get_db),
) -> ReviewDetailDTO:
    """
    Submits a procurement query, extracts requirements, performs hybrid retrieval & reranking,
    resolves knowledge graph & QCO relationships, evaluates requirement coverage and specification gaps,
    and returns a persistent review package for officer decision-making.
    """
    try:
        review_dto = ReviewService.create_review_from_query(
            db=db,
            query_text=request.query_text,
            input_type=request.input_type or "text",
            top_k=request.top_k or 10,
        )
        return review_dto
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process procurement review: {str(e)}",
        )


@router.get(
    "/reviews",
    response_model=ReviewListResponse,
    summary="List Procurement Reviews with Filters",
)
def list_reviews(
    status_filter: Optional[str] = FastQuery(None, alias="status", description="PENDING | UNDER_REVIEW | ACCEPTED | REJECTED | NEEDS_VERIFICATION | REQUEST_REVISION"),
    decision_state: Optional[str] = FastQuery(None, description="Filter by final officer decision"),
    sector: Optional[str] = FastQuery(None, description="Filter by procurement sector"),
    search: Optional[str] = FastQuery(None, description="Search in tender text or review ID"),
    limit: int = FastQuery(50, ge=1, le=100),
    offset: int = FastQuery(0, ge=0),
    db: Session = Depends(get_db),
) -> ReviewListResponse:
    """Retrieve paginated list of procurement reviews."""
    return ReviewService.list_reviews(
        db=db,
        status=status_filter,
        decision_state=decision_state,
        sector=sector,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewDetailDTO,
    summary="Get Detailed Review Session",
)
def get_review(
    review_id: str,
    db: Session = Depends(get_db),
) -> ReviewDetailDTO:
    """Retrieve full review details including candidates, coverage, gaps, decision, and audit trail."""
    try:
        return ReviewService.get_review_detail(db=db, review_identifier=review_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/reviews/{review_id}/candidates",
    response_model=List[CandidateDTO],
    summary="Get Candidates for Review",
)
def get_review_candidates(
    review_id: str,
    db: Session = Depends(get_db),
) -> List[CandidateDTO]:
    """Get all ranked candidate standards evaluated for a specific review."""
    review_dto = get_review(review_id=review_id, db=db)
    return review_dto.candidates


@router.get(
    "/reviews/{review_id}/candidates/{candidate_id}",
    response_model=CandidateDTO,
    summary="Get Specific Candidate Detail",
)
def get_candidate_detail(
    review_id: str,
    candidate_id: int,
    db: Session = Depends(get_db),
) -> CandidateDTO:
    """Get deep inspection detail for a single candidate standard."""
    review_dto = get_review(review_id=review_id, db=db)
    for c in review_dto.candidates:
        if c.id == candidate_id:
            return c
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate '{candidate_id}' not found in review '{review_id}'.",
    )


# -----------------------------------------------------------------------------
# Verification & Decision
# -----------------------------------------------------------------------------

@router.post(
    "/reviews/{review_id}/verify",
    response_model=VerificationItemDTO,
    summary="Update Officer Verification Item",
)
def update_verification(
    review_id: str,
    request: UpdateVerificationRequest,
    db: Session = Depends(get_db),
) -> VerificationItemDTO:
    """
    Update the verification state of a checklist item.
    For regulatory items, changing state to VERIFIED strictly requires an evidence reference and note.
    """
    try:
        return ReviewService.update_verification_item(
            db=db,
            review_identifier=review_id,
            verification_item_id=request.verification_item_id,
            officer_state=request.officer_state,
            evidence_reference=request.officer_evidence_reference,
            officer_note=request.officer_note,
            officer_id=request.officer_id or "officer_001",
        )
    except VerificationConstraintError as vce:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(vce))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/reviews/{review_id}/decision",
    response_model=OfficerDecisionDTO,
    summary="Record Officer Decision",
)
def submit_decision(
    review_id: str,
    request: SubmitDecisionRequest,
    db: Session = Depends(get_db),
) -> OfficerDecisionDTO:
    """
    Record an authorized procurement officer's decision with audit event generation.
    Maintains strict separation between AI recommendation and Human Officer decision.
    """
    try:
        return ReviewService.submit_officer_decision(
            db=db,
            review_identifier=review_id,
            target_state=request.state,
            selected_candidate_id=request.selected_candidate_id,
            rejection_reason=request.rejection_reason,
            rejection_note=request.rejection_note,
            officer_id=request.officer_id or "officer_001",
            officer_role=request.officer_role or "Procurement Officer",
            decision_summary=request.decision_summary,
            supporting_evidence_references=request.supporting_evidence_references,
        )
    except InvalidStateTransitionError as iste:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(iste))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/reviews/{review_id}/reopen",
    response_model=ReviewDetailDTO,
    summary="Reopen Finalized Review",
)
def reopen_review(
    review_id: str,
    request: ReopenReviewRequest,
    db: Session = Depends(get_db),
) -> ReviewDetailDTO:
    """Reopen an accepted or rejected review back to UNDER_REVIEW state."""
    try:
        return ReviewService.reopen_review(
            db=db,
            review_identifier=review_id,
            reason=request.reason,
            officer_id=request.officer_id or "officer_001",
        )
    except InvalidStateTransitionError as iste:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(iste))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# -----------------------------------------------------------------------------
# Comparison & Audit
# -----------------------------------------------------------------------------

@router.get(
    "/reviews/{review_id}/comparison",
    response_model=CandidateComparisonResponse,
    summary="Side-by-Side Candidate Comparison",
)
def compare_candidates(
    review_id: str,
    candidate_ids: str = FastQuery(..., description="Comma-separated candidate IDs (2 to 3)"),
    db: Session = Depends(get_db),
) -> CandidateComparisonResponse:
    """Generate side-by-side factual comparison matrix for 2-3 candidate standards."""
    try:
        c_ids = [int(x.strip()) for x in candidate_ids.split(",") if x.strip()]
        if len(c_ids) < 2 or len(c_ids) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please specify between 2 and 3 candidate IDs for side-by-side comparison.",
            )

        from backend.app.models.models import Review
        if str(review_id).isdigit():
            db_review = db.query(Review).filter(Review.id == int(review_id)).first()
        else:
            db_review = db.query(Review).filter(Review.review_id == str(review_id)).first()

        if not db_review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review '{review_id}' not found.")

        return CandidateComparisonEngine.compare(db=db, review=db_review, candidate_ids=c_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/reviews/{review_id}/audit",
    response_model=List[AuditEventDTO],
    summary="Get Append-Only Audit Trail",
)
def get_audit_trail(
    review_id: str,
    db: Session = Depends(get_db),
) -> List[AuditEventDTO]:
    """Retrieve immutable chronological audit events for a review."""
    review_dto = get_review(review_id=review_id, db=db)
    return review_dto.audit_events


# -----------------------------------------------------------------------------
# Dashboard & Reference Data
# -----------------------------------------------------------------------------

@router.get(
    "/dashboard/stats",
    response_model=DashboardStatsResponse,
    summary="Dashboard Operational Metrics",
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
) -> DashboardStatsResponse:
    """Get aggregate operational statistics for the officer decision-support dashboard."""
    return ReviewService.get_dashboard_metrics(db=db)


@router.get(
    "/standards",
    summary="Search & Browse Authoritative Seed Standards",
)
def list_standards(
    search: Optional[str] = FastQuery(None, description="Search by IS number or title keyword"),
    sector: Optional[str] = FastQuery(None, description="Filter by sector"),
    limit: int = FastQuery(50, ge=1, le=100),
    offset: int = FastQuery(0, ge=0),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Search seed standards database."""
    query = db.query(Standard)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(Standard.is_number.ilike(s), Standard.title.ilike(s)))
    if sector:
        query = query.filter(Standard.sector.ilike(f"%{sector.strip()}%"))

    total = query.count()
    stds = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "standards": [
            {
                "standard_id": s.standard_id,
                "is_number": s.is_number,
                "title": s.title,
                "sector": s.sector,
                "status": s.status,
                "year": s.year,
                "application": s.application,
                "materials": s.materials,
                "technical_parameters": s.technical_parameters,
                "source_url": s.source_url,
            }
            for s in stds
        ],
    }


@router.get(
    "/examples",
    summary="Sample Procurement Queries for Demo / Testing",
)
def get_sample_queries() -> List[Dict[str, Any]]:
    """Return realistic procurement query examples from synthetic benchmark dataset."""
    sample_queries_path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_queries_v1.jsonl"
    examples = []
    if sample_queries_path.exists():
        with open(sample_queries_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 12:
                    break
                rec = json.loads(line)
                examples.append({
                    "id": rec.get("id"),
                    "title": rec.get("product_clean", "Procurement Query"),
                    "query": rec.get("query"),
                    "sector": rec.get("sector_clean"),
                })
    if not examples:
        # Static curated examples if synthetic file is missing
        examples = [
            {
                "id": "demo_01",
                "title": "Domestic LPG Gas Stove",
                "query": "Procurement of domestic LPG gas stoves for institutional kitchens, stainless steel body with 2 burners, thermal efficiency above 65%.",
                "sector": "Domestic Cookers and Stoves",
            },
            {
                "id": "demo_02",
                "title": "Submersible Pumpset for Irrigation",
                "query": "Supply of submersible pump sets for deep tube wells, power rating 7.5 kW (10 HP), operating voltage 415V 3-phase AC 50 Hz, head 100 meters.",
                "sector": "Pumps",
            },
            {
                "id": "demo_03",
                "title": "Industrial Safety Helmets",
                "query": "Supply of non-metallic industrial safety helmets for construction workers, high-density polyethylene (HDPE) shell with adjustable chin strap.",
                "sector": "Personal Safety Equipment",
            },
            {
                "id": "demo_04",
                "title": "PVC Insulated Electric Cables",
                "query": "Procurement of copper conductor PVC insulated cables for working voltage up to 1100 V, 4 core 16 sq mm for building wiring.",
                "sector": "Electrical Wires and Cables",
            },
        ]
    return examples
