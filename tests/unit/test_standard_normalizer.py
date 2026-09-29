"""
tests/unit/test_standard_normalizer.py
======================================

Unit tests for Indian Standard identifier normalizer:
- Whitespace variations
- Colon variations
- Year suffix extraction and handling
- Part and section notation
- Multi-part standard separation (preventing false merges)
"""

import pytest
from backend.graph.standard_normalizer import (
    normalize_is_identifier,
    parse_is_identifier,
    is_same_standard,
)


def test_normalize_whitespace_variants():
    """Ensure various whitespace patterns normalize to standard spacing."""
    assert normalize_is_identifier("IS  1180") == "IS 1180"
    assert normalize_is_identifier("IS 1180  ") == "IS 1180"
    assert normalize_is_identifier("IS1180") == "IS 1180"
    assert normalize_is_identifier("  IS   269   ") == "IS 269"


def test_normalize_colon_variants():
    """Colons after IS or between part/section must normalize cleanly."""
    assert normalize_is_identifier("IS:1180") == "IS 1180"
    assert normalize_is_identifier("IS : 1180") == "IS 1180"
    assert normalize_is_identifier("IS 302 : Part 1") == "IS 302 (Part 1)"
    assert normalize_is_identifier("IS:302:Part 1") == "IS 302 (Part 1)"


def test_extract_and_strip_year():
    """Year suffixes must be extracted and stripped when requested."""
    parsed = parse_is_identifier("IS 374:2019")
    assert parsed.year == 2019
    assert parsed.canonical_without_year == "IS 374"
    assert parsed.canonical == "IS 374:2019"

    parsed2 = parse_is_identifier("IS 302 : Part 1 (2024)")
    assert parsed2.year == 2024
    assert parsed2.canonical_without_year == "IS 302 (Part 1)"


def test_part_notation_variants():
    """Handle diverse part notations: Part 1, Part-1, Pt 1, (Part 1)."""
    assert normalize_is_identifier("IS 1489 Part 1") == "IS 1489 (Part 1)"
    assert normalize_is_identifier("IS 1489 Part-1") == "IS 1489 (Part 1)"
    assert normalize_is_identifier("IS 1489 Pt 1") == "IS 1489 (Part 1)"
    assert normalize_is_identifier("IS 1489 (Part 1)") == "IS 1489 (Part 1)"


def test_section_notation_variants():
    """Handle combined Part and Section notations."""
    raw1 = "IS 302 : Part 2 : Sec 80 (2017)"
    raw2 = "IS 302 (Part 2/Sec 80)"
    raw3 = "IS 302 (Part 2/Section 80)"
    assert normalize_is_identifier(raw1) == "IS 302 (Part 2/Sec 80)"
    assert normalize_is_identifier(raw2) == "IS 302 (Part 2/Sec 80)"
    assert normalize_is_identifier(raw3) == "IS 302 (Part 2/Sec 80)"


def test_multi_part_standards_remain_distinct():
    """CRITICAL: IS 1489 Part 1 and Part 2 must NOT be merged."""
    p1 = "IS 1489 (Part 1)"
    p2 = "IS 1489 (Part 2)"
    assert normalize_is_identifier(p1) != normalize_is_identifier(p2)
    assert not is_same_standard(p1, p2)


def test_base_standard_vs_multi_part_distinct():
    """CRITICAL: Base IS 1180 must NOT merge with IS 1180 (Part 1)."""
    base = "IS 1180"
    part = "IS 1180 (Part 1)"
    assert normalize_is_identifier(base) != normalize_is_identifier(part)
    assert not is_same_standard(base, part)


def test_is_same_standard_logic():
    """Test identity equivalence under different year and whitespace settings."""
    assert is_same_standard("IS 269", "IS:269")
    assert is_same_standard("IS 269:2015", "IS 269", strict_year=False)
    assert not is_same_standard("IS 269:2015", "IS 269", strict_year=True)
    assert is_same_standard("IS 302 : Part 1 (2024)", "IS 302 (Part 1)", strict_year=False)
    assert not is_same_standard("IS 302 (Part 2/Sec 3)", "IS 302 (Part 2/Sec 30)")
