"""
backend/graph/graph_schema.py
=============================

Pydantic schemas and enums defining the knowledge graph schema for Indian Standards,
regulatory Quality Control Orders (QCOs), and normative references.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RelationshipType(str, Enum):
    """Standard relationship taxonomy as required by PS26108 Phase 5."""
    NORMATIVE_REFERENCE = "NORMATIVE_REFERENCE"
    RELATED_STANDARD = "RELATED_STANDARD"
    STANDARD_PART = "STANDARD_PART"
    SUPERSEDES = "SUPERSEDES"
    AMENDS = "AMENDS"
    ASSOCIATED_QCO = "ASSOCIATED_QCO"


class ReferenceResolutionStatus(str, Enum):
    """Status of reference resolution in the knowledge graph."""
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID_SOURCE = "INVALID_SOURCE"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class StandardNode(BaseModel):
    """Standard node representation in the knowledge graph."""
    model_config = ConfigDict(extra="ignore")

    standard_id: str
    is_number: str
    is_number_canonical: str
    title: str
    sector: Optional[str] = None
    year: Optional[int] = None
    status: str = "UNKNOWN"
    source: str = "PS26108_Seed_Dataset_v1.xlsx"
    source_url: Optional[str] = None
    node_type: str = "STANDARD"


class QCONode(BaseModel):
    """Quality Control Order (QCO) node in the knowledge graph."""
    model_config = ConfigDict(extra="ignore")

    qco_id: str
    order_identifier: str
    title: str
    authority: Optional[str] = None
    effective_date: Optional[str] = None
    source: str = "PS26108_Seed_Dataset_v1.xlsx"
    status: str = "needs_current_order_resolution"
    node_type: str = "QCO_ORDER"


class ReferenceNode(BaseModel):
    """Representation of a normative reference (resolved or unresolved)."""
    model_config = ConfigDict(extra="ignore")

    reference_id: str
    source_standard_id: str
    source_is_number: str
    raw_reference: str
    target_standard_id: Optional[str] = None
    target_is_number: Optional[str] = None
    reference_type: str = "normative_reference"
    resolution_status: ReferenceResolutionStatus = ReferenceResolutionStatus.UNRESOLVED
    evidence_source: Optional[str] = None
    source_url: Optional[str] = None
    node_type: str = "REFERENCE"


class GraphEdge(BaseModel):
    """Directed edge in the knowledge graph connecting standards and regulatory orders."""
    model_config = ConfigDict(extra="ignore")

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    evidence_source: Optional[str] = None
    source_url: Optional[str] = None
    confidence: str = "candidate"


class GraphMetadata(BaseModel):
    """Metadata describing the knowledge graph construction and completeness."""
    model_config = ConfigDict(extra="ignore")

    graph_version: str = "v1.0.0"
    created_at: str
    standard_nodes: int
    qco_nodes: int
    reference_edges: int
    qco_edges: int
    resolved_references: int
    unresolved_references: int
    status: str = "sparse_bootstrap_graph"
