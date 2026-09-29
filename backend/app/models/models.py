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
