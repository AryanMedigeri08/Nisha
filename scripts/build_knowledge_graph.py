"""
scripts/build_knowledge_graph.py
================================

CLI script to construct the NetworkX Indian Standards Knowledge Graph,
resolve normative references, connect QCO regulatory orders, and write graph metadata.

Usage:
    python scripts/build_knowledge_graph.py
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.graph.graph_builder import KnowledgeGraphBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    start = time.perf_counter()
    builder = KnowledgeGraphBuilder()
    graph = builder.build_graph()
    graph_path, meta_path = builder.save_graph()
    elapsed = time.perf_counter() - start

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("=" * 60)
    print("KNOWLEDGE GRAPH BUILD COMPLETE")
    print(f"Total Nodes:          {graph.number_of_nodes()}")
    print(f"  Standard Nodes:     {meta['standard_nodes']}")
    print(f"  QCO Nodes:          {meta['qco_nodes']}")
    print(f"Total Edges:          {graph.number_of_edges()}")
    print(f"  QCO Edges:          {meta['qco_edges']}")
    print(f"  Resolved Refs:      {meta['resolved_references']}")
    print(f"  Unresolved Refs:    {meta['unresolved_references']}")
    print(f"Graph JSON:           {graph_path}")
    print(f"Metadata JSON:        {meta_path}")
    print(f"Build Duration:       {elapsed:.3f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    main()
