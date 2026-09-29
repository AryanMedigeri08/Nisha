"""
scripts/ingest_seed.py
=====================

Reads PS26108_Seed_Dataset_v1.xlsx, validates, normalizes, and loads data
into the SQLite (Phase 1) / PostgreSQL (Phase 6+) database.

This script is **repeatable**: running it again will drop and recreate
all rows from the seed dataset. Non-seed data (user queries, etc.) is
not affected.

Usage:
    python -m scripts.ingest_seed          # from project root
    python scripts/ingest_seed.py          # also works
"""
from __future__ import annotations

import ast
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import openpyxl

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.app.core.config import SEED_DATASET_PATH, PROCESSED_DIR
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.models import Standard, Reference, QCO, QCOStandardLink


# ===================================================================
# Helpers
# ===================================================================

def normalize_is_number(raw: str) -> str:
    """
    Create a canonical form for IS number matching.

    'IS 1489 (Part 1)' → 'IS1489PART1'
    'IS 302 : Part 2 : Sec 80 (2017)' → 'IS302PART2SEC80'

    The year is stripped from the normalized form (kept separately).
    """
    s = raw.upper().strip()
    # Remove known year patterns: ":2019", "(2019)", etc.
    s = re.sub(r'[:\s]*\(?(\d{4})\)?$', '', s)
    # Remove colons, parentheses, hyphens, extra spaces
    s = re.sub(r'[:()\-/]', ' ', s)
    s = re.sub(r'\s+', '', s)
    return s


def extract_year_from_is(is_number: str) -> int | None:
    """
    Extract the trailing year from an IS number string.
    'IS 374:2019' → 2019
    'IS 302 : Part 1 (2024)' → 2024
    'IS 269' → None
    """
    m = re.search(r'[:\s(]+(\d{4})\)?$', is_number.strip())
    if m:
        year = int(m.group(1))
        if 1900 <= year <= 2100:
            return year
    return None


def safe_parse_json_list(val: str | list | None) -> list:
    """Parse stringified Python list, e.g. "['pvc']" → ['pvc']."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    val = str(val).strip()
    if val in ("", "[]", "None"):
        return []
    try:
        result = ast.literal_eval(val)
        if isinstance(result, list):
            return result
        return [str(result)]
    except Exception:
        return [val]


def safe_date(val) -> date | None:
    """Coerce various date representations to a date object."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        return datetime.strptime(str(val).strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def read_sheet(wb: openpyxl.Workbook, name: str) -> list[dict]:
    """Read a worksheet into a list of dicts keyed by header row."""
    if name not in wb.sheetnames:
        return []
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    headers = [str(h).strip() if h is not None else f"__col_{i}"
               for i, h in enumerate(rows[0])]
    result = []
    for row in rows[1:]:
        d = {}
        for i, h in enumerate(headers):
            d[h] = row[i] if i < len(row) else None
        result.append(d)
    return result


# ===================================================================
# Ingestion functions
# ===================================================================

