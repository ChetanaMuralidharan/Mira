from agent.state import ClinIQState
from agent.prompts import RAG_SYNTHESIZER_PROMPT, RAG_CHUNK_FORMAT_TEMPLATE
from agent.llm_client import call_llm


def rag_synthesizer(state: ClinIQState) -> ClinIQState:
    chunks = state.get("rag_chunks", [])

    if not chunks:
        state["rag_result"] = "No relevant clinical guidelines or protocols were found for this question."
        return state

    formatted_chunks = "\n\n".join(
        RAG_CHUNK_FORMAT_TEMPLATE.format(
            document_name=c["document_name"],
            document_type=c["document_type"],
            chunk_text=c["chunk_text"],
        )
        for c in chunks
    )

    prompt = RAG_SYNTHESIZER_PROMPT.format(
        formatted_chunks=formatted_chunks,
        question=state["user_question"],
    )
    state["rag_result"] = call_llm(prompt, "rag_synthesizer", model_tier="quality")
    state["validation_status"] = "not_applicable"
    return state