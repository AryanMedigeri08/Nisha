"""
backend/regulatory/applicability.py
===================================

Applicability State Engine for PS26108.
Combines retrieval relevance, edition currency/version status, and QCO regulatory associations
into a structured, explainable legal applicability determination.

CRITICAL PRINCIPLE:
RETRIEVAL RELEVANCE != LEGAL APPLICABILITY
Never output 'APPLICABLE' without complete gazette-level verification.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.regulatory.evidence import EvidenceItem, VerificationStatus, SourceType
from backend.regulatory.version_resolver import VersionStatus, VersionResolutionResult
from backend.regulatory.qco_resolver import QCOStatus, QCOResolutionResult
from backend.retrieval.schemas import RetrievalCandidate

logger = logging.getLogger(__name__)


class ApplicabilityState(str, Enum):
    """Overall applicability classification preserving regulatory uncertainty."""
    RELEVANT = "RELEVANT"
    RELEVANT_BUT_STATUS_UNKNOWN = "RELEVANT_BUT_STATUS_UNKNOWN"
    REGULATORYALLY_ASSOCIATED = "REGULATORYALLY_ASSOCIATED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ApplicabilityAssessment(BaseModel):
    """Complete structured applicability object."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    title: str
    sector: Optional[str] = None
    retrieval_rank: int
    retrieval_relevance_score: Optional[float] = None
    standard_status: VersionStatus
    reference_status: str = "VERIFIED"
    qco_status: QCOStatus
    overall_applicability: ApplicabilityState
    notes: str = ""
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ApplicabilityEngine:
    """Evaluates the composite applicability state of retrieved standard candidates."""

    def assess(
        self,
        candidate: RetrievalCandidate,
        version_result: VersionResolutionResult,
        qco_result: QCOResolutionResult,
        reference_status: str = "VERIFIED",
    ) -> ApplicabilityAssessment:
        """
        Synthesize retrieval relevance, standard version status, and QCO status
        into an honest, evidence-grounded applicability state.
        """
        all_evidence: List[EvidenceItem] = []
        all_evidence.extend(version_result.evidence)
        all_evidence.extend(qco_result.evidence)

        # Retrieval score (reranker_score or rrf_score or bm25/dense)
        relevance_score = (
            candidate.reranker_score
            if candidate.reranker_score is not None
            else candidate.rrf_score
        )

        # Determine overall applicability state
        # 1. If candidate is withdrawn or superseded
        if version_result.status in (VersionStatus.WITHDRAWN, VersionStatus.SUPERSEDED):
            overall = ApplicabilityState.INSUFFICIENT_EVIDENCE
            notes = f"Standard is marked as {version_result.status.value}; not legally applicable for new procurement."

        # 2. If associated with QCO
        elif qco_result.qco_status in (QCOStatus.ASSOCIATED_NEEDS_VERIFICATION, QCOStatus.APPLICABLE_VERIFIED):
            overall = ApplicabilityState.REGULATORYALLY_ASSOCIATED
            notes = (
                f"Standard is technically relevant and associated with QCO '{qco_result.order_names[0] if qco_result.order_names else 'Order'}'. "
                "Official notification date and notifying authority require live BIS/DPIIT confirmation."
            )

        # 3. If standard currency is unverified but relevant
        elif version_result.status in (VersionStatus.UNKNOWN, VersionStatus.NEEDS_VERIFICATION):
            overall = ApplicabilityState.RELEVANT_BUT_STATUS_UNKNOWN
            notes = (
                "Standard is technically matched to procurement requirements, but current revision status "
                "is pending gazette verification."
            )

        # 4. Standard is current with no QCO
        elif version_result.status == VersionStatus.CURRENT:
            overall = ApplicabilityState.RELEVANT
            notes = "Standard is current and matches procurement requirements; voluntary BIS standard."

        else:
            overall = ApplicabilityState.NEEDS_VERIFICATION
            notes = "Insufficient verified data to establish legal enforceability."

        return ApplicabilityAssessment(
            standard_id=candidate.standard_id,
            is_number=candidate.is_number,
            title=candidate.title,
            sector=candidate.sector,
            retrieval_rank=candidate.final_rank,
            retrieval_relevance_score=relevance_score,
            standard_status=version_result.status,
            reference_status=reference_status,
            qco_status=qco_result.qco_status,
            overall_applicability=overall,
            notes=notes,
            evidence=all_evidence,
        )
