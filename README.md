# PS26108 — AI-Powered Indian Standards Recommendation Engine

> **Problem Statement PS26108**
>
> AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications.
> **Phase 7 — Human-in-the-Loop Officer Review & Decision-Support System with Production UI**

---

## 1. Overview & Core Philosophy

This system accepts procurement tender technical schedules, free-text specifications, or product descriptions and produces evidence-backed candidate Indian Standards (BIS Scheme-1) with Quality Control Order (QCO) regulatory verification and an interactive Officer Review Workspace.

### Non-Negotiable Separation of Concerns
The system maintains strict semantic separation:
$$\text{Retrieval Relevance} \neq \text{Requirement Coverage} \neq \text{Recommendation State} \neq \text{QCO Association} \neq \text{Legal Applicability} \neq \text{Officer Decision}$$

The system operates as **authorized decision support**, not autonomous legal approval. The procurement officer is the final decision-maker, supported by immutable audit trails, provenance evidence spans, and gap-grounded verification checklists.

---

## 2. End-to-End Pipeline Architecture

```
PROCUREMENT TENDER QUERY
        ↓
[Phase 3] REQUIREMENT EXTRACTION ENGINE (Product, Sector, Application, Materials, Parameters + Spans)
        ↓
[Phase 4] HYBRID RETRIEVAL (BM25 Sparse + all-MiniLM-L6-v2 Dense 384-d Vector Indexing)
        ↓
[Phase 4] CROSS-ENCODER RERANKING (ms-marco-MiniLM-L-6-v2 Neural Scoring)
        ↓
[Phase 5] KNOWLEDGE GRAPH & TRAVERSAL (128 Nodes, 93 Edges — Standard Relationships & QCO Links)
        ↓
[Phase 5.1] REGULATORY RESOLUTION (Scheme-1 Seed QCO Association & Currency Status)
        ↓
[Phase 6 & 6.1] EVIDENCE-BACKED RECOMMENDATION (Coverage Matrix + Gap Detection Engine)
        ↓
[Phase 7] OFFICER REVIEW & DECISION WORKSPACE (Interactive 3-Column UI & Verification Checklist)
        ↓
[Phase 7] OFFICER DECISION & OVERRIDE HANDLING (ACCEPT / REJECT / VERIFY / REVISION)
        ↓
[Phase 7] IMMUTABLE AUDIT TRAIL (Append-Only Event Ledger)
```

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| **Database** | PostgreSQL / SQLite local fallback (`data/ps26108_local.db`) |
| **Information Retrieval** | Rank-BM25 Lexical Indexing + Dense SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Neural Reranking** | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| **Knowledge Graph** | NetworkX directed multigraph with depth-bounded BFS |
| **Frontend UI** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, TanStack Query |
| **Deployment** | Docker multi-stage build, Docker Compose, Uvicorn |

---

## 4. Key Screens in Production Web UI

1. **Operational Dashboard:** Live counters of reviews (Total, Pending, Under Review, Accepted, Rejected, Needs Verification) and recent review queue.
2. **New Procurement Query:** Tender technical schedule input, preset ground truth examples, and real pipeline stage progress tracking.
3. **Review Workspace (3-Column Layout):**
   - *Left Column:* Extracted procurement requirements with exact evidence spans for provenance.
   - *Center Column:* Top-10 retrieved candidate standards, coverage badges (`MATCH`, `PARTIAL_MATCH`, `UNKNOWN`, `CONFLICT`), gap counts, and regulatory status.
   - *Right Column:* Dynamic gap-grounded officer verification checklist, authoritative evidence inspector, and audit history.
   - *Action Controls:* Record officer decision with structured rejection reason codes, override detection, or review reopening.
4. **Side-by-Side Comparison Matrix:** Compare 2 to 3 candidate standards across requirement facets, regulatory QCO orders, and gap burdens.
5. **Candidate Detail View:** Deep-dive accordion view across standard scope, retrieval signals, parameter coverage, regulatory citations, and evidence records.
6. **Review Queue & History:** Filterable by lifecycle status, date, sector, and free-text search.

---

## 5. Quick Start (Local Development)

### 1. Backend

```bash
# Clone repository and activate venv
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Ingest authoritative seed dataset
python scripts/ingest_seed.py

# Launch FastAPI backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` (development server with proxy) or `http://localhost:8000` (production mode).

---

## 6. Docker Deployment

```bash
# Launch PostgreSQL and unified FastAPI + React container
docker-compose up --build -d

# Verify system health
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
```

---

## 7. Testing & Verification

Run the entire test suite across all phases:
```bash
pytest tests/unit/ -v
```

Run Phase 7 evaluation and integrity scripts:
```bash
python scripts/evaluate_review_workflow.py
python scripts/review_integrity.py
```

---

## 8. Disclaimer
*This system is an AI-powered decision-support prototype. Regulatory applicability, Quality Control Order enforcement dates, and final procurement decisions require authorized human verification against official Gazette notifications.*
