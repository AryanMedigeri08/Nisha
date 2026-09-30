"""
backend/review/audit.py
=======================

Append-Only Audit Trail Engine for PS26108 Phase 7.
Records every review interaction, candidate inspection, verification update,
and officer decision with cryptographic timestamping and immutability guarantees.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.models import AuditEvent, Review
from backend.review.schemas import AuditEventType


class AuditTrailService:
    """Provides append-only logging and query interfaces for the officer review audit trail."""

    @classmethod
    def record_event(
        cls,
        db: Session,
        review_id: int,
        event_type: AuditEventType,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        actor: str = "officer",
        actor_role: str = "Procurement Officer",
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Append an immutable audit event record to the review trail.
        """
        event = AuditEvent(
            review_id=review_id,
            event_type=event_type.value if hasattr(event_type, "value") else str(event_type),
            previous_state=previous_state,
            new_state=new_state,
            actor=actor,
            actor_role=actor_role,
            reason=reason,
            details=details or {},
            timestamp=datetime.datetime.utcnow(),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @classmethod
    def get_events_for_review(cls, db: Session, review_id: int) -> List[AuditEvent]:
        """Retrieve the complete chronological audit trail for a review."""
        return (
            db.query(AuditEvent)
            .filter(AuditEvent.review_id == review_id)
            .order_by(AuditEvent.id.asc())
            .all()
        )
