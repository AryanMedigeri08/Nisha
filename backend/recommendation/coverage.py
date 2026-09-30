"""
backend/recommendation/coverage.py
==================================

Requirement Coverage Engine for PS26108.
Factual facet-by-facet comparison between extracted procurement requirements
and standard facet metadata.

CRITICAL RULES:
- Never collapse UNKNOWN into NO_MATCH.
- Never collapse PARTIAL_MATCH into MATCH.
- Preserve exact counts for auditable breakdown.
"""

from __future__ import annotations

import re
from typing import List, Optional, Set
from backend.extraction.schemas import ProcurementRequirements, ExtractedField, ExtractedParameter
from backend.recommendation.schemas import CoverageItem, CoverageStatus, RequirementCoverage
from backend.retrieval.schemas import StandardDocument


def _tokenize(text: Optional[str]) -> Set[str]:
    """Tokenize text into lowercase words for set comparison."""
    if not text:
        return set()
    return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))


class CoverageEngine:
    """Evaluates requirement coverage across all extracted procurement dimensions."""

    def evaluate_coverage(
        self,
        requirements: ProcurementRequirements,
        standard: StandardDocument,
    ) -> RequirementCoverage:
        """
        Compare extracted requirements with standard profile facets.
        Produces transparent, factually-bounded coverage items.
        """
        items: List[CoverageItem] = []

        # 1. Product Coverage
        product_cov = self._evaluate_product(requirements.product, standard)
        items.append(product_cov)

        # 2. Sector Coverage
        sector_cov = self._evaluate_sector(requirements.sector, standard)
        items.append(sector_cov)

        # 3. Application Coverage
        app_cov = self._evaluate_application(requirements.application, standard)
        if app_cov:
            items.append(app_cov)

        # 4. Materials Coverage
        mat_covs = self._evaluate_materials(requirements.materials, standard)
        items.extend(mat_covs)

        # 5. Parameters Coverage
        param_covs = self._evaluate_parameters(requirements.parameters, standard)
        items.extend(param_covs)

        # Breakdown counts
        direct_matches = sum(1 for it in items if it.status == CoverageStatus.MATCH)
        partial_matches = sum(1 for it in items if it.status == CoverageStatus.PARTIAL_MATCH)
        unknown_count = sum(1 for it in items if it.status == CoverageStatus.UNKNOWN)
        conflicts_count = sum(1 for it in items if it.status == CoverageStatus.CONFLICT)
        no_match_count = sum(1 for it in items if it.status == CoverageStatus.NO_MATCH)

        return RequirementCoverage(
            product=product_cov,
            sector=sector_cov,
            application=app_cov,
            materials=mat_covs,
            parameters=param_covs,
            direct_matches=direct_matches,
            partial_matches=partial_matches,
            unknown_count=unknown_count,
            conflicts_count=conflicts_count,
            no_match_count=no_match_count,
            total_evaluated=len(items),
        )

    def _evaluate_product(
        self,
        extracted_product: Optional[ExtractedField],
        standard: StandardDocument,
    ) -> CoverageItem:
        """Compare extracted product phrase against standard title, aliases, and IS number."""
        if not extracted_product or not extracted_product.value:
            return CoverageItem(
                field="product",
                query_value=None,
                standard_value=standard.title,
                status=CoverageStatus.UNKNOWN,
                notes="No explicit product entity extracted from procurement query.",
                evidence_span=None,
            )

        q_val = extracted_product.value.strip()
        q_tokens = _tokenize(q_val)

        std_title_tokens = _tokenize(standard.title)
        std_alias_tokens: Set[str] = set()
        aliases = getattr(standard, "product_aliases", None) or []
        if isinstance(aliases, list):
            for alias in aliases:
                std_alias_tokens.update(_tokenize(alias))

        combined_std_tokens = std_title_tokens.union(std_alias_tokens)

        # Check exact or near-complete token overlap
        overlap = q_tokens.intersection(combined_std_tokens)
        if len(q_tokens) > 0 and len(overlap) == len(q_tokens):
            return CoverageItem(
                field="product",
                query_value=q_val,
                standard_value=standard.title,
                status=CoverageStatus.MATCH,
                notes=f"Direct product match against standard title/aliases: '{standard.title}'",
                evidence_span=extracted_product.evidence or q_val,
            )
        elif len(overlap) > 0:
            return CoverageItem(
                field="product",
                query_value=q_val,
                standard_value=standard.title,
                status=CoverageStatus.PARTIAL_MATCH,
                notes=f"Partial product overlap on keywords {overlap} in '{standard.title}'",
                evidence_span=extracted_product.evidence or q_val,
            )
        else:
            return CoverageItem(
                field="product",
                query_value=q_val,
                standard_value=standard.title,
                status=CoverageStatus.NO_MATCH,
                notes=f"Extracted product '{q_val}' not matched in standard title '{standard.title}'",
                evidence_span=extracted_product.evidence or q_val,
            )

    def _evaluate_sector(
        self,
        extracted_sector: Optional[ExtractedField],
        standard: StandardDocument,
    ) -> CoverageItem:
        """Compare extracted sector against standard sector classification."""
        std_sector = standard.sector or "Unclassified"

        if not extracted_sector or not extracted_sector.value:
            return CoverageItem(
                field="sector",
                query_value=None,
                standard_value=std_sector,
                status=CoverageStatus.UNKNOWN,
                notes="No sector specified in procurement query.",
                evidence_span=None,
            )

        q_val = extracted_sector.value.strip()
        q_tokens = _tokenize(q_val)
        std_tokens = _tokenize(std_sector)

        overlap = q_tokens.intersection(std_tokens)
        if len(q_tokens) > 0 and (len(overlap) == len(q_tokens) or q_val.lower() == std_sector.lower()):
            return CoverageItem(
                field="sector",
                query_value=q_val,
                standard_value=std_sector,
                status=CoverageStatus.MATCH,
                notes=f"Sector match: '{std_sector}'",
                evidence_span=extracted_sector.evidence or q_val,
            )
        elif len(overlap) > 0:
            return CoverageItem(
                field="sector",
                query_value=q_val,
                standard_value=std_sector,
                status=CoverageStatus.PARTIAL_MATCH,
                notes=f"Related sector classification: '{std_sector}'",
                evidence_span=extracted_sector.evidence or q_val,
            )
        else:
            return CoverageItem(
                field="sector",
                query_value=q_val,
                standard_value=std_sector,
                status=CoverageStatus.NO_MATCH,
                notes=f"Query sector '{q_val}' differs from standard sector '{std_sector}'",
                evidence_span=extracted_sector.evidence or q_val,
            )

    def _evaluate_application(
        self,
        extracted_apps: List[ExtractedField],
        standard: StandardDocument,
    ) -> Optional[CoverageItem]:
        """Compare extracted application context against standard application facet."""
        std_app_raw = getattr(standard, "application", "")
        if isinstance(std_app_raw, list):
            std_app = ", ".join(std_app_raw)
        else:
            std_app = str(std_app_raw or "")

        if not extracted_apps:
            if not std_app:
                return None
            return CoverageItem(
                field="application",
                query_value=None,
                standard_value=std_app,
                status=CoverageStatus.UNKNOWN,
                notes="No explicit application specified in query.",
                evidence_span=None,
            )

        q_val = ", ".join(a.value for a in extracted_apps if a.value)
        evidence = extracted_apps[0].evidence if extracted_apps else None

        if not std_app:
            return CoverageItem(
                field="application",
                query_value=q_val,
                standard_value=None,
                status=CoverageStatus.UNKNOWN,
                notes="Standard has no derived application facet in seed data.",
                evidence_span=evidence,
            )

        q_tokens = _tokenize(q_val)
        std_tokens = _tokenize(std_app)
        overlap = q_tokens.intersection(std_tokens)

        if len(overlap) >= len(q_tokens) and len(q_tokens) > 0:
            status = CoverageStatus.MATCH
            notes = f"Application match: '{std_app}'"
        elif len(overlap) > 0:
            status = CoverageStatus.PARTIAL_MATCH
            notes = f"Partial application match: '{std_app}'"
        else:
            status = CoverageStatus.UNKNOWN
            notes = f"Application domain '{q_val}' unverified in standard seed facet '{std_app}'"

        return CoverageItem(
            field="application",
            query_value=q_val,
            standard_value=std_app,
            status=status,
            notes=notes,
            evidence_span=evidence,
        )

    def _evaluate_materials(
        self,
        extracted_materials: List[ExtractedField],
        standard: StandardDocument,
    ) -> List[CoverageItem]:
        """Compare extracted materials against standard material facets."""
        results: List[CoverageItem] = []
        std_materials = standard.materials or []
        std_mat_str = ", ".join(std_materials) if std_materials else "None specified"

        for mat in extracted_materials:
            if not mat.value:
                continue
            m_val = mat.value.strip().lower()
            m_tokens = _tokenize(m_val)

            # Check exact presence in standard materials list or title
            found_exact = False
            for sm in std_materials:
                sm_tokens = _tokenize(sm)
                if m_tokens.issubset(sm_tokens) or sm.lower() == m_val:
                    found_exact = True
                    break

            if found_exact or m_val in standard.title.lower():
                results.append(
                    CoverageItem(
                        field=f"material:{mat.value}",
                        query_value=mat.value,
                        standard_value=std_mat_str,
                        status=CoverageStatus.MATCH,
                        notes=f"Material '{mat.value}' supported in standard facets.",
                        evidence_span=mat.evidence or mat.value,
                    )
                )
            elif not std_materials:
                results.append(
                    CoverageItem(
                        field=f"material:{mat.value}",
                        query_value=mat.value,
                        standard_value=None,
                        status=CoverageStatus.UNKNOWN,
                        notes=f"Standard material scope unverified from seed facets for '{mat.value}'.",
                        evidence_span=mat.evidence or mat.value,
                    )
                )
            else:
                results.append(
                    CoverageItem(
                        field=f"material:{mat.value}",
                        query_value=mat.value,
                        standard_value=std_mat_str,
                        status=CoverageStatus.UNKNOWN,
                        notes=f"Material '{mat.value}' not explicitly listed in standard facets ({std_mat_str}).",
                        evidence_span=mat.evidence or mat.value,
                    )
                )

        return results

    def _evaluate_parameters(
        self,
        extracted_params: List[ExtractedParameter],
        standard: StandardDocument,
    ) -> List[CoverageItem]:
        """Compare extracted technical parameters against standard technical parameter facets."""
        results: List[CoverageItem] = []
        std_params = standard.technical_parameters or []
        std_param_str = "; ".join(std_params) if std_params else "None specified"

        for param in extracted_params:
            p_name = param.name.strip()
            p_val = str(param.value) if param.value is not None else ""
            p_unit = param.unit or ""
            p_display = f"{p_name} {p_val} {p_unit}".strip()

            matched_in_std = False
            conflict_detected = False

            p_tokens = _tokenize(p_name)

            for sp in std_params:
                sp_tokens = _tokenize(sp)
                if p_tokens.intersection(sp_tokens):
                    # Parameter name is referenced in standard
                    if p_val and str(p_val) in sp:
                        matched_in_std = True
                        break
                    elif p_val and any(char.isdigit() for char in sp):
                        # Contains different numbers -> conflict or specific requirement
                        conflict_detected = False  # Keep as unknown unless strictly incompatible

            if matched_in_std:
                results.append(
                    CoverageItem(
                        field=f"parameter:{p_name}",
                        query_value=p_display,
                        standard_value=std_param_str,
                        status=CoverageStatus.MATCH,
                        notes=f"Parameter '{p_display}' directly matches standard specification.",
                        evidence_span=getattr(param, "evidence", None) or p_display,
                    )
                )
            elif conflict_detected:
                results.append(
                    CoverageItem(
                        field=f"parameter:{p_name}",
                        query_value=p_display,
                        standard_value=std_param_str,
                        status=CoverageStatus.CONFLICT,
                        notes=f"Parameter '{p_display}' potentially conflicts with standard specification.",
                        evidence_span=getattr(param, "evidence", None) or p_display,
                    )
                )
            else:
                results.append(
                    CoverageItem(
                        field=f"parameter:{p_name}",
                        query_value=p_display,
                        standard_value=std_param_str,
                        status=CoverageStatus.UNKNOWN,
                        notes=f"Parameter '{p_display}' requires detailed clause verification.",
                        evidence_span=getattr(param, "evidence", None) or p_display,
                    )
                )

        return results
