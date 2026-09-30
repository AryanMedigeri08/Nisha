"""
backend/recommendation/engine.py
================================

Unified AI Recommendation Engine for PS26108 Phase 6 & 6.1.
Synthesizes requirement coverage, gap detection, version currency, QCO status,
and retrieval ranking into evidence-backed decision support recommendations.

CRITICAL SEPARATION:
Retrieval Relevance != Requirement Coverage != Recommendation State != QCO Association != Legal Applicability
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.extraction.schemas import ProcurementRequirements
from backend.recommendation.coverage import CoverageEngine
from backend.recommendation.gaps import GapDetector
from backend.recommendation.schemas import (
    AIRecommendationState,
    CandidateRecommendation,
    CoverageStatus,
    GapCategory,
    GapSeverity,
)
from backend.regulatory.applicability import ApplicabilityAssessment, ApplicabilityState
from backend.regulatory.evidence import EvidenceItem, SourceType, VerificationStatus
from backend.regulatory.qco_resolver import QCOResolutionResult, QCOStatus
from backend.regulatory.version_resolver import VersionResolutionResult, VersionStatus
from backend.retrieval.schemas import RetrievalCandidate, StandardDocument

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates evidence-backed standard recommendations for procurement review."""

    def __init__(self):
        self.coverage_engine = CoverageEngine()
        self.gap_detector = GapDetector()

    def build_recommendation(
        self,
        requirements: ProcurementRequirements,
        candidate: RetrievalCandidate,
        standard: StandardDocument,
        version_result: VersionResolutionResult,
        qco_result: QCOResolutionResult,
        applicability: ApplicabilityAssessment,
        normative_references: Optional[List[Dict[str, Any]]] = None,
    ) -> CandidateRecommendation:
        """
        Synthesize all upstream signals into a structured candidate recommendation.
        """
        norm_refs = normative_references or []

        # 1. Evaluate facet-by-facet requirement coverage
        coverage = self.coverage_engine.evaluate_coverage(requirements, standard)

        # 2. Detect specification & compliance gaps
        gaps = self.gap_detector.detect_gaps(
            requirements=requirements,
            coverage=coverage,
            version_result=version_result,
            qco_result=qco_result,
            standard=standard,
        )

        # 3. Determine AI Recommendation State
        has_high_gaps = any(g.severity == GapSeverity.HIGH for g in gaps if g.category != GapCategory.REGULATORY_VERIFICATION_REQUIRED)
        has_conflict = coverage.conflicts_count > 0
        is_withdrawn = version_result.status in (VersionStatus.WITHDRAWN, VersionStatus.SUPERSEDED)

        if is_withdrawn or has_conflict or coverage.product.status == CoverageStatus.NO_MATCH:
            recommendation_state = AIRecommendationState.INSUFFICIENT_EVIDENCE
            explanation = (
                f"Candidate {standard.is_number} exhibits critical incompatibilities "
                f"({ 'withdrawn/superseded' if is_withdrawn else 'product/parameter mismatch' }); "
                "not recommended as primary procurement specification."
            )
        elif candidate.final_rank <= 3 and coverage.product.status == CoverageStatus.MATCH and not has_high_gaps:
            recommendation_state = AIRecommendationState.RECOMMENDED_FOR_REVIEW
            explanation = (
                f"Candidate {standard.is_number} demonstrates high retrieval relevance (Rank #{candidate.final_rank}) "
                f"and direct product/sector alignment. Recommended for officer review and verification."
            )
        elif coverage.product.status in (CoverageStatus.MATCH, CoverageStatus.PARTIAL_MATCH):
            recommendation_state = AIRecommendationState.REVIEW_REQUIRED
            explanation = (
                f"Candidate {standard.is_number} is relevant to the procurement scope with partial requirement coverage "
                f"or pending regulatory verification. Officer review required."
            )
        else:
            recommendation_state = AIRecommendationState.POTENTIALLY_RELEVANT
            explanation = (
                f"Candidate {standard.is_number} is potentially related as an allied or general framework standard; "
                "further scoping verification required."
            )

        # 4. Collate all inspectable evidence items
        all_evidence: List[EvidenceItem] = []
        all_evidence.extend(version_result.evidence)
        all_evidence.extend(qco_result.evidence)

        # Add retrieval provenance evidence
        retrieval_text = (
            f"Retrieval Rank: #{candidate.final_rank}, "
            f"Cross-Encoder Score: {candidate.reranker_score if candidate.reranker_score is not None else 'N/A'}, "
            f"RRF Score: {round(candidate.rrf_score, 4) if candidate.rrf_score is not None else 'N/A'}."
        )
        app_str = ", ".join(standard.application) if isinstance(standard.application, list) else getattr(standard, "application", None)
        source_url_val = getattr(standard, "source_url", None)

        all_evidence.append(
            EvidenceItem(
                source_type=SourceType.SEED_DATASET.value,
                source_id=standard.standard_id,
                source_url=source_url_val,
                claim=f"Candidate {standard.is_number} retrieved via hybrid sparse+dense search.",
                evidence_text=retrieval_text,
                verification_status=VerificationStatus.VERIFIED,
            )
        )

        return CandidateRecommendation(
            standard_id=standard.standard_id,
            is_number=standard.is_number,
            title=standard.title,
            sector=standard.sector,
            application=app_str,
            materials=standard.materials or [],
            technical_parameters=standard.technical_parameters or [],
            retrieval_rank=candidate.final_rank,
            reranker_score=candidate.reranker_score,
            rrf_score=candidate.rrf_score,
            retrieval_method="hybrid_cross_encoder",
            coverage=coverage,
            gaps=gaps,
            standard_status=version_result.status,
            qco_status=qco_result.qco_status,
            qco_ids=qco_result.qco_ids,
            order_names=qco_result.order_names,
            effective_date=qco_result.effective_date,
            authority=qco_result.authority,
            overall_applicability=applicability.overall_applicability,
            recommendation_state=recommendation_state,
            explanation=explanation,
            evidence_items=all_evidence,
            normative_references=norm_refs,
        )
