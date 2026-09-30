"""
ORM models for PS26108.

Design notes:
- `Standard` stores authoritative fields from seed dataset.
- Derived facets (application, materials, technical_parameters) are kept
  separate with a `facet_source` field to mark them as non-authoritative.
- `Reference` stores known/candidate graph edges between standards.
- `QCO` stores regulatory order metadata; individual standard links are in
  `QCOStandardLink`.
- `Query` and `Recommendation` support the recommendation pipeline.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON, Date,
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


# ====================================================================
# STANDARD
# ====================================================================
class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    standard_id = Column(String(128), unique=True, nullable=False, index=True,
                         comment="Seed identifier, e.g. 'is_269'")
    is_number = Column(String(256), nullable=False, index=True,
                       comment="IS number as printed, e.g. 'IS 269'")
    is_number_normalized = Column(String(256), nullable=False, index=True,
                                  comment="Normalized form for matching, e.g. 'IS269'")
    title = Column(Text, nullable=False)
    sector = Column(String(256), nullable=True)
    status = Column(String(128), nullable=False, default="unknown",
                    comment="E.g. scheme1_listed_source_record, current, superseded, withdrawn")
    scheme = Column(String(128), nullable=True)
    qco_or_regulatory_order = Column(Text, nullable=True,
                                     comment="QCO order name from seed (for cross-reference)")
    certification_status = Column(Text, nullable=True,
                                  comment="Raw certification status string from seed")
    year = Column(Integer, nullable=True,
                  comment="Year extracted from IS number, if present")
    superseded_by = Column(String(256), nullable=True)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(128), nullable=True)
    source_as_of = Column(Date, nullable=True)

    # Derived facets — NOT authoritative scope text
    application = Column(Text, nullable=True)
    materials = Column(JSON, nullable=True, comment="List of material strings")
    product_aliases = Column(JSON, nullable=True, comment="List of alias strings")
    technical_parameters = Column(JSON, nullable=True, comment="List of parameter strings")
    facet_source = Column(Text, nullable=True,
                          comment="Provenance of derived facets, e.g. 'derived from title'")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # Relationships
    outgoing_references = relationship(
        "Reference", foreign_keys="Reference.source_standard_id",
        back_populates="source_standard", lazy="select",
    )
    incoming_references = relationship(
        "Reference", foreign_keys="Reference.target_standard_id",
        back_populates="target_standard", lazy="select",
    )
    qco_links = relationship("QCOStandardLink", back_populates="standard", lazy="select")
    recommendations = relationship("Recommendation", back_populates="standard", lazy="select")

    def __repr__(self):
        return f"<Standard {self.is_number} – {self.title[:40]}>"


# ====================================================================
# REFERENCE (graph edges between standards)
# ====================================================================
class Reference(Base):
    __tablename__ = "references"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False, index=True)
    target_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False, index=True)
    reference_type = Column(String(128), nullable=False,
                            comment="E.g. safety/particular_requirements, general_safety_framework")
    evidence_source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    confidence = Column(String(64), nullable=True, default="candidate",
                        comment="verified | candidate | inferred")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source_standard = relationship("Standard", foreign_keys=[source_standard_id],
                                   back_populates="outgoing_references")
    target_standard = relationship("Standard", foreign_keys=[target_standard_id],
                                   back_populates="incoming_references")

    def __repr__(self):
        return f"<Reference {self.source_standard_id} → {self.target_standard_id} ({self.reference_type})>"


# ====================================================================
# QCO (Quality Control Order)
# ====================================================================
class QCO(Base):
    __tablename__ = "qco_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qco_id = Column(String(64), unique=True, nullable=False, index=True)
    order_name = Column(Text, nullable=False)
    status = Column(String(128), nullable=False, default="needs_current_order_resolution",
                    comment="needs_current_order_resolution | active | superseded | unknown")
    effective_date = Column(Date, nullable=True)
    notifying_authority = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(128), nullable=True)
    as_of_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    linked_seed_standards_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    standard_links = relationship("QCOStandardLink", back_populates="qco", lazy="select")

    def __repr__(self):
        return f"<QCO {self.qco_id} – {self.order_name[:40]}>"


class QCOStandardLink(Base):
    """Join table linking QCO orders to specific standards."""
    __tablename__ = "qco_standard_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qco_id = Column(Integer, ForeignKey("qco_orders.id"), nullable=False, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False, index=True)

    qco = relationship("QCO", back_populates="standard_links")
    standard = relationship("Standard", back_populates="qco_links")


# ====================================================================
# QUERY (user input)
# ====================================================================
class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_text = Column(Text, nullable=False)
    input_type = Column(String(64), nullable=True,
                        comment="text | pdf | docx | gem_spec")
    language = Column(String(32), nullable=True, default="en")
    product = Column(Text, nullable=True)
    application = Column(Text, nullable=True)
    materials = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    cited_standards = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    recommendations = relationship("Recommendation", back_populates="query", lazy="select")

    def __repr__(self):
        return f"<Query {self.id} – {self.raw_text[:40]}>"


# ====================================================================
# RECOMMENDATION
# ====================================================================
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False, index=True)
    retrieval_method = Column(String(64), nullable=True,
                              comment="bm25 | vector | hybrid")
    relevance_score = Column(Float, nullable=True)
    matched_signals = Column(JSON, nullable=True,
                             comment="List of signal strings")
    version_status = Column(String(128), nullable=True)
    qco_status = Column(String(128), nullable=True)
    relationship_type = Column(String(128), nullable=True,
                               comment="primary | normative_reference | related")
    evidence = Column(Text, nullable=True)
    reviewer_decision = Column(String(64), nullable=True,
                               comment="accepted | rejected | pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    query = relationship("Query", back_populates="recommendations")
    standard = relationship("Standard", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation Q{self.query_id} → S{self.standard_id} ({self.relevance_score})>"


# ====================================================================
# PHASE 7: REVIEW & DECISION-SUPPORT MODELS
# ====================================================================

class Review(Base):
    """Persistent Human-in-the-Loop review session for a procurement query."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), unique=True, nullable=False, index=True,
                       comment="Human-readable ID e.g. 'REV-000001'")
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=True, index=True)
    raw_text = Column(Text, nullable=False)
    input_type = Column(String(64), nullable=True, default="text")
    procurement_requirements = Column(JSON, nullable=True,
                                      comment="Extracted ProcurementRequirements as JSON")
    status = Column(String(64), nullable=False, default="PENDING", index=True,
                    comment="PENDING | UNDER_REVIEW | ACCEPTED | REJECTED | NEEDS_VERIFICATION | REQUEST_REVISION")
    selected_candidate_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    candidates = relationship("ReviewCandidate", back_populates="review",
                              cascade="all, delete-orphan", order_by="ReviewCandidate.retrieval_rank")
    verification_items = relationship("VerificationItem", back_populates="review",
                                      cascade="all, delete-orphan")
    officer_decision = relationship("OfficerDecision", back_populates="review",
                                    uselist=False, cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="review",
                                cascade="all, delete-orphan", order_by="AuditEvent.id")
    officer_evidences = relationship("OfficerEvidence", back_populates="review",
                                     cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Review {self.review_id} – {self.status}>"


class ReviewCandidate(Base):
    """Candidate standard evaluated for a specific review."""
    __tablename__ = "review_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    standard_id = Column(String(128), nullable=False, index=True)
    is_number = Column(String(256), nullable=False)
    title = Column(Text, nullable=False)
    sector = Column(String(256), nullable=True)
    application = Column(Text, nullable=True)
    materials = Column(JSON, nullable=True)
    technical_parameters = Column(JSON, nullable=True)

    # Retrieval signals
    retrieval_rank = Column(Integer, nullable=False)
    reranker_score = Column(Float, nullable=True)
    rrf_score = Column(Float, nullable=True)
    retrieval_method = Column(String(64), nullable=True, default="hybrid_cross_encoder")

    # Phase 6 & 6.1 signals
    requirement_coverage = Column(JSON, nullable=True,
                                comment="Facet-by-facet requirement coverage with MATCH/PARTIAL/UNKNOWN/CONFLICT")
    gaps = Column(JSON, nullable=True,
                  comment="List of detected gaps with category and severity")

    # Regulatory signals
    standard_status = Column(String(128), nullable=True, default="NEEDS_VERIFICATION")
    qco_status = Column(String(128), nullable=True, default="NOT_FOUND_IN_SEED")
    qco_ids = Column(JSON, nullable=True)
    order_names = Column(JSON, nullable=True)
    effective_date = Column(String(64), nullable=True)
    authority = Column(String(256), nullable=True)

    # Composite AI recommendation state
    ai_recommendation_state = Column(String(64), nullable=False, default="REVIEW_REQUIRED",
                                     comment="RECOMMENDED_FOR_REVIEW | REVIEW_REQUIRED | POTENTIALLY_RELEVANT | INSUFFICIENT_EVIDENCE")
    notes = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True, comment="List of verifiable EvidenceItems")
    normative_references = Column(JSON, nullable=True, comment="Linked graph standard references")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="candidates")

    def __repr__(self):
        return f"<ReviewCandidate R{self.review_id} → {self.is_number} Rank #{self.retrieval_rank}>"