def ingest_standards(session, rows: list[dict], warnings: list[str]) -> dict:
    """Ingest standards_seed rows."""
    stats = {
        "total": len(rows),
        "loaded": 0,
        "duplicates": 0,
        "missing_is_number": 0,
        "missing_title": 0,
        "missing_source_url": 0,
        "year_parse_issues": 0,
    }
    seen_ids: set[str] = set()

    for row in rows:
        sid = str(row.get("standard_id", "")).strip()
        is_num = str(row.get("is_number", "")).strip()
        title = str(row.get("title", "")).strip()

        # Validate required fields
        if not is_num or is_num == "None":
            stats["missing_is_number"] += 1
            warnings.append(f"Row with standard_id={sid}: missing is_number")
            continue
        if not title or title == "None":
            stats["missing_title"] += 1
            warnings.append(f"Row with standard_id={sid}: missing title")
            continue

        # Duplicate check
        if sid in seen_ids:
            stats["duplicates"] += 1
            warnings.append(f"Duplicate standard_id={sid}")
            continue
        seen_ids.add(sid)

        # Source URL
        source_url = str(row.get("source_url", "")).strip()
        if not source_url or source_url == "None":
            stats["missing_source_url"] += 1
            warnings.append(f"standard_id={sid}: missing source_url")

        # Year
        year_raw = row.get("year_in_is_number")
        year_extracted = extract_year_from_is(is_num)
        year = None
        if year_raw is not None:
            try:
                yr = int(year_raw)
                if 1900 <= yr <= 2100:
                    year = yr
                else:
                    stats["year_parse_issues"] += 1
                    warnings.append(
                        f"standard_id={sid}: year_in_is_number={year_raw} "
                        f"looks like an IS number, not a year"
                    )
            except (ValueError, TypeError):
                stats["year_parse_issues"] += 1
                warnings.append(f"standard_id={sid}: unparseable year={year_raw}")
        if year is None and year_extracted is not None:
            year = year_extracted

        std = Standard(
            standard_id=sid,
            is_number=is_num,
            is_number_normalized=normalize_is_number(is_num),
            title=title,
            sector=str(row.get("sector", "")).strip() or None,
            status=str(row.get("status", "unknown")).strip(),
            scheme=str(row.get("scheme", "")).strip() or None,
            qco_or_regulatory_order=str(row.get("qco_or_regulatory_order", "")).strip() or None,
            certification_status=str(row.get("certification_status", "")).strip() or None,
            year=year,
            source_url=source_url if source_url and source_url != "None" else None,
            source_type=str(row.get("source_type", "")).strip() or None,
            source_as_of=safe_date(row.get("source_as_of")),
            application=str(row.get("application", "")).strip() or None,
            materials=safe_parse_json_list(row.get("materials")),
            product_aliases=safe_parse_json_list(row.get("product_aliases")),
            technical_parameters=safe_parse_json_list(row.get("technical_parameters")),
            facet_source=str(row.get("facet_source", "")).strip() or None,
        )
        session.add(std)
        stats["loaded"] += 1

    session.flush()
    return stats


def ingest_references(session, rows: list[dict], warnings: list[str]) -> dict:
    """
    Ingest reference_seed rows.

    References link standards by IS number strings. We resolve them to
    Standard.id via is_number lookup. If a target standard doesn't exist
    in our seed, we still store the edge but with target_standard_id = NULL
    and log a warning.
    """
    stats = {"total": len(rows), "loaded": 0, "unresolved_source": 0, "unresolved_target": 0}

    # Build IS number → Standard.id lookup
    all_standards = session.query(Standard).all()
    # Use both raw and normalized forms
    is_map: dict[str, int] = {}
    for s in all_standards:
        is_map[s.is_number.strip()] = s.id
        is_map[s.is_number_normalized] = s.id

    for row in rows:
        src_is = str(row.get("source_standard", "")).strip()
        tgt_is = str(row.get("target_standard", "")).strip()
        ref_type = str(row.get("reference_type", "")).strip()

        src_id = is_map.get(src_is) or is_map.get(normalize_is_number(src_is))
        tgt_id = is_map.get(tgt_is) or is_map.get(normalize_is_number(tgt_is))

        if src_id is None:
            stats["unresolved_source"] += 1
            warnings.append(f"Reference source '{src_is}' not found in standards")
            continue
        if tgt_id is None:
            stats["unresolved_target"] += 1
            warnings.append(f"Reference target '{tgt_is}' not found in standards")
            continue

        ref = Reference(
            source_standard_id=src_id,
            target_standard_id=tgt_id,
            reference_type=ref_type,
            evidence_source=str(row.get("evidence_source", "")).strip() or None,
            source_url=str(row.get("source_url", "")).strip() or None,
            confidence="candidate",
        )
        session.add(ref)
        stats["loaded"] += 1

    session.flush()
    return stats


def ingest_qco(session, rows: list[dict], standards_rows: list[dict],
               warnings: list[str]) -> dict:
    """
    Ingest qco_seed rows and create QCOStandardLink entries by matching
    the qco_or_regulatory_order field in standards_seed to qco order_name.
    """
    stats = {"total": len(rows), "loaded": 0, "links_created": 0}

    for row in rows:
        qco_id_str = str(row.get("qco_id", "")).strip()
        order_name = str(row.get("order_name", "")).strip()

        qco = QCO(
            qco_id=qco_id_str,
            order_name=order_name,
            status=str(row.get("status", "needs_current_order_resolution")).strip(),
            effective_date=safe_date(row.get("effective_date")),
            notifying_authority=str(row.get("notifying_authority", "")).strip() or None,
            source_url=str(row.get("source_url", "")).strip() or None,
            source_type=str(row.get("source_type", "")).strip() or None,
            as_of_date=safe_date(row.get("source_as_of")),
            note=str(row.get("note", "")).strip() or None,
            linked_seed_standards_count=(
                int(row["linked_seed_standards_count"])
                if row.get("linked_seed_standards_count") else None
            ),
        )
        session.add(qco)
        session.flush()  # Get qco.id

        # Link standards whose qco_or_regulatory_order matches this order
        linked_standards = (
            session.query(Standard)
            .filter(Standard.qco_or_regulatory_order == order_name)
            .all()
        )
        for std in linked_standards:
            link = QCOStandardLink(qco_id=qco.id, standard_id=std.id)
            session.add(link)
            stats["links_created"] += 1

        stats["loaded"] += 1

    session.flush()
    return stats


