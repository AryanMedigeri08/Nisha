"""
Unit tests for the synthetic dataset generator (scripts/generate_synthetic.py).
Validates requirements from Phase 2 and Phase 2.1 specifications:
- Total count (500), difficulty distribution, ground-truth validity
- Absence of data leakage and fabricated claims
- Provenance tracking (ground_truth_evidence) with 100% coverage
- Zero unsupported technical facts (materials, parameters, numeric values)
- NEAR_MATCH quality: primary never in candidates, candidates valid & distinct, similarity signals
- Sector/product consistency (sector_original, sector_normalized, IS 4151)
- Fluff ratio constraint on HARD records (15-30%)
- Deterministic reproducibility
"""

import json
import re
import pytest
from pathlib import Path

from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, Reference
from scripts.generate_synthetic import (
    GroundedSyntheticGenerator,
    SyntheticDatasetGenerator,
    load_standards_and_references,
    extract_numbers_from_text,
)

DATA_PATH = Path("data/synthetic/synthetic_queries_v1.jsonl")
REPORT_PATH = Path("data/synthetic/synthetic_validation_report.json")
SAMPLE_PATH = Path("data/synthetic/manual_review_sample.jsonl")
CONFIG_PATH = Path("data/synthetic/generation_config.json")
PROFILES_PATH = Path("data/processed/standards_profiles_grounded.json")


@pytest.fixture(scope="module")
def dataset_records():
    """Load the generated dataset records."""
    assert DATA_PATH.exists(), f"Synthetic dataset {DATA_PATH} not found. Run generator first."
    records = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


@pytest.fixture(scope="module")
def db_standards_map():
    """Load standards dict from database."""
    session = SessionLocal()
    stds = session.query(Standard).all()
    standards = {
        s.is_number: {
            "title": s.title,
            "sector": s.sector,
            "application": s.application,
            "materials": s.materials or [],
            "technical_parameters": s.technical_parameters or [],
            "year": s.year,
        }
        for s in stds
    }
    session.close()
    return standards


@pytest.fixture(scope="module")
def db_standards_set(db_standards_map):
    """Set of valid IS numbers directly from database."""
    return set(db_standards_map.keys())


# 1. Correct total record count
def test_correct_total_record_count(dataset_records):
    assert len(dataset_records) == 500, f"Expected 500 records, got {len(dataset_records)}"


# 2. Correct difficulty distribution
def test_correct_difficulty_distribution(dataset_records):
    easy = sum(1 for r in dataset_records if r["difficulty"] == "EASY")
    normal = sum(1 for r in dataset_records if r["difficulty"] == "NORMAL")
    hard = sum(1 for r in dataset_records if r["difficulty"] == "HARD")
    near_match = sum(1 for r in dataset_records if r["difficulty"] == "NEAR_MATCH")

    assert easy == 150, f"Expected 150 EASY, got {easy}"
    assert normal == 200, f"Expected 200 NORMAL, got {normal}"
    assert hard == 100, f"Expected 100 HARD, got {hard}"
    assert near_match == 50, f"Expected 50 NEAR_MATCH, got {near_match}"


# 3. Every primary ground-truth standard exists in database
def test_every_primary_ground_truth_exists(dataset_records, db_standards_set):
    for r in dataset_records:
        prim = r.get("ground_truth_primary")
        assert prim and isinstance(prim, list), f"Record {r['id']} missing ground_truth_primary"
        assert len(prim) == 1, f"Record {r['id']} expected 1 primary standard, got {len(prim)}"
        assert prim[0] in db_standards_set, f"Record {r['id']} primary {prim[0]} not in database"


# 4. Every related standard exists in database
def test_every_related_standard_exists(dataset_records, db_standards_set):
    for r in dataset_records:
        related = r.get("ground_truth_related")
        assert isinstance(related, list), f"Record {r['id']} ground_truth_related must be list"
        for rel in related:
            assert rel in db_standards_set, f"Record {r['id']} related {rel} not in database"


