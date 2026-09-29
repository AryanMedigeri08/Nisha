# PS26108 — AI-Powered Indian Standards Recommendation Engine

> **SIH 2026 Problem Statement PS26108**
>
> AI-Powered Recommendation Engine for Identifying Applicable Indian Standards
> for Procurement Specifications.

## Overview

This system accepts procurement tender text, PDF/DOCX tender documents, or
free-text product descriptions and produces:

1. Extracted procurement requirements
2. Applicable primary Indian Standards (IS)
3. Related/allied/normative standards
4. Relevance ranking with evidence
5. Version/status information
6. QCO/certification information
7. Specification-gap suggestions
8. A procurement-ready report

The system is a **decision-support/co-pilot**. The LLM is never the source of
truth for IS numbers, standard status, versions, supersession, or QCO/legal
status. These always come from structured data.

## Project Structure

```
/
├── PS26108_Seed_Dataset_v1.xlsx   # Authoritative seed corpus
├── data/
│   ├── raw/                       # Raw data files
│   ├── processed/                 # Processed data + validation reports
│   ├── synthetic/                 # Generated training queries
│   ├── evaluation/                # Gold benchmark data
│   └── embeddings/                # Vector embeddings
├── scripts/
│   ├── ingest_seed.py             # Seed dataset ingestion
│   ├── validate_seed.py           # Post-ingestion validation
│   ├── generate_synthetic.py      # Synthetic query generator
│   ├── build_embeddings.py        # Embedding builder
│   ├── build_graph.py             # Knowledge graph builder
│   └── evaluate.py                # Evaluation runner
├── backend/
│   ├── app/
│   │   ├── api/                   # FastAPI routes
│   │   ├── core/                  # Config, database
│   │   ├── models/                # ORM models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic
│   │   └── main.py                # FastAPI application
│   ├── extraction/                # Requirement extraction
│   ├── retrieval/                 # BM25 + vector retrieval
│   ├── ranking/                   # Cross-encoder reranking
│   ├── graph/                     # Knowledge graph
│   ├── qco/                       # QCO/version engine
│   ├── gaps/                      # Specification gap detection
│   └── explanation/               # Evidence engine
├── frontend/                      # React + Vite + Tailwind
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run seed ingestion
python scripts/ingest_seed.py

# 3. Run validation
python scripts/validate_seed.py

# 4. Run tests
pytest tests/ -v
```

## Technology Stack

| Layer         | Technology                           |
| ------------- | ------------------------------------ |
| Backend       | Python, FastAPI, Pydantic, SQLAlchemy|
| Database      | PostgreSQL (SQLite for Phase 1)      |
| Vector Search | pgvector                             |
| Lexical Search| BM25                                 |
| Embeddings    | Sentence Transformers                |
| Reranking     | Cross-encoder                        |
| Graph         | NetworkX / PostgreSQL references     |
| Document Parse| PyMuPDF, pdfplumber, python-docx     |
| Frontend      | React, Vite, Tailwind CSS            |
| Reports       | ReportLab, python-docx               |

## Seed Dataset

The seed dataset (`PS26108_Seed_Dataset_v1.xlsx`) contains:

- **91 Indian Standards** across 22 sectors
- **3 reference edges** (normative/safety relationships)
- **35 QCO orders** with standard linkages
- Source: BIS Scheme-I page

All facets (application, materials, technical parameters) are derived from
titles and sectors — they are **not** authoritative scope text.

## Development Phases

1. Project structure + configuration ✅
2. Seed dataset ingestion + validation ✅
3. Database/schema ✅
4. Synthetic dataset generator
5. Requirement extraction
6. Hybrid retrieval
7. Ranking/reranking
8. Knowledge graph
9. Version/status engine
10. QCO/certification engine
11. Specification gap detection
12. Evidence/explanation layer
13. Evaluation framework
14. FastAPI backend
15. Frontend
16. End-to-end integration
17. Demo optimization
