"""
backend/recommendation/schemas.py
=================================

Pydantic schemas for Requirement Coverage, Specification Gap Detection,
and Evidence-Backed AI Recommendations.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.regulatory.evidence import EvidenceItem
from backend.regulatory.version_resolver import VersionResolutionResult, VersionStatus
from backend.regulatory.qco_resolver import QCOResolutionResult, QCOStatus
from backend.regulatory.applicability import ApplicabilityAssessment, ApplicabilityState
from backend.retrieval.schemas import RetrievalCandidate, StandardDocument


class CoverageStatus(str, Enum):
    """Factual semantic status of a requirement facet."""
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


class GapCategory(str, Enum):
    """Specification gap classification."""
    MISSING_REQUIREMENT = "MISSING_REQUIREMENT"
    PARAMETER_UNVERIFIED = "PARAMETER_UNVERIFIED"
    PARAMETER_CONFLICT = "PARAMETER_CONFLICT"
    MATERIAL_UNVERIFIED = "MATERIAL_UNVERIFIED"
    APPLICATION_UNVERIFIED = "APPLICATION_UNVERIFIED"
    VERSION_UNVERIFIED = "VERSION_UNVERIFIED"
    REGULATORY_VERIFICATION_REQUIRED = "REGULATORY_VERIFICATION_REQUIRED"


class GapSeverity(str, Enum):
    """Impact of gap on procurement safety and compliance."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AIRecommendationState(str, Enum):
    """System recommendation classification (Decision support, not legal approval)."""
    RECOMMENDED_FOR_REVIEW = "RECOMMENDED_FOR_REVIEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    POTENTIALLY_RELEVANT = "POTENTIALLY_RELEVANT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class CoverageItem(BaseModel):
    """Detailed evaluation of a single requirement dimension."""
    model_config = ConfigDict(extra="ignore")

    field: str
    query_value: Optional[str] = None
    standard_value: Optional[str] = None
    status: CoverageStatus = CoverageStatus.UNKNOWN
    notes: str = ""
    evidence_span: Optional[str] = None


class RequirementCoverage(BaseModel):
    """Composite requirement coverage report preserving exact semantic breakdown."""
    model_config = ConfigDict(extra="ignore")

    product: CoverageItem
    sector: CoverageItem
    application: Optional[CoverageItem] = None
    materials: List[CoverageItem] = Field(default_factory=list)
    parameters: List[CoverageItem] = Field(default_factory=list)

    # Breakdown counts
    direct_matches: int = 0
    partial_matches: int = 0
    unknown_count: int = 0
    conflicts_count: int = 0
    no_match_count: int = 0
    total_evaluated: int = 0


class SpecificationGap(BaseModel):
    """Identified requirement gap requiring human verification."""
    model_config = ConfigDict(extra="ignore")

    category: GapCategory
    severity: GapSeverity
    title: str
    explanation: str
    evidence: Optional[str] = None
    verification_requirement: str


class CandidateRecommendation(BaseModel):
    """Complete synthesized candidate standard recommendation."""
    model_config = ConfigDict(extra="ignore")

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

    coverage: RequirementCoverage
    gaps: List[SpecificationGap] = Field(default_factory=list)

    standard_status: VersionStatus = VersionStatus.NEEDS_VERIFICATION
    qco_status: QCOStatus = QCOStatus.NOT_FOUND_IN_SEED
    qco_ids: List[str] = Field(default_factory=list)
    order_names: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    authority: Optional[str] = None

    overall_applicability: ApplicabilityState = ApplicabilityState.NEEDS_VERIFICATION
    recommendation_state: AIRecommendationState = AIRecommendationState.REVIEW_REQUIRED
    explanation: str = ""
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    normative_references: List[Dict[str, Any]] = Field(default_factory=list)
