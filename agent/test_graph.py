from dotenv import load_dotenv
load_dotenv()

from agent.graph import compiled_graph
from agent.state import initial_state

TEST_QUESTIONS = [
    "How many patients have Type 2 diabetes?",
    "What is the most common encounter class?",
    "What are the ADA's A1c targets for elderly diabetic patients?",
]

for q in TEST_QUESTIONS:
    print(f"\n{'='*60}\nQ: {q}\n{'='*60}")
    result = compiled_graph.invoke(initial_state(q))
    print("Intent:", result.get("intent"))
    print("Generated SQL:", result.get("generated_sql"))
    print("SQL error:", result.get("sql_error"))
    print("SQL result:", result.get("sql_result"))
    print("Validation status:", result.get("validation_status"))
    print("Retry count:", result.get("retry_count"))
    print("Answer:", result.get("final_explanation"))