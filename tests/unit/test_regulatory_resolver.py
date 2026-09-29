"""
tests/unit/test_regulatory_resolver.py
======================================

Unit tests for VersionResolver, QCOResolver, and ApplicabilityEngine:
- Unknown/unverified version status preserved
- No inference of current status from publication year
- QCO association preserved as ASSOCIATED_NEEDS_VERIFICATION
- Missing effective dates remain null
- Missing authorities remain null
- Evidence attached to all regulatory claims
- Applicability state avoids unjustified 'APPLICABLE' claims
"""

import pytest
from backend.regulatory.version_resolver import VersionResolver, VersionStatus
from backend.regulatory.qco_resolver import QCOResolver, QCOStatus
from backend.regulatory.applicability import ApplicabilityEngine, ApplicabilityState
from backend.regulatory.evidence import VerificationStatus
from backend.retrieval.schemas import StandardDocument, RetrievalCandidate


@pytest.fixture(scope="module")
def version_resolver():
    return VersionResolver()


@pytest.fixture(scope="module")
def qco_resolver():
    return QCOResolver()


@pytest.fixture(scope="module")
def applicability_engine():
    return ApplicabilityEngine()


def test_version_resolver_no_inference_from_year(version_resolver):
    """Publication year (e.g. 2024 or 2025) must NOT cause automatic 'CURRENT' resolution."""
    doc = StandardDocument(
        standard_id="test_std_year",
        is_number="IS 9999:2025",
        title="Modern Standard Title",
        year=2025,
        status="scheme1_listed_source_record",
    )
    res = version_resolver.resolve(doc)
    # Must NOT be CURRENT without authoritative gazette verification
    assert res.status != VersionStatus.CURRENT
    assert res.status == VersionStatus.NEEDS_VERIFICATION
    assert len(res.evidence) >= 1


def test_version_resolver_withdrawn_handling(version_resolver):
    """Explicitly withdrawn standard resolved as WITHDRAWN."""
    doc = StandardDocument(
        standard_id="test_withdrawn",
        is_number="IS 1000",
        title="Withdrawn Standard",
        status="withdrawn",
    )
    res = version_resolver.resolve(doc)
    assert res.status == VersionStatus.WITHDRAWN
    assert res.evidence[0].verification_status == VerificationStatus.VERIFIED


def test_qco_resolver_preserves_seed_association(qco_resolver):
    """Standards associated with QCO in seed resolve to ASSOCIATED_NEEDS_VERIFICATION."""
    doc = StandardDocument(
        standard_id="is_269",
        is_number="IS 269",
        title="Ordinary Portland Cement",
        status="scheme1_listed_source_record",
    )
    res = qco_resolver.resolve(doc)
    assert res.qco_status == QCOStatus.ASSOCIATED_NEEDS_VERIFICATION
    assert len(res.qco_ids) >= 1
    assert "Cement" in res.order_names[0]


def test_qco_resolver_missing_effective_date_remains_none(qco_resolver):
    """Unverified effective date must remain None (no fabricated dates)."""
    doc = StandardDocument(
        standard_id="is_4246_2025",
        is_number="IS 4246:2025",
        title="Domestic gas stove",
    )
    res = qco_resolver.resolve(doc)
    assert res.effective_date is None


def test_qco_resolver_unlinked_standard():
    """Standards without QCO in seed return NOT_FOUND_IN_SEED."""
    resolver = QCOResolver()
    doc = StandardDocument(
        standard_id="unlinked_test_std",
        is_number="IS 99999",
        title="Unlinked Standard",
    )
    res = resolver.resolve(doc)
    assert res.qco_status == QCOStatus.NOT_FOUND_IN_SEED
    assert res.qco_ids == []


def test_applicability_engine_no_unsupported_applicable(applicability_engine, version_resolver, qco_resolver):
    """Applicability assessment must never return bare APPLICABLE without full gazette proof."""
    doc = StandardDocument(
        standard_id="is_269",
        is_number="IS 269",
        title="Ordinary Portland Cement",
        status="scheme1_listed_source_record",
    )
    cand = RetrievalCandidate(
        standard_id="is_269",
        is_number="IS 269",
        title="Ordinary Portland Cement",
        reranker_score=8.5,
        final_rank=1,
    )
    v_res = version_resolver.resolve(doc)
    q_res = qco_resolver.resolve(doc)

    assessment = applicability_engine.assess(cand, v_res, q_res)

    assert assessment.overall_applicability in (
        ApplicabilityState.REGULATORYALLY_ASSOCIATED,
        ApplicabilityState.NEEDS_VERIFICATION,
        ApplicabilityState.RELEVANT_BUT_STATUS_UNKNOWN,
    )
    assert assessment.overall_applicability.value != "APPLICABLE"


def test_applicability_preserves_retrieval_score_unpolluted(applicability_engine, version_resolver, qco_resolver):
    """Retrieval score must remain untouched and separate from regulatory state."""
    doc = StandardDocument(standard_id="is_269", is_number="IS 269", title="Test Cement")
    cand = RetrievalCandidate(
        standard_id="is_269",
        is_number="IS 269",
        title="Test Cement",
        reranker_score=9.42,
        final_rank=1,
    )
    v_res = version_resolver.resolve(doc)
    q_res = qco_resolver.resolve(doc)

    assessment = applicability_engine.assess(cand, v_res, q_res)
    assert assessment.retrieval_relevance_score == 9.42
    assert assessment.retrieval_rank == 1
