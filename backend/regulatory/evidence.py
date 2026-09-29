"""
backend/regulatory/evidence.py
==============================

Evidence models and verification statuses for regulatory and knowledge graph claims.
Ensures that every version, QCO association, or relationship has clear provenance.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VerificationStatus(str, Enum):
    """Status of factual verification for a regulatory claim or edge."""
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    INCOMPLETE = "INCOMPLETE"
    CONFLICTING = "CONFLICTING"


class SourceType(str, Enum):
    """Authoritative source category."""
    BIS = "BIS"
    DPIIT = "DPIIT"
    MINISTRY = "MINISTRY"
    SEED_DATASET = "SEED_DATASET"
    LIMS = "LIMS"
    UNKNOWN = "UNKNOWN"


class EvidenceItem(BaseModel):
    """Verifiable evidence item supporting a regulatory association or standard fact."""
    model_config = ConfigDict(extra="ignore")

    source_type: str = SourceType.SEED_DATASET.value
    source_id: str
    source_url: Optional[str] = None
    claim: str
    evidence_text: str
    verification_status: VerificationStatus = VerificationStatus.INCOMPLETE
