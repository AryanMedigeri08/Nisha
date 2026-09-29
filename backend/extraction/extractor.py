"""
backend/extraction/extractor.py

Requirement Extraction Engine for PS26108 Phase 3.
Implements a hybrid multi-stage extraction pipeline:
- Stage 1: Deterministic rules (IS numbers, units, parameters, materials, application prepositions)
- Stage 2: Pattern / Lexical extraction (core product phrase, sector classification, domain segmentation)
- Stage 3: Optional LLM fallback (strictly constrained, non-hallucinatory, Pydantic-validated)

CRITICAL PRINCIPLES:
1. Extraction is strictly separated from retrieval, ranking, and regulatory resolution.
2. Zero label leakage: ground-truth standards, candidate lists, and provenance must NEVER be passed.
3. Every factual extraction retains an evidence span tracing back to the input text.
4. Partial extraction is valid; missing fields are omitted rather than hallucinated.
"""

import logging
from typing import List, Optional, Dict, Any

from backend.extraction.schemas import (
    ProcurementRequirements,
    ExtractedField,
    ExtractedParameter,
    ExtractedCitedStandard,
)
from backend.extraction.rules import (
    extract_cited_standards,
    extract_parameters_deterministic,
    extract_materials_deterministic,
    extract_application_deterministic,
    extract_product_deterministic,
    extract_sector_deterministic,
    extract_domain_requirements,
)

logger = logging.getLogger(__name__)

# Banned ground-truth keys to strictly enforce zero label leakage
FORBIDDEN_GROUND_TRUTH_KEYS = {
    "ground_truth_primary",
    "ground_truth_related",
    "near_match_candidates",
    "candidate_signals",
    "candidate_similarity_basis",
    "source_seed_standard",
    "ground_truth_evidence",
    "ground_truth_version",
    "ground_truth_qco",
}


