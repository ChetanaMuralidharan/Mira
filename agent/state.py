"""
ClinIQ Agent State
Single source of truth passed between every LangGraph node.
Every node reads from and writes to this shape only — no side channels.
"""

from typing import TypedDict, List, Dict, Optional, Literal


IntentType = Literal[
    "data_query", "visualization", "trend_analysis",
    "document_query", "hybrid", "out_of_scope"
]

ValidationStatus = Literal["valid", "empty", "out_of_range", "suspect"]

ChartType = Literal["bar", "line", "scatter", "pie", "metric_card", "table", "none"]


class ToolCallLogEntry(TypedDict):
    node: str
    tool_name: str
    arguments: dict
    result_summary: str
    latency_ms: int


class ClinIQState(TypedDict, total=False):
    # --- Input (immutable after entry) ---
    user_question: str

    # --- Routing ---
    intent: IntentType
    data_sources_needed: List[str]          # e.g. ["sql"], ["rag"], ["sql", "rag"]

    # --- SQL path ---
    schema_context: str                     # formatted table/column descriptions for prompt
    relevant_tables: List[str]              # table names retrieved by schema_retriever
    generated_sql: str
    sql_result: List[Dict]                  # list of row dicts from DuckDB
    sql_error: Optional[str]                # last execution error, if any
    retry_count: int                        # capped at 3

    # --- RAG path ---
    rag_chunks: List[Dict]                  # [{document_name, chunk_text, document_type, relevance_score}]
    rag_result: str                         # synthesized, cited answer text

    # --- Validation ---
    validation_status: ValidationStatus
    validation_notes: Optional[str]         # why it was flagged suspect/out_of_range

    # --- Visualization ---
    chart_type: ChartType
    chart_spec: Optional[Dict]              # Plotly figure as JSON-serializable dict

    # --- Final output ---
    final_explanation: str
    suggested_followup: str

    # --- Observability ---
    mlflow_run_id: str
    tool_calls_log: List[ToolCallLogEntry]
    total_latency_ms: int


def initial_state(user_question: str) -> ClinIQState:
    """Factory for a clean state object at the start of every invocation."""
    return ClinIQState(
        user_question=user_question,
        intent="out_of_scope",
        data_sources_needed=[],
        schema_context="",
        relevant_tables=[],
        generated_sql="",
        sql_result=[],
        sql_error=None,
        retry_count=0,
        rag_chunks=[],
        rag_result="",
        validation_status="empty",
        validation_notes=None,
        chart_type="none",
        chart_spec=None,
        final_explanation="",
        suggested_followup="",
        mlflow_run_id="",
        tool_calls_log=[],
        total_latency_ms=0,
    )