# 5. No fabricated IS numbers in ground truth, candidates, or evidence
def test_no_fabricated_is_numbers(dataset_records, db_standards_set):
    for r in dataset_records:
        for p in r["ground_truth_primary"]:
            assert p in db_standards_set
        for rel in r["ground_truth_related"]:
            assert rel in db_standards_set
        for cand in r.get("near_match_candidates", []):
            assert cand in db_standards_set, f"Record {r['id']} near-match candidate {cand} not in DB"
        for ev in r.get("ground_truth_evidence", []):
            if ev.get("field") == "related_standard":
                assert ev["value"] in db_standards_set


# 6. No IS numbers in generated queries (data leakage prevention)
def test_no_is_numbers_in_queries(dataset_records):
    is_pattern = re.compile(r"\bIS\s*\d+", re.IGNORECASE)
    for r in dataset_records:
        match = is_pattern.search(r["query"])
        assert not match, f"Data leakage in {r['id']}: found '{match.group(0)}' in query '{r['query']}'"


# 7. No empty or too short queries
def test_no_empty_or_short_queries(dataset_records):
    for r in dataset_records:
        q = r.get("query", "").strip()
        assert len(q) >= 35, f"Record {r['id']} query too short ({len(q)} chars)"
        assert len(q.split()) >= 6, f"Record {r['id']} query too few words ({len(q.split())} words)"


# 8. No duplicate IDs
def test_no_duplicate_ids(dataset_records):
    ids = [r["id"] for r in dataset_records]
    assert len(ids) == len(set(ids)), "Duplicate record IDs found"
    assert ids[0] == "syn_000001"
    assert ids[-1] == "syn_000500"


# 9. Synthetic flag always true
def test_synthetic_flag_always_true(dataset_records):
    for r in dataset_records:
        assert r.get("synthetic") is True, f"Record {r['id']} synthetic flag is not True"


# 10. QCO status does not contain unsupported legal claims
def test_qco_status_unsupported_claims(dataset_records):
    for r in dataset_records:
        assert r["ground_truth_qco"] == "UNKNOWN", (
            f"Record {r['id']} has invalid QCO status: {r['ground_truth_qco']}"
        )


# 11. Version status set to UNKNOWN
def test_version_status_unknown(dataset_records):
    for r in dataset_records:
        assert r["ground_truth_version"] == "UNKNOWN", (
            f"Record {r['id']} has invalid version status: {r['ground_truth_version']}"
        )


# 12. Deterministic generation with fixed seed
def test_deterministic_generation():
    gen1 = GroundedSyntheticGenerator(seed=42)
    records1, _ = gen1.generate_dataset(total_count=100)

    gen2 = GroundedSyntheticGenerator(seed=42)
    records2, _ = gen2.generate_dataset(total_count=100)

    assert len(records1) == len(records2)
    for r1, r2 in zip(records1, records2):
        assert r1["id"] == r2["id"]
        assert r1["query"] == r2["query"]
        assert r1["ground_truth_primary"] == r2["ground_truth_primary"]
        assert r1["difficulty"] == r2["difficulty"]


# 13. Phase 2.1: Provenance coverage 100%
def test_provenance_coverage_100_percent(dataset_records):
    for r in dataset_records:
        evidence = r.get("ground_truth_evidence")
        assert evidence and isinstance(evidence, list), f"Record {r['id']} missing ground_truth_evidence"
        assert len(evidence) >= 2, f"Record {r['id']} has fewer than 2 provenance items"
        fields = {ev["field"] for ev in evidence}
        assert "product" in fields, f"Record {r['id']} evidence missing 'product'"
        assert "sector" in fields, f"Record {r['id']} evidence missing 'sector'"
        for ev in evidence:
            assert ev["source"].startswith("seed."), f"Record {r['id']} invalid source: {ev['source']}"
            assert ev["value"], f"Record {r['id']} empty value for evidence field {ev['field']}"


# 14. Phase 2.1: No unsupported technical parameters
def test_no_unsupported_technical_parameters(dataset_records, db_standards_map):
    for r in dataset_records:
        src = db_standards_map[r["source_seed_standard"]]
        src_params = src.get("technical_parameters") or []
        rec_params = r.get("parameters") or {}
        if not src_params:
            assert rec_params == {}, (
                f"Record {r['id']} has unsupported parameters {rec_params} for {r['source_seed_standard']}"
            )


