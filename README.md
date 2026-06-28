# ClinIQ — Autonomous Clinical Intelligence Platform

A locally deployable clinical intelligence platform that allows non-technical 
clinical users to ask questions in plain English and receive data-driven answers 
from a synthetic EHR database and clinical document knowledge base.

## Architecture

- **Data Layer**: Synthea synthetic EHR → Delta Lake (Parquet) → dbt on DuckDB
- **Semantic Layer**: PostgreSQL + pgvector for RAG over clinical guidelines
- **Agent**: LangGraph stateful graph with MCP tool servers
- **Inference**: Ollama (local LLMs, no data leaves machine)
- **Tracking**: MLflow experiment tracking with benchmark evaluation
- **API**: FastAPI backend + Streamlit frontend
- **Orchestration**: Airflow running in Docker

## Setup

```powershell
git clone git@github.com:yourusername/cliniq.git
cd cliniq
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd docker && docker compose up -d postgres
python pipeline\run_phase1.py
```

## Status

- [x] Phase 0 — Project setup
- [ ] Phase 1A — Data generation and raw storage
- [ ] Phase 1B — dbt transformation layer
- [ ] Phase 1C — Great Expectations + Airflow
- [ ] Phase 2 — Vector store and RAG
- [ ] Phase 3 — Agent core
- [ ] Phase 4 — Evaluation and MLflow
- [ ] Phase 5 — API and frontend