import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import duckdb
from mcp.server.fastmcp import FastMCP

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = os.getenv("DUCKDB_PATH", str(PROJECT_ROOT / "cliniq.duckdb"))
SCHEMA_REGISTRY_PATH = PROJECT_ROOT / "docs" / "schema_registry.json"

print(f"[SERVER] DB_PATH={DB_PATH}", file=sys.stderr, flush=True)
print(f"[SERVER] DB exists={Path(DB_PATH).exists()}", file=sys.stderr, flush=True)

mcp = FastMCP("cliniq-database-server", port=8765)


def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


def is_select_only(sql: str) -> bool:
    stripped = sql.strip().lower().rstrip(";").strip()
    if not stripped.startswith("select"):
        return False
    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "truncate", "attach", "copy"]
    return not any(f" {word} " in f" {stripped} " for word in forbidden)


@mcp.tool()
def query_clinical_database(sql: str) -> str:
    """Executes a read-only SELECT query against the clinical DuckDB warehouse.
    Returns rows as JSON. Rejects non-SELECT statements. Auto-applies a 1000-row limit."""
    print(f"[SERVER] query_clinical_database entered", file=sys.stderr, flush=True)
    if not is_select_only(sql):
        return json.dumps({"error": "Only single, read-only SELECT statements are permitted."})
    try:
        final_sql = sql if "limit" in sql.lower() else sql.rstrip(";") + " LIMIT 1000"
        print(f"[SERVER] running query: {final_sql[:80]}", file=sys.stderr, flush=True)
        conn = get_connection()
        try:
            df = conn.execute(final_sql).fetchdf()
        finally:
            conn.close()
        print(f"[SERVER] query done, rows={len(df)}", file=sys.stderr, flush=True)
        return df.to_json(orient="records")
    except Exception as e:
        print(f"[SERVER] exception: {e}", file=sys.stderr, flush=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_schema_info(tables: list[str]) -> str:
    """Returns column-level schema and descriptions for specified tables, sourced from dbt docs."""
    try:
        registry = json.loads(SCHEMA_REGISTRY_PATH.read_text())
        all_tables = registry["tables"]
        requested = set(tables)
        subset = [t for t in all_tables if t["name"] in requested]
        return json.dumps(subset)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_metric_summary(metric_name: str) -> str:
    """Returns precomputed values from a metrics_* dbt model instead of running ad-hoc SQL."""
    try:
        conn = get_connection()
        try:
            df = conn.execute(f"SELECT * FROM {metric_name}").fetchdf()
        finally:
            conn.close()
        return df.to_json(orient="records")
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")