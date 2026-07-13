from langgraph.graph import StateGraph, END
from agent.state import ClinIQState, initial_state
from agent.nodes import (
    intent_classifier, schema_retriever, sql_generator, sql_executor,
    validator, rag_retriever, rag_synthesizer, visualizer, response_synthesizer
)


def route_after_intent(state: ClinIQState) -> str:
    intent = state["intent"]
    if intent in ("data_query", "visualization", "trend_analysis", "hybrid"):
        return "schema_retriever"
    if intent == "document_query":
        return "rag_retriever"
    return "response_synthesizer"


def route_after_execution(state: ClinIQState) -> str:
    if state.get("sql_error") and state.get("retry_count", 0) < 3:
        return "sql_generator"
    return "validator"


def route_after_validation(state: ClinIQState) -> str:
    status = state["validation_status"]
    if status == "valid":
        return "visualizer"
    if status == "suspect" and state.get("retry_count", 0) < 3:
        return "sql_generator"
    return "response_synthesizer"


def route_after_visualizer(state: ClinIQState) -> str:
    # Hybrid intent still needs the RAG side before final synthesis
    if state["intent"] == "hybrid" and not state.get("rag_result"):
        return "rag_retriever"
    return "response_synthesizer"


graph = StateGraph(ClinIQState)

graph.add_node("intent_classifier", intent_classifier)
graph.add_node("schema_retriever", schema_retriever)
graph.add_node("sql_generator", sql_generator)
graph.add_node("sql_executor", sql_executor)
graph.add_node("validator", validator)
graph.add_node("rag_retriever", rag_retriever)
graph.add_node("rag_synthesizer", rag_synthesizer)
graph.add_node("visualizer", visualizer)
graph.add_node("response_synthesizer", response_synthesizer)

graph.set_entry_point("intent_classifier")
graph.add_conditional_edges("intent_classifier", route_after_intent)
graph.add_edge("schema_retriever", "sql_generator")
graph.add_edge("sql_generator", "sql_executor")
graph.add_conditional_edges("sql_executor", route_after_execution)
graph.add_conditional_edges("validator", route_after_validation)
graph.add_conditional_edges("visualizer", route_after_visualizer)
graph.add_edge("rag_retriever", "rag_synthesizer")
graph.add_edge("rag_synthesizer", "response_synthesizer")
graph.add_edge("response_synthesizer", END)

compiled_graph = graph.compile()