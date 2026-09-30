"""
backend/review/verification.py
==============================

Officer Verification Engine for PS26108 Phase 7.
Generates dynamic verification checklists grounded strictly in actual specification
gaps and regulatory claims. Manages officer verification state and audit linkage.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.models import VerificationItem, ReviewCandidate
from backend.recommendation.schemas import (
    CandidateRecommendation,
    GapCategory,
    SpecificationGap,
)
from backend.regulatory.qco_resolver import QCOStatus
from backend.regulatory.version_resolver import VersionStatus
from backend.review.schemas import VerificationState
from backend.review.state_machine import ReviewStateMachine


class VerificationService:
    """Manages candidate verification items and officer verification interactions."""

    @classmethod
    def generate_verification_items(
        cls,
        candidate_rec: CandidateRecommendation,
        review_id: int,
        candidate_id: Optional[int] = None,
    ) -> List[VerificationItem]:
        """
        Generate verification items dynamically from actual gaps and regulatory state.
        Never generates placeholder items without corresponding evidence/gaps.
        """
        items: List[VerificationItem] = []
        std_id = candidate_rec.standard_id
        is_num = candidate_rec.is_number

        # 1. Standard Currency Verification Item
        if candidate_rec.standard_status in (VersionStatus.NEEDS_VERIFICATION, VersionStatus.UNKNOWN):
            items.append(
                VerificationItem(
                    review_id=review_id,
                    candidate_id=candidate_id,
                    standard_id=std_id,
                    item_key=f"{std_id}_standard_currency",
                    title=f"Verify {is_num} Active BIS Currency & Amendments",
                    category="STANDARD_STATUS",
                    system_state="NEEDS_VERIFICATION",
                    officer_state=VerificationState.UNVERIFIED.value,
                    is_regulatory=False,
                    system_evidence={
                        "source": "SEED_DATASET",
                        "status": candidate_rec.standard_status.value,
                        "notes": "Listed in Scheme-1 seed dataset. Requires live Manakonline confirmation.",
                    },
                )
            )

        # 2. Regulatory QCO Verification Items
        if candidate_rec.qco_status == QCOStatus.ASSOCIATED_NEEDS_VERIFICATION:
            qco_names = ", ".join(candidate_rec.order_names) if candidate_rec.order_names else "Quality Control Order"
            items.append(
                VerificationItem(
                    review_id=review_id,
                    candidate_id=candidate_id,
                    standard_id=std_id,
                    item_key=f"{std_id}_qco_gazette_order",
                    title=f"Verify QCO Gazette Notification: {qco_names}",
                    category="REGULATORY",
                    system_state="NEEDS_VERIFICATION",
                    officer_state=VerificationState.UNVERIFIED.value,
                    is_regulatory=True,
                    system_evidence={
                        "source": "SEED_DATASET",
                        "qco_ids": candidate_rec.qco_ids,
                        "order_names": candidate_rec.order_names,
                        "claim": f"{is_num} associated with {qco_names} in seed records.",
                    },
                )
            )
            items.append(
                VerificationItem(
                    review_id=review_id,
                    candidate_id=candidate_id,
                    standard_id=std_id,
                    item_key=f"{std_id}_qco_effective_date",
                    title=f"Verify Enforcement Effective Date & Notifying Authority",
                    category="REGULATORY",
                    system_state="NEEDS_VERIFICATION",
                    officer_state=VerificationState.UNVERIFIED.value,
                    is_regulatory=True,
                    system_evidence={
                        "source": "SEED_DATASET",
                        "effective_date": candidate_rec.effective_date or "NOT_AVAILABLE",
                        "authority": candidate_rec.authority or "NOT_AVAILABLE",
                    },
                )
            )

        # 3. Gap-Driven Technical Verification Items
        for gap in candidate_rec.gaps:
            if gap.category in (GapCategory.PARAMETER_UNVERIFIED, GapCategory.PARAMETER_CONFLICT):
                key = f"{std_id}_param_{gap.title.lower().replace(' ', '_')[:30]}"
                # Avoid duplicate keys
                if not any(it.item_key == key for it in items):
                    items.append(
                        VerificationItem(
                            review_id=review_id,
                            candidate_id=candidate_id,
                            standard_id=std_id,
                            item_key=key,
                            title=gap.title,
                            category="TECHNICAL_PARAMETER",
                            system_state=gap.severity.value,
                            officer_state=VerificationState.UNVERIFIED.value,
                            is_regulatory=False,
                            system_evidence={
                                "explanation": gap.explanation,
                                "evidence": gap.evidence,
                                "verification_requirement": gap.verification_requirement,
                            },
                        )
                    )
            elif gap.category == GapCategory.MATERIAL_UNVERIFIED:
                key = f"{std_id}_material_{gap.title.lower().replace(' ', '_')[:30]}"
                if not any(it.item_key == key for it in items):
                    items.append(
                        VerificationItem(
                            review_id=review_id,
                            candidate_id=candidate_id,
                            standard_id=std_id,
                            item_key=key,
                            title=gap.title,
                            category="MATERIAL",
                            system_state=gap.severity.value,
                            officer_state=VerificationState.UNVERIFIED.value,
                            is_regulatory=False,
                            system_evidence={
                                "explanation": gap.explanation,
                                "evidence": gap.evidence,
                                "verification_requirement": gap.verification_requirement,
                            },
                        )
                    )
            elif gap.category == GapCategory.APPLICATION_UNVERIFIED:
                key = f"{std_id}_app_scope"
                if not any(it.item_key == key for it in items):
                    items.append(
                        VerificationItem(
                            review_id=review_id,
                            candidate_id=candidate_id,
                            standard_id=std_id,
                            item_key=key,
                            title=gap.title,
                            category="APPLICATION",
                            system_state=gap.severity.value,
                            officer_state=VerificationState.UNVERIFIED.value,
                            is_regulatory=False,
                            system_evidence={
                                "explanation": gap.explanation,
                                "evidence": gap.evidence,
                                "verification_requirement": gap.verification_requirement,
                            },
                        )
                    )

        return items

    @classmethod
    def apply_verification_update(
        cls,
        db: Session,
        item: VerificationItem,
        new_state: VerificationState,
        evidence_reference: Optional[str],
        officer_note: Optional[str],
        officer_id: str,
    ) -> VerificationItem:
        """
        Update verification item ensuring regulatory invariants are upheld.
        """
        # Validate regulatory invariant
        ReviewStateMachine.validate_regulatory_verification(
            is_regulatory=item.is_regulatory,
            current_state=VerificationState(item.officer_state),
            new_state=new_state,
            evidence_reference=evidence_reference,
            officer_note=officer_note,
        )

        item.officer_state = new_state.value
        item.officer_evidence_reference = evidence_reference.strip() if evidence_reference else None
        item.officer_note = officer_note.strip() if officer_note else None
        item.verified_by = officer_id
        item.verified_at = datetime.datetime.utcnow()

        db.add(item)
        db.commit()
        db.refresh(item)
        return item
