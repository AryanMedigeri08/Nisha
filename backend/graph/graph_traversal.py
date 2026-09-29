"""
backend/graph/graph_traversal.py
================================

Graph traversal engine for expanding candidate standard evidence.
Traverses normative references and QCO associations up to max_depth = 2.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
import networkx as nx

from backend.graph.graph_schema import RelationshipType

logger = logging.getLogger(__name__)

DEFAULT_MAX_DEPTH = 2


class GraphTraversalEngine:
    """Performs controlled BFS traversal from a standard node for evidence expansion."""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def traverse(
        self,
        standard_id: str,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> Dict[str, Any]:
        """
        Traverse outgoing and incoming edges for standard_id up to max_depth.
        Returns structured relationships, associated QCOs, and referenced standards.
        """
        if standard_id not in self.graph:
            return {
                "standard_id": standard_id,
                "found_in_graph": False,
                "references": [],
                "referenced_by": [],
                "associated_qcos": [],
                "unresolved_references": [],
                "traversed_node_count": 0,
            }

        direct_refs: List[Dict[str, Any]] = []
        referenced_by: List[Dict[str, Any]] = []
        associated_qcos: List[Dict[str, Any]] = []
        unresolved_refs: List[Dict[str, Any]] = []

        visited: Set[str] = {standard_id}
        queue = [(standard_id, 0)]

        while queue:
            curr_node, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            # Outgoing edges from curr_node
            for neighbor in self.graph.successors(curr_node):
                edge_data = self.graph.get_edge_data(curr_node, neighbor)
                rel_type = edge_data.get("relationship_type")
                target_attrs = self.graph.nodes[neighbor]
                node_type = target_attrs.get("node_type")

                if node_type == "QCO_ORDER":
                    associated_qcos.append({
                        "qco_id": neighbor,
                        "title": target_attrs.get("title"),
                        "authority": target_attrs.get("authority"),
                        "effective_date": target_attrs.get("effective_date"),
                        "status": target_attrs.get("status"),
                        "depth": depth + 1,
                    })

                elif node_type == "STANDARD":
                    direct_refs.append({
                        "source_id": curr_node,
                        "target_id": neighbor,
                        "target_is_number": target_attrs.get("is_number"),
                        "target_title": target_attrs.get("title"),
                        "relationship_type": rel_type,
                        "reference_type": edge_data.get("reference_type"),
                        "depth": depth + 1,
                    })

                elif node_type == "REFERENCE":
                    unresolved_refs.append({
                        "source_id": curr_node,
                        "reference_id": neighbor,
                        "raw_reference": target_attrs.get("raw_reference"),
                        "reference_type": target_attrs.get("reference_type"),
                        "status": target_attrs.get("resolution_status"),
                        "depth": depth + 1,
                    })

                if neighbor not in visited and depth + 1 < max_depth:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

            # Incoming references (standards that cite curr_node)
            for predecessor in self.graph.predecessors(curr_node):
                edge_data = self.graph.get_edge_data(predecessor, curr_node)
                src_attrs = self.graph.nodes[predecessor]
                if src_attrs.get("node_type") == "STANDARD":
                    referenced_by.append({
                        "source_id": predecessor,
                        "source_is_number": src_attrs.get("is_number"),
                        "source_title": src_attrs.get("title"),
                        "relationship_type": edge_data.get("relationship_type"),
                        "reference_type": edge_data.get("reference_type"),
                    })

        return {
            "standard_id": standard_id,
            "found_in_graph": True,
            "references": direct_refs,
            "referenced_by": referenced_by,
            "associated_qcos": associated_qcos,
            "unresolved_references": unresolved_refs,
            "traversed_node_count": len(visited),
        }
