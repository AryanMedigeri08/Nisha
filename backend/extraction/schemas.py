"""
backend/extraction/schemas.py

Pydantic schemas for the Phase 3 Requirement Extraction Engine.
Defines the output structure for converting raw procurement query texts
into structured procurement requirements with provenance and confidence scores.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ExtractedField(BaseModel):
    """Generic extracted field containing extracted value, extraction confidence, and textual evidence."""
    model_config = ConfigDict(extra="ignore")

    value: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: Optional[str] = None
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None


class ExtractedParameter(BaseModel):
    """Structured technical parameter with parameter name, numerical/categorical value, unit, and evidence."""
    model_config = ConfigDict(extra="ignore")

    name: str
    value: str
    unit: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: str
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None


class ExtractedCitedStandard(BaseModel):
    """Explicitly mentioned standard number in the procurement text."""
    model_config = ConfigDict(extra="ignore")

    standard_number: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: str
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None


class ProcurementRequirements(BaseModel):
    """Complete structured procurement requirement extraction output."""
    model_config = ConfigDict(extra="ignore")

    query_id: str
    product: Optional[ExtractedField] = None
    sector: Optional[ExtractedField] = None
    application: List[ExtractedField] = Field(default_factory=list)
    materials: List[ExtractedField] = Field(default_factory=list)
    parameters: List[ExtractedParameter] = Field(default_factory=list)
    safety_requirements: List[ExtractedField] = Field(default_factory=list)
    electrical_requirements: List[ExtractedField] = Field(default_factory=list)
    mechanical_requirements: List[ExtractedField] = Field(default_factory=list)
    cited_standards: List[ExtractedCitedStandard] = Field(default_factory=list)
    language: str = "en"
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
