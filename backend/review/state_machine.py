"""
backend/review/state_machine.py
===============================

Controlled State Machine for Officer Review Lifecycle.
Guarantees strict state transitions, audit trail triggers, and invariant enforcement.

TRANSITION GRAPH:
PENDING -> UNDER_REVIEW
UNDER_REVIEW -> ACCEPTED | REJECTED | NEEDS_VERIFICATION | REQUEST_REVISION
NEEDS_VERIFICATION -> UNDER_REVIEW | ACCEPTED | REJECTED
REQUEST_REVISION -> UNDER_REVIEW
ACCEPTED / REJECTED -> UNDER_REVIEW (Only via explicit Reopen action)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple
from backend.review.schemas import (
    OfficerDecisionState,
    VerificationState,
    RejectionReason,
)
from backend.recommendation.schemas import AIRecommendationState


class InvalidStateTransitionError(Exception):
    """Raised when an illegal review state transition is attempted."""
    def __init__(self, from_state: str, to_state: str, message: Optional[str] = None):
        self.from_state = from_state
        self.to_state = to_state
        msg = message or f"Illegal transition from '{from_state}' to '{to_state}'."
        super().__init__(msg)


class VerificationConstraintError(Exception):
    """Raised when regulatory verification is claimed without required evidence reference."""
    pass


class ReviewStateMachine:
    """Enforces valid lifecycle transitions and business rules for officer reviews."""

    ALLOWED_TRANSITIONS: Dict[OfficerDecisionState, Set[OfficerDecisionState]] = {
        OfficerDecisionState.PENDING: {
            OfficerDecisionState.UNDER_REVIEW,
        },
        OfficerDecisionState.UNDER_REVIEW: {
            OfficerDecisionState.ACCEPTED,
            OfficerDecisionState.REJECTED,
            OfficerDecisionState.NEEDS_VERIFICATION,
            OfficerDecisionState.REQUEST_REVISION,
        },
        OfficerDecisionState.NEEDS_VERIFICATION: {
            OfficerDecisionState.UNDER_REVIEW,
            OfficerDecisionState.ACCEPTED,
            OfficerDecisionState.REJECTED,
        },
        OfficerDecisionState.REQUEST_REVISION: {
            OfficerDecisionState.UNDER_REVIEW,
        },
        OfficerDecisionState.ACCEPTED: {
            # Direct transition blocked; must use explicit reopen
        },
        OfficerDecisionState.REJECTED: {
            # Direct transition blocked; must use explicit reopen
        },
    }

    @classmethod
    def validate_transition(
        cls,
        current_state: OfficerDecisionState,
        target_state: OfficerDecisionState,
        is_reopen: bool = False,
    ) -> None:
        """
        Validate whether transitioning from current_state to target_state is permitted.
        Raises InvalidStateTransitionError if illegal.
        """
        if is_reopen:
            if current_state in (OfficerDecisionState.ACCEPTED, OfficerDecisionState.REJECTED, OfficerDecisionState.NEEDS_VERIFICATION):
                if target_state == OfficerDecisionState.UNDER_REVIEW:
                    return
            raise InvalidStateTransitionError(
                current_state.value, target_state.value,
                f"Cannot reopen review from state '{current_state.value}' to '{target_state.value}'. Reopening must target 'UNDER_REVIEW'."
            )

        if current_state == target_state:
            return  # Idempotent state update

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                current_state.value,
                target_state.value,
                f"Transition from '{current_state.value}' to '{target_state.value}' is not permitted in the review workflow."
            )

    @classmethod
    def validate_regulatory_verification(
        cls,
        is_regulatory: bool,
        current_state: VerificationState,
        new_state: VerificationState,
        evidence_reference: Optional[str],
        officer_note: Optional[str],
    ) -> None:
        """
        Enforce that marking a regulatory claim as VERIFIED strictly requires
        an authoritative evidence reference and explanatory note.
        """
        if is_regulatory and new_state == VerificationState.VERIFIED:
            if not evidence_reference or not evidence_reference.strip():
                raise VerificationConstraintError(
                    "Regulatory claims cannot be marked as VERIFIED without an explicit authoritative "
                    "Evidence Reference (e.g. DPIIT Gazette Order No. or BIS Gazette Notification)."
                )
            if not officer_note or not officer_note.strip():
                raise VerificationConstraintError(
                    "Regulatory verification requires an Officer Note explaining the verification basis."
                )

    @classmethod
    def check_override(
        cls,
        ai_recommendation_state: Optional[str],
        officer_decision_state: OfficerDecisionState,
    ) -> bool:
        """
        Determine if the officer's decision overrides the AI's recommendation state.
        Preserves AI state and officer state as independent concepts.
        """
        if not ai_recommendation_state:
            return False

        ai_state = ai_recommendation_state.upper()

        # If AI recommended for review but Officer rejected
        if ai_state == AIRecommendationState.RECOMMENDED_FOR_REVIEW.value:
            if officer_decision_state == OfficerDecisionState.REJECTED:
                return True

        # If AI determined Insufficient Evidence or Review Required but Officer directly accepted
        if ai_state in (AIRecommendationState.INSUFFICIENT_EVIDENCE.value, AIRecommendationState.POTENTIALLY_RELEVANT.value):
            if officer_decision_state == OfficerDecisionState.ACCEPTED:
                return True

        return False
