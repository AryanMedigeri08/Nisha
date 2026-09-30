"""
tests/unit/test_phase7_review.py
================================

Comprehensive test suite for Phase 7 Human-in-the-Loop Officer Review & Decision-Support:
1. Review creation from procurement query
2. Review retrieval & detail verification
3. State machine transitions (valid & invalid)
4. Audit trail logging and immutability
5. Dynamic verification item generation
6. Regulatory verification requiring evidence reference and note
7. Officer decision recording
8. AI recommendation vs Officer decision separation & override detection
9. Standardized rejection reason codes
10. Candidate side-by-side comparison
11. Review reopening workflow
12. Dashboard metrics aggregation
13. API endpoint tests (FastAPI TestClient)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base, get_db
from backend.app.models.models import (
    Review,
    ReviewCandidate,
    VerificationItem,
    OfficerDecision,
    AuditEvent,
    Standard,
)
from backend.app.main import app
from backend.review.schemas import (
    OfficerDecisionState,
    VerificationState,
    RejectionReason,
    AuditEventType,
    CreateReviewRequest,
    SubmitDecisionRequest,
    UpdateVerificationRequest,
    ReopenReviewRequest,
)
from backend.review.state_machine import (
    ReviewStateMachine,
    InvalidStateTransitionError,
    VerificationConstraintError,
)
from backend.review.verification import VerificationService
from backend.review.audit import AuditTrailService
from backend.review.comparison import CandidateComparisonEngine
from backend.review.review_service import ReviewService, PipelineContext
from backend.recommendation.schemas import (
    CandidateRecommendation,
    AIRecommendationState,
    RequirementCoverage,
    CoverageItem,
    CoverageStatus,
    SpecificationGap,
    GapCategory,
    GapSeverity,
)
from backend.regulatory.version_resolver import VersionStatus, VersionResolutionResult
from backend.regulatory.qco_resolver import QCOStatus, QCOResolutionResult
from backend.regulatory.applicability import ApplicabilityAssessment, ApplicabilityState
from backend.retrieval.schemas import RetrievalCandidate, StandardDocument


# -----------------------------------------------------------------------------
# Pytest Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pipeline_ctx():
    """Ensure pipeline context is initialized."""
    return PipelineContext.get_instance()


@pytest.fixture
def db_session():
    """Yields a database session from the test engine."""
    from backend.app.core.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient fixture."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# -----------------------------------------------------------------------------
# 1. State Machine Tests
# -----------------------------------------------------------------------------

def test_state_machine_valid_transitions():
    """Ensure standard legal transitions succeed."""
    # PENDING -> UNDER_REVIEW
    ReviewStateMachine.validate_transition(OfficerDecisionState.PENDING, OfficerDecisionState.UNDER_REVIEW)

    # UNDER_REVIEW -> ACCEPTED, REJECTED, NEEDS_VERIFICATION, REQUEST_REVISION
    ReviewStateMachine.validate_transition(OfficerDecisionState.UNDER_REVIEW, OfficerDecisionState.ACCEPTED)
    ReviewStateMachine.validate_transition(OfficerDecisionState.UNDER_REVIEW, OfficerDecisionState.REJECTED)
    ReviewStateMachine.validate_transition(OfficerDecisionState.UNDER_REVIEW, OfficerDecisionState.NEEDS_VERIFICATION)
    ReviewStateMachine.validate_transition(OfficerDecisionState.UNDER_REVIEW, OfficerDecisionState.REQUEST_REVISION)

    # NEEDS_VERIFICATION -> UNDER_REVIEW, ACCEPTED, REJECTED
    ReviewStateMachine.validate_transition(OfficerDecisionState.NEEDS_VERIFICATION, OfficerDecisionState.UNDER_REVIEW)
    ReviewStateMachine.validate_transition(OfficerDecisionState.NEEDS_VERIFICATION, OfficerDecisionState.ACCEPTED)
    ReviewStateMachine.validate_transition(OfficerDecisionState.NEEDS_VERIFICATION, OfficerDecisionState.REJECTED)


def test_state_machine_invalid_transitions():
    """Ensure illegal transitions raise InvalidStateTransitionError."""
    # PENDING cannot directly jump to ACCEPTED or REJECTED
    with pytest.raises(InvalidStateTransitionError):
        ReviewStateMachine.validate_transition(OfficerDecisionState.PENDING, OfficerDecisionState.ACCEPTED)

    with pytest.raises(InvalidStateTransitionError):
        ReviewStateMachine.validate_transition(OfficerDecisionState.PENDING, OfficerDecisionState.REJECTED)

    # ACCEPTED cannot directly transition without reopen
    with pytest.raises(InvalidStateTransitionError):
        ReviewStateMachine.validate_transition(OfficerDecisionState.ACCEPTED, OfficerDecisionState.REJECTED)


def test_state_machine_reopen_workflow():
    """Ensure reopen action allows transition from ACCEPTED/REJECTED to UNDER_REVIEW."""
    ReviewStateMachine.validate_transition(OfficerDecisionState.ACCEPTED, OfficerDecisionState.UNDER_REVIEW, is_reopen=True)
    ReviewStateMachine.validate_transition(OfficerDecisionState.REJECTED, OfficerDecisionState.UNDER_REVIEW, is_reopen=True)

    # Invalid reopen target
    with pytest.raises(InvalidStateTransitionError):
        ReviewStateMachine.validate_transition(OfficerDecisionState.ACCEPTED, OfficerDecisionState.PENDING, is_reopen=True)


# -----------------------------------------------------------------------------
# 2. Regulatory Verification Constraint Tests
# -----------------------------------------------------------------------------

def test_regulatory_verification_requires_evidence():
    """Marking a regulatory claim as VERIFIED without evidence must fail."""
    # Regulatory item, transitioning to VERIFIED without reference
    with pytest.raises(VerificationConstraintError):
        ReviewStateMachine.validate_regulatory_verification(
            is_regulatory=True,
            current_state=VerificationState.UNVERIFIED,
            new_state=VerificationState.VERIFIED,
            evidence_reference="",
            officer_note="Verified by phone",
        )

    # Regulatory item, transitioning to VERIFIED without note
    with pytest.raises(VerificationConstraintError):
        ReviewStateMachine.validate_regulatory_verification(
            is_regulatory=True,
            current_state=VerificationState.UNVERIFIED,
            new_state=VerificationState.VERIFIED,
            evidence_reference="DPIIT Order 2023-S.O.123",
            officer_note="",
        )

    # Regulatory item with valid evidence and note must succeed
    ReviewStateMachine.validate_regulatory_verification(
        is_regulatory=True,
        current_state=VerificationState.UNVERIFIED,
        new_state=VerificationState.VERIFIED,
        evidence_reference="DPIIT Gazette Notification S.O. 452(E)",
        officer_note="Confirmed applicability on DPIIT portal as of current date.",
    )


def test_non_regulatory_verification_allows_flexible_evidence():
    """Non-regulatory items (e.g. material/scope) do not strictly enforce gazette reference format."""
    ReviewStateMachine.validate_regulatory_verification(
        is_regulatory=False,
        current_state=VerificationState.UNVERIFIED,
        new_state=VerificationState.VERIFIED,
        evidence_reference=None,
        officer_note="Material checked against tender specs",
    )


# -----------------------------------------------------------------------------
# 3. AI Separation & Human Override Detection Tests
# -----------------------------------------------------------------------------

def test_officer_override_detection():
    """Check that human override flag is accurately set when officer diverges from AI."""
    # AI Recommended -> Officer Rejected = Override
    assert ReviewStateMachine.check_override(
        ai_recommendation_state="RECOMMENDED_FOR_REVIEW",
        officer_decision_state=OfficerDecisionState.REJECTED,
    ) is True

    # AI Insufficient Evidence -> Officer Accepted = Override
    assert ReviewStateMachine.check_override(
        ai_recommendation_state="INSUFFICIENT_EVIDENCE",
        officer_decision_state=OfficerDecisionState.ACCEPTED,
    ) is True

    # AI Recommended -> Officer Accepted = Normal agreement (Not Override)
    assert ReviewStateMachine.check_override(
        ai_recommendation_state="RECOMMENDED_FOR_REVIEW",
        officer_decision_state=OfficerDecisionState.ACCEPTED,
    ) is False

    # AI Review Required -> Officer Needs Verification = Normal
    assert ReviewStateMachine.check_override(
        ai_recommendation_state="REVIEW_REQUIRED",
        officer_decision_state=OfficerDecisionState.NEEDS_VERIFICATION,
    ) is False


# -----------------------------------------------------------------------------
# 4. Review Service End-to-End Workflow Tests
# -----------------------------------------------------------------------------

def test_create_review_from_query(db_session):
    """Submit a realistic procurement query and verify review persistence."""
    query = "Procurement of ordinary portland cement 43 grade for bridge pier construction, minimum compressive strength 43 MPa, bag packing 50 kg."
    review_dto = ReviewService.create_review_from_query(
        db=db_session,
        query_text=query,
        input_type="text",
        top_k=5,
    )

    assert review_dto.id is not None
    assert review_dto.review_id.startswith("REV-")
    assert review_dto.status == OfficerDecisionState.PENDING
    assert len(review_dto.candidates) > 0
    assert review_dto.procurement_requirements is not None
    assert len(review_dto.verification_items) > 0

    # Top candidate should be relevant cement standard (e.g. IS 8112 or IS 269)
    top_cand = review_dto.candidates[0]
    assert top_cand.is_number is not None
    assert top_cand.requirement_coverage is not None
    assert "direct_matches" in top_cand.requirement_coverage

    # Verify audit event recorded
    assert any(a.event_type == AuditEventType.REVIEW_CREATED for a in review_dto.audit_events)


def test_get_review_detail(db_session):
    """Retrieve review by ID and verify all structured fields are intact."""
    query = "Supply of domestic LPG gas stoves for institutional kitchens, stainless steel body."
    created = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=3)

    retrieved = ReviewService.get_review_detail(db=db_session, review_identifier=created.review_id)
    assert retrieved.id == created.id
    assert retrieved.review_id == created.review_id
    assert len(retrieved.candidates) == len(created.candidates)


def test_update_verification_item(db_session):
    """Update verification item and check state changes and audit logging."""
    query = "Procurement of copper conductor PVC insulated cables for 1100 V working voltage."
    review_dto = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=3)

    assert len(review_dto.verification_items) > 0
    item = review_dto.verification_items[0]

    if item.is_regulatory:
        updated = ReviewService.update_verification_item(
            db=db_session,
            review_identifier=review_dto.id,
            verification_item_id=item.id,
            officer_state=VerificationState.VERIFIED,
            evidence_reference="Gazette Order SO-2023-45",
            officer_note="Verified on ministry portal",
            officer_id="officer_77",
        )
    else:
        updated = ReviewService.update_verification_item(
            db=db_session,
            review_identifier=review_dto.id,
            verification_item_id=item.id,
            officer_state=VerificationState.VERIFIED,
            evidence_reference="Tender clause 4.2",
            officer_note="Technical compliance verified",
            officer_id="officer_77",
        )

    assert updated.officer_state == VerificationState.VERIFIED
    assert updated.verified_by == "officer_77"

    # Review status should automatically move to UNDER_REVIEW
    refreshed_review = ReviewService.get_review_detail(db=db_session, review_identifier=review_dto.id)
    assert refreshed_review.status == OfficerDecisionState.UNDER_REVIEW


def test_submit_officer_decision_accept(db_session):
    """Record an ACCEPTED decision for a selected candidate standard."""
    query = "Submersible pump sets for deep tube well irrigation, 10 HP."
    review_dto = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=3)

    # First move to UNDER_REVIEW
    ReviewService.update_verification_item(
        db=db_session,
        review_identifier=review_dto.id,
        verification_item_id=review_dto.verification_items[0].id,
        officer_state=VerificationState.NOT_APPLICABLE,
        evidence_reference=None,
        officer_note="Not applicable for this site",
    )

    selected_cand = review_dto.candidates[0]
    decision = ReviewService.submit_officer_decision(
        db=db_session,
        review_identifier=review_dto.id,
        target_state=OfficerDecisionState.ACCEPTED,
        selected_candidate_id=selected_cand.id,
        officer_id="senior_officer_10",
        officer_role="Chief Procurement Officer",
        decision_summary="Standard matches all hydrological and electrical requirements.",
        supporting_evidence_references=["Tender Technical Spec TS-101"],
    )

    assert decision.state == OfficerDecisionState.ACCEPTED
    assert decision.selected_candidate_id == selected_cand.id
    assert decision.officer_id == "senior_officer_10"

    # Verify review status updated
    refreshed = ReviewService.get_review_detail(db=db_session, review_identifier=review_dto.id)
    assert refreshed.status == OfficerDecisionState.ACCEPTED


def test_submit_officer_decision_reject_with_reason(db_session):
    """Record a REJECTED decision with standardized reason code."""
    query = "Procurement of safety helmets for industrial workers."
    review_dto = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=3)

    # Move to UNDER_REVIEW
    ReviewService.update_verification_item(
        db=db_session,
        review_identifier=review_dto.id,
        verification_item_id=review_dto.verification_items[0].id,
        officer_state=VerificationState.CONFLICTING,
        evidence_reference=None,
        officer_note="Discrepancy in shell material",
    )

    decision = ReviewService.submit_officer_decision(
        db=db_session,
        review_identifier=review_dto.id,
        target_state=OfficerDecisionState.REJECTED,
        rejection_reason=RejectionReason.INSUFFICIENT_TECHNICAL_COVERAGE,
        rejection_note="Tender requires special electrical insulation not covered by standard.",
        officer_id="safety_auditor_5",
    )

    assert decision.state == OfficerDecisionState.REJECTED
    assert decision.rejection_reason == RejectionReason.INSUFFICIENT_TECHNICAL_COVERAGE


def test_candidate_comparison_engine(db_session):
    """Compare 2 candidates side-by-side."""
    query = "Procurement of electric cables and wires."
    review_dto = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=4)

    cand_ids = [c.id for c in review_dto.candidates[:2]]
    comp_res = ReviewService.get_review_detail(db=db_session, review_identifier=review_dto.id)

    from backend.app.models.models import Review
    db_review = db_session.query(Review).filter(Review.id == review_dto.id).first()
    comparison = CandidateComparisonEngine.compare(db=db_session, review=db_review, candidate_ids=cand_ids)

    assert len(comparison.candidates) == 2
    assert len(comparison.facet_comparison) > 0
    assert len(comparison.regulatory_comparison) > 0
    assert len(comparison.gaps_comparison) > 0


def test_audit_trail_append_only(db_session):
    """Verify audit events form an immutable append-only chronological log."""
    query = "Procurement of distribution transformers 2500 kVA 33 kV."
    review_dto = ReviewService.create_review_from_query(db=db_session, query_text=query, top_k=3)

    events_before = len(review_dto.audit_events)
    assert events_before >= 1

    # Add verification update
    ReviewService.update_verification_item(
        db=db_session,
        review_identifier=review_dto.id,
        verification_item_id=review_dto.verification_items[0].id,
        officer_state=VerificationState.NOT_APPLICABLE,
        evidence_reference=None,
        officer_note="Noted",
    )

    refreshed = ReviewService.get_review_detail(db=db_session, review_identifier=review_dto.id)
    events_after = len(refreshed.audit_events)
    assert events_after == events_before + 1

    # Verify event order
    timestamps = [e.timestamp for e in refreshed.audit_events]
    assert timestamps == sorted(timestamps)


def test_dashboard_metrics(db_session):
    """Verify aggregation of dashboard operational statistics."""
    stats = ReviewService.get_dashboard_metrics(db=db_session)
    assert stats.total_reviews >= 1
    assert stats.agreement_rate >= 0.0
    assert stats.override_rate >= 0.0
    assert isinstance(stats.recent_reviews, list)


# -----------------------------------------------------------------------------
# 5. FastAPI REST API Endpoint Tests
# -----------------------------------------------------------------------------

def test_api_health_endpoint(client):
    """GET /health must return 200 with status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data


