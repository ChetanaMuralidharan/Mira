import json, re
from agent.state import ClinIQState
from agent.prompts import INTENT_CLASSIFIER_PROMPT
from agent.llm_client import call_llm


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    return json.loads(text)


def intent_classifier(state: ClinIQState) -> ClinIQState:
    print("[NODE] intent_classifier: start", flush=True)
    prompt = INTENT_CLASSIFIER_PROMPT.format(question=state["user_question"])
    raw = call_llm(prompt, "intent_classifier", model_tier="fast")
    print(f"[NODE] intent_classifier: raw LLM output: {raw[:200]}", flush=True)

    try:
        parsed = _extract_json(raw)
        state["intent"] = parsed.get("intent", "out_of_scope")
        state["data_sources_needed"] = parsed.get("data_sources_needed", [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[NODE] intent_classifier: JSON parse failed: {e}", flush=True)
        state["intent"] = "out_of_scope"
        state["data_sources_needed"] = []

    state.setdefault("tool_calls_log", []).append({
        "node": "intent_classifier", "tool_name": "llm_call",
        "arguments": {"question": state["user_question"]},
        "result_summary": f"intent={state['intent']}", "latency_ms": 0
    })
    print(f"[NODE] intent_classifier: done, intent={state['intent']}", flush=True)
    return state