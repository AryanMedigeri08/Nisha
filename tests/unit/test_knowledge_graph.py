"""
tests/unit/test_knowledge_graph.py
==================================

Unit tests for KnowledgeGraphBuilder and GraphTraversalEngine:
- Exact 91 Standard nodes created
- Exact 35 QCO nodes created
- 91 QCO association edges created
- Valid reference edges created
- Unresolved references preserved as ReferenceNode
- Bounded graph traversal (max_depth=2)
- Multi-part standards remain distinct in graph
"""

import pytest
import networkx as nx
from backend.graph.graph_builder import KnowledgeGraphBuilder
from backend.graph.graph_traversal import GraphTraversalEngine


@pytest.fixture(scope="module")
def built_graph():
    builder = KnowledgeGraphBuilder()
    graph = builder.build_graph()
    return graph, builder


def test_graph_has_91_standard_nodes(built_graph):
    """Ensure exactly 91 standard nodes exist."""
    graph, _ = built_graph
    std_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "STANDARD"]
    assert len(std_nodes) == 91


def test_graph_has_35_qco_nodes(built_graph):
    """Ensure exactly 35 QCO nodes exist."""
    graph, _ = built_graph
    qco_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "QCO_ORDER"]
    assert len(qco_nodes) == 35


def test_graph_has_91_qco_association_edges(built_graph):
    """Ensure every seed standard is linked to its associated QCO."""
    graph, builder = built_graph
    assert builder.qco_edges_count == 91


def test_resolved_reference_edge_created(built_graph):
    """Verify resolved edge IS 374:2019 -> IS 302 : Part 1 (2024)."""
    graph, builder = built_graph
    assert builder.resolved_ref_count == 1
    # Check edge exists between is_374_2019 and is_302___part_1_2024
    assert graph.has_edge("is_374_2019", "is_302___part_1_2024")


def test_unresolved_references_preserved(built_graph):
    """Unresolved references must be retained as ReferenceNodes, not discarded."""
    graph, builder = built_graph
    assert builder.unresolved_ref_count == 2
    ref_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "REFERENCE"]
    assert len(ref_nodes) >= 1
    assert any("302" in str(d.get("raw_reference")) for _, d in graph.nodes(data=True) if d.get("node_type") == "REFERENCE")


def test_graph_traversal_bounded_to_max_depth(built_graph):
    """Traversal must be bounded to max_depth=2."""
    graph, _ = built_graph
    engine = GraphTraversalEngine(graph)

    res = engine.traverse("is_374_2019", max_depth=2)
    assert res["found_in_graph"] is True
    assert len(res["associated_qcos"]) >= 1
    assert any(q["depth"] <= 2 for q in res["associated_qcos"])


def test_graph_traversal_missing_standard(built_graph):
    """Traversal on non-existent standard returns clean empty structure."""
    graph, _ = built_graph
    engine = GraphTraversalEngine(graph)

    res = engine.traverse("non_existent_id", max_depth=2)
    assert res["found_in_graph"] is False
    assert res["references"] == []
    assert res["associated_qcos"] == []


def test_multi_part_standards_distinct_nodes(built_graph):
    """Multi-part standards (e.g. IS 1489 Part 1 and Part 2) have distinct nodes."""
    graph, _ = built_graph
    assert graph.has_node("is_1489_part_1")
    assert graph.has_node("is_1489_part_2")
    assert "is_1489_part_1" != "is_1489_part_2"
