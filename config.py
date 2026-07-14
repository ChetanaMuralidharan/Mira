import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PARQUET_DIR = os.path.join(DATA_DIR, "parquet", "raw")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
SCHEMA_REGISTRY_PATH = os.path.join(DOCS_DIR, "schema_registry.json")

# DuckDB
DUCKDB_PATH = os.path.join(BASE_DIR, "cliniq.duckdb")

# PostgreSQL
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "cliniq_db"
POSTGRES_USER = "cliniq"
POSTGRES_PASSWORD = "cliniq_pass"
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODELS = {
    "intent_classifier": "mistral:7b",
    "sql_generator": "codellama:7b",
    "response_synthesizer": "llama3.1:8b",
    "rag_synthesizer": "llama3.1:8b",
    "validator": "mistral:7b",
}

# Synthea
SYNTHEA_SEED = 42
SYNTHEA_PATIENT_COUNT = 5000
SYNTHEA_STATE = "Massachusetts"

# Agent
MAX_SQL_RETRIES = 3
MAX_QUERY_ROWS = 1000
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
RAG_TOP_K = 5

#ML-FLOW
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "MIRA Agent Evaluation")

LLM_PROVIDER = "groq"
PROMPT_VERSION_INTENT = "intent_v1"
PROMPT_VERSION_SQL = "sql_v1"
PROMPT_VERSION_RAG = "rag_v1"
PROMPT_VERSION_RESPONSE = "response_v1"
PROMPT_VERSION_VALIDATOR = "validator_v1"