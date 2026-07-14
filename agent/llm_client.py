import os
from groq import Groq
import time
from groq import RateLimitError

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def call_llm(prompt: str, node_name: str, model_tier: str = "fast") -> str:
    model = os.getenv("GROQ_MODEL_FAST") if model_tier == "fast" else os.getenv("GROQ_MODEL_QUALITY")
    client = get_client()

    max_retries = 5
    wait_seconds = 2

    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"[LLM] {node_name}: calling Groq model={model} "
                f"(attempt {attempt}/{max_retries})...",
                flush=True,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                timeout=20,
            )

            print(f"[LLM] {node_name}: got response", flush=True)
            return response.choices[0].message.content.strip()

        except RateLimitError:
            if attempt == max_retries:
                print(f"[LLM] {node_name}: rate limit retries exhausted", flush=True)
                raise

            print(
                f"[LLM] {node_name}: rate limited. Waiting {wait_seconds}s before retry...",
                flush=True,
            )
            time.sleep(wait_seconds)
            wait_seconds *= 2

        except Exception as e:
            print(f"[LLM] {node_name}: EXCEPTION: {e}", flush=True)
            raise

    raise RuntimeError(f"[LLM] {node_name}: failed after {max_retries} retries")