# 15. Phase 2.1: No unsupported materials
def test_no_unsupported_materials(dataset_records, db_standards_map):
    for r in dataset_records:
        src = db_standards_map[r["source_seed_standard"]]
        src_mats = set(src.get("materials") or [])
        rec_mats = set(r.get("materials") or [])
        assert rec_mats.issubset(src_mats), (
            f"Record {r['id']} has unsupported materials: {rec_mats - src_mats}"
        )


# 16. Phase 2.1: No unsupported numeric values in query
def test_no_unsupported_numeric_values(dataset_records, db_standards_map):
    for r in dataset_records:
        src = db_standards_map[r["source_seed_standard"]]
        raw_params = src.get("technical_parameters") or []
        p_text = json.dumps(raw_params) if isinstance(raw_params, (dict, list)) else str(raw_params)
        allowed_text = f"{src['title']} {p_text} {src.get('year') or ''}"
        allowed_nums = extract_numbers_from_text(allowed_text)
        query_nums = extract_numbers_from_text(r["query"])
        unsupported = query_nums - allowed_nums
        assert not unsupported, (
            f"Record {r['id']} ({r['source_seed_standard']}) has unsupported numbers {unsupported} in query: '{r['query']}'"
        )


# 17. Phase 2.1: Ground truth primary MUST NOT appear inside near_match_candidates
def test_near_match_no_ground_truth_overlap(dataset_records):
    near_matches = [r for r in dataset_records if r["difficulty"] == "NEAR_MATCH"]
    assert len(near_matches) == 50
    for r in near_matches:
        primary = r["ground_truth_primary"][0]
        cands = r.get("near_match_candidates", [])
        assert primary not in cands, (
            f"Record {r['id']} ground_truth_primary {primary} found inside near_match_candidates {cands}"
        )


# 18. Phase 2.1: Every near-match candidate exists in seed standards and differs from ground truth
def test_near_match_candidates_valid_and_distinct(dataset_records, db_standards_set):
    near_matches = [r for r in dataset_records if r["difficulty"] == "NEAR_MATCH"]
    for r in near_matches:
        primary = r["ground_truth_primary"][0]
        cands = r.get("near_match_candidates", [])
        assert len(cands) >= 2, f"Record {r['id']} has fewer than 2 candidates: {cands}"
        for c in cands:
            assert c in db_standards_set, f"Record {r['id']} candidate {c} not in seed standards"
            assert c != primary, f"Record {r['id']} candidate {c} is identical to primary standard"


# 19. Phase 2.1: Candidate signals and similarity basis populated
def test_candidate_signals_and_basis_populated(dataset_records):
    near_matches = [r for r in dataset_records if r["difficulty"] == "NEAR_MATCH"]
    valid_signals = {
        "sector_overlap",
        "title_similarity",
        "application_overlap",
        "material_overlap",
        "parameter_overlap",
    }
    for r in near_matches:
        cands = r.get("near_match_candidates", [])
        signals = r.get("candidate_signals", {})
        basis = r.get("candidate_similarity_basis", [])

        assert signals and isinstance(signals, dict), f"Record {r['id']} missing candidate_signals"
        assert basis and isinstance(basis, list), f"Record {r['id']} missing candidate_similarity_basis"

        for c in cands:
            assert c in signals, f"Candidate {c} missing signals in record {r['id']}"
            cand_sig_list = signals[c]
            assert len(cand_sig_list) >= 1, f"Candidate {c} has empty signal list in {r['id']}"
            for sig in cand_sig_list:
                assert sig in valid_signals, f"Invalid signal {sig} in record {r['id']}"


# 20. Phase 2.1: Product / Sector consistency (sector_original, sector_normalized, IS 4151)
def test_product_sector_consistency(dataset_records, db_standards_map):
    for r in dataset_records:
        src = db_standards_map[r["source_seed_standard"]]
        assert r["sector_original"] == src["sector"], (
            f"Record {r['id']} sector_original '{r['sector_original']}' != seed '{src['sector']}'"
        )
        assert "sector_normalized" in r, f"Record {r['id']} missing sector_normalized"
        assert r["sector_normalized"], f"Record {r['id']} empty sector_normalized"

        # IS 4151:2015 helmet check
        if r["source_seed_standard"] == "IS 4151:2015":
            assert r["sector_normalized"] == "PPE"
            lower_q = r["query"].lower()
            assert "footwear" not in lower_q, f"IS 4151 query mentions footwear: '{r['query']}'"
            assert "shoe" not in lower_q, f"IS 4151 query mentions shoe: '{r['query']}'"
            assert "boot" not in lower_q, f"IS 4151 query mentions boot: '{r['query']}'"


