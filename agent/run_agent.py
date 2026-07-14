import os

import mlflow
from dotenv import load_dotenv

load_dotenv()

from agent.graph import compiled_graph
from agent.state import initial_state
from agent.observability import (
    setup_mlflow,
    start_timer,
    elapsed_ms,
    log_json_artifact,
    log_text_artifact,
)

from config import (
    PROMPT_VERSION_INTENT,
    PROMPT_VERSION_SQL,
    PROMPT_VERSION_RAG,
    PROMPT_VERSION_RESPONSE,
    PROMPT_VERSION_VALIDATOR,
)


def run_mira(question: str, benchmark_id: str | None = None):
    setup_mlflow()
    timer = start_timer()

    with mlflow.start_run(run_name=benchmark_id or question[:80]) as run:
        state = initial_state(question)
        state["mlflow_run_id"] = run.info.run_id

        mlflow.log_param("project", "MIRA")
        mlflow.log_param("llm_provider", "groq")
        mlflow.log_param("question", question)
        mlflow.log_param("benchmark_id", benchmark_id or "")

        mlflow.log_param("groq_model_fast", os.getenv("GROQ_MODEL_FAST"))
        mlflow.log_param("groq_model_quality", os.getenv("GROQ_MODEL_QUALITY"))

        mlflow.log_param("prompt_version_intent", PROMPT_VERSION_INTENT)
        mlflow.log_param("prompt_version_sql", PROMPT_VERSION_SQL)
        mlflow.log_param("prompt_version_rag", PROMPT_VERSION_RAG)
        mlflow.log_param("prompt_version_response", PROMPT_VERSION_RESPONSE)
        mlflow.log_param("prompt_version_validator", PROMPT_VERSION_VALIDATOR)

        result = compiled_graph.invoke(state)

        latency_ms = elapsed_ms(timer)
        result["total_latency_ms"] = latency_ms

        mlflow.log_param("intent", result.get("intent"))
        mlflow.log_param("data_sources_needed", str(result.get("data_sources_needed")))
        mlflow.log_param("validation_status", result.get("validation_status"))
        mlflow.log_param("chart_type", result.get("chart_type"))

        mlflow.log_metric("total_latency_ms", latency_ms)
        mlflow.log_metric("retry_count", result.get("retry_count", 0))
        mlflow.log_metric("rag_chunk_count", len(result.get("rag_chunks", [])))

        sql_success = 1 if result.get("generated_sql") and not result.get("sql_error") else 0
        mlflow.log_metric("sql_success", sql_success)

        log_text_artifact("generated_sql.sql", result.get("generated_sql", ""))
        log_json_artifact("sql_result.json", result.get("sql_result", []))
        log_json_artifact("rag_chunks.json", result.get("rag_chunks", []))
        log_json_artifact("chart_spec.json", result.get("chart_spec", {}))
        log_text_artifact("final_answer.txt", result.get("final_explanation", ""))
        log_json_artifact("tool_calls_log.json", result.get("tool_calls_log", []))

        return result