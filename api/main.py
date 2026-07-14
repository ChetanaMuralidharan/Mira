from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.run_agent import run_mira
from api.schemas import AskRequest, AskResponse
from api.history_store import init_history_db, save_query, list_history, get_history_item


app = FastAPI(
    title="MIRA API",
    description="Medical Intelligence and Reasoning Agent backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_history_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "mira-api"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = run_mira(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    payload = {
        "question": request.question,
        "answer": result.get("final_explanation", ""),
        "intent": result.get("intent", ""),
        "data_sources_needed": result.get("data_sources_needed", []),
        "generated_sql": result.get("generated_sql", ""),
        "sql_result": result.get("sql_result", []),
        "validation_status": result.get("validation_status"),
        "validation_notes": result.get("validation_notes"),
        "chart_type": result.get("chart_type"),
        "chart_spec": result.get("chart_spec"),
        "rag_chunks": result.get("rag_chunks", []),
        "suggested_followup": result.get("suggested_followup", ""),
        "mlflow_run_id": result.get("mlflow_run_id", ""),
        "tool_calls_log": result.get("tool_calls_log", []),
        "total_latency_ms": result.get("total_latency_ms"),
    }

    save_query(payload)
    return payload


@app.get("/history")
def history(limit: int = 25):
    return list_history(limit=limit)


@app.get("/history/{item_id}")
def history_item(item_id: int):
    item = get_history_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="History item not found")
    return item