"""
backend/review
==============

Phase 7 Human-in-the-Loop Officer Review & Decision Support Package.
"""

from backend.review.schemas import (
    OfficerDecisionState,
    VerificationState,
    RejectionReason,
    AuditEventType,
    VerificationItemDTO,
    CandidateDTO,
    OfficerDecisionDTO,
    AuditEventDTO,
    ReviewListItemDTO,
    ReviewDetailDTO,
    CreateReviewRequest,
    SubmitDecisionRequest,
    UpdateVerificationRequest,
    ReopenReviewRequest,
    CompareCandidatesRequest,
    ReviewListResponse,
    CandidateComparisonResponse,
    DashboardStatsResponse,
)
from backend.review.state_machine import ReviewStateMachine, InvalidStateTransitionError, VerificationConstraintError
from backend.review.verification import VerificationService
from backend.review.audit import AuditTrailService
from backend.review.comparison import CandidateComparisonEngine
from backend.review.review_service import ReviewService, PipelineContext

__all__ = [
    "OfficerDecisionState",
    "VerificationState",
    "RejectionReason",
    "AuditEventType",
    "VerificationItemDTO",
    "CandidateDTO",
    "OfficerDecisionDTO",
    "AuditEventDTO",
    "ReviewListItemDTO",
    "ReviewDetailDTO",
    "CreateReviewRequest",
    "SubmitDecisionRequest",
    "UpdateVerificationRequest",
    "ReopenReviewRequest",
    "CompareCandidatesRequest",
    "ReviewListResponse",
    "CandidateComparisonResponse",
    "DashboardStatsResponse",
    "ReviewStateMachine",
    "InvalidStateTransitionError",
    "VerificationConstraintError",
    "VerificationService",
    "AuditTrailService",
    "CandidateComparisonEngine",
    "ReviewService",
    "PipelineContext",
]
