"""
backend/review/schemas.py
=========================

Pydantic schemas and enums for Phase 7 Human-in-the-Loop Officer Review
and Decision Support Workflow.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class OfficerDecisionState(str, Enum):
    """Controlled lifecycle states for officer review."""
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    REQUEST_REVISION = "REQUEST_REVISION"


class VerificationState(str, Enum):
    """Human officer verification status on specific factual claims."""
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    CONFLICTING = "CONFLICTING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RejectionReason(str, Enum):
    """Standardized rejection reason codes."""
    WRONG_PRODUCT = "WRONG_PRODUCT"
    WRONG_SECTOR = "WRONG_SECTOR"
    INSUFFICIENT_TECHNICAL_COVERAGE = "INSUFFICIENT_TECHNICAL_COVERAGE"
    PARAMETER_CONFLICT = "PARAMETER_CONFLICT"
    OUTDATED_STANDARD = "OUTDATED_STANDARD"
    REGULATORY_MISMATCH = "REGULATORY_MISMATCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    DUPLICATE_STANDARD = "DUPLICATE_STANDARD"
    OTHER = "OTHER"


class AuditEventType(str, Enum):
    """Append-only audit trail event types."""
    REVIEW_CREATED = "REVIEW_CREATED"
    REVIEW_OPENED = "REVIEW_OPENED"
    CANDIDATE_SELECTED = "CANDIDATE_SELECTED"
    CANDIDATE_COMPARISON = "CANDIDATE_COMPARISON"
    EVIDENCE_OPENED = "EVIDENCE_OPENED"
    VERIFICATION_CHANGED = "VERIFICATION_CHANGED"
    DECISION_MADE = "DECISION_MADE"
    DECISION_MODIFIED = "DECISION_MODIFIED"
    REVIEW_REOPENED = "REVIEW_REOPENED"


# -----------------------------------------------------------------------------
# DTO / Data Transfer Schemas
# -----------------------------------------------------------------------------

class VerificationItemDTO(BaseModel):
    """Verification item displayed in officer checklist."""
    model_config = ConfigDict(extra="ignore")

    id: int
    review_id: int
    candidate_id: Optional[int] = None
    standard_id: Optional[str] = None
    item_key: str
    title: str
    category: str
    system_state: str
    officer_state: VerificationState
    is_regulatory: bool
    system_evidence: Optional[Any] = None
    officer_evidence_reference: Optional[str] = None
    officer_note: Optional[str] = None
    verified_at: Optional[datetime.datetime] = None
    verified_by: Optional[str] = None
    created_at: Optional[datetime.datetime] = None


class CandidateDTO(BaseModel):
    """Candidate standard view within a review session."""
    model_config = ConfigDict(extra="ignore")

    id: int
    review_id: int
    standard_id: str
    is_number: str
    title: str
    sector: Optional[str] = None
    application: Optional[str] = None
    materials: List[str] = Field(default_factory=list)
    technical_parameters: List[str] = Field(default_factory=list)

    retrieval_rank: int
    reranker_score: Optional[float] = None
    rrf_score: Optional[float] = None
    retrieval_method: str = "hybrid_cross_encoder"

    requirement_coverage: Optional[Dict[str, Any]] = None
    gaps: Optional[List[Dict[str, Any]]] = None

    standard_status: Optional[str] = "NEEDS_VERIFICATION"
    qco_status: Optional[str] = "NOT_FOUND_IN_SEED"
    qco_ids: List[str] = Field(default_factory=list)
    order_names: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    authority: Optional[str] = None

    ai_recommendation_state: str = "REVIEW_REQUIRED"
    notes: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    normative_references: Optional[List[Dict[str, Any]]] = None
    verification_items: List[VerificationItemDTO] = Field(default_factory=list)


class OfficerDecisionDTO(BaseModel):
    """Officer decision record with AI separation and override metadata."""
    model_config = ConfigDict(extra="ignore")

    state: OfficerDecisionState
    selected_candidate_id: Optional[int] = None
    selected_standard_id: Optional[str] = None
    selected_is_number: Optional[str] = None
    ai_recommendation_state: Optional[str] = None
    is_override: bool = False
    rejection_reason: Optional[RejectionReason] = None
    rejection_note: Optional[str] = None
    officer_id: Optional[str] = None
    officer_role: Optional[str] = None
    decision_summary: Optional[str] = None
    supporting_evidence_references: Optional[List[str]] = None
    timestamp: Optional[datetime.datetime] = None


class AuditEventDTO(BaseModel):
    """Immutable audit event."""
    model_config = ConfigDict(extra="ignore")

    id: int
    review_id: int
    event_type: AuditEventType
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    actor: str
    actor_role: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime.datetime


class ReviewListItemDTO(BaseModel):
    """Summary record for review queue and history tables."""
    model_config = ConfigDict(extra="ignore")

    id: int
    review_id: str
    raw_text: str
    product: Optional[str] = None
    sector: Optional[str] = None
    status: OfficerDecisionState
    top_candidate_is_number: Optional[str] = None
    top_candidate_title: Optional[str] = None
    top_candidate_rank: Optional[int] = None
    ai_recommendation_state: Optional[str] = None
    decision_state: Optional[str] = None
    is_override: bool = False
    candidate_count: int = 0
    pending_verification_count: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ReviewDetailDTO(BaseModel):
    """Complete review package including requirements, candidates, decision, and audit trail."""
    model_config = ConfigDict(extra="ignore")

    id: int
    review_id: str
    query_id: Optional[int] = None
    raw_text: str
    input_type: Optional[str] = "text"
    procurement_requirements: Optional[Dict[str, Any]] = None
    status: OfficerDecisionState
    selected_candidate_id: Optional[int] = None
    candidates: List[CandidateDTO] = Field(default_factory=list)
    officer_decision: Optional[OfficerDecisionDTO] = None
    verification_items: List[VerificationItemDTO] = Field(default_factory=list)
    audit_events: List[AuditEventDTO] = Field(default_factory=list)
    created_at: datetime.datetime
    updated_at: datetime.datetime


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------

class CreateReviewRequest(BaseModel):
    """Initiate a procurement standard recommendation and review session."""
    query_text: str = Field(..., min_length=3, description="Procurement tender description or specification text")
    input_type: Optional[str] = Field("text", description="text | pdf | docx | gem_spec")
    top_k: Optional[int] = Field(10, ge=1, le=20, description="Number of candidate standards to evaluate")


class SubmitDecisionRequest(BaseModel):
    """Submit authorized officer decision."""
    state: OfficerDecisionState
    selected_candidate_id: Optional[int] = None
    rejection_reason: Optional[RejectionReason] = None
    rejection_note: Optional[str] = None
    officer_id: Optional[str] = "officer_001"
    officer_role: Optional[str] = "Procurement Officer"
    decision_summary: Optional[str] = None
    supporting_evidence_references: Optional[List[str]] = Field(default_factory=list)


class UpdateVerificationRequest(BaseModel):
    """Update human verification status of a specific item."""
    verification_item_id: int
    officer_state: VerificationState
    officer_evidence_reference: Optional[str] = None
    officer_note: Optional[str] = None
    officer_id: Optional[str] = "officer_001"


class ReopenReviewRequest(BaseModel):
    """Reopen a finalized review session for additional officer inspection."""
    reason: str = Field(..., min_length=3)
    officer_id: Optional[str] = "officer_001"


class CompareCandidatesRequest(BaseModel):
    """Request side-by-side comparison for 2-3 candidates."""
    candidate_ids: List[int] = Field(..., min_length=2, max_length=3)


# -----------------------------------------------------------------------------
# Response Schemas
# -----------------------------------------------------------------------------

class ReviewListResponse(BaseModel):
    """Paginated review queue / history response."""
    total: int
    limit: int
    offset: int
    reviews: List[ReviewListItemDTO]


class CandidateComparisonResponse(BaseModel):
    """Side-by-side comparative matrix response."""
    review_id: str
    candidates: List[CandidateDTO]
    facet_comparison: List[Dict[str, Any]]
    regulatory_comparison: List[Dict[str, Any]]
    gaps_comparison: List[Dict[str, Any]]


class DashboardStatsResponse(BaseModel):
    """Operational metrics for the officer decision dashboard."""
    total_reviews: int
    pending_reviews: int
    under_review: int
    accepted: int
    rejected: int
    needs_verification: int
    request_revision: int
    agreement_rate: float
    override_rate: float
    avg_candidates_inspected: float
    avg_verification_items: float
    recent_reviews: List[ReviewListItemDTO]
