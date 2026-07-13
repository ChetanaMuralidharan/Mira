import asyncio
from agent.state import ClinIQState
from agent.mcp_client import call_mcp_tool


def sql_executor(state: ClinIQState) -> ClinIQState:
    print("[NODE] sql_executor: start", flush=True)
    sql = state.get("generated_sql", "")
    if not sql:
        state["sql_error"] = state.get("sql_error", "No SQL was generated.")
        state["retry_count"] = state.get("retry_count", 0) + 1
        print("[NODE] sql_executor: no SQL, skipping", flush=True)
        return state

    print(f"[NODE] sql_executor: calling MCP with sql={sql[:100]}", flush=True)
    result = asyncio.run(call_mcp_tool("database", "query_clinical_database", {"sql": sql}))
    print("[NODE] sql_executor: got MCP result", flush=True)

    if isinstance(result, dict) and "error" in result:
        state["sql_error"] = result["error"]
        state["retry_count"] = state.get("retry_count", 0) + 1
        state["sql_result"] = []
    else:
        state["sql_result"] = result if isinstance(result, list) else []
        state["sql_error"] = None

    state.setdefault("tool_calls_log", []).append({
        "node": "sql_executor", "tool_name": "query_clinical_database",
        "arguments": {"sql": sql},
        "result_summary": state.get("sql_error") or f"{len(state['sql_result'])} rows",
        "latency_ms": 0,
    })
    print("[NODE] sql_executor: done", flush=True)
    return state