def test_api_readiness_endpoint(client):
    """GET /health/ready must report database and model readiness."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "degraded")
    assert data["models_loaded"] is True


def test_api_create_review_endpoint(client):
    """POST /api/reviews must create review and return 201."""
    payload = {
        "query_text": "Procurement of Portland Pozzolana Cement (fly ash based) for building construction.",
        "input_type": "text",
        "top_k": 3,
    }
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "review_id" in data
    assert len(data["candidates"]) == 3
    assert data["status"] == "PENDING"


def test_api_list_reviews_endpoint(client):
    """GET /api/reviews must return paginated reviews."""
    response = client.get("/api/reviews?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "reviews" in data
    assert isinstance(data["reviews"], list)


def test_api_get_review_detail_endpoint(client):
    """GET /api/reviews/{review_id} must return full review package."""
    # First create
    create_res = client.post("/api/reviews", json={"query_text": "Testing review get endpoint for electric motors."})
    assert create_res.status_code == 201
    rev_id = create_res.json()["review_id"]

    # Then retrieve
    get_res = client.get(f"/api/reviews/{rev_id}")
    assert get_res.status_code == 200
    assert get_res.json()["review_id"] == rev_id


def test_api_update_verification_regulatory_constraint(client):
    """POST /api/reviews/{review_id}/verify must reject unverified regulatory claims without evidence."""
    create_res = client.post("/api/reviews", json={"query_text": "Cables for domestic electrification 1100V."})
    rev_data = create_res.json()
    rev_id = rev_data["review_id"]

    reg_items = [v for v in rev_data["verification_items"] if v["is_regulatory"]]
    if reg_items:
        v_id = reg_items[0]["id"]
        # Attempt without evidence reference
        bad_res = client.post(
            f"/api/reviews/{rev_id}/verify",
            json={
                "verification_item_id": v_id,
                "officer_state": "VERIFIED",
                "officer_evidence_reference": "",
                "officer_note": "Just verified",
            },
        )
        assert bad_res.status_code == 422

        # Valid with evidence reference
        good_res = client.post(
            f"/api/reviews/{rev_id}/verify",
            json={
                "verification_item_id": v_id,
                "officer_state": "VERIFIED",
                "officer_evidence_reference": "DPIIT Order 2023 Gazette Notification",
                "officer_note": "Verified Gazette Order entry.",
            },
        )
        assert good_res.status_code == 200
        assert good_res.json()["officer_state"] == "VERIFIED"


def test_api_submit_decision_and_reopen(client):
    """Test full decision and reopen cycle via API."""
    create_res = client.post("/api/reviews", json={"query_text": "Supply of domestic cookers."})
    rev_id = create_res.json()["review_id"]

    # First update an item to move to UNDER_REVIEW
    v_item = create_res.json()["verification_items"][0]
    client.post(
        f"/api/reviews/{rev_id}/verify",
        json={
            "verification_item_id": v_item["id"],
            "officer_state": "NOT_APPLICABLE",
        },
    )

    # Submit decision
    dec_res = client.post(
        f"/api/reviews/{rev_id}/decision",
        json={
            "state": "ACCEPTED",
            "selected_candidate_id": create_res.json()["candidates"][0]["id"],
            "decision_summary": "Meets institutional cooker tender requirements.",
        },
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["state"] == "ACCEPTED"

    # Reopen review
    reopen_res = client.post(
        f"/api/reviews/{rev_id}/reopen",
        json={"reason": "Auditor requested additional clause verification."},
    )
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "UNDER_REVIEW"


def test_api_comparison_endpoint(client):
    """GET /api/reviews/{review_id}/comparison must return comparison matrix."""
    create_res = client.post("/api/reviews", json={"query_text": "Pumps and electric motors for agricultural pumping."})
    rev_data = create_res.json()
    rev_id = rev_data["review_id"]
    cands = rev_data["candidates"]

    if len(cands) >= 2:
        c_ids = f"{cands[0]['id']},{cands[1]['id']}"
        comp_res = client.get(f"/api/reviews/{rev_id}/comparison?candidate_ids={c_ids}")
        assert comp_res.status_code == 200
        data = comp_res.json()
        assert "facet_comparison" in data
        assert "regulatory_comparison" in data
