"""
backend/recommendation/gaps.py
==============================

Specification Gap Detection Engine for PS26108.
Identifies factual gaps in requirement coverage, version currency,
and regulatory applicability without inventing arbitrary issues.
"""

from __future__ import annotations

from typing import List
from backend.extraction.schemas import ProcurementRequirements
from backend.recommendation.schemas import (
    GapCategory,
    GapSeverity,
    RequirementCoverage,
    SpecificationGap,
    CoverageStatus,
)
from backend.regulatory.version_resolver import VersionResolutionResult, VersionStatus
from backend.regulatory.qco_resolver import QCOResolutionResult, QCOStatus
from backend.retrieval.schemas import StandardDocument


class GapDetector:
    """Detects factual compliance, technical, and regulatory specification gaps."""

    def detect_gaps(
        self,
        requirements: ProcurementRequirements,
        coverage: RequirementCoverage,
        version_result: VersionResolutionResult,
        qco_result: QCOResolutionResult,
        standard: StandardDocument,
    ) -> List[SpecificationGap]:
        """
        Identify transparent specification gaps requiring human verification.
        """
        gaps: List[SpecificationGap] = []

        # 1. Regulatory Verification Required
        if qco_result.qco_status == QCOStatus.ASSOCIATED_NEEDS_VERIFICATION:
            order_str = ", ".join(qco_result.order_names) if qco_result.order_names else "Quality Control Order"
            gaps.append(
                SpecificationGap(
                    category=GapCategory.REGULATORY_VERIFICATION_REQUIRED,
                    severity=GapSeverity.HIGH,
                    title="QCO Gazette Verification Pending",
                    explanation=(
                        f"Standard {standard.is_number} is associated with QCO '{order_str}' in seed records, "
                        "but official effective date and notifying ministry gazette notification require live confirmation."
                    ),
                    evidence=f"Seed QCO IDs: {', '.join(qco_result.qco_ids) if qco_result.qco_ids else 'None'}",
                    verification_requirement="Verify current DPIIT/Ministry Gazette QCO enforcement date and HS code applicability.",
                )
            )

        # 2. Standard Currency / Version Unverified
        if version_result.status in (VersionStatus.NEEDS_VERIFICATION, VersionStatus.UNKNOWN):
            gaps.append(
                SpecificationGap(
                    category=GapCategory.VERSION_UNVERIFIED,
                    severity=GapSeverity.MEDIUM,
                    title="Standard Edition Currency Unverified",
                    explanation=(
                        f"Standard {standard.is_number} is listed in Scheme-1 seed data, but full BIS portal gazette "
                        "currency (amendments/reaffirmation) is unverified in offline dataset."
                    ),
                    evidence=f"Seed status: '{standard.status}', publication year: {standard.year or 'Unspecified'}",
                    verification_requirement="Confirm standard is current and active on BIS Manakonline portal.",
                )
            )
        elif version_result.status in (VersionStatus.SUPERSEDED, VersionStatus.WITHDRAWN):
            gaps.append(
                SpecificationGap(
                    category=GapCategory.VERSION_UNVERIFIED,
                    severity=GapSeverity.HIGH,
                    title=f"Standard Marked as {version_result.status.value}",
                    explanation=f"Standard {standard.is_number} has been superseded or withdrawn. New procurement must use successor standard.",
                    evidence=f"Status: {version_result.status.value}, Superseded By: {version_result.superseded_by or 'None specified'}",
                    verification_requirement="Identify and apply active replacement standard for procurement tender.",
                )
            )

        # 3. Product or Sector Mismatch
        if coverage.product.status == CoverageStatus.PARTIAL_MATCH:
            gaps.append(
                SpecificationGap(
                    category=GapCategory.MISSING_REQUIREMENT,
                    severity=GapSeverity.MEDIUM,
                    title="Partial Product Scope Alignment",
                    explanation=f"Extracted product '{coverage.product.query_value}' partially overlaps with standard title '{standard.title}'.",
                    evidence=coverage.product.evidence_span,
                    verification_requirement="Review standard scope clause 1 to verify full product inclusion.",
                )
            )
        elif coverage.product.status == CoverageStatus.NO_MATCH:
            gaps.append(
                SpecificationGap(
                    category=GapCategory.MISSING_REQUIREMENT,
                    severity=GapSeverity.HIGH,
                    title="Product Scope Discrepancy",
                    explanation=f"Extracted product '{coverage.product.query_value}' does not match standard title '{standard.title}'.",
                    evidence=coverage.product.evidence_span,
                    verification_requirement="Confirm if standard is applicable as an allied or general framework standard.",
                )
            )

        # 4. Parameter Conflicts and Unverified Parameters
        for p_cov in coverage.parameters:
            if p_cov.status == CoverageStatus.CONFLICT:
                gaps.append(
                    SpecificationGap(
                        category=GapCategory.PARAMETER_CONFLICT,
                        severity=GapSeverity.HIGH,
                        title=f"Parameter Specification Conflict: {p_cov.field}",
                        explanation=f"Query requirement '{p_cov.query_value}' conflicts with standard facet '{p_cov.standard_value}'.",
                        evidence=p_cov.evidence_span,
                        verification_requirement="Review technical clauses to confirm whether required parameter rating is compliant.",
                    )
                )
            elif p_cov.status == CoverageStatus.UNKNOWN:
                gaps.append(
                    SpecificationGap(
                        category=GapCategory.PARAMETER_UNVERIFIED,
                        severity=GapSeverity.LOW,
                        title=f"Parameter Compliance Unverified: {p_cov.field}",
                        explanation=f"Parameter requirement '{p_cov.query_value}' is not explicitly listed in standard seed facets.",
                        evidence=p_cov.evidence_span,
                        verification_requirement="Check detailed standard table of performance ratings / test methods.",
                    )
                )

        # 5. Material Unverified
        for m_cov in coverage.materials:
            if m_cov.status == CoverageStatus.UNKNOWN:
                gaps.append(
                    SpecificationGap(
                        category=GapCategory.MATERIAL_UNVERIFIED,
                        severity=GapSeverity.LOW,
                        title=f"Material Compatibility Unverified: {m_cov.query_value}",
                        explanation=f"Required material '{m_cov.query_value}' is not explicitly enumerated in seed material facets.",
                        evidence=m_cov.evidence_span,
                        verification_requirement="Verify approved materials in standard Section 3 (Raw Materials & Composition).",
                    )
                )

        # 6. Application Unverified
        if coverage.application and coverage.application.status == CoverageStatus.UNKNOWN and coverage.application.query_value:
            gaps.append(
                SpecificationGap(
                    category=GapCategory.APPLICATION_UNVERIFIED,
                    severity=GapSeverity.LOW,
                    title="Application Context Unverified",
                    explanation=f"Procurement application '{coverage.application.query_value}' is not listed in standard summary.",
                    evidence=coverage.application.evidence_span,
                    verification_requirement="Confirm application suitability under standard environmental/duty conditions.",
                )
            )

        return gaps
