"""
backend/review/review_service.py
================================

Orchestration Service for Phase 7 Human-in-the-Loop Officer Review Workflow.
Connects Phase 3 Requirement Extraction, Phase 4 Hybrid Retrieval, Phase 5 Knowledge Graph &
Regulatory Resolution, Phase 6 Recommendation Engine, and Phase 7 Decision & Audit Systems.
"""

from __future__ import annotations

import json
import logging
import time
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session

from backend.app.core.config import PROJECT_ROOT
from backend.app.models.models import (
    AuditEvent,
    OfficerDecision,
    OfficerEvidence,
    Query,
    Review,
    ReviewCandidate,
    Standard,
    VerificationItem,
)
from backend.extraction.extractor import RequirementExtractor
from backend.extraction.schemas import ProcurementRequirements
from backend.graph.graph_builder import KnowledgeGraphBuilder
from backend.graph.graph_traversal import GraphTraversalEngine
from backend.recommendation.engine import RecommendationEngine
from backend.recommendation.schemas import CandidateRecommendation, AIRecommendationState
from backend.regulatory.applicability import ApplicabilityEngine
from backend.regulatory.qco_resolver import QCOResolver
from backend.regulatory.version_resolver import VersionResolver
from backend.retrieval.retrieval_engine import RetrievalEngine
from backend.retrieval.schemas import RetrievalCandidate, StandardDocument
from backend.review.audit import AuditTrailService
from backend.review.comparison import CandidateComparisonEngine
from backend.review.schemas import (
    AuditEventDTO,
    AuditEventType,
    CandidateDTO,
    DashboardStatsResponse,
    OfficerDecisionDTO,
    OfficerDecisionState,
    RejectionReason,
    ReviewDetailDTO,
    ReviewListItemDTO,
    ReviewListResponse,
    VerificationItemDTO,
    VerificationState,
)
from backend.review.state_machine import ReviewStateMachine, InvalidStateTransitionError
from backend.review.verification import VerificationService

logger = logging.getLogger(__name__)


class PipelineContext:
    """Singleton-style cache for ML models and index data."""
    _instance: Optional["PipelineContext"] = None

    def __init__(self):
        logger.info("Initializing PipelineContext and loading models...")
        from backend.app.core.database import init_db
        init_db()
        self.extractor = RequirementExtractor()
        self.retrieval_engine = RetrievalEngine()

        # Build Knowledge Graph & Traversal
        graph_builder = KnowledgeGraphBuilder()
        self.graph = graph_builder.build_graph()
        self.traversal_engine = GraphTraversalEngine(self.graph)

        self.version_resolver = VersionResolver()
        self.qco_resolver = QCOResolver()
        self.applicability_engine = ApplicabilityEngine()
        self.recommendation_engine = RecommendationEngine()

        # Load canonical standards corpus
        corpus_path = PROJECT_ROOT / "data" / "index" / "standards_corpus.json"
        if corpus_path.exists():
            with open(corpus_path, "r", encoding="utf-8") as f:
                docs = [StandardDocument(**item) for item in json.load(f)]
            self.doc_map: Dict[str, StandardDocument] = {d.standard_id: d for d in docs}
        else:
            self.doc_map = {}
        logger.info("PipelineContext loaded successfully with %d indexed standards.", len(self.doc_map))

    @classmethod
    def get_instance(cls) -> "PipelineContext":
        if cls._instance is None:
            cls._instance = PipelineContext()
        return cls._instance


