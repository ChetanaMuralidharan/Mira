import json
import re
from pathlib import Path

import duckdb
import mlflow
from dotenv import load_dotenv

load_dotenv()

from config import DUCKDB_PATH
from agent.run_agent import run_mira

from datetime import datetime, timezone
import pandas as pd
import time


BENCHMARK_PATH = Path(__file__).parent / "benchmark_questions.json"
RESULTS_PATH = Path(__file__).parent / "benchmark_results.md"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def run_expected_sql(sql: str):
    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    try:
        return con.execute(sql).fetchdf().to_dict(orient="records")
    finally:
        con.close()


def first_value(rows):
    if not rows:
        return None
    return list(rows[0].values())[0]


def score_sql(result, benchmark):
    if result.get("sql_error"):
        return 0, "SQL execution failed"

    expected_rows = run_expected_sql(benchmark["expected_sql"])
    actual_rows = result.get("sql_result", [])

    if not expected_rows:
        return 0, "Expected SQL returned no rows"

    if not actual_rows:
        return 0, "Agent SQL returned no rows"

    expected_value = first_value(expected_rows)
    actual_value = first_value(actual_rows)

    answer_type = benchmark["answer_type"]

    if answer_type == "numeric_exact":
        try:
            return int(int(float(expected_value)) == int(float(actual_value))), f"expected={expected_value}, actual={actual_value}"
        except Exception:
            return 0, f"Could not compare numeric values: expected={expected_value}, actual={actual_value}"

    if answer_type == "numeric_tolerance":
        tolerance = benchmark.get("tolerance", 0.5)
        try:
            diff = abs(float(expected_value) - float(actual_value))
            return int(diff <= tolerance), f"expected={expected_value}, actual={actual_value}, diff={diff}"
        except Exception:
            return 0, f"Could not compare tolerance values: expected={expected_value}, actual={actual_value}"

    if answer_type == "top_category":
        expected_norm = normalize_value(expected_value)
        actual_norm = normalize_value(actual_value)
        return int(expected_norm == actual_norm), (
    f"expected={expected_value}, actual={actual_value}, "
    f"expected_norm={expected_norm}, actual_norm={actual_norm}"
)
    
    if answer_type == "contains_top_items":
        expected_col = list(expected_rows[0].keys())[0]
        actual_text = normalize_text(result.get("final_explanation", "")) + " " + normalize_text(str(actual_rows))

        top_n = benchmark.get("top_n", 5)
        expected_items = [normalize_text(row[expected_col]) for row in expected_rows[:top_n]]

        hits = [item for item in expected_items if item in actual_text]
        required_hits = max(1, top_n // 2)

        return int(len(hits) >= required_hits), f"top_item_hits={hits}, required={required_hits}"

    return 0, "Unknown SQL answer type"


def score_rag(result, benchmark):
    answer = normalize_text(result.get("final_explanation", ""))
    keywords = benchmark.get("expected_keywords", [])

    hits = [kw for kw in keywords if normalize_text(kw) in answer]
    required_hits = max(1, len(keywords) // 2)

    score = int(len(hits) >= required_hits)
    return score, f"keyword_hits={hits}, required={required_hits}"

def normalize_value(value):
    if value is None:
        return ""

    # Handle numeric Unix timestamps, including float versions like 1617235200.0
    try:
        numeric_value = float(value)
        if 1_000_000_000 <= numeric_value <= 2_000_000_000:
            return datetime.fromtimestamp(
    int(numeric_value),
    tz=timezone.utc
).strftime("%Y-%m-%d")
    except Exception:
        pass

    # Handle datetime/date-like values
    try:
        parsed = pd.to_datetime(value)
        if not pd.isna(parsed):
            return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass

    return normalize_text(value)


def main():
    questions = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))

    total = 0
    passed = 0

    sql_total = 0
    sql_passed = 0

    rag_total = 0
    rag_passed = 0

    rows = []

    for item in questions:
        print(f"\nRunning {item['id']}: {item['question']}")

        result = run_mira(item["question"], benchmark_id=item["id"])

        if item["type"] == "sql":
            score, reason = score_sql(result, item)
            sql_total += 1
            sql_passed += int(score)
        elif item["type"] == "rag":
            score, reason = score_rag(result, item)
            rag_total += 1
            rag_passed += int(score)
        else:
            score, reason = 0, "Unknown benchmark type"

        total += 1
        passed += int(score)

        with mlflow.start_run(run_id=result["mlflow_run_id"]):
            mlflow.log_metric("answer_accuracy", int(score))

        row = {
            "id": item["id"],
            "type": item["type"],
            "question": item["question"],
            "score": int(score),
            "reason": reason,
            "intent": result.get("intent"),
            "validation_status": result.get("validation_status"),
            "retry_count": result.get("retry_count", 0),
            "latency_ms": result.get("total_latency_ms"),
            "sql": result.get("generated_sql", "")
        }

        rows.append(row)

        print(f"Score: {score}")
        print(f"Reason: {reason}")
        print(f"Intent: {row['intent']}")
        print(f"Latency: {row['latency_ms']} ms")
        time.sleep(3)

    overall_accuracy = passed / total if total else 0
    sql_accuracy = sql_passed / sql_total if sql_total else 0
    rag_accuracy = rag_passed / rag_total if rag_total else 0

    report_lines = [
        "# MIRA Phase 4 Benchmark Results",
        "",
        f"Overall accuracy: {passed}/{total} = {overall_accuracy:.2%}",
        f"SQL accuracy: {sql_passed}/{sql_total} = {sql_accuracy:.2%}",
        f"RAG accuracy: {rag_passed}/{rag_total} = {rag_accuracy:.2%}",
        "",
        "| ID | Type | Score | Intent | Validation | Retries | Latency ms | Reason |",
        "|---|---|---:|---|---|---:|---:|---|"
    ]

    for row in rows:
        report_lines.append(
            f"| {row['id']} | {row['type']} | {row['score']} | {row['intent']} | "
            f"{row['validation_status']} | {row['retry_count']} | {row['latency_ms']} | {row['reason']} |"
        )

    RESULTS_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nBenchmark complete")
    print(f"Overall accuracy: {overall_accuracy:.2%}")
    print(f"SQL accuracy: {sql_accuracy:.2%}")
    print(f"RAG accuracy: {rag_accuracy:.2%}")
    print(f"Results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()