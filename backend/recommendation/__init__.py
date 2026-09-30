"""
backend/recommendation
======================

Phase 6 & 6.1 Recommendation, Requirement Coverage, and Gap Detection package.
"""

from backend.recommendation.schemas import (
    CoverageStatus,
    GapCategory,
    GapSeverity,
    AIRecommendationState,
    CoverageItem,
    RequirementCoverage,
    SpecificationGap,
    CandidateRecommendation,
)
from backend.recommendation.coverage import CoverageEngine
from backend.recommendation.gaps import GapDetector
from backend.recommendation.engine import RecommendationEngine

__all__ = [
    "CoverageStatus",
    "GapCategory",
    "GapSeverity",
    "AIRecommendationState",
    "CoverageItem",
    "RequirementCoverage",
    "SpecificationGap",
    "CandidateRecommendation",
    "CoverageEngine",
    "GapDetector",
    "RecommendationEngine",
]
