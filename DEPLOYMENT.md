# PS26108 — Production Deployment & Architecture Guide

This document describes the production deployment architecture for **PS26108 (AI-Powered Indian Standards Recommendation Engine)**, decoupled across **Vercel** (Frontend) and **Render** (FastAPI Backend + PostgreSQL Database).

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   VERCEL FRONTEND                      │
│         React 18 + TypeScript + Vite + Tailwind        │
│             (https://<your-app>.vercel.app)            │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS (REST API & CORS)
                           │ VITE_API_URL
                           ▼
┌────────────────────────────────────────────────────────┐
│                RENDER FASTAPI BACKEND                  │
│       Python 3.11 + Uvicorn + ML Pipelines (CPU)       │
│      (https://<your-backend-name>.onrender.com)        │
│          • PORT dynamically bound by Render            │
│          • Lazy-loaded SentenceTransformer & Reranker  │
│          • Liveness & Readiness Probes (/health)       │
└──────────────────────────┬─────────────────────────────┘
                           │ TCP / PostgreSQL Wire Protocol
                           │ DATABASE_URL
                           ▼
┌────────────────────────────────────────────────────────┐
│               RENDER POSTGRESQL DATABASE               │
│                     `ps26108-db`                       │
│    • 91 Scheme-1 Standards • 35 QCO Orders             │
│    • Persistent Reviews, Verifications & Audit Events  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Render Deployment (FastAPI Backend)

### Step 1: Create or Connect Render PostgreSQL Database
1. In the Render Dashboard, create a **PostgreSQL** database named `ps26108-db`.
2. Copy the **Internal Database URL** (for services running on Render) or **External Database URL**.

### Step 2: Deploy Backend Web Service
1. In Render, select **New +** > **Web Service**.
2. Connect your GitHub repository (`Nisha`).
3. Configure service settings:
   - **Name:** `ps26108-backend` (or your chosen name)
   - **Environment:** `Docker` (or `Python 3`)
   - **Region:** Same region as your database (e.g. `Oregon` or `Frankfurt`)
   - **Branch:** `main`
   - **Plan:** Free or Starter (Minimum 1GB RAM recommended)
4. Set **Environment Variables** in Render:

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@dpg-xxxx-a:5432/ps26108_db` | Render PostgreSQL internal connection string |
| `FRONTEND_URL` | `https://<your-vercel-app>.vercel.app` | Allowed CORS origin from Vercel |
| `ENVIRONMENT` | `production` | Operational mode |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder reranker model |
| `PYTHONPATH` | `/app` | Python module resolution path |

5. **Health Check Path:** Set `/health` in Render service settings.
6. Click **Create Web Service**. Render will build the Docker container and start Uvicorn on the dynamic `${PORT}`.

---

## 3. Vercel Deployment (React Frontend)

### Step 1: Import Project in Vercel
1. In the Vercel Dashboard, click **Add New...** > **Project**.
2. Select your repository (`Nisha`).
3. Set **Framework Preset:** `Vite`.
4. Set **Root Directory:** `frontend`
5. Build and Output Settings:
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

### Step 2: Configure Environment Variables in Vercel

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://ps26108-backend.onrender.com` | Base URL of your deployed Render backend |

6. Click **Deploy**. Vercel will build the frontend and serve it with automatic HTTPS and SPA routing rules ([`vercel.json`](file:///c:/Users/naiky/OneDrive/Desktop/Projects/NISHA/Nisha/frontend/vercel.json)).

### Step 3: Link Vercel URL back to Render Backend
Once Vercel assigns your production URL (e.g. `https://ps26108.vercel.app`):
1. Go to your Render Backend settings.
2. Update the `FRONTEND_URL` environment variable to `https://ps26108.vercel.app`.
3. Save changes (Render will perform a zero-downtime redeploy).

---

## 4. Local Development Setup

Run both services locally:

### 1. Start Backend:
```bash
# In project root with active venv:
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 5. System Health & Verification

- Backend Liveness: `GET https://<render-backend-url>/health`
- Backend Readiness: `GET https://<render-backend-url>/health/ready`
- OpenAPI Documentation: `GET https://<render-backend-url>/docs`