class VerificationItem(Base):
    """Specific verification task derived from gaps and regulatory claims."""
    __tablename__ = "verification_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("review_candidates.id"), nullable=True, index=True)
    standard_id = Column(String(128), nullable=True, index=True)

    item_key = Column(String(128), nullable=False,
                      comment="Unique key e.g. 'qco_gazette_verification', 'param_voltage'")
    title = Column(String(256), nullable=False)
    category = Column(String(128), nullable=False,
                      comment="REGULATORY | STANDARD_STATUS | TECHNICAL_PARAMETER | MATERIAL | APPLICATION")
    system_state = Column(String(64), nullable=False, default="NEEDS_VERIFICATION")
    officer_state = Column(String(64), nullable=False, default="UNVERIFIED",
                           comment="UNVERIFIED | VERIFIED | CONFLICTING | NOT_APPLICABLE")
    is_regulatory = Column(Boolean, nullable=False, default=False)
    system_evidence = Column(JSON, nullable=True)
    officer_evidence_reference = Column(Text, nullable=True,
                                        comment="Mandatory reference for regulatory items when verified")
    officer_note = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="verification_items")

    def __repr__(self):
        return f"<VerificationItem {self.item_key}: {self.officer_state}>"


class OfficerDecision(Base):
    """Final decision recorded by an authorized procurement officer."""
    __tablename__ = "officer_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), unique=True, nullable=False, index=True)
    state = Column(String(64), nullable=False,
                   comment="ACCEPTED | REJECTED | NEEDS_VERIFICATION | REQUEST_REVISION")
    selected_candidate_id = Column(Integer, nullable=True)
    selected_standard_id = Column(String(128), nullable=True)
    selected_is_number = Column(String(256), nullable=True)

    ai_recommendation_state = Column(String(64), nullable=True)
    is_override = Column(Boolean, nullable=False, default=False,
                          comment="True if officer decision diverges from AI recommendation")
    rejection_reason = Column(String(128), nullable=True,
                              comment="WRONG_PRODUCT | WRONG_SECTOR | INSUFFICIENT_TECHNICAL_COVERAGE | PARAMETER_CONFLICT | OUTDATED_STANDARD | REGULATORY_MISMATCH | INSUFFICIENT_EVIDENCE | DUPLICATE_STANDARD | OTHER")
    rejection_note = Column(Text, nullable=True)
    officer_id = Column(String(128), nullable=True, default="officer_001")
    officer_role = Column(String(128), nullable=True, default="Procurement Officer")
    decision_summary = Column(Text, nullable=True)
    supporting_evidence_references = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="officer_decision")

    def __repr__(self):
        return f"<OfficerDecision R{self.review_id}: {self.state} (Override={self.is_override})>"


