import os
from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def call_llm(prompt: str, node_name: str, model_tier: str = "fast") -> str:
    """
    model_tier: "fast" for classification/routing, "quality" for synthesis/RAG/SQL generation.
    Every node calls this — never call the Groq SDK directly from a node.
    """
    model = os.getenv("GROQ_MODEL_FAST") if model_tier == "fast" else os.getenv("GROQ_MODEL_QUALITY")
    print(f"[LLM] {node_name}: calling Groq model={model}...", flush=True)
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            timeout=20,
        )
    except Exception as e:
        print(f"[LLM] {node_name}: EXCEPTION: {e}", flush=True)
        raise
    print(f"[LLM] {node_name}: got response", flush=True)
    return response.choices[0].message.content.strip()