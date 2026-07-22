# MIRA — Medical Intelligence and Reasoning Agent

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-6C5CE7)
![LangChain](https://img.shields.io/badge/LangChain-LLM_Orchestration-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM_Inference-F55036)
![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-Embeddings-FFD21E?logo=huggingface&logoColor=000000)
![MCP](https://img.shields.io/badge/MCP-Tool_Servers-5B5BD6)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics_Warehouse-FFF000?logo=duckdb&logoColor=000000)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-Lakehouse-00ADD8?logo=databricks&logoColor=white)
![Apache Parquet](https://img.shields.io/badge/Apache_Parquet-Columnar_Storage-50ABF1?logo=apacheparquet&logoColor=white)
![PyArrow](https://img.shields.io/badge/PyArrow-Data_Processing-326CE5)
![dbt](https://img.shields.io/badge/dbt-Analytics_Engineering-FF694B?logo=dbt&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-Orchestration-017CEE?logo=apacheairflow&logoColor=white)
![Great Expectations](https://img.shields.io/badge/Great_Expectations-Data_Quality-FC5424)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Transformation-150458?logo=pandas&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Clinical_Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?logo=plotly&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-Evaluation_%26_Tracing-0194E2?logo=mlflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized_Services-2496ED?logo=docker&logoColor=white)
![Synthea](https://img.shields.io/badge/Synthea-Synthetic_EHR_Data-2E8B57)

**A production-inspired clinical intelligence platform that combines healthcare data engineering, Text-to-SQL, retrieval-augmented generation, and agentic reasoning to answer analytics and policy questions in natural language.**

> MIRA is a personal engineering project built with synthetic Synthea data. It is not a medical device and must not be used for clinical decision-making.

---

## Key Results

| Metric | Result |
|---|---:|
| End-to-end benchmark | **48/50 questions passed — 96.0% overall accuracy** |
| Core reasoning benchmark | **47/47 passed — 100% across SQL, RAG, and hybrid workflows** |
| Text-to-SQL accuracy | **25/25 — 100%** |
| Clinical RAG accuracy | **15/15 — 100%** |
| Hybrid SQL + RAG accuracy | **7/7 — 100%** |
| Benchmark retries | **0 across 50 evaluated questions** |
| Synthetic patient population | **5,760 patients** |
| Clinical encounters modeled | **11,722 encounters** |
| Active medication records analyzed | **14,911 records** |
| Abnormal laboratory results available for analysis | **178,544 results** |
| Curated clinical knowledge base | **24 guidelines, policies, and protocols** |
| Analytics engineering layer | **12 dbt models** across staging, marts, and metrics |
| Agent workflow | **9 specialized LangGraph nodes** |
| Data-quality coverage | **Great Expectations suites + dbt structural and domain tests** |

The benchmark evaluates exact numerical answers, tolerant numerical comparisons, categorical ranking, source-grounded clinical responses, hybrid data-and-policy reasoning, chart generation, validation status, retries, and latency. Core reasoning achieved perfect accuracy; the two remaining benchmark misses are isolated to visualization-output equivalence and chart-selection behavior rather than SQL, retrieval, or hybrid reasoning.

---

## Why This Project Exists

Healthcare data is fragmented across two fundamentally different information systems:

1. **Structured clinical data** such as patients, encounters, laboratory results, medications, costs, and chronic-condition indicators.
2. **Unstructured clinical knowledge** such as care policies, disease-management guidelines, escalation protocols, and discharge procedures.

Answering a real operational question often requires both. A care analyst may need to know not only **how many patients meet a clinical criterion**, but also **what the relevant guideline recommends doing next**.

Traditional analytics workflows require SQL expertise, repeated handoffs between technical and clinical teams, manual document searches, and limited traceability. Generic chatbots solve none of those problems reliably because they are disconnected from governed data, validated metrics, and source documents.

**MIRA's thesis:** a useful clinical intelligence system should route each question to the correct data source, generate and validate the analysis, retrieve supporting clinical knowledge, expose its evidence, and return one understandable answer.

MIRA therefore integrates the full workflow:

- ingestion and lakehouse-style storage,
- analytics engineering and dimensional modeling,
- data-quality validation,
- semantic schema retrieval,
- Text-to-SQL generation and execution,
- clinical RAG,
- hybrid SQL + document reasoning,
- result validation and retry handling,
- visualization,
- API delivery,
- query history,
- MLflow evaluation and traceability.

---

## System Architecture

```text
                         Natural-Language Question
                                    │
                                    ▼
                         Streamlit Clinical UI
                                    │
                                    ▼
                            FastAPI Service
                                    │
                                    ▼
                          LangGraph Orchestrator
                                    │
                ┌───────────────────┼────────────────────┐
                │                   │                    │
                ▼                   ▼                    ▼
        Intent Classification   Data Query          Document Query
                │                   │                    │
                │          Semantic Schema Search       │
                │                   │                    │
                │             Text-to-SQL               │
                │                   │                    │
                │              SQL Validator      Hybrid Retrieval
                │                   │              Vector + Keyword
                │                   ▼                    │
                │          Database MCP Server          ▼
                │                   │             Vector MCP Server
                │                   ▼                    │
                │          DuckDB Analytics      PostgreSQL + pgvector
                │              Warehouse                 │
                └───────────────────┴────────────────────┘
                                    │
                                    ▼
                     Response Synthesis + Validation
                                    │
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                       Answer    Plotly      Evidence
                                  Chart     SQL + Sources
                                    │
                                    ▼
                         MLflow Trace and History
```

### Data platform flow

```text
Synthea CSV Data
       │
       ▼
Delta Lake / Parquet
       │
       ▼
DuckDB Raw Layer
       │
       ▼
dbt Staging Models
       │
       ▼
dbt Dimensional Marts
       │
       ▼
dbt Metrics Models
       │
       ├──────────────► Automated Schema Registry
       │
       ├──────────────► Great Expectations + dbt Tests
       │
       └──────────────► Text-to-SQL Agent
```

---

## What MIRA Can Do

### 1. Structured clinical analytics through Text-to-SQL

MIRA converts plain-English analytical questions into executable DuckDB SQL. It does not inject the entire warehouse schema into every prompt. Instead, it embeds documented table descriptions and retrieves only the most relevant schema context for each question.

Examples:

- How many patients have diabetes?
- What percentage of patients are female?
- Which chronic condition is most prevalent?
- What is the average A1c among diabetic patients?
- Which medication class is prescribed most frequently?
- What are the five most frequently prescribed medications?

The SQL workflow includes:

- intent classification,
- semantic schema retrieval,
- prompt-grounded SQL generation,
- execution through a database MCP server,
- result validation,
- retry support,
- natural-language synthesis,
- optional chart generation.

### 2. Clinical RAG over policies, guidelines, and protocols

The knowledge base contains **24 curated clinical documents** across:

- diabetes,
- heart failure,
- hypertension,
- chronic kidney disease,
- COPD,
- asthma,
- stroke prevention,
- anticoagulation,
- infection control,
- medication reconciliation,
- hypoglycemia management,
- abnormal-lab escalation,
- ICU escalation,
- discharge and care-transition procedures.

Documents are chunked, embedded with `all-MiniLM-L6-v2`, and stored in PostgreSQL with pgvector. Retrieval combines:

- vector similarity search,
- PostgreSQL full-text keyword search,
- Reciprocal Rank Fusion,
- source metadata and relevance scores.

This hybrid retrieval design is more resilient than vector-only search for clinical abbreviations, named policies, and exact medical terminology.

### 3. Hybrid reasoning across data and clinical knowledge

Hybrid questions trigger both analytical and retrieval paths before a unified response is synthesized.

Example:

> How many diabetic patients have A1c values above 8, and what does the blood-glucose monitoring protocol recommend following hypoglycemia?

MIRA independently:

1. generates and executes the patient-level SQL,
2. retrieves the relevant protocol passages,
3. validates the structured result,
4. combines the numerical finding with source-grounded recommendations,
5. exposes the SQL and source context to the user.

This is the project's central capability: **reasoning across governed enterprise data and unstructured domain knowledge in one workflow.**

### 4. Transparent and traceable responses

The application exposes more than a final paragraph. Depending on the query, users can inspect:

- generated SQL,
- structured query results,
- validation status,
- retrieved document names and passages,
- chart type and visualization,
- execution latency,
- retry count,
- MLflow run metadata,
- historical queries.

This makes the system easier to debug, evaluate, and trust than a black-box chatbot.

---

## Data Engineering and Analytics Engineering

### Lakehouse-style storage

Synthea-generated clinical data is converted into Delta Lake and Parquet assets for reproducible local analytics. DuckDB provides a lightweight analytical warehouse without requiring an external cloud platform.

### dbt transformation layer

The project contains **12 dbt models**:

| Layer | Models | Purpose |
|---|---:|---|
| Staging | 5 | Standardize patients, encounters, conditions, observations, and medications |
| Marts | 4 | Build patient, encounter, laboratory, and medication analytical models |
| Metrics | 3 | Precompute population, condition-prevalence, and encounter-volume metrics |

Key modeled assets include:

- `dim_patients` — one row per patient with demographics, chronic-condition flags, latest A1c, and latest BMI,
- `fact_encounters` — encounter timing, class, diagnosis, duration, claims, and patient attributes,
- `fact_lab_results` — LOINC-aligned laboratory and vital results with reference-range abnormality flags,
- `fact_medications` — medication records enriched with RxNorm codes, mapped drug classes, active status, and patient conditions,
- reusable metrics for population summaries, disease prevalence, and encounter trends.

### Healthcare terminology enrichment

Seed-based mappings enrich raw records with:

- SNOMED/condition group mappings,
- LOINC normal ranges,
- RxNorm medication class patterns.

These mappings transform low-level codes into business-friendly analytical concepts and allow the agent to answer questions such as disease prevalence, abnormal-lab counts, and medication-class frequency without complex ad hoc joins.

### Data-quality controls

Quality checks operate at multiple layers:

- Great Expectations validation suites for core patient, encounter, and laboratory datasets,
- dbt `not_null`, `unique`, relationship, and structural tests,
- custom healthcare-domain validation,
- schema-registry generation from documented dbt metadata,
- SQL-result validation inside the agent workflow.

This layered approach prevents poor-quality source data or malformed SQL from silently reaching the final response.

---

## Agentic AI Workflow

MIRA uses LangGraph to model the reasoning process as explicit, inspectable nodes rather than one monolithic prompt.

| Node | Responsibility |
|---|---|
| Intent classifier | Routes questions to SQL, RAG, hybrid, or visualization workflows |
| Schema retriever | Semantically selects relevant warehouse tables and columns |
| SQL generator | Produces DuckDB-compatible SQL from the question and retrieved schema |
| SQL executor | Calls the database MCP server and returns structured results |
| Validator | Checks correctness, completeness, and failure conditions |
| RAG retriever | Searches the clinical knowledge base through the vector MCP server |
| RAG synthesizer | Produces source-grounded clinical explanations |
| Response synthesizer | Combines data results, clinical context, and validation evidence |
| Visualizer | Selects and generates metric cards, bar charts, line charts, or scatter plots |

The graph maintains shared typed state across nodes, enabling controlled branching, retries, error propagation, evidence preservation, and observability.

---

## Model Context Protocol Tools

MIRA separates reasoning from execution through two MCP-style services:

- **Database MCP Server** — executes approved read-only analytical SQL against DuckDB.
- **Vector MCP Server** — retrieves ranked clinical document chunks from PostgreSQL/pgvector.

This abstraction keeps tool access modular and makes the reasoning layer independent of the underlying database implementation. It also mirrors how production AI agents expose governed capabilities through restricted tools rather than direct infrastructure access.

---

## Evaluation and Observability

### 50-question benchmark

The evaluation suite contains:

| Category | Questions | Passed | Accuracy |
|---|---:|---:|---:|
| Text-to-SQL | 25 | 25 | **100%** |
| Clinical RAG | 15 | 15 | **100%** |
| Hybrid SQL + RAG | 7 | 7 | **100%** |
| Visualization | 3 | 1 | 33.3% |
| **Overall** | **50** | **48** | **96.0%** |
| **Core reasoning only** | **47** | **47** | **100%** |

The benchmark covers:

- exact counts,
- numerical tolerance,
- top-category ranking,
- top-N list validation,
- date normalization,
- source keyword coverage,
- hybrid SQL-and-RAG correctness,
- chart presence and chart type,
- latency,
- validation outcome,
- retry behavior.

All 50 benchmark executions completed with **zero retries**. Average observed benchmark latency was approximately **9.1 seconds**, with SQL and RAG requests completing faster than multi-stage hybrid questions.

### MLflow tracking

Each run records execution metadata in MLflow, including:

- benchmark ID,
- route and intent,
- generated SQL,
- validation status,
- retrieved sources,
- chart type,
- latency,
- retries,
- output artifacts.

This allows individual failures to be reproduced and inspected rather than treating accuracy as a single opaque score.

> The current benchmark's two failed cases are limited to visualization equivalence: one compares semantically equivalent monthly series produced from different warehouse layers, and one requires further chart-selection refinement. SQL correctness, retrieval grounding, and hybrid reasoning all passed at 100%.

---

## Dashboard and API

### Streamlit dashboard

The Streamlit interface provides:

- natural-language question entry,
- suggested analytical and clinical prompts,
- route and validation indicators,
- answer summaries,
- generated Plotly visualizations,
- returned data tables,
- generated SQL evidence,
- retrieved clinical sources,
- technical trace information,
- query history.

Add the redesigned dashboard screenshot to the repository as `images/dashboard.png`, then keep the following block:

```html
<h3 align="center">MIRA Clinical Intelligence Dashboard</h3>

<p align="center">
  <img src="images/dashboard.png" width="1000">
</p>

<p align="center">
Natural-language clinical analytics with validated SQL, source-grounded RAG,
interactive visualizations, and execution traceability.
</p>
```

### FastAPI service

The API separates the user interface from the agent runtime and provides endpoints for:

- submitting a question,
- returning normalized agent output,
- storing query history,
- retrieving previous query results.

This makes the project usable as an application backend rather than only as a notebook or command-line demonstration.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Language | Python 3.11 |
| Synthetic healthcare data | Synthea |
| Storage | Delta Lake, Apache Parquet |
| Analytical warehouse | DuckDB |
| Data processing | Pandas, NumPy, PyArrow |
| Analytics engineering | dbt Core, dbt-duckdb |
| Dimensional modeling | Staging models, dimensions, facts, metrics marts |
| Data quality | Great Expectations, dbt tests, custom clinical validations |
| Orchestration | Apache Airflow |
| Clinical terminology | SNOMED mappings, LOINC ranges, RxNorm/drug-class mappings |
| Agent framework | LangGraph |
| LLM inference | Groq-hosted models |
| Schema retrieval | Sentence Transformers |
| RAG database | PostgreSQL 15, pgvector |
| Retrieval | Vector similarity, full-text search, Reciprocal Rank Fusion |
| Tool layer | Model Context Protocol-style database and vector servers |
| Backend | FastAPI, Pydantic, Uvicorn |
| Frontend | Streamlit |
| Visualization | Plotly |
| Evaluation and tracing | MLflow, custom benchmark framework |
| Containerization | Docker Compose |

---

## Repository Structure

```text
MIRA/
│
├── agent/
│   ├── graph.py                    # LangGraph workflow definition
│   ├── state.py                    # typed shared agent state
│   ├── prompts.py                  # versioned SQL and RAG prompts
│   ├── llm_client.py               # Groq model client and retry handling
│   ├── mcp_client.py               # tool-server communication
│   ├── observability.py            # MLflow tracing and metadata
│   ├── run_agent.py                # agent entry point
│   └── nodes/                      # specialized reasoning nodes
│
├── airflow_dags/
│   └── cliniq_pipeline.py          # pipeline orchestration DAG
│
├── api/
│   ├── main.py                     # FastAPI application
│   ├── schemas.py                  # request/response models
│   └── history_store.py            # query-history persistence
│
├── dbt_project/
│   ├── models/
│   │   ├── staging/                # standardized source models
│   │   ├── marts/                  # dimensions and facts
│   │   └── metrics/                # reusable analytical metrics
│   ├── seeds/                      # concept and reference mappings
│   └── tests/
│
├── docker/
│   ├── docker-compose.yml          # PostgreSQL, Airflow, and MLflow
│   ├── Dockerfile.airflow
│   ├── Dockerfile.api
│   └── Dockerfile.streamlit
│
├── docs/
│   └── schema_registry.json        # generated semantic warehouse schema
│
├── evaluation/
│   ├── benchmark_questions.json    # 50-question evaluation suite
│   ├── run_benchmark.py            # benchmark runner and scoring logic
│   └── benchmark_results.md        # latest detailed results
│
├── frontend/
│   ├── app.py                      # Streamlit clinical dashboard
│   └── api_client.py               # frontend-to-API client
│
├── great_expectations/
│   ├── expectations/               # validation suites
│   └── validation_definitions/
│
├── mcp_servers/
│   ├── database_server.py          # governed DuckDB query tool
│   └── vector_server.py            # clinical retrieval tool
│
├── pipeline/
│   ├── convert_to_delta.py
│   ├── run_custom_data_quality.py
│   ├── run_great_expectations.py
│   └── update_schema_registry.py
│
├── vector_store/
│   ├── documents/                  # 24 clinical knowledge documents
│   ├── embed_documents.py          # incremental embedding pipeline
│   ├── retriever.py                # hybrid retrieval + RRF
│   └── schema.sql                  # pgvector schema
│
├── config.py                       # centralized environment configuration
├── start_servers.py                # local MCP server launcher
├── requirements.txt
└── README.md
```

---

## Running the Project

### Prerequisites

- Python 3.10 or 3.11
- Docker Desktop
- Git
- Groq API key
- Generated Synthea CSV data or the project's prepared local data assets

### 1. Clone the repository

```bash
git clone https://github.com/ChetanaMuralidharan/Mira.git
cd Mira
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux or macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from your local configuration template and provide the required credentials and paths.

```env
GROQ_API_KEY=your_groq_api_key
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cliniq_db
POSTGRES_USER=cliniq
POSTGRES_PASSWORD=cliniq_pass
MLFLOW_TRACKING_URI=http://localhost:5000
```

Do not commit `.env` or any credentials to source control.

### 5. Start infrastructure services

The Compose file is stored inside `docker/`:

```bash
docker compose -f docker/docker-compose.yml up -d
```

This starts PostgreSQL/pgvector, Airflow services, and MLflow.

### 6. Build and validate the data platform

```bash
python pipeline/convert_to_delta.py
python pipeline/run_custom_data_quality.py
python pipeline/run_great_expectations.py
```

Run dbt from the project directory:

```bash
cd dbt_project
dbt seed
dbt run
dbt test
dbt docs generate
cd ..
```

Generate the semantic schema registry:

```bash
python pipeline/update_schema_registry.py
```

### 7. Embed the clinical knowledge base

```bash
python vector_store/embed_documents.py
```

The embedding process is incremental: unchanged documents are not unnecessarily re-embedded.

### 8. Start the MCP tool servers

```bash
python start_servers.py
```

### 9. Start the FastAPI backend

In a separate terminal:

```bash
uvicorn api.main:app --reload
```

### 10. Launch the Streamlit dashboard

In another terminal:

```bash
streamlit run frontend/app.py
```

### 11. Run the benchmark

```bash
python -m evaluation.run_benchmark
```

Detailed results are written to:

```text
evaluation/benchmark_results.md
```

### 12. Open supporting services

```text
Streamlit:  http://localhost:8501
FastAPI:    http://localhost:8000
API docs:   http://localhost:8000/docs
Airflow:    http://localhost:8080
MLflow:     http://localhost:5000
```

---

## Design Decisions Worth Knowing

### Why DuckDB instead of a cloud warehouse?

DuckDB provides columnar analytical execution, SQL compatibility, and fast local development while keeping the entire project reproducible on a laptop. The warehouse models follow patterns that can be migrated to Snowflake, BigQuery, Databricks SQL, or Redshift.

### Why use dbt when the agent could query raw tables?

Raw healthcare data contains technical codes, repeated records, inconsistent types, and multi-table logic. dbt creates governed analytical assets with documented fields, tests, reusable metrics, chronic-condition flags, and lab abnormality logic. The agent reasons over curated business models rather than rediscovering transformations in every query.

### Why retrieve schema context semantically?

Passing the full schema wastes tokens and increases the chance that the LLM selects an irrelevant table. Semantic schema retrieval narrows the prompt to the most relevant documented models and improves maintainability as the warehouse grows.

### Why hybrid retrieval instead of vector search alone?

Clinical documents contain exact terms, acronyms, medication names, and named protocols. Vector similarity captures semantic meaning, while full-text search preserves exact lexical matches. Reciprocal Rank Fusion combines both without requiring scores from the two systems to share the same scale.

### Why LangGraph instead of a single LLM call?

The application needs conditional routing, tool execution, validation, retries, evidence preservation, and hybrid workflows. A graph makes each operation explicit and testable and avoids hiding the entire application inside one prompt.

### Why use MCP-style servers?

The reasoning layer should not have unrestricted database access. Tool servers expose narrow capabilities for SQL execution and document retrieval, making infrastructure replaceable and access easier to govern.

### Why expose generated SQL and sources?

Clinical and analytical users need to understand where a response came from. Showing SQL, returned data, source documents, validation state, and run metadata makes errors visible and supports human review.

### Why benchmark the system end to end?

A good prompt on a few hand-picked examples is not evidence of reliability. MIRA's benchmark evaluates routing, SQL, data correctness, retrieval, synthesis, hybrid reasoning, visualization, retries, and latency across 50 fixed questions. This converts subjective demos into repeatable engineering evidence.

---

## Known Limitations

**Synthetic data only:** The project uses Synthea-generated records. Results demonstrate system behavior and engineering design, not real-world clinical prevalence or outcomes.

**Not a clinical decision-support system:** Clinical documents in the knowledge base are curated for demonstration. They are not automatically synchronized with current institutional policies or medical guidelines and must not guide patient care.

**No PHI security certification:** Although synthetic data avoids PHI exposure, the application has not undergone HIPAA security review, threat modeling, penetration testing, or production access-control implementation.

**Limited visualization benchmark:** Two visualization cases require additional equivalence and chart-selection refinement. Core SQL, RAG, and hybrid reasoning reached 100% on the current benchmark.

**Local infrastructure:** The project is designed for reproducible local execution. Production deployment would require secrets management, authentication, role-based authorization, encrypted transport, managed databases, monitoring, and CI/CD.

**LLM variability:** Model outputs may vary across provider or model versions. The validator, retry workflow, benchmark suite, and versioned prompts reduce this risk but do not eliminate it.

**Curated knowledge scope:** The RAG corpus contains 24 documents and does not represent a complete medical knowledge base. Retrieval quality outside the represented conditions and workflows is not guaranteed.

---

## Future Enhancements

- Redesign the Streamlit interface as a professional light-themed clinical operations dashboard.
- Add role-based access for analysts, clinicians, and administrators.
- Introduce FHIR-compatible ingestion and terminology normalization.
- Add source freshness, guideline versioning, and document approval workflows.
- Expand the benchmark with adversarial, ambiguity, and hallucination tests.
- Add SQL safety policies, query-cost controls, and row-level authorization.
- Add human feedback capture and evaluation datasets from reviewed answers.
- Package API and frontend services as deployable containers.
- Add CI/CD checks for dbt tests, Great Expectations, retrieval tests, and benchmark regression.
- Evaluate local or private LLM deployment for sensitive environments.

---

## Disclaimer

MIRA is an engineering and portfolio demonstration built with synthetic healthcare data. It is not a medical device, has not been clinically validated, and is not intended to diagnose, treat, or support decisions about real patients.

---

## Author

**Chetana Muralidharan**  
Data Engineer | AI Engineer | Applied Data Intelligence

GitHub: [github.com/ChetanaMuralidharan](https://github.com/ChetanaMuralidharan)