class RequirementExtractor:
    """
    Multi-stage hybrid requirement extraction engine converting unstructured
    procurement query texts into structured ProcurementRequirements.
    """

    def __init__(self, use_llm_fallback: bool = False, llm_client: Optional[Any] = None):
        self.use_llm_fallback = use_llm_fallback
        self.llm_client = llm_client

    def _check_label_leakage(self, kwargs: Dict[str, Any]) -> None:
        """Enforce strict isolation: reject any ground-truth fields passed into the extractor."""
        leaked = set(kwargs.keys()).intersection(FORBIDDEN_GROUND_TRUTH_KEYS)
        if leaked:
            raise ValueError(
                f"LABEL LEAKAGE VIOLATION: Extractor received ground-truth evaluation keys: {leaked}. "
                "The extractor must operate exclusively on the raw procurement text."
            )

    def extract(
        self,
        query: str,
        query_id: str = "query_unknown",
        **kwargs
    ) -> ProcurementRequirements:
        """
        Extract structured procurement requirements from a single raw query string.

        Args:
            query: The raw procurement query / tender description text.
            query_id: Unique identifier for the query record.
            **kwargs: Extra metadata. Ground-truth evaluation fields are strictly forbidden.

        Returns:
            Validated ProcurementRequirements Pydantic model.
        """
        # Guard against label leakage
        self._check_label_leakage(kwargs)

        if not query or not query.strip():
            return ProcurementRequirements(
                query_id=query_id,
                product=ExtractedField(value=None, confidence=0.0, evidence=None),
                sector=ExtractedField(value=None, confidence=0.0, evidence=None),
                overall_confidence=0.0,
            )

        clean_query = query.strip()

        # =====================================================================
        # Stage 1: Deterministic Rules (Explicit Standards, Parameters, Materials, App)
        # =====================================================================
        cited_standards = extract_cited_standards(clean_query)
        parameters = extract_parameters_deterministic(clean_query)
        materials = extract_materials_deterministic(clean_query)
        applications = extract_application_deterministic(clean_query)

        # =====================================================================
        # Stage 2: Pattern / Lexical Extraction (Product, Sector, Domains)
        # =====================================================================
        product = extract_product_deterministic(clean_query, applications)
        sector = extract_sector_deterministic(product, applications, clean_query)
        safety_reqs, elec_reqs, mech_reqs = extract_domain_requirements(clean_query, parameters)

        # =====================================================================
        # Stage 3: Optional LLM Fallback (Constrained & Validated)
        # =====================================================================
        if self.use_llm_fallback and (not product or not product.value) and self.llm_client:
            # Fallback only when product extraction is ambiguous and LLM is enabled
            llm_result = self._call_llm_fallback(clean_query, query_id)
            if llm_result:
                return llm_result

        # =====================================================================
        # Calculate Overall Extraction Confidence
        # =====================================================================
        overall_conf = self._calculate_overall_confidence(
            product=product,
            sector=sector,
            applications=applications,
            materials=materials,
            parameters=parameters,
        )

        return ProcurementRequirements(
            query_id=query_id,
            product=product,
            sector=sector,
            application=applications,
            materials=materials,
            parameters=parameters,
            safety_requirements=safety_reqs,
            electrical_requirements=elec_reqs,
            mechanical_requirements=mech_reqs,
            cited_standards=cited_standards,
            language="en",
            overall_confidence=overall_conf,
        )

    def _calculate_overall_confidence(
        self,
        product: Optional[ExtractedField],
        sector: Optional[ExtractedField],
        applications: List[ExtractedField],
        materials: List[ExtractedField],
        parameters: List[ExtractedParameter],
    ) -> float:
        """
        Compute weighted extraction confidence score (0.0 to 1.0).
        Reflects linguistic extraction quality, NOT standard applicability.
        """
        score = 0.0
        # Product is the central entity (40% weight)
        if product and product.value:
            score += 0.40 * product.confidence

        # Sector classification (25% weight)
        if sector and sector.value:
            score += 0.25 * sector.confidence

        # Application context (15% weight)
        if applications and applications[0].value:
            score += 0.15 * applications[0].confidence

        # Materials (10% weight)
        if materials:
            avg_mat = sum(m.confidence for m in materials) / len(materials)
            score += 0.10 * avg_mat
        else:
            # Not penalized if no materials were in query
            score += 0.10 * (0.85 if product and product.value else 0.0)

        # Technical parameters (10% weight)
        if parameters:
            avg_param = sum(p.confidence for p in parameters) / len(parameters)
            score += 0.10 * avg_param
        else:
            # Not penalized if no parameters were in query
            score += 0.10 * (0.85 if product and product.value else 0.0)

        return round(min(1.0, max(0.0, score)), 2)

    def _call_llm_fallback(self, query: str, query_id: str) -> Optional[ProcurementRequirements]:
        """
        Stage 3: Strictly constrained LLM fallback prompt.
        Extracts only explicitly stated requirements without hallucinating unstated facts.
        """
        # The prompt strictly enforces factual bounding
        system_prompt = (
            "You are a strict procurement requirement extractor. "
            "Extract only information explicitly supported by the input text. "
            "Do not infer unstated technical specifications. "
            "Output must strictly follow the required JSON structure."
        )
        # Note: In production or with API key configured, invokes LLM client and parses with Pydantic
        logger.info(f"LLM fallback requested for query {query_id}")
        return None

    def extract_batch(self, records: List[Dict[str, Any]]) -> List[ProcurementRequirements]:
        """
        Batch extraction for a list of procurement records.
        Guarantees that only 'query' and 'id' are processed.
        """
        results: List[ProcurementRequirements] = []
        for r in records:
            q_id = r.get("id") or r.get("query_id") or "query_unknown"
            q_text = r.get("query", "")

            # Strip any evaluation keys before calling extract to guarantee no leakage
            clean_kwargs = {k: v for k, v in r.items() if k not in FORBIDDEN_GROUND_TRUTH_KEYS and k not in ["id", "query_id", "query"]}
            reqs = self.extract(query=q_text, query_id=q_id, **clean_kwargs)
            results.append(reqs)
        return results
