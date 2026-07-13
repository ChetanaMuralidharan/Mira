"""
Validates that hybrid search returns sensible results for known queries.
Run this after any changes to documents or the embedding pipeline.
"""
from vector_store.retriever import hybrid_search

TEST_CASES = [
    {
        "query": "A1c target for elderly diabetic patients",
        "expected_doc_fragment": "ada_diabetes",
        "min_results": 1,
    },
    {
        "query": "heart failure readmission criteria",
        "expected_doc_fragment": "readmission",
        "min_results": 1,
    },
    {
        "query": "SGLT2 inhibitor kidney disease",
        "expected_doc_fragment": "ada_diabetes",
        "min_results": 1,
    },
    {
        "query": "abnormal lab escalation protocol steps",
        "expected_doc_fragment": "escalation",
        "min_results": 1,
    },
    {
        "query": "infection control hand hygiene procedure",
        "expected_doc_fragment": "infection",
        "min_results": 1,
    },
]

def run_tests():
    passed = 0
    failed = 0
    for tc in TEST_CASES:
        results = hybrid_search(tc["query"], top_k=5)
        doc_names = [r["document_name"] for r in results]
        found = any(tc["expected_doc_fragment"] in name for name in doc_names)
        count_ok = len(results) >= tc["min_results"]

        if found and count_ok:
            print(f"  PASS: '{tc['query'][:50]}' → {doc_names[0]}")
            passed += 1
        else:
            print(f"  FAIL: '{tc['query'][:50]}'")
            print(f"        Expected fragment '{tc['expected_doc_fragment']}' in {doc_names}")
            failed += 1

    print(f"\n{passed}/{passed+failed} tests passed.")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)