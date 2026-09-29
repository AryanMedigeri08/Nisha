"""
backend/graph/standard_normalizer.py
====================================

Robust normalization for Indian Standard identifiers.
Handles variations in whitespace, punctuation, year annotations, and part/section formatting.

CRITICAL RULE:
Multi-part standards (e.g., IS 1489 Part 1 vs Part 2) MUST NOT be merged.
They represent distinct technical standards with different scopes.
"""

from __future__ import annotations

import re
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ParsedISIdentifier(BaseModel):
    """Structured decomposition of an Indian Standard identifier."""
    model_config = ConfigDict(extra="ignore")

    raw: str
    canonical: str
    canonical_without_year: str
    base_number: str
    part: Optional[str] = None
    section: Optional[str] = None
    year: Optional[int] = None
    is_multi_part: bool = False


def extract_year(text: str) -> Optional[int]:
    """Extract a 4-digit publication or revision year from an IS string."""
    m = re.search(r"[:\s(]+(19\d\d|20\d\d)\)?(?:\s*$|\))", text.strip())
    if m:
        val = int(m.group(1))
        if 1900 <= val <= 2100:
            return val
    return None


def parse_is_identifier(raw: str) -> ParsedISIdentifier:
    """
    Parse an Indian Standard identifier string into canonical components.
    
    Examples:
        'IS:1180 Part 1:2014' -> base='1180', part='1', year=2014, canonical='IS 1180 (Part 1):2014'
        'IS 302 : Part 2 : Sec 80 (2017)' -> base='302', part='2', section='80', year=2017
        'IS 269' -> base='269', canonical='IS 269'
    """
    s = raw.strip()
    year = extract_year(s)

    # Clean string by removing the extracted year
    s_clean = s
    if year:
        s_clean = re.sub(rf"[:\s(]+{year}\)?(?:\s*$|\))", "", s_clean).strip()

    # Normalize prefix 'IS'
    s_clean = re.sub(r"^IS[\s:/]*", "", s_clean, flags=re.IGNORECASE).strip()

    # Extract base number (leading digits)
    base_match = re.match(r"^(\d+)", s_clean)
    if not base_match:
        # Fallback if non-standard format
        base_number = re.sub(r"\s+", "", s_clean)
        return ParsedISIdentifier(
            raw=raw,
            canonical=f"IS {base_number}",
            canonical_without_year=f"IS {base_number}",
            base_number=base_number,
            year=year,
            is_multi_part=False,
        )

    base_number = base_match.group(1)
    remainder = s_clean[len(base_number):].strip()

    # Parse Part and Section
    part: Optional[str] = None
    section: Optional[str] = None

    # Matches: Part 2 / Sec 80, Part 2: Sec 80, Part 2/Section 14
    part_sec_match = re.search(
        r"(?:Part|Pt)[\s\-:]*(\d+|[A-Z]+)[\s/:,]+(?:Section|Sec)\b[\s\-:]*(\d+|[A-Z]+)",
        remainder,
        re.IGNORECASE,
    )
    if part_sec_match:
        part = part_sec_match.group(1).upper()
        section = part_sec_match.group(2).upper()
    else:
        # Matches: Part 1, Part-1, (Part 1), Pt 1
        part_match = re.search(r"(?:Part|Pt)[\s\-:]*(\d+|[A-Z]+)", remainder, re.IGNORECASE)
        if part_match:
            part = part_match.group(1).upper()

        # Matches standalone: Sec 80, Section 3
        sec_match = re.search(r"(?:Section|Sec)\b[\s\-:]*(\d+|[A-Z]+)", remainder, re.IGNORECASE)
        if sec_match:
            section = sec_match.group(1).upper()

    # Assemble canonical string
    parts = [f"IS {base_number}"]
    is_multi_part = False

    if part and section:
        parts.append(f"(Part {part}/Sec {section})")
        is_multi_part = True
    elif part:
        parts.append(f"(Part {part})")
        is_multi_part = True
    elif section:
        parts.append(f"(Sec {section})")
        is_multi_part = True

    canonical_no_year = " ".join(parts)
    canonical = f"{canonical_no_year}:{year}" if year else canonical_no_year

    return ParsedISIdentifier(
        raw=raw,
        canonical=canonical,
        canonical_without_year=canonical_no_year,
        base_number=base_number,
        part=part,
        section=section,
        year=year,
        is_multi_part=is_multi_part,
    )


def normalize_is_identifier(raw: str, keep_year: bool = False) -> str:
    """Normalize an IS string to its canonical representation."""
    parsed = parse_is_identifier(raw)
    return parsed.canonical if keep_year else parsed.canonical_without_year


def is_same_standard(id1: str, id2: str, strict_year: bool = False) -> bool:
    """
    Determine if two IS identifiers denote the same technical standard.
    
    Guarantees:
        IS 1489 (Part 1) != IS 1489 (Part 2) -> False
        IS 1180 != IS 1180 (Part 1) -> False
        IS 269:2015 == IS 269 (if strict_year=False) -> True
        IS 302 : Part 1 (2024) == IS 302 (Part 1) -> True
    """
    p1 = parse_is_identifier(id1)
    p2 = parse_is_identifier(id2)

    # Base numbers must match
    if p1.base_number != p2.base_number:
        return False

    # Part numbers must match exactly
    if p1.part != p2.part:
        return False

    # Sections must match exactly
    if p1.section != p2.section:
        return False

    if strict_year:
        return p1.year == p2.year

    return True
