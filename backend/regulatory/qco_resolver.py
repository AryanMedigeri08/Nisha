"""
backend/regulatory/qco_resolver.py
==================================

Quality Control Order (QCO) regulatory resolver.
Resolves QCO association status without fabricating legal enforceability.

Possible QCO states:
- APPLICABLE_VERIFIED: Full gazette order with verified effective date and authority confirmed.
- ASSOCIATED_NEEDS_VERIFICATION: Standard associated with a QCO in seed dataset, but effective date or gazette order requires verification.
- NOT_FOUND_IN_SEED: No QCO record or association exists in the seed dataset.
- UNKNOWN: Regulatory association cannot be determined.

CRITICAL RULE:
Never claim "QCO applies" or invent effective dates / authorities when absent from seed data.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, QCO, QCOStandardLink
from backend.regulatory.evidence import EvidenceItem, VerificationStatus, SourceType
from backend.retrieval.schemas import StandardDocument

logger = logging.getLogger(__name__)


class QCOStatus(str, Enum):
    """Regulatory QCO association status."""
    APPLICABLE_VERIFIED = "APPLICABLE_VERIFIED"
    ASSOCIATED_NEEDS_VERIFICATION = "ASSOCIATED_NEEDS_VERIFICATION"
    NOT_FOUND_IN_SEED = "NOT_FOUND_IN_SEED"
    UNKNOWN = "UNKNOWN"


class QCOResolutionResult(BaseModel):
    """Resolved QCO regulatory status with supporting evidence."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    qco_status: QCOStatus
    qco_ids: List[str] = Field(default_factory=list)
    order_names: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    authority: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)


class QCOResolver:
    """Resolves QCO regulatory associations from the authoritative database."""

    def __init__(self):
        self._load_qco_data()

    def _load_qco_data(self):
        """Pre-load QCO records and links from database."""
        session = SessionLocal()
        try:
            links = session.query(QCOStandardLink).all()
            qcos = session.query(QCO).all()
            qco_by_id = {q.id: q for q in qcos}

            # Map standard_id (e.g. 'is_269') to list of QCO objects
            self.std_qco_map: Dict[str, List[QCO]] = {}
            for link in links:
                std = link.standard
                qco = qco_by_id.get(link.qco_id)
                if std and qco:
                    self.std_qco_map.setdefault(std.standard_id, []).append(qco)
        finally:
            session.close()

    def resolve(self, standard: StandardDocument) -> QCOResolutionResult:
        """
        Resolve regulatory QCO status for a retrieved standard.
        Preserves uncertainty where dates or gazette authorities are unverified.
        """
        std_id = standard.standard_id
        is_num = standard.is_number

        associated_qcos = self.std_qco_map.get(std_id, [])

        if not associated_qcos:
            evidence = [
                EvidenceItem(
                    source_type=SourceType.SEED_DATASET.value,
                    source_id=std_id,
                    claim=f"No QCO order association found in seed dataset for {is_num}.",
                    evidence_text=f"qco_or_regulatory_order is null or unlinked.",
                    verification_status=VerificationStatus.INCOMPLETE,
                )
            ]
            return QCOResolutionResult(
                standard_id=std_id,
                is_number=is_num,
                qco_status=QCOStatus.NOT_FOUND_IN_SEED,
                qco_ids=[],
                order_names=[],
                effective_date=None,
                authority=None,
                evidence=evidence,
            )

        qco_ids: List[str] = []
        order_names: List[str] = []
        authorities: List[str] = []
        effective_dates: List[str] = []
        evidence_items: List[EvidenceItem] = []

        is_fully_verified = True

        for q in associated_qcos:
            qco_ids.append(q.qco_id)
            order_names.append(q.order_name)
            if q.notifying_authority:
                authorities.append(q.notifying_authority)
            if q.effective_date:
                effective_dates.append(str(q.effective_date))
            else:
                is_fully_verified = False

            # In seed dataset, status is 'needs_current_order_resolution'
            if q.status == "needs_current_order_resolution":
                is_fully_verified = False

            evidence_items.append(
                EvidenceItem(
                    source_type=SourceType.SEED_DATASET.value,
                    source_id=q.qco_id,
                    source_url=q.source_url,
                    claim=f"Standard {is_num} associated with QCO '{q.order_name}' in seed dataset.",
                    evidence_text=(
                        f"Seed QCO ID: {q.qco_id}, Order: '{q.order_name}', "
                        f"Status: '{q.status}', Effective Date: {q.effective_date or 'null'}, "
                        f"Authority: {q.notifying_authority or 'null'}."
                    ),
                    verification_status=(
                        VerificationStatus.VERIFIED if is_fully_verified else VerificationStatus.INCOMPLETE
                    ),
                )
            )

        # Determine overall QCO status
        if is_fully_verified and effective_dates and authorities:
            qco_status = QCOStatus.APPLICABLE_VERIFIED
        else:
            qco_status = QCOStatus.ASSOCIATED_NEEDS_VERIFICATION

        return QCOResolutionResult(
            standard_id=std_id,
            is_number=is_num,
            qco_status=qco_status,
            qco_ids=qco_ids,
            order_names=order_names,
            effective_date=effective_dates[0] if effective_dates else None,
            authority=authorities[0] if authorities else None,
            evidence=evidence_items,
        )
