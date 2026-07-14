from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class RagChunk(BaseModel):
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    chunk_text: Optional[str] = None
    relevance_score: Optional[float] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    intent: str
    data_sources_needed: List[str]
    generated_sql: Optional[str] = None
    sql_result: List[Dict[str, Any]] = []
    validation_status: Optional[str] = None
    validation_notes: Optional[str] = None
    chart_type: Optional[str] = None
    chart_spec: Optional[Dict[str, Any]] = None
    rag_chunks: List[Dict[str, Any]] = []
    suggested_followup: Optional[str] = None
    mlflow_run_id: Optional[str] = None
    tool_calls_log: List[Dict[str, Any]] = []
    total_latency_ms: Optional[int] = None


class HistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    intent: str
    validation_status: Optional[str] = None
    mlflow_run_id: Optional[str] = None
    total_latency_ms: Optional[int] = None
    created_at: str