# ===================================================================
# Main
# ===================================================================

def main():
    print(f"[ingest_seed] Reading {SEED_DATASET_PATH} ...")

    if not SEED_DATASET_PATH.exists():
        print(f"ERROR: Seed file not found: {SEED_DATASET_PATH}")
        sys.exit(1)

    wb = openpyxl.load_workbook(str(SEED_DATASET_PATH), data_only=True)
    print(f"[ingest_seed] Sheets found: {wb.sheetnames}")

    standards_rows = read_sheet(wb, "standards_seed")
    reference_rows = read_sheet(wb, "reference_seed")
    qco_rows = read_sheet(wb, "qco_seed")
    wb.close()

    print(f"[ingest_seed] standards_seed: {len(standards_rows)} rows")
    print(f"[ingest_seed] reference_seed: {len(reference_rows)} rows")
    print(f"[ingest_seed] qco_seed:       {len(qco_rows)} rows")

    # Create/reset tables
    print("[ingest_seed] Creating database tables ...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    warnings: list[str] = []
    session = SessionLocal()

    try:
        # 1. Standards
        print("[ingest_seed] Ingesting standards ...")
        std_stats = ingest_standards(session, standards_rows, warnings)

        # 2. References
        print("[ingest_seed] Ingesting references ...")
        ref_stats = ingest_references(session, reference_rows, warnings)

        # 3. QCO
        print("[ingest_seed] Ingesting QCO orders ...")
        qco_stats = ingest_qco(session, qco_rows, standards_rows, warnings)

        session.commit()
        print("[ingest_seed] Commit successful.")

    except Exception as e:
        session.rollback()
        print(f"[ingest_seed] ERROR during ingestion: {e}")
        raise
    finally:
        session.close()

    # -------------------------------------------------------------------
    # Validation report
    # -------------------------------------------------------------------
    report = {
        "seed_file": str(SEED_DATASET_PATH),
        "ingestion_timestamp": datetime.utcnow().isoformat(),
        "standards": std_stats,
        "references": ref_stats,
        "qco": qco_stats,
        "total_warnings": len(warnings),
        "warnings": warnings,
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROCESSED_DIR / "seed_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"  SEED INGESTION REPORT")
    print(f"{'=' * 60}")
    print(f"  Standards loaded:    {std_stats['loaded']} / {std_stats['total']}")
    print(f"  Duplicates:          {std_stats['duplicates']}")
    print(f"  Missing IS numbers:  {std_stats['missing_is_number']}")
    print(f"  Missing titles:      {std_stats['missing_title']}")
    print(f"  Missing source URLs: {std_stats['missing_source_url']}")
    print(f"  Year parse issues:   {std_stats['year_parse_issues']}")
    print(f"  Reference edges:     {ref_stats['loaded']} / {ref_stats['total']}")
    print(f"  Unresolved sources:  {ref_stats['unresolved_source']}")
    print(f"  Unresolved targets:  {ref_stats['unresolved_target']}")
    print(f"  QCO orders loaded:   {qco_stats['loaded']} / {qco_stats['total']}")
    print(f"  QCO->Standard links: {qco_stats['links_created']}")
    print(f"  Total warnings:      {len(warnings)}")
    print(f"{'=' * 60}")
    print(f"  Full report: {report_path}")
    print(f"{'=' * 60}")

    if warnings:
        print(f"\n  First 10 warnings:")
        for w in warnings[:10]:
            print(f"    [!] {w}")
        if len(warnings) > 10:
            print(f"    ... and {len(warnings) - 10} more (see report)")


if __name__ == "__main__":
    main()
