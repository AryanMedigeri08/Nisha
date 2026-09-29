"""
backend/graph
=============

Knowledge graph and Indian Standard normalization package for PS26108 Phase 5.
Provides standard identifier parsing, NetworkX graph construction,
and bounded relationship traversal.
"""

from backend.graph.graph_schema import (
    StandardNode,
    QCONode,
    ReferenceNode,
    RelationshipType,
    ReferenceResolutionStatus,
    GraphEdge,
    GraphMetadata,
)
from backend.graph.standard_normalizer import (
    ParsedISIdentifier,
    normalize_is_identifier,
    parse_is_identifier,
    is_same_standard,
)
from backend.graph.graph_builder import KnowledgeGraphBuilder
from backend.graph.graph_traversal import GraphTraversalEngine

__all__ = [
    "StandardNode",
    "QCONode",
    "ReferenceNode",
    "RelationshipType",
    "ReferenceResolutionStatus",
    "GraphEdge",
    "GraphMetadata",
    "ParsedISIdentifier",
    "normalize_is_identifier",
    "parse_is_identifier",
    "is_same_standard",
    "KnowledgeGraphBuilder",
    "GraphTraversalEngine",
]
