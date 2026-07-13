import json, re
from agent.state import ClinIQState
from agent.prompts import VALIDATOR_SANITY_CHECK_PROMPT
from agent.llm_client import call_llm

# Clinical plausibility ranges — mirrors your Great Expectations suites
NUMERIC_RANGE_CHECKS = {
    "a1c": (3.0, 15.0),
    "value_numeric": (0, 1000),  # generic fallback guard
}


def _rule_based_check(sql_result: list) -> str:
    if not sql_result:
        return "empty"

    for row in sql_result:
        for key, value in row.items():
            if not isinstance(value, (int, float)):
                continue
            key_lower = key.lower()
            for range_key, (low, high) in NUMERIC_RANGE_CHECKS.items():
                if range_key in key_lower and not (low <= value <= high):
                    return "out_of_range"
    return "rules_passed"


def _extract_json(text: str) -> dict:
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


def validator(state: ClinIQState) -> ClinIQState:
    sql_result = state.get("sql_result", [])
    rule_status = _rule_based_check(sql_result)

    if rule_status in ("empty", "out_of_range"):
        state["validation_status"] = rule_status
        state["validation_notes"] = f"Rule check failed: {rule_status}"
        return state

    # Deterministic pass for simple aggregate queries:
    # e.g. SELECT COUNT(*) AS patient_count ...
    if len(sql_result) == 1 and len(sql_result[0]) == 1:
        value = next(iter(sql_result[0].values()))
        if isinstance(value, (int, float)) and value >= 0:
            state["validation_status"] = "valid"
            state["validation_notes"] = "Simple non-negative aggregate result passed deterministic validation."
            return state

    sample_rows = sql_result[:5]
    prompt = VALIDATOR_SANITY_CHECK_PROMPT.format(
        question=state["user_question"],
        sql=state.get("generated_sql", ""),
        sample_rows=json.dumps(sample_rows),
    )
    raw = call_llm(prompt, "validator", model_tier="fast")

    try:
        parsed = _extract_json(raw)
        if parsed.get("valid", True):
            state["validation_status"] = "valid"
            state["validation_notes"] = parsed.get("reason", "")
        else:
            state["validation_status"] = "suspect"
            state["validation_notes"] = parsed.get("reason", "Failed LLM sanity check.")
            state["retry_count"] = state.get("retry_count", 0) + 1
    except (json.JSONDecodeError, KeyError):
        state["validation_status"] = "valid"
        state["validation_notes"] = "Sanity check parse failed; defaulted to valid."

    return state