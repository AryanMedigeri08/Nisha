"""
scripts/build_retrieval_index.py
================================

CLI script to build the canonical searchable standards corpus,
dense vector embeddings, and retrieval index metadata.

Usage:
    python scripts/build_retrieval_index.py
"""

import logging
import sys
from pathlib import Path

# Add project root to sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.retrieval.index_builder import SearchIndexBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    builder = SearchIndexBuilder()
    metadata, duration = builder.build_and_save_index()
    print("=" * 60)
    print("RETRIEVAL INDEX BUILD COMPLETED")
    print(f"Standards Indexed: {metadata.standard_count}")
    print(f"Embedding Model:   {metadata.embedding_model}")
    print(f"Embedding Dim:     {metadata.embedding_dimension}")
    print(f"Reranker Model:    {metadata.reranker_model}")
    print(f"Build Time:        {duration:.2f} seconds")
    print(f"Index Version:     {metadata.index_version}")
    print("=" * 60)


if __name__ == "__main__":
    main()
