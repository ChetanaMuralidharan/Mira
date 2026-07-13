import re
from agent.state import ClinIQState
from agent.prompts import (
    SQL_GENERATOR_PROMPT, SQL_GENERATOR_RETRY_CONTEXT_TEMPLATE, SQL_FEW_SHOT_EXAMPLES
)
from agent.llm_client import call_llm


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def sql_generator(state: ClinIQState) -> ClinIQState:
    print("[NODE] sql_generator: start", flush=True)
    retry_context = ""
    if state.get("sql_error"):
        retry_context = SQL_GENERATOR_RETRY_CONTEXT_TEMPLATE.format(
            previous_sql=state.get("generated_sql", ""),
            error_message=state["sql_error"],
        )

    prompt = SQL_GENERATOR_PROMPT.format(
        schema_context=state.get("schema_context", ""),
        few_shot_examples=SQL_FEW_SHOT_EXAMPLES,
        retry_context=retry_context,
        question=state["user_question"],
    )

    raw_sql = call_llm(prompt, "sql_generator", model_tier="quality")
    clean_sql = _strip_markdown_fences(raw_sql)
    print(f"[NODE] sql_generator: got SQL: {clean_sql[:100]}", flush=True)

    if not clean_sql.strip().upper().startswith("SELECT"):
        state["generated_sql"] = ""
        state["sql_error"] = "Generated output did not start with SELECT."
        print("[NODE] sql_generator: rejected, does not start with SELECT", flush=True)
        return state

    state["generated_sql"] = clean_sql
    print("[NODE] sql_generator: done", flush=True)
    return state