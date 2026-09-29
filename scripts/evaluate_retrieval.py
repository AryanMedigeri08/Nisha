"""
scripts/evaluate_retrieval.py
=============================

Phase 4 Comprehensive Evaluation and Ablation Suite for Hybrid Retrieval Engine.

Evaluates all 500 queries in data/synthetic/synthetic_queries_v1.jsonl across:
- Experiment A: BM25 Only
- Experiment B: Dense Only
- Experiment C: BM25 + Dense -> RRF
- Experiment D: BM25 + Dense -> RRF -> Cross-Encoder

Strict Compliance:
- RULE 1: Zero label leakage during retrieval inference.
- RULE 2: Benchmark file is frozen and untouched.
- RULE 3: Zero fabricated data.

Generates:
- data/evaluation/retrieval_results.jsonl
- data/evaluation/retrieval_metrics.json
- data/evaluation/retrieval_error_analysis.json
- data/evaluation/near_match_analysis.json
- data/evaluation/retrieval_ablation.json
"""

from __future__ import annotations

import json
import logging
import math
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root to sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from backend.extraction.extractor import RequirementExtractor
from backend.extraction.schemas import ProcurementRequirements
from backend.retrieval.retrieval_engine import RetrievalEngine
from backend.retrieval.schemas import RetrievalCandidate, RetrievalResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ===================================================================
# Metrics Computation Helpers
# ===================================================================

def compute_recall_at_k(candidates: List[RetrievalCandidate], gt_primaries: Set[str], k: int) -> float:
    """Return 1.0 if any primary ground truth standard is in candidates[:k], else 0.0."""
    sub_cands = candidates[:k]
    for c in sub_cands:
        if c.is_number in gt_primaries:
            return 1.0
    return 0.0


def compute_reciprocal_rank(candidates: List[RetrievalCandidate], gt_primaries: Set[str]) -> float:
    """Return 1.0 / rank (1-indexed) of first primary ground truth standard, or 0.0."""
    for rank, c in enumerate(candidates, start=1):
        if c.is_number in gt_primaries:
            return 1.0 / rank
    return 0.0


def compute_ndcg_at_k(
    candidates: List[RetrievalCandidate],
    gt_primaries: Set[str],
    gt_related: Set[str],
    k: int = 10,
) -> float:
    """
    Compute Normalized Discounted Cumulative Gain at rank k.
    Relevance:
        Primary Standard = 2
        Related Standard = 1
        Other = 0
    """
    sub_cands = candidates[:k]
    dcg = 0.0
    for i, c in enumerate(sub_cands, start=1):
        rel = 0
        if c.is_number in gt_primaries:
            rel = 2
        elif c.is_number in gt_related:
            rel = 1

        if rel > 0:
            dcg += (math.pow(2, rel) - 1.0) / math.log2(i + 1)

    # Ideal ranking: primaries first, then related
    ideal_rels = ([2] * len(gt_primaries)) + ([1] * len(gt_related))
    ideal_rels.sort(reverse=True)
    ideal_rels = ideal_rels[:k]

    idcg = 0.0
    for i, rel in enumerate(ideal_rels, start=1):
        idcg += (math.pow(2, rel) - 1.0) / math.log2(i + 1)

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def evaluate_system_candidates(
    query_eval_pairs: List[Tuple[Dict[str, Any], List[RetrievalCandidate]]],
    k_list: List[int] = [1, 5, 10, 20],
) -> Dict[str, float]:
    """Calculate aggregated Recall@1, 5, 10, 20, MRR, NDCG@10 for a given candidate set."""
    total = len(query_eval_pairs)
    if total == 0:
        return {}

    recalls = {f"Recall@{k}": 0.0 for k in k_list}
    mrr_sum = 0.0
    ndcg_sum = 0.0

    for query_item, candidates in query_eval_pairs:
        gt_primaries = set(query_item["ground_truth_primary"])
        gt_related = set(query_item.get("ground_truth_related", []))

        for k in k_list:
            recalls[f"Recall@{k}"] += compute_recall_at_k(candidates, gt_primaries, k)

        mrr_sum += compute_reciprocal_rank(candidates, gt_primaries)
        ndcg_sum += compute_ndcg_at_k(candidates, gt_primaries, gt_related, k=10)

    result = {k: round(v / total, 4) for k, v in recalls.items()}
    result["MRR"] = round(mrr_sum / total, 4)
    result["NDCG@10"] = round(ndcg_sum / total, 4)
    return result


# ===================================================================
# Main Evaluation Pipeline
# ===================================================================

