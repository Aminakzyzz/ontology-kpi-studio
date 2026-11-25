# Ontology KPI Studio

Local-first semantic analytics for exploring operational data through a governed ontology.

The project combines a conversational dashboard workflow with an ontology-backed data layer. It ships with a self-contained SQLite dataset and a deterministic query path, so it runs without Databricks, enterprise credentials, or model API keys. NVIDIA Auto Ontology is supported as an optional external semantic service through an adapter boundary.

## Features

- Local SQLite demo dataset for delivery, service quality, and customer metrics
- Versioned domain ontology describing metrics, tables, and relationships
- Natural-language query presets with transparent generated SQL
- Interactive dashboard cards and ontology graph
- Conversation persistence in the browser
- Optional NVIDIA Auto Ontology integration point, isolated from the UI

## Architecture

```text
React UI
   │
   ├── chat, dashboard, ontology explorer
   │
FastAPI application
   ├── local semantic adapter (included)
   ├── optional Auto Ontology adapter
   └── read-only SQLite executor
   │
SQLite sample data + ontology YAML
```

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000

cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend proxies `/api` to the local backend.

## Optional NVIDIA Auto Ontology

Auto Ontology is not bundled or started automatically. Its ingestion pipeline may inspect schema metadata and sample values; use only data you are permitted to process. Set `AUTO_ONTOLOGY_URL` to an independently deployed instance once it is available. The adapter intentionally has no credentials in this repository.

`GET /api/integration` reports whether the application is running solely on its included local semantic adapter or has been configured for an external semantic service. The UI never receives a semantic-service credential.

## Repository layout

- `backend/` FastAPI service and local semantic adapter
- `frontend/` React/Vite UI
- `ontology/` portable domain definitions
- `data/` generated local SQLite demo database
- `latex/` technical report scaffold

## Data safety

The included application executes only read-only SQL against the generated local database. It contains no Mercedes-Benz, Databricks, or previously used API credentials.