# 21. Phase 2.1: Procurement fluff ratio in HARD records between 15% and 30%
def test_procurement_fluff_ratio(dataset_records):
    hard_records = [r for r in dataset_records if r["difficulty"] == "HARD"]
    assert len(hard_records) == 100
    ratios = []
    for r in hard_records:
        words = r["query"].split()
        prefix = " ".join(words[:4])
        ratio = len(prefix) / len(r["query"])
        ratios.append(ratio)
        assert ratio < 0.40, f"Record {r['id']} has excessive fluff ratio {ratio:.2f}: '{r['query']}'"

    avg_fluff = sum(ratios) / len(ratios)
    assert 0.15 <= avg_fluff <= 0.30, f"Average fluff ratio {avg_fluff:.3f} outside [0.15, 0.30]"


# 22. Manual review sample distribution and fields
def test_manual_review_sample_distribution():
    assert SAMPLE_PATH.exists()
    sample_records = []
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                sample_records.append(json.loads(line))

    assert len(sample_records) == 50, f"Expected 50 manual review records, got {len(sample_records)}"
    easy = sum(1 for r in sample_records if r["difficulty"] == "EASY")
    normal = sum(1 for r in sample_records if r["difficulty"] == "NORMAL")
    hard = sum(1 for r in sample_records if r["difficulty"] == "HARD")
    near = sum(1 for r in sample_records if r["difficulty"] == "NEAR_MATCH")

    assert easy == 15, f"Expected 15 EASY sample, got {easy}"
    assert normal == 15, f"Expected 15 NORMAL sample, got {normal}"
    assert hard == 10, f"Expected 10 HARD sample, got {hard}"
    assert near == 10, f"Expected 10 NEAR_MATCH sample, got {near}"

    # Verify required sample fields
    for s in sample_records:
        assert "ground_truth_evidence" in s
        assert "ground_truth_primary" in s
        assert "difficulty" in s
        assert "generation_method" in s
        if s["difficulty"] == "NEAR_MATCH":
            assert "near_match_candidates" in s
            assert len(s["near_match_candidates"]) >= 2


# 23. Validation report metrics and quality targets
def test_validation_report_metrics():
    assert REPORT_PATH.exists()
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        rep = json.load(f)

    assert rep["total_records"] == 500
    assert rep["easy_count"] == 150
    assert rep["normal_count"] == 200
    assert rep["hard_count"] == 100
    assert rep["near_match_count"] == 50
    assert rep["unique_source_standards"] == 91
    assert rep["duplicate_count"] == 0
    assert rep["invalid_ground_truth_count"] == 0
    assert rep["unknown_standard_references"] == 0
    assert rep["average_query_length"] > 100

    # Phase 2.1 Quality Targets
    assert rep["unsupported_fact_count"] == 0, f"Unsupported facts: {rep['unsupported_fact_count']}"
    assert rep["unsupported_fact_rate"] == 0.0
    assert rep["sector_product_mismatch_count"] == 0
    assert rep["near_match_ground_truth_overlap_count"] == 0
    assert rep["near_match_invalid_candidate_count"] == 0
    assert rep["provenance_coverage"] == "100.0%"
    assert 0.15 <= rep["procurement_fluff_ratio"] <= 0.30


# 24. All 91 seed standards represented in dataset
def test_all_91_seed_standards_represented(dataset_records, db_standards_set):
    used_standards = {r["source_seed_standard"] for r in dataset_records}
    assert used_standards == db_standards_set, (
        f"Missing standards: {db_standards_set - used_standards}"
    )


# 25. No duplicate queries across all 500 records
def test_no_duplicate_queries(dataset_records):
    normalized_queries = [" ".join(r["query"].lower().split()) for r in dataset_records]
    assert len(normalized_queries) == len(set(normalized_queries)), "Found duplicate queries"
