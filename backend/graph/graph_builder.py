"""
backend/graph/graph_builder.py
==============================

Constructs a NetworkX directed knowledge graph connecting:
- 91 Indian Standards (STANDARD nodes)
- 35 Quality Control Orders (QCO_ORDER nodes)
- Normative reference edges (RESOLVED)
- Unresolved / external references (preserved with status UNRESOLVED)

CRITICAL RULES:
- Never infer 'RELATED_TO' from 'same sector'.
- Never infer 'NORMATIVE_REFERENCE' from 'semantic similarity'.
- Preserve all unresolved reference edges without deleting or falsely merging them.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import openpyxl

from backend.app.core.config import SEED_DATASET_PATH
from backend.app.core.database import SessionLocal
from backend.app.models.models import Standard, Reference, QCO, QCOStandardLink
from backend.graph.graph_schema import (
    GraphEdge,
    GraphMetadata,
    QCONode,
    ReferenceNode,
    ReferenceResolutionStatus,
    RelationshipType,
    StandardNode,
)
from backend.graph.standard_normalizer import normalize_is_identifier, parse_is_identifier

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds and serializes the NetworkX knowledge graph for Indian Standards and QCOs."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data" / "graph")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.graph = nx.DiGraph()

    def build_graph(self) -> nx.DiGraph:
        """Construct the complete DiGraph from the database and seed dataset."""
        self.graph.clear()
        session = SessionLocal()

        try:
            # 1. Add 91 Standard Nodes
            standards = session.query(Standard).order_by(Standard.id).all()
            std_by_is: Dict[str, Standard] = {}
            for std in standards:
                canonical_is = normalize_is_identifier(std.is_number, keep_year=False)
                std_node = StandardNode(
                    standard_id=std.standard_id,
                    is_number=std.is_number,
                    is_number_canonical=canonical_is,
                    title=std.title,
                    sector=std.sector,
                    year=std.year,
                    status=std.status,
                    source_url=std.source_url,
                )
                self.graph.add_node(
                    std.standard_id,
                    **std_node.model_dump(),
                )
                std_by_is[std.is_number.strip()] = std
                std_by_is[canonical_is] = std

            # 2. Add 35 QCO Nodes
            qcos = session.query(QCO).order_by(QCO.id).all()
            for q in qcos:
                qco_node = QCONode(
                    qco_id=q.qco_id,
                    order_identifier=q.order_name,
                    title=q.order_name,
                    authority=q.notifying_authority,
                    effective_date=str(q.effective_date) if q.effective_date else None,
                    status=q.status,
                )
                self.graph.add_node(
                    q.qco_id,
                    **qco_node.model_dump(),
                )

            # 3. Add QCO Association Edges (STANDARD -> ASSOCIATED_WITH -> QCO_ORDER)
            qco_links = session.query(QCOStandardLink).all()
            qco_edges_count = 0
            for link in qco_links:
                std = link.standard
                qco = link.qco
                if std and qco:
                    self.graph.add_edge(
                        std.standard_id,
                        qco.qco_id,
                        relationship_type=RelationshipType.ASSOCIATED_QCO.value,
                        evidence_source=f"Seed dataset QCO mapping: '{qco.order_name}'",
                        confidence="verified_seed_association",
                    )
                    qco_edges_count += 1

            # 4. Ingest and Resolve References from Excel seed (preserving unresolved)
            resolved_count = 0
            unresolved_count = 0
            self.unresolved_references: List[ReferenceNode] = []

            if SEED_DATASET_PATH.exists():
                wb = openpyxl.load_workbook(str(SEED_DATASET_PATH), data_only=True)
                if "reference_seed" in wb.sheetnames:
                    sheet = wb["reference_seed"]
                    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=1):
                        src_raw = str(row[0] or "").strip()
                        tgt_raw = str(row[1] or "").strip()
                        ref_type = str(row[2] or "normative_reference").strip()
                        evidence = str(row[3] or "").strip()
                        src_url = str(row[4] or "").strip()

                        # Try to resolve source standard
                        src_canonical = normalize_is_identifier(src_raw, keep_year=False)
                        tgt_canonical = normalize_is_identifier(tgt_raw, keep_year=False)

                        src_std = std_by_is.get(src_raw) or std_by_is.get(src_canonical)
                        tgt_std = std_by_is.get(tgt_raw) or std_by_is.get(tgt_canonical)

                        ref_id = f"ref_{idx:03d}"

                        if src_std and tgt_std:
                            # Fully resolved edge between two standards in the 91-standard corpus
                            self.graph.add_edge(
                                src_std.standard_id,
                                tgt_std.standard_id,
                                relationship_type=RelationshipType.NORMATIVE_REFERENCE.value,
                                reference_type=ref_type,
                                evidence_source=evidence,
                                source_url=src_url,
                                confidence="candidate",
                            )
                            resolved_count += 1
                        else:
                            # Unresolved reference: preserved without deletion
                            unresolved_count += 1
                            unresolved_node = ReferenceNode(
                                reference_id=ref_id,
                                source_standard_id=src_std.standard_id if src_std else "EXTERNAL_SOURCE",
                                source_is_number=src_raw,
                                raw_reference=tgt_raw,
                                target_standard_id=tgt_std.standard_id if tgt_std else None,
                                target_is_number=tgt_raw if not tgt_std else tgt_std.is_number,
                                reference_type=ref_type,
                                resolution_status=ReferenceResolutionStatus.UNRESOLVED,
                                evidence_source=evidence,
                                source_url=src_url,
                            )
                            self.unresolved_references.append(unresolved_node)

                            # Add reference node to graph so external citation is preserved
                            self.graph.add_node(
                                ref_id,
                                **unresolved_node.model_dump(),
                            )
                            if src_std:
                                self.graph.add_edge(
                                    src_std.standard_id,
                                    ref_id,
                                    relationship_type=RelationshipType.NORMATIVE_REFERENCE.value,
                                    status="UNRESOLVED_TARGET",
                                    evidence_source=evidence,
                                )
                wb.close()

            logger.info(
                "Graph built: %d nodes (%d standards, %d QCOs), %d edges (%d QCO links, %d resolved refs, %d unresolved refs)",
                self.graph.number_of_nodes(),
                len(standards),
                len(qcos),
                self.graph.number_of_edges(),
                qco_edges_count,
                resolved_count,
                unresolved_count,
            )

            self.resolved_ref_count = resolved_count
            self.unresolved_ref_count = unresolved_count
            self.qco_edges_count = qco_edges_count

            return self.graph

        finally:
            session.close()

    def save_graph(self) -> Tuple[Path, Path]:
        """Save graph data to JSON and write graph_metadata.json."""
        if not self.graph:
            self.build_graph()

        # Serialize graph nodes and edges
        nodes_data = [
            {"id": n, **attrs} for n, attrs in self.graph.nodes(data=True)
        ]
        edges_data = [
            {"source": u, "target": v, **attrs} for u, v, attrs in self.graph.edges(data=True)
        ]

        graph_payload = {
            "version": "v1.0.0",
            "nodes": nodes_data,
            "edges": edges_data,
            "unresolved_references": [r.model_dump() for r in self.unresolved_references],
        }

        graph_path = self.data_dir / "standards_graph.json"
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph_payload, f, indent=2, ensure_ascii=False)

        # Build metadata
        std_nodes_count = sum(1 for _, d in self.graph.nodes(data=True) if d.get("node_type") == "STANDARD")
        qco_nodes_count = sum(1 for _, d in self.graph.nodes(data=True) if d.get("node_type") == "QCO_ORDER")

        meta = GraphMetadata(
            graph_version="v1.0.0",
            created_at=datetime.now(timezone.utc).isoformat(),
            standard_nodes=std_nodes_count,
            qco_nodes=qco_nodes_count,
            reference_edges=self.resolved_ref_count,
            qco_edges=self.qco_edges_count,
            resolved_references=self.resolved_ref_count,
            unresolved_references=self.unresolved_ref_count,
            status="sparse_bootstrap_graph",
        )

        meta_path = self.data_dir / "graph_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta.model_dump(), f, indent=2)

        return graph_path, meta_path
