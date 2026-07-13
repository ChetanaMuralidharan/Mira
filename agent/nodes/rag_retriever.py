import asyncio
from agent.state import ClinIQState
from agent.mcp_client import call_mcp_tool


def rag_retriever(state: ClinIQState) -> ClinIQState:
    result = asyncio.run(call_mcp_tool(
        "vector", "search_clinical_documents",
        {"query": state["user_question"], "top_k": 5}
    ))

    chunks = result.get("chunks", []) if isinstance(result, dict) else []
    state["rag_chunks"] = chunks

    state.setdefault("tool_calls_log", []).append({
        "node": "rag_retriever", "tool_name": "search_clinical_documents",
        "arguments": {"query": state["user_question"]},
        "result_summary": f"{len(chunks)} chunks retrieved", "latency_ms": 0,
    })
    return state