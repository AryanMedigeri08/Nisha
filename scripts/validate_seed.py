"""
scripts/validate_seed.py
========================

Post-ingestion validation: queries the database and produces a
comprehensive quality report.

Usage:
    python scripts/validate_seed.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.app.core.config import PROCESSED_DIR
from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, Reference, QCO, QCOStandardLink


def validate():
    session = SessionLocal()

    # -------------------------------------------------------------------
    # Standards
    # -------------------------------------------------------------------
    standards = session.query(Standard).all()
    total_standards = len(standards)

    # Duplicate normalized IS numbers
    norm_counts = Counter(s.is_number_normalized for s in standards)
    duplicate_normals = {k: v for k, v in norm_counts.items() if v > 1}

    # Sector distribution
    sector_dist = Counter(s.sector for s in standards)

    # Year coverage
    with_year = sum(1 for s in standards if s.year is not None)
    without_year = total_standards - with_year

    # Year range check (potential non-year values)
    suspicious_years = [
        {"standard_id": s.standard_id, "is_number": s.is_number, "year": s.year}
        for s in standards
        if s.year is not None and (s.year < 1950 or s.year > 2030)
    ]

    # Materials coverage
    with_materials = sum(1 for s in standards if s.materials and len(s.materials) > 0)

    # Technical parameters coverage
    with_params = sum(1 for s in standards
                      if s.technical_parameters and len(s.technical_parameters) > 0)

    # Source URL check
    without_source_url = sum(1 for s in standards if not s.source_url)

    # Facet source check
    facet_sources = Counter(s.facet_source for s in standards)

    # -------------------------------------------------------------------
    # References
    # -------------------------------------------------------------------
    references = session.query(Reference).all()
    total_references = len(references)
    ref_type_dist = Counter(r.reference_type for r in references)

    # -------------------------------------------------------------------
    # QCO
    # -------------------------------------------------------------------
    qco_orders = session.query(QCO).all()
    total_qco = len(qco_orders)
    qco_links = session.query(QCOStandardLink).all()
    total_qco_links = len(qco_links)

    # QCO status distribution
    qco_status_dist = Counter(q.status for q in qco_orders)

    # QCO with missing effective_date
    qco_missing_date = sum(1 for q in qco_orders if q.effective_date is None)

    # QCO with missing notifying_authority
    qco_missing_authority = sum(1 for q in qco_orders if not q.notifying_authority)

    # Expected vs actual link counts
    qco_link_mismatches = []
    for q in qco_orders:
        expected = q.linked_seed_standards_count or 0
        actual = sum(1 for lk in qco_links if lk.qco_id == q.id)
        if expected != actual:
            qco_link_mismatches.append({
                "qco_id": q.qco_id,
                "order_name": q.order_name[:60],
                "expected_links": expected,
                "actual_links": actual,
            })

    session.close()

    # -------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------
    report = {
        "database_validation_timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "standards": {
            "total": total_standards,
            "with_year": with_year,
            "without_year": without_year,
            "suspicious_years": suspicious_years,
            "with_materials": with_materials,
            "with_technical_parameters": with_params,
            "without_source_url": without_source_url,
            "duplicate_normalized_is_numbers": duplicate_normals,
            "sector_distribution": dict(sector_dist.most_common()),
            "facet_sources": dict(facet_sources),
        },
        "references": {
            "total": total_references,
            "type_distribution": dict(ref_type_dist),
        },
        "qco": {
            "total_orders": total_qco,
            "total_standard_links": total_qco_links,
            "status_distribution": dict(qco_status_dist),
            "missing_effective_date": qco_missing_date,
            "missing_notifying_authority": qco_missing_authority,
            "link_count_mismatches": qco_link_mismatches,
        },
        "data_quality_flags": [],
    }

    # Flag potential issues
    flags = report["data_quality_flags"]
    if duplicate_normals:
        flags.append(f"[!] {len(duplicate_normals)} duplicate normalized IS numbers detected")
    if suspicious_years:
        flags.append(f"[!] {len(suspicious_years)} standards with suspicious year values")
    if without_source_url > 0:
        flags.append(f"[!] {without_source_url} standards without source_url")
    if qco_missing_date == total_qco and total_qco > 0:
        flags.append("[!] ALL QCO orders have missing effective_date - needs resolution")
    if qco_missing_authority == total_qco and total_qco > 0:
        flags.append("[!] ALL QCO orders have missing notifying_authority - needs resolution")
    if qco_link_mismatches:
        flags.append(f"[!] {len(qco_link_mismatches)} QCO orders have link-count mismatches")
    if total_references < 5:
        flags.append(f"[!] Only {total_references} reference edges - knowledge graph will be sparse")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROCESSED_DIR / "seed_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  DATABASE VALIDATION REPORT")
    print(f"{'=' * 60}")
    print(f"  Standards:              {total_standards}")
    print(f"    with year:            {with_year}")
    print(f"    without year:         {without_year}")
    print(f"    suspicious years:     {len(suspicious_years)}")
    print(f"    with materials:       {with_materials}")
    print(f"    with tech params:     {with_params}")
    print(f"    without source_url:   {without_source_url}")
    print(f"    duplicate norm IS#:   {len(duplicate_normals)}")
    print(f"  Sectors:                {len(sector_dist)}")
    print(f"  References:             {total_references}")
    print(f"  QCO orders:             {total_qco}")
    print(f"    QCO->Standard links:  {total_qco_links}")
    print(f"    link mismatches:      {len(qco_link_mismatches)}")
    print(f"{'=' * 60}")

    if flags:
        print(f"\n  DATA QUALITY FLAGS:")
        for flag in flags:
            print(f"    {flag}")
    else:
        print("\n  [OK] No data quality flags.")

    print(f"\n  Report saved: {report_path}")
    print(f"{'=' * 60}")

    # Sector breakdown
    print(f"\n  SECTOR DISTRIBUTION:")
    for sector, count in sector_dist.most_common():
        print(f"    {sector:35s} {count:3d}")

    return report


if __name__ == "__main__":
    validate()