class ReviewService:
    """Main business logic service for review management."""

    @classmethod
    def create_review_from_query(
        cls,
        db: Session,
        query_text: str,
        input_type: str = "text",
        top_k: int = 10,
    ) -> ReviewDetailDTO:
        """
        Execute full end-to-end pipeline and persist review object with candidates,
        requirement coverage, gaps, regulatory status, and verification checklist.
        """
        ctx = PipelineContext.get_instance()

        # 1. Phase 3: Requirement Extraction
        requirements: ProcurementRequirements = ctx.extractor.extract(
            query=query_text,
            query_id=f"q_{int(time.time() * 1000)}",
        )

        # 2. Phase 4: Hybrid Retrieval & Reranking
        retrieval_result = ctx.retrieval_engine.retrieve(
            requirements=requirements,
            query_text=query_text,
            top_k=top_k,
        )

        # 3. Phase 5 & 6: Regulatory, Graph, Coverage, and Recommendation
        candidate_recommendations: List[CandidateRecommendation] = []

        for cand in retrieval_result.candidates:
            std_doc = ctx.doc_map.get(cand.standard_id)
            if not std_doc:
                continue

            # Graph traversal for normative references
            traversal_res = ctx.traversal_engine.traverse(cand.standard_id, max_depth=1)
            norm_ref_dicts = traversal_res.get("references", [])

            # Regulatory resolutions
            version_res = ctx.version_resolver.resolve(std_doc)
            qco_res = ctx.qco_resolver.resolve(std_doc)
            app_res = ctx.applicability_engine.assess(cand, version_res, qco_res)

            # Build Phase 6 recommendation
            cand_rec = ctx.recommendation_engine.build_recommendation(
                requirements=requirements,
                candidate=cand,
                standard=std_doc,
                version_result=version_res,
                qco_result=qco_res,
                applicability=app_res,
                normative_references=norm_ref_dicts,
            )
            candidate_recommendations.append(cand_rec)

        # 4. Save Query to DB
        q_record = Query(
            raw_text=query_text,
            input_type=input_type,
            language="en",
            product=requirements.product.value if requirements.product else None,
            application=", ".join(a.value for a in requirements.application) if requirements.application else None,
            materials=[m.value for m in requirements.materials if m.value],
            parameters=[p.model_dump() for p in requirements.parameters],
            cited_standards=[c.model_dump() for c in requirements.cited_standards],
            created_at=datetime.datetime.utcnow(),
        )
        db.add(q_record)
        db.flush()

        # 5. Create Review Record
        # Generate readable Review ID e.g. REV-000101
        count_existing = db.query(func.count(Review.id)).scalar() or 0
        review_code = f"REV-{count_existing + 1:06d}"

        review = Review(
            review_id=review_code,
            query_id=q_record.id,
            raw_text=query_text,
            input_type=input_type,
            procurement_requirements=requirements.model_dump(),
            status=OfficerDecisionState.PENDING.value,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(review)
        db.flush()

        # 6. Save Candidates & Generate Verification Items
        for cand_rec in candidate_recommendations:
            rc = ReviewCandidate(
                review_id=review.id,
                standard_id=cand_rec.standard_id,
                is_number=cand_rec.is_number,
                title=cand_rec.title,
                sector=cand_rec.sector,
                application=cand_rec.application,
                materials=cand_rec.materials,
                technical_parameters=cand_rec.technical_parameters,
                retrieval_rank=cand_rec.retrieval_rank,
                reranker_score=cand_rec.reranker_score,
                rrf_score=cand_rec.rrf_score,
                retrieval_method=cand_rec.retrieval_method,
                requirement_coverage=cand_rec.coverage.model_dump(),
                gaps=[g.model_dump() for g in cand_rec.gaps],
                standard_status=cand_rec.standard_status.value,
                qco_status=cand_rec.qco_status.value,
                qco_ids=cand_rec.qco_ids,
                order_names=cand_rec.order_names,
                effective_date=cand_rec.effective_date,
                authority=cand_rec.authority,
                ai_recommendation_state=cand_rec.recommendation_state.value,
                notes=cand_rec.explanation,
                evidence=[e.model_dump() for e in cand_rec.evidence_items],
                normative_references=cand_rec.normative_references,
                created_at=datetime.datetime.utcnow(),
            )
            db.add(rc)
            db.flush()

            # Generate dynamic verification items
            v_items = VerificationService.generate_verification_items(
                candidate_rec=cand_rec,
                review_id=review.id,
                candidate_id=rc.id,
            )
            for vi in v_items:
                db.add(vi)

        # 7. Record Audit Event
        AuditTrailService.record_event(
            db=db,
            review_id=review.id,
            event_type=AuditEventType.REVIEW_CREATED,
            previous_state=None,
            new_state=OfficerDecisionState.PENDING.value,
            actor="system",
            actor_role="Recommendation Pipeline",
            reason="Procurement query submitted and candidates retrieved.",
            details={
                "query_length": len(query_text),
                "candidates_count": len(candidate_recommendations),
                "top_candidate": candidate_recommendations[0].is_number if candidate_recommendations else None,
            },
        )

        db.commit()
        db.refresh(review)

        return cls.get_review_detail(db, review.id)

    @classmethod
    def get_review_detail(cls, db: Session, review_identifier: Any) -> ReviewDetailDTO:
        """Fetch complete review details by database id or string review_id."""
        if isinstance(review_identifier, int) or str(review_identifier).isdigit():
            review = db.query(Review).filter(Review.id == int(review_identifier)).first()
        else:
            review = db.query(Review).filter(Review.review_id == str(review_identifier)).first()

        if not review:
            raise ValueError(f"Review '{review_identifier}' not found.")

        # Build CandidateDTOs
        cand_dtos: List[CandidateDTO] = []
        for c in review.candidates:
            v_dtos = [
                VerificationItemDTO(
                    id=v.id,
                    review_id=v.review_id,
                    candidate_id=v.candidate_id,
                    standard_id=v.standard_id,
                    item_key=v.item_key,
                    title=v.title,
                    category=v.category,
                    system_state=v.system_state,
                    officer_state=VerificationState(v.officer_state),
                    is_regulatory=v.is_regulatory,
                    system_evidence=v.system_evidence,
                    officer_evidence_reference=v.officer_evidence_reference,
                    officer_note=v.officer_note,
                    verified_at=v.verified_at,
                    verified_by=v.verified_by,
                    created_at=v.created_at,
                )
                for v in review.verification_items
                if v.candidate_id == c.id or v.standard_id == c.standard_id
            ]

            cand_dtos.append(
                CandidateDTO(
                    id=c.id,
                    review_id=c.review_id,
                    standard_id=c.standard_id,
                    is_number=c.is_number,
                    title=c.title,
                    sector=c.sector,
                    application=c.application,
                    materials=c.materials or [],
                    technical_parameters=c.technical_parameters or [],
                    retrieval_rank=c.retrieval_rank,
                    reranker_score=c.reranker_score,
                    rrf_score=c.rrf_score,
                    retrieval_method=c.retrieval_method or "hybrid_cross_encoder",
                    requirement_coverage=c.requirement_coverage,
                    gaps=c.gaps,
                    standard_status=c.standard_status,
                    qco_status=c.qco_status,
                    qco_ids=c.qco_ids or [],
                    order_names=c.order_names or [],
                    effective_date=c.effective_date,
                    authority=c.authority,
                    ai_recommendation_state=c.ai_recommendation_state,
                    notes=c.notes,
                    evidence=c.evidence,
                    normative_references=c.normative_references or [],
                    verification_items=v_dtos,
                )
            )

        # Build DecisionDTO
        decision_dto: Optional[OfficerDecisionDTO] = None
        if review.officer_decision:
            od = review.officer_decision
            decision_dto = OfficerDecisionDTO(
                state=OfficerDecisionState(od.state),
                selected_candidate_id=od.selected_candidate_id,
                selected_standard_id=od.selected_standard_id,
                selected_is_number=od.selected_is_number,
                ai_recommendation_state=od.ai_recommendation_state,
                is_override=od.is_override,
                rejection_reason=RejectionReason(od.rejection_reason) if od.rejection_reason else None,
                rejection_note=od.rejection_note,
                officer_id=od.officer_id,
                officer_role=od.officer_role,
                decision_summary=od.decision_summary,
                supporting_evidence_references=od.supporting_evidence_references or [],
                timestamp=od.timestamp,
            )

        # Build VerificationItemDTOs for all items
        all_v_dtos = [
            VerificationItemDTO(
                id=v.id,
                review_id=v.review_id,
                candidate_id=v.candidate_id,
                standard_id=v.standard_id,
                item_key=v.item_key,
                title=v.title,
                category=v.category,
                system_state=v.system_state,
                officer_state=VerificationState(v.officer_state),
                is_regulatory=v.is_regulatory,
                system_evidence=v.system_evidence,
                officer_evidence_reference=v.officer_evidence_reference,
                officer_note=v.officer_note,
                verified_at=v.verified_at,
                verified_by=v.verified_by,
                created_at=v.created_at,
            )
            for v in review.verification_items
        ]

        # Build AuditEventDTOs
        audit_dtos = [
            AuditEventDTO(
                id=a.id,
                review_id=a.review_id,
                event_type=AuditEventType(a.event_type),
                previous_state=a.previous_state,
                new_state=a.new_state,
                actor=a.actor,
                actor_role=a.actor_role,
                reason=a.reason,
                details=a.details,
                timestamp=a.timestamp,
            )
            for a in review.audit_events
        ]

        return ReviewDetailDTO(
            id=review.id,
            review_id=review.review_id,
            query_id=review.query_id,
            raw_text=review.raw_text,
            input_type=review.input_type,
            procurement_requirements=review.procurement_requirements,
            status=OfficerDecisionState(review.status),
            selected_candidate_id=review.selected_candidate_id,
            candidates=cand_dtos,
            officer_decision=decision_dto,
            verification_items=all_v_dtos,
            audit_events=audit_dtos,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    @classmethod
    def list_reviews(
        cls,
        db: Session,
        status: Optional[str] = None,
        decision_state: Optional[str] = None,
        sector: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ReviewListResponse:
        """List reviews with filtering and pagination."""
        query = db.query(Review)

        if status:
            query = query.filter(Review.status == status.upper())

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Review.raw_text.ilike(search_pattern),
                    Review.review_id.ilike(search_pattern),
                )
            )

        total = query.count()
        reviews = query.order_by(desc(Review.created_at)).offset(offset).limit(limit).all()

        items: List[ReviewListItemDTO] = []
        for r in reviews:
            top_c = r.candidates[0] if r.candidates else None
            reqs = r.procurement_requirements or {}
            prod = reqs.get("product", {}).get("value") if isinstance(reqs, dict) else None
            sec = reqs.get("sector", {}).get("value") if isinstance(reqs, dict) else None

            # Filter by sector if provided
            if sector and sec and sector.lower() not in sec.lower():
                continue

            pending_v_count = sum(
                1 for v in r.verification_items if v.officer_state == VerificationState.UNVERIFIED.value
            )

            dec_state = r.officer_decision.state if r.officer_decision else None
            is_over = r.officer_decision.is_override if r.officer_decision else False

            items.append(
                ReviewListItemDTO(
                    id=r.id,
                    review_id=r.review_id,
                    raw_text=r.raw_text,
                    product=prod,
                    sector=sec,
                    status=OfficerDecisionState(r.status),
                    top_candidate_is_number=top_c.is_number if top_c else None,
                    top_candidate_title=top_c.title if top_c else None,
                    top_candidate_rank=top_c.retrieval_rank if top_c else None,
                    ai_recommendation_state=top_c.ai_recommendation_state if top_c else None,
                    decision_state=dec_state,
                    is_override=is_over,
                    candidate_count=len(r.candidates),
                    pending_verification_count=pending_v_count,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )

        return ReviewListResponse(
            total=total,
            limit=limit,
            offset=offset,
            reviews=items,
        )

    @classmethod
    def update_verification_item(
        cls,
        db: Session,
        review_identifier: Any,
        verification_item_id: int,
        officer_state: VerificationState,
        evidence_reference: Optional[str] = None,
        officer_note: Optional[str] = None,
        officer_id: str = "officer_001",
    ) -> VerificationItemDTO:
        """Update a verification checklist item."""
        if isinstance(review_identifier, int) or str(review_identifier).isdigit():
            review = db.query(Review).filter(Review.id == int(review_identifier)).first()
        else:
            review = db.query(Review).filter(Review.review_id == str(review_identifier)).first()

        if not review:
            raise ValueError(f"Review '{review_identifier}' not found.")

        item = db.query(VerificationItem).filter(
            VerificationItem.id == verification_item_id,
            VerificationItem.review_id == review.id,
        ).first()

        if not item:
            raise ValueError(f"VerificationItem '{verification_item_id}' not found in review '{review.review_id}'.")

        prev_state = item.officer_state
        updated_item = VerificationService.apply_verification_update(
            db=db,
            item=item,
            new_state=officer_state,
            evidence_reference=evidence_reference,
            officer_note=officer_note,
            officer_id=officer_id,
        )

        # Move review to UNDER_REVIEW if it was PENDING
        if review.status == OfficerDecisionState.PENDING.value:
            review.status = OfficerDecisionState.UNDER_REVIEW.value
            review.updated_at = datetime.datetime.utcnow()
            db.add(review)

        # Record Audit Event
        AuditTrailService.record_event(
            db=db,
            review_id=review.id,
            event_type=AuditEventType.VERIFICATION_CHANGED,
            previous_state=prev_state,
            new_state=officer_state.value,
            actor=officer_id,
            actor_role="Procurement Officer",
            reason=f"Verification status updated for item '{item.item_key}'.",
            details={
                "item_key": item.item_key,
                "title": item.title,
                "category": item.category,
                "evidence_reference": evidence_reference,
                "officer_note": officer_note,
            },
        )

        return VerificationItemDTO(
            id=updated_item.id,
            review_id=updated_item.review_id,
            candidate_id=updated_item.candidate_id,
            standard_id=updated_item.standard_id,
            item_key=updated_item.item_key,
            title=updated_item.title,
            category=updated_item.category,
            system_state=updated_item.system_state,
            officer_state=VerificationState(updated_item.officer_state),
            is_regulatory=updated_item.is_regulatory,
            system_evidence=updated_item.system_evidence,
            officer_evidence_reference=updated_item.officer_evidence_reference,
            officer_note=updated_item.officer_note,
            verified_at=updated_item.verified_at,
            verified_by=updated_item.verified_by,
            created_at=updated_item.created_at,
        )

    @classmethod
    def submit_officer_decision(
        cls,
        db: Session,
        review_identifier: Any,
        target_state: OfficerDecisionState,
        selected_candidate_id: Optional[int] = None,
        rejection_reason: Optional[RejectionReason] = None,
        rejection_note: Optional[str] = None,
        officer_id: str = "officer_001",
        officer_role: str = "Procurement Officer",
        decision_summary: Optional[str] = None,
        supporting_evidence_references: Optional[List[str]] = None,
    ) -> OfficerDecisionDTO:
        """Record authorized human officer decision with strict state transition validation."""
        if isinstance(review_identifier, int) or str(review_identifier).isdigit():
            review = db.query(Review).filter(Review.id == int(review_identifier)).first()
        else:
            review = db.query(Review).filter(Review.review_id == str(review_identifier)).first()

        if not review:
            raise ValueError(f"Review '{review_identifier}' not found.")

        current_state = OfficerDecisionState(review.status)

        # Validate transition
        ReviewStateMachine.validate_transition(current_state, target_state, is_reopen=False)

        selected_std_id: Optional[str] = None
        selected_is_num: Optional[str] = None
        ai_state: Optional[str] = None

        if selected_candidate_id:
            cand = db.query(ReviewCandidate).filter(
                ReviewCandidate.id == selected_candidate_id,
                ReviewCandidate.review_id == review.id,
            ).first()
            if cand:
                selected_std_id = cand.standard_id
                selected_is_num = cand.is_number
                ai_state = cand.ai_recommendation_state

        if not ai_state and review.candidates:
            ai_state = review.candidates[0].ai_recommendation_state
            if not selected_std_id:
                selected_std_id = review.candidates[0].standard_id
                selected_is_num = review.candidates[0].is_number

        # Override detection
        is_override = ReviewStateMachine.check_override(ai_state, target_state)

        # Check existing decision or create new
        decision = review.officer_decision
        is_modification = decision is not None

        if not decision:
            decision = OfficerDecision(
                review_id=review.id,
                state=target_state.value,
                selected_candidate_id=selected_candidate_id,
                selected_standard_id=selected_std_id,
                selected_is_number=selected_is_num,
                ai_recommendation_state=ai_state,
                is_override=is_override,
                rejection_reason=rejection_reason.value if rejection_reason else None,
                rejection_note=rejection_note,
                officer_id=officer_id,
                officer_role=officer_role,
                decision_summary=decision_summary,
                supporting_evidence_references=supporting_evidence_references or [],
                timestamp=datetime.datetime.utcnow(),
            )
            db.add(decision)
        else:
            decision.state = target_state.value
            decision.selected_candidate_id = selected_candidate_id
            decision.selected_standard_id = selected_std_id
            decision.selected_is_number = selected_is_num
            decision.ai_recommendation_state = ai_state
            decision.is_override = is_override
            decision.rejection_reason = rejection_reason.value if rejection_reason else None
            decision.rejection_note = rejection_note
            decision.officer_id = officer_id
            decision.officer_role = officer_role
            decision.decision_summary = decision_summary
            decision.supporting_evidence_references = supporting_evidence_references or []
            decision.timestamp = datetime.datetime.utcnow()
            db.add(decision)

        # Update Review state
        review.status = target_state.value
        review.selected_candidate_id = selected_candidate_id
        review.updated_at = datetime.datetime.utcnow()
        db.add(review)

        # Append Audit Event
        AuditTrailService.record_event(
            db=db,
            review_id=review.id,
            event_type=AuditEventType.DECISION_MODIFIED if is_modification else AuditEventType.DECISION_MADE,
            previous_state=current_state.value,
            new_state=target_state.value,
            actor=officer_id,
            actor_role=officer_role,
            reason=rejection_note or decision_summary or f"Officer marked review as {target_state.value}",
            details={
                "selected_standard": selected_is_num,
                "ai_state": ai_state,
                "is_override": is_override,
                "rejection_reason": rejection_reason.value if rejection_reason else None,
                "evidence_references": supporting_evidence_references,
            },
        )

        db.commit()
        db.refresh(decision)

        return OfficerDecisionDTO(
            state=OfficerDecisionState(decision.state),
            selected_candidate_id=decision.selected_candidate_id,
            selected_standard_id=decision.selected_standard_id,
            selected_is_number=decision.selected_is_number,
            ai_recommendation_state=decision.ai_recommendation_state,
            is_override=decision.is_override,
            rejection_reason=RejectionReason(decision.rejection_reason) if decision.rejection_reason else None,
            rejection_note=decision.rejection_note,
            officer_id=decision.officer_id,
            officer_role=decision.officer_role,
            decision_summary=decision.decision_summary,
            supporting_evidence_references=decision.supporting_evidence_references or [],
            timestamp=decision.timestamp,
        )

    @classmethod
    def reopen_review(
        cls,
        db: Session,
        review_identifier: Any,
        reason: str,
        officer_id: str = "officer_001",
    ) -> ReviewDetailDTO:
        """Reopen a finalized review back to UNDER_REVIEW state."""
        if isinstance(review_identifier, int) or str(review_identifier).isdigit():
            review = db.query(Review).filter(Review.id == int(review_identifier)).first()
        else:
            review = db.query(Review).filter(Review.review_id == str(review_identifier)).first()

        if not review:
            raise ValueError(f"Review '{review_identifier}' not found.")

        current_state = OfficerDecisionState(review.status)
        ReviewStateMachine.validate_transition(current_state, OfficerDecisionState.UNDER_REVIEW, is_reopen=True)

        review.status = OfficerDecisionState.UNDER_REVIEW.value
        review.updated_at = datetime.datetime.utcnow()
        db.add(review)

        AuditTrailService.record_event(
            db=db,
            review_id=review.id,
            event_type=AuditEventType.REVIEW_REOPENED,
            previous_state=current_state.value,
            new_state=OfficerDecisionState.UNDER_REVIEW.value,
            actor=officer_id,
            actor_role="Procurement Officer",
            reason=reason,
            details={"reopen_timestamp": datetime.datetime.utcnow().isoformat()},
        )

        db.commit()
        db.refresh(review)

        return cls.get_review_detail(db, review.id)

    @classmethod
    def get_dashboard_metrics(cls, db: Session) -> DashboardStatsResponse:
        """Aggregate operational dashboard statistics."""
        reviews = db.query(Review).all()
        total = len(reviews)

        pending = sum(1 for r in reviews if r.status == OfficerDecisionState.PENDING.value)
        under_review = sum(1 for r in reviews if r.status == OfficerDecisionState.UNDER_REVIEW.value)
        accepted = sum(1 for r in reviews if r.status == OfficerDecisionState.ACCEPTED.value)
        rejected = sum(1 for r in reviews if r.status == OfficerDecisionState.REJECTED.value)
        needs_ver = sum(1 for r in reviews if r.status == OfficerDecisionState.NEEDS_VERIFICATION.value)
        req_rev = sum(1 for r in reviews if r.status == OfficerDecisionState.REQUEST_REVISION.value)

        decisions = [r.officer_decision for r in reviews if r.officer_decision]
        overrides = sum(1 for d in decisions if d.is_override)
        dec_count = len(decisions)

        override_rate = round((overrides / dec_count) * 100, 2) if dec_count > 0 else 0.0
        agreement_rate = round(100.0 - override_rate, 2) if dec_count > 0 else 100.0

        avg_cands = round(sum(len(r.candidates) for r in reviews) / total, 1) if total > 0 else 0.0
        avg_v_items = round(sum(len(r.verification_items) for r in reviews) / total, 1) if total > 0 else 0.0

        # Recent 5 reviews
        recent = cls.list_reviews(db=db, limit=5, offset=0).reviews

        return DashboardStatsResponse(
            total_reviews=total,
            pending_reviews=pending,
            under_review=under_review,
            accepted=accepted,
            rejected=rejected,
            needs_verification=needs_ver,
            request_revision=req_rev,
            agreement_rate=agreement_rate,
            override_rate=override_rate,
            avg_candidates_inspected=avg_cands,
            avg_verification_items=avg_v_items,
            recent_reviews=recent,
        )