class AuditEvent(Base):
    """Append-only audit trail event for every review interaction."""
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True,
                        comment="REVIEW_CREATED | REVIEW_OPENED | CANDIDATE_SELECTED | CANDIDATE_COMPARISON | EVIDENCE_OPENED | VERIFICATION_CHANGED | DECISION_MADE | DECISION_MODIFIED | REVIEW_REOPENED")
    previous_state = Column(String(64), nullable=True)
    new_state = Column(String(64), nullable=True)
    actor = Column(String(128), nullable=False, default="officer")
    actor_role = Column(String(128), nullable=True, default="Procurement Officer")
    reason = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="audit_events")

    def __repr__(self):
        return f"<AuditEvent R{self.review_id}: {self.event_type} at {self.timestamp}>"


class OfficerEvidence(Base):
    """Officer-provided external evidence records, stored separately from AI seed evidence."""
    __tablename__ = "officer_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    candidate_id = Column(Integer, nullable=True)
    verification_item_id = Column(Integer, ForeignKey("verification_items.id"), nullable=True)
    evidence_type = Column(String(64), nullable=False,
                          comment="GAZETTE_ORDER | BIS_PORTAL | MINISTRY_CIRCULAR | TECHNICAL_SPEC | OTHER")
    reference_id = Column(String(256), nullable=False)
    url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    uploaded_by = Column(String(128), nullable=False, default="officer")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="officer_evidences")

    def __repr__(self):
        return f"<OfficerEvidence R{self.review_id}: {self.evidence_type} {self.reference_id}>"

