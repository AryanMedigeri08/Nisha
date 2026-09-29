"""
tests/unit/test_ingest_seed.py
==============================

Unit tests for the seed ingestion pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, Reference, QCO, QCOStandardLink
from scripts.ingest_seed import normalize_is_number, extract_year_from_is, safe_parse_json_list


# ====================================================================
# normalize_is_number
# ====================================================================

def test_normalize_simple():
    assert normalize_is_number("IS 269") == "IS269"

def test_normalize_with_year():
    assert normalize_is_number("IS 374:2019") == "IS374"

def test_normalize_part():
    assert normalize_is_number("IS 1489 (Part 1)") == "IS1489PART1"

def test_normalize_complex():
    assert normalize_is_number("IS 302 : Part 2 : Sec 80 (2017)") == "IS302PART2SEC80"

def test_normalize_part1_2024():
    assert normalize_is_number("IS 302 : Part 1 (2024)") == "IS302PART1"


# ====================================================================
# extract_year_from_is
# ====================================================================

def test_year_colon():
    assert extract_year_from_is("IS 374:2019") == 2019

def test_year_parentheses():
    assert extract_year_from_is("IS 302 : Part 1 (2024)") == 2024

def test_year_none():
    assert extract_year_from_is("IS 269") is None

def test_year_is_number_not_year():
    # "IS 8041" -- 8041 is not a year
    assert extract_year_from_is("IS 8041") is None


# ====================================================================
# safe_parse_json_list
# ====================================================================

def test_parse_empty():
    assert safe_parse_json_list("[]") == []

def test_parse_list():
    assert safe_parse_json_list("['pvc']") == ['pvc']

def test_parse_multiple():
    assert safe_parse_json_list("['steel', 'aluminium']") == ['steel', 'aluminium']

def test_parse_none():
    assert safe_parse_json_list(None) == []


# ====================================================================
# Database integrity after ingestion
# ====================================================================

def test_standards_loaded():
    """After ingestion, we should have 91 standards."""
    session = SessionLocal()
    count = session.query(Standard).count()
    session.close()
    assert count == 91, f"Expected 91 standards, got {count}"

def test_no_null_is_numbers():
    """All standards must have non-null is_number."""
    session = SessionLocal()
    nulls = session.query(Standard).filter(Standard.is_number == None).count()
    session.close()
    assert nulls == 0

def test_no_null_titles():
    """All standards must have non-null titles."""
    session = SessionLocal()
    nulls = session.query(Standard).filter(Standard.title == None).count()
    session.close()
    assert nulls == 0

def test_qco_orders_loaded():
    """After ingestion, we should have 35 QCO orders."""
    session = SessionLocal()
    count = session.query(QCO).count()
    session.close()
    assert count == 35, f"Expected 35 QCO orders, got {count}"

def test_qco_links_count():
    """All 91 standards should be linked to QCO orders."""
    session = SessionLocal()
    count = session.query(QCOStandardLink).count()
    session.close()
    assert count == 91, f"Expected 91 QCO-standard links, got {count}"

def test_references_loaded():
    """At least 1 reference edge should be loaded."""
    session = SessionLocal()
    count = session.query(Reference).count()
    session.close()
    assert count >= 1, f"Expected >= 1 reference edges, got {count}"

def test_all_standards_have_source_url():
    """All standards should have a source_url."""
    session = SessionLocal()
    missing = session.query(Standard).filter(Standard.source_url == None).count()
    session.close()
    assert missing == 0

def test_sector_coverage():
    """We should have standards across multiple sectors."""
    session = SessionLocal()
    from sqlalchemy import func
    distinct = session.query(func.count(func.distinct(Standard.sector))).scalar()
    session.close()
    assert distinct >= 15, f"Expected >= 15 distinct sectors, got {distinct}"

def test_facet_source_preserved():
    """All standards should have facet_source set (non-authoritative marker)."""
    session = SessionLocal()
    missing = session.query(Standard).filter(Standard.facet_source == None).count()
    session.close()
    assert missing == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