def main():
    start_eval_time = time.perf_counter()
    project_root = Path(__file__).resolve().parent.parent
    benchmark_path = project_root / "data" / "synthetic" / "synthetic_queries_v1.jsonl"
    eval_dir = project_root / "data" / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading 500 benchmark queries from %s...", benchmark_path)
    with open(benchmark_path, "r", encoding="utf-8") as f:
        query_records = [json.loads(line) for line in f]
    logger.info("Loaded %d queries.", len(query_records))

    logger.info("Initializing RequirementExtractor and RetrievalEngine...")
    extractor = RequirementExtractor()
    engine = RetrievalEngine()

    results_records: List[Dict[str, Any]] = []

    # Intermediate candidate lists for ablation studies
    bm25_eval_pairs: List[Tuple[Dict[str, Any], List[RetrievalCandidate]]] = []
    dense_eval_pairs: List[Tuple[Dict[str, Any], List[RetrievalCandidate]]] = []
    rrf_eval_pairs: List[Tuple[Dict[str, Any], List[RetrievalCandidate]]] = []
    final_eval_pairs: List[Tuple[Dict[str, Any], List[RetrievalCandidate]]] = []

    # Latency tracking
    bm25_latencies: List[float] = []
    dense_latencies: List[float] = []
    rrf_latencies: List[float] = []
    rerank_latencies: List[float] = []
    total_latencies: List[float] = []

    logger.info("Executing retrieval inference over 500 benchmark queries (Rule 1: No Label Leakage)...")

    for idx, q_item in enumerate(query_records, start=1):
        q_text = q_item["query"]
        q_id = q_item["id"]

        t0 = time.perf_counter()

        # Step 1: Extraction (inference purely on query text)
        req = extractor.extract(q_text, query_id=q_id)

        # Step 2: BM25 retrieval
        t_bm25_start = time.perf_counter()
        bm25_cands = engine.retrieve_bm25(req, top_k=20)
        t_bm25_end = time.perf_counter()
        bm25_latencies.append((t_bm25_end - t_bm25_start) * 1000.0)

        # Step 3: Dense retrieval
        t_dense_start = time.perf_counter()
        dense_cands = engine.retrieve_dense(req, top_k=20)
        t_dense_end = time.perf_counter()
        dense_latencies.append((t_dense_end - t_dense_start) * 1000.0)

        # Step 4: RRF Fusion
        t_rrf_start = time.perf_counter()
        rrf_cands = engine.fuse_rrf(bm25_cands, dense_cands, k=60, top_k=20)
        t_rrf_end = time.perf_counter()
        rrf_latencies.append((t_rrf_end - t_rrf_start) * 1000.0)

        # Step 5: Cross-Encoder Reranking
        t_rerank_start = time.perf_counter()
        final_cands = engine.rerank_cross_encoder(q_text, rrf_cands, top_k=10)
        t_rerank_end = time.perf_counter()
        rerank_latencies.append((t_rerank_end - t_rerank_start) * 1000.0)

        total_latencies.append((time.perf_counter() - t0) * 1000.0)

        # Store for ablation
        bm25_eval_pairs.append((q_item, bm25_cands))
        dense_eval_pairs.append((q_item, dense_cands))
        rrf_eval_pairs.append((q_item, rrf_cands))
        final_eval_pairs.append((q_item, final_cands))

        # Store result record
        results_records.append({
            "query_id": q_id,
            "query": q_text,
            "difficulty": q_item["difficulty"],
            "sector": q_item.get("sector"),
            "ground_truth_primary": q_item["ground_truth_primary"],
            "ground_truth_related": q_item.get("ground_truth_related", []),
            "near_match_candidates": q_item.get("near_match_candidates", []),
            "bm25_candidates": [c.model_dump() for c in bm25_cands],
            "dense_candidates": [c.model_dump() for c in dense_cands],
            "rrf_candidates": [c.model_dump() for c in rrf_cands],
            "final_candidates": [c.model_dump() for c in final_cands],
        })

        if idx % 100 == 0:
            logger.info("Processed %d / %d queries...", idx, len(query_records))

    # Save detailed retrieval results
    results_path = eval_dir / "retrieval_results.jsonl"
    with open(results_path, "w", encoding="utf-8") as f:
        for r in results_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info("Saved retrieval results to %s", results_path)

    # ===================================================================
    # 1. Ablation Study
    # ===================================================================
    logger.info("Computing Ablation Study...")
    metrics_bm25 = evaluate_system_candidates(bm25_eval_pairs, k_list=[1, 5, 10, 20])
    metrics_dense = evaluate_system_candidates(dense_eval_pairs, k_list=[1, 5, 10, 20])
    metrics_rrf = evaluate_system_candidates(rrf_eval_pairs, k_list=[1, 5, 10, 20])
    metrics_final = evaluate_system_candidates(final_eval_pairs, k_list=[1, 5, 10])

    ablation_data = {
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_queries": len(query_records),
        "systems": {
            "BM25_Only": {
                "description": "Experiment A: BM25 Sparse Lexical Retrieval",
                "Recall@1": metrics_bm25["Recall@1"],
                "Recall@5": metrics_bm25["Recall@5"],
                "Recall@10": metrics_bm25["Recall@10"],
                "Recall@20": metrics_bm25["Recall@20"],
                "MRR": metrics_bm25["MRR"],
                "NDCG@10": metrics_bm25["NDCG@10"],
            },
            "Dense_Only": {
                "description": "Experiment B: SentenceTransformer (all-MiniLM-L6-v2) Semantic Retrieval",
                "Recall@1": metrics_dense["Recall@1"],
                "Recall@5": metrics_dense["Recall@5"],
                "Recall@10": metrics_dense["Recall@10"],
                "Recall@20": metrics_dense["Recall@20"],
                "MRR": metrics_dense["MRR"],
                "NDCG@10": metrics_dense["NDCG@10"],
            },
            "RRF_Fused": {
                "description": "Experiment C: BM25 (20) + Dense (20) -> Reciprocal Rank Fusion (k=60)",
                "Recall@1": metrics_rrf["Recall@1"],
                "Recall@5": metrics_rrf["Recall@5"],
                "Recall@10": metrics_rrf["Recall@10"],
                "Recall@20": metrics_rrf["Recall@20"],
                "MRR": metrics_rrf["MRR"],
                "NDCG@10": metrics_rrf["NDCG@10"],
            },
            "RRF_CrossEncoder": {
                "description": "Experiment D: BM25 + Dense -> RRF -> Cross-Encoder (ms-marco-MiniLM-L-6-v2)",
                "Recall@1": metrics_final["Recall@1"],
                "Recall@5": metrics_final["Recall@5"],
                "Recall@10": metrics_final["Recall@10"],
                "MRR": metrics_final["MRR"],
                "NDCG@10": metrics_final["NDCG@10"],
            },
        },
        "candidate_recall_at_20": {
            "bm25_candidate_recall_at_20": metrics_bm25["Recall@20"],
            "dense_candidate_recall_at_20": metrics_dense["Recall@20"],
            "rrf_candidate_recall_at_20": metrics_rrf["Recall@20"],
        }
    }

    ablation_path = eval_dir / "retrieval_ablation.json"
    with open(ablation_path, "w", encoding="utf-8") as f:
        json.dump(ablation_data, f, indent=2)
    logger.info("Saved ablation analysis to %s", ablation_path)

    # ===================================================================
    # 2. Difficulty-Level Breakdown
    # ===================================================================
    logger.info("Computing Difficulty-Level Breakdown...")
    difficulty_groups: Dict[str, List[int]] = defaultdict(list)
    for i, q in enumerate(query_records):
        difficulty_groups[q["difficulty"]].append(i)

    diff_table: Dict[str, Dict[str, float]] = {}
    for diff, indices in difficulty_groups.items():
        sub_bm25 = [bm25_eval_pairs[i] for i in indices]
        sub_dense = [dense_eval_pairs[i] for i in indices]
        sub_rrf = [rrf_eval_pairs[i] for i in indices]
        sub_final = [final_eval_pairs[i] for i in indices]

        diff_table[diff] = {
            "query_count": len(indices),
            "BM25_R@5": evaluate_system_candidates(sub_bm25, [5])["Recall@5"],
            "Dense_R@5": evaluate_system_candidates(sub_dense, [5])["Recall@5"],
            "RRF_R@5": evaluate_system_candidates(sub_rrf, [5])["Recall@5"],
            "Hybrid_R@1": evaluate_system_candidates(sub_final, [1])["Recall@1"],
            "Hybrid_R@5": evaluate_system_candidates(sub_final, [5])["Recall@5"],
            "Hybrid_R@10": evaluate_system_candidates(sub_final, [10])["Recall@10"],
            "Hybrid_MRR": evaluate_system_candidates(sub_final, [1])["MRR"],
            "Hybrid_NDCG@10": evaluate_system_candidates(sub_final, [1])["NDCG@10"],
        }

    # ===================================================================
    # 3. Sector-Wise Breakdown
    # ===================================================================
    logger.info("Computing Sector-Wise Breakdown...")
    sector_groups: Dict[str, List[int]] = defaultdict(list)
    for i, q in enumerate(query_records):
        sec = q.get("sector", "Unknown")
        sector_groups[sec].append(i)

    sector_table: Dict[str, Dict[str, Any]] = {}
    for sec, indices in sorted(sector_groups.items()):
        sub_final = [final_eval_pairs[i] for i in indices]
        sec_metrics = evaluate_system_candidates(sub_final, [1, 5, 10])
        sector_table[sec] = {
            "query_count": len(indices),
            "Recall@1": sec_metrics["Recall@1"],
            "Recall@5": sec_metrics["Recall@5"],
            "Recall@10": sec_metrics["Recall@10"],
            "MRR": sec_metrics["MRR"],
            "NDCG@10": sec_metrics["NDCG@10"],
        }

    # ===================================================================
    # 4. Near-Match Analysis
    # ===================================================================
    logger.info("Computing Near-Match Analysis...")
    near_match_cases: List[Dict[str, Any]] = []
    near_match_queries = [r for r in results_records if r["difficulty"] == "NEAR_MATCH"]

    primary_ranked_above_near_count = 0
    primary_at_rank_1_count = 0
    near_match_in_top_10_count = 0

    for nm_item in near_match_queries:
        gt_primary = nm_item["ground_truth_primary"][0]
        near_candidates = nm_item["near_match_candidates"]
        final_top10 = nm_item["final_candidates"]

        # Find primary rank in final top 10
        primary_rank = None
        for cand in final_top10:
            if cand["is_number"] == gt_primary:
                primary_rank = cand["final_rank"]
                break

        # Find near match ranks
        near_ranks: Dict[str, Optional[int]] = {}
        for nm_std in near_candidates:
            nm_rank = None
            for cand in final_top10:
                if cand["is_number"] == nm_std:
                    nm_rank = cand["final_rank"]
                    break
            near_ranks[nm_std] = nm_rank

        # Comparison logic
        if primary_rank == 1:
            primary_at_rank_1_count += 1

        if any(r is not None for r in near_ranks.values()):
            near_match_in_top_10_count += 1

        # Check if primary beat all retrieved near-match candidates
        if primary_rank is not None:
            retrieved_nm_ranks = [r for r in near_ranks.values() if r is not None]
            if not retrieved_nm_ranks or primary_rank < min(retrieved_nm_ranks):
                primary_ranked_above_near_count += 1

        near_match_cases.append({
            "query_id": nm_item["query_id"],
            "query": nm_item["query"],
            "primary_standard": gt_primary,
            "near_match_candidates": near_candidates,
            "retrieved_top_10": [c["is_number"] for c in final_top10],
            "primary_rank": primary_rank,
            "near_match_ranks": near_ranks,
        })

    near_match_analysis = {
        "total_near_match_queries": len(near_match_queries),
        "primary_at_rank_1": primary_at_rank_1_count,
        "primary_at_rank_1_rate": round(primary_at_rank_1_count / max(len(near_match_queries), 1), 4),
        "primary_ranked_above_near_matches": primary_ranked_above_near_count,
        "primary_ranked_above_rate": round(primary_ranked_above_near_count / max(len(near_match_queries), 1), 4),
        "near_match_retrieved_in_top_10_count": near_match_in_top_10_count,
        "cases": near_match_cases,
    }

    near_match_path = eval_dir / "near_match_analysis.json"
    with open(near_match_path, "w", encoding="utf-8") as f:
        json.dump(near_match_analysis, f, indent=2)
    logger.info("Saved near match analysis to %s", near_match_path)

    # ===================================================================
    # 5. Retrieval Error Analysis
    # ===================================================================
    logger.info("Classifying Retrieval Errors...")
    error_buckets: Dict[str, List[Dict[str, Any]]] = {
        "PRIMARY_NOT_RETRIEVED": [],
        "PRIMARY_RANKED_TOO_LOW": [],
        "SEMANTIC_NEAR_MATCH_CONFUSION": [],
        "LEXICAL_MISMATCH": [],
        "SECTOR_CONFUSION": [],
        "PRODUCT_CONFUSION": [],
        "APPLICATION_CONFUSION": [],
        "PARAMETER_MISMATCH": [],
        "MULTI_SECTOR_AMBIGUITY": [],
    }

    for item in results_records:
        gt_primary = item["ground_truth_primary"][0]
        final_cands = item["final_candidates"]
        bm25_cands = item["bm25_candidates"]
        dense_cands = item["dense_candidates"]
        query_text = item["query"]

        # Check primary rank
        primary_rank = None
        for c in final_cands:
            if c["is_number"] == gt_primary:
                primary_rank = c["final_rank"]
                break

        bm25_has_primary = any(c["is_number"] == gt_primary for c in bm25_cands)
        dense_has_primary = any(c["is_number"] == gt_primary for c in dense_cands)

        # Categorize
        if primary_rank is None:
            # Primary was not in top 10
            error_entry = {
                "query_id": item["query_id"],
                "query": query_text,
                "primary_standard": gt_primary,
                "difficulty": item["difficulty"],
                "sector": item.get("sector"),
                "top_retrieved": final_cands[0]["is_number"] if final_cands else None,
                "top_retrieved_title": final_cands[0]["title"] if final_cands else None,
                "in_bm25_pool": bm25_has_primary,
                "in_dense_pool": dense_has_primary,
            }
            error_buckets["PRIMARY_NOT_RETRIEVED"].append(error_entry)

            if not bm25_has_primary and dense_has_primary:
                error_buckets["LEXICAL_MISMATCH"].append(error_entry)

        elif primary_rank > 1:
            top_cand = final_cands[0]
            error_entry = {
                "query_id": item["query_id"],
                "query": query_text,
                "primary_standard": gt_primary,
                "primary_rank": primary_rank,
                "top_standard": top_cand["is_number"],
                "top_title": top_cand["title"],
                "top_sector": top_cand.get("sector"),
                "difficulty": item["difficulty"],
            }
            error_buckets["PRIMARY_RANKED_TOO_LOW"].append(error_entry)

            # Sub-type diagnosis
            if item["difficulty"] == "NEAR_MATCH" and top_cand["is_number"] in item["near_match_candidates"]:
                error_buckets["SEMANTIC_NEAR_MATCH_CONFUSION"].append(error_entry)
            elif top_cand.get("sector") != item.get("sector"):
                error_buckets["SECTOR_CONFUSION"].append(error_entry)
            elif any(param_word in query_text.lower() for param_word in ["kv", "kva", "litre", "mm", "mpa"]):
                error_buckets["PARAMETER_MISMATCH"].append(error_entry)
            elif any(ambig in (item.get("sector") or "").lower() for ambig in ["accessories", "cables", "ppe"]):
                error_buckets["MULTI_SECTOR_AMBIGUITY"].append(error_entry)
            else:
                error_buckets["PRODUCT_CONFUSION"].append(error_entry)

    error_analysis_summary = {
        "summary": {cat: len(cases) for cat, cases in error_buckets.items()},
        "categories": {cat: cases[:10] for cat, cases in error_buckets.items()},
    }

    error_analysis_path = eval_dir / "retrieval_error_analysis.json"
    with open(error_analysis_path, "w", encoding="utf-8") as f:
        json.dump(error_analysis_summary, f, indent=2)
    logger.info("Saved retrieval error analysis to %s", error_analysis_path)

    # ===================================================================
    # 6. Overall Metrics Compilation
    # ===================================================================
    avg_latency = {
        "bm25_latency_ms": round(sum(bm25_latencies) / len(bm25_latencies), 2),
        "dense_latency_ms": round(sum(dense_latencies) / len(dense_latencies), 2),
        "rrf_latency_ms": round(sum(rrf_latencies) / len(rrf_latencies), 2),
        "reranker_latency_ms": round(sum(rerank_latencies) / len(rerank_latencies), 2),
        "total_latency_ms": round(sum(total_latencies) / len(total_latencies), 2),
    }

    metrics_payload = {
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_queries_evaluated": len(query_records),
        "overall_metrics": {
            "BM25": metrics_bm25,
            "Dense": metrics_dense,
            "RRF": metrics_rrf,
            "Hybrid_Reranked": metrics_final,
        },
        "difficulty_breakdown": diff_table,
        "sector_breakdown": sector_table,
        "candidate_recall": {
            "bm25_recall_at_20": metrics_bm25["Recall@20"],
            "dense_recall_at_20": metrics_dense["Recall@20"],
            "rrf_recall_at_20": metrics_rrf["Recall@20"],
        },
        "near_match_summary": {
            "total_queries": len(near_match_queries),
            "primary_at_rank_1_rate": near_match_analysis["primary_at_rank_1_rate"],
            "primary_ranked_above_near_matches_rate": near_match_analysis["primary_ranked_above_rate"],
        },
        "error_summary": {cat: len(cases) for cat, cases in error_buckets.items()},
        "latency_profile": avg_latency,
    }

    metrics_path = eval_dir / "retrieval_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
    logger.info("Saved retrieval metrics to %s", metrics_path)

    total_eval_duration = time.perf_counter() - start_eval_time
    logger.info("Phase 4 Evaluation complete in %.2f seconds.", total_eval_duration)


if __name__ == "__main__":
    main()
