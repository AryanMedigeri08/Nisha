"""
backend/regulatory/version_resolver.py
======================================

Version and legal currency resolver for Indian Standards.
Distinguishes CURRENT, SUPERSEDED, WITHDRAWN, DRAFT, UNKNOWN, and NEEDS_VERIFICATION.

CRITICAL RULES:
- Never infer 'CURRENT' from publication year alone.
- Never infer 'CURRENT' from numerical ordering of IS numbers.
- Never infer 'CURRENT' from semantic similarity or synthetic query text.
- If the seed dataset does not establish official BIS currency, return UNKNOWN or NEEDS_VERIFICATION.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.regulatory.evidence import EvidenceItem, VerificationStatus, SourceType
from backend.retrieval.schemas import StandardDocument

logger = logging.getLogger(__name__)


class VersionStatus(str, Enum):
    """Standard legal currency / version status."""
    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"
    DRAFT = "DRAFT"
    UNKNOWN = "UNKNOWN"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class VersionResolutionResult(BaseModel):
    """Resolved version and currency status with supporting evidence."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    status: VersionStatus
    year: Optional[int] = None
    superseded_by: Optional[str] = None
    notes: str = ""
    evidence: List[EvidenceItem] = Field(default_factory=list)


class VersionResolver:
    """Resolves standard version and validity status from verified seed records."""

    def resolve(self, standard: StandardDocument) -> VersionResolutionResult:
        """
        Resolve standard status without fabricating currency claims.
        """
        std_id = standard.standard_id
        is_num = standard.is_number
        year = standard.year
        raw_status = (standard.status or "").lower()

        evidence_list: List[EvidenceItem] = []

        # Check explicit withdrawal or supersession
        if "withdrawn" in raw_status:
            evidence_list.append(
                EvidenceItem(
                    source_type=SourceType.SEED_DATASET.value,
                    source_id=std_id,
                    claim=f"Standard {is_num} is marked as withdrawn in seed dataset.",
                    evidence_text=f"Raw status field: '{standard.status}'",
                    verification_status=VerificationStatus.VERIFIED,
                )
            )
            return VersionResolutionResult(
                standard_id=std_id,
                is_number=is_num,
                status=VersionStatus.WITHDRAWN,
                year=year,
                evidence=evidence_list,
            )

        if "superseded" in raw_status:
            evidence_list.append(
                EvidenceItem(
                    source_type=SourceType.SEED_DATASET.value,
                    source_id=std_id,
                    claim=f"Standard {is_num} is superseded.",
                    evidence_text=f"Raw status field: '{standard.status}'",
                    verification_status=VerificationStatus.VERIFIED,
                )
            )
            return VersionResolutionResult(
                standard_id=std_id,
                is_number=is_num,
                status=VersionStatus.SUPERSEDED,
                year=year,
                evidence=evidence_list,
            )

        # In Scheme-1 bootstrap seed, records are listed as Scheme-1 source records,
        # but full gazette-level currency verification is pending.
        evidence_list.append(
            EvidenceItem(
                source_type=SourceType.SEED_DATASET.value,
                source_id=std_id,
                claim=f"Standard {is_num} listed in Scheme-1 seed dataset; full BIS gazette currency unverified.",
                evidence_text=f"Seed status: '{standard.status}'. Publication year: {year or 'None'}.",
                verification_status=VerificationStatus.INCOMPLETE,
            )
        )

        return VersionResolutionResult(
            standard_id=std_id,
            is_number=is_num,
            status=VersionStatus.NEEDS_VERIFICATION,
            year=year,
            notes="Standard listed in seed Scheme-1 dataset; live BIS portal confirmation required before production procurement.",
            evidence=evidence_list,
        )
