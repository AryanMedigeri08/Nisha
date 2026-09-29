"""
backend/regulatory
==================

Regulatory and version resolution module for PS26108 Phase 5.
Includes version currency resolver, QCO regulatory resolver,
evidence provenance models, and structured applicability state assessment.
"""

from backend.regulatory.evidence import (
    EvidenceItem,
    VerificationStatus,
    SourceType,
)
from backend.regulatory.version_resolver import (
    VersionResolver,
    VersionStatus,
    VersionResolutionResult,
)
from backend.regulatory.qco_resolver import (
    QCOResolver,
    QCOStatus,
    QCOResolutionResult,
)
from backend.regulatory.applicability import (
    ApplicabilityEngine,
    ApplicabilityState,
    ApplicabilityAssessment,
)

__all__ = [
    "EvidenceItem",
    "VerificationStatus",
    "SourceType",
    "VersionResolver",
    "VersionStatus",
    "VersionResolutionResult",
    "QCOResolver",
    "QCOStatus",
    "QCOResolutionResult",
    "ApplicabilityEngine",
    "ApplicabilityState",
    "ApplicabilityAssessment",
]
