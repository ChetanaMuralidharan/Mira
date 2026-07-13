import json
from agent.state import ClinIQState
from agent.prompts import (
    RESPONSE_SYNTHESIZER_SQL_PROMPT, RESPONSE_SYNTHESIZER_HYBRID_PROMPT,
    RESPONSE_SYNTHESIZER_CAVEAT, RESPONSE_SYNTHESIZER_OUT_OF_SCOPE,
    RESPONSE_SYNTHESIZER_NO_DATA, RESPONSE_SYNTHESIZER_SQL_FAILURE,
)
from agent.llm_client import call_llm


def response_synthesizer(state: ClinIQState) -> ClinIQState:
    intent = state.get("intent", "out_of_scope")

    if intent == "out_of_scope":
        state["final_explanation"] = RESPONSE_SYNTHESIZER_OUT_OF_SCOPE
        state["suggested_followup"] = ""
        return state

    if intent == "document_query":
        state["final_explanation"] = state.get("rag_result", "") + RESPONSE_SYNTHESIZER_CAVEAT
        return state

    if intent in ("data_query", "visualization", "trend_analysis", "hybrid"):
        # Only check SQL-specific failure states for paths that actually ran SQL
        if state.get("sql_error") and state.get("retry_count", 0) >= 3:
            state["final_explanation"] = RESPONSE_SYNTHESIZER_SQL_FAILURE
            state["suggested_followup"] = ""
            return state

        if state.get("validation_status") == "empty":
            state["final_explanation"] = RESPONSE_SYNTHESIZER_NO_DATA
            state["suggested_followup"] = ""
            return state

        if intent == "hybrid":
            sql_summary = json.dumps(state.get("sql_result", [])[:5])
            prompt = RESPONSE_SYNTHESIZER_HYBRID_PROMPT.format(
                question=state["user_question"],
                sql_summary=sql_summary,
                rag_result=state.get("rag_result", ""),
            )
            text = call_llm(prompt, "response_synthesizer", model_tier="quality")
            state["final_explanation"] = text + RESPONSE_SYNTHESIZER_CAVEAT
            return state

        prompt = RESPONSE_SYNTHESIZER_SQL_PROMPT.format(
            question=state["user_question"],
            sql_result=json.dumps(state.get("sql_result", [])[:10]),
        )
        text = call_llm(prompt, "response_synthesizer", model_tier="quality")
        state["final_explanation"] = text + RESPONSE_SYNTHESIZER_CAVEAT
        return state

    state["final_explanation"] = RESPONSE_SYNTHESIZER_OUT_OF_SCOPE
    return state