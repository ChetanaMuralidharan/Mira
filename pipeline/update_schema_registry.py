import json
import sys
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "docs" / "schema_registry.json"
DBT_TARGET_DIR = Path(__file__).parent.parent / "dbt_project" / "target"


def build_schema_registry():
    manifest_path = DBT_TARGET_DIR / "manifest.json"
    catalog_path = DBT_TARGET_DIR / "catalog.json"

    if not manifest_path.exists():
        print("manifest.json not found. Run 'dbt docs generate' first.")
        sys.exit(1)

    if not catalog_path.exists():
        print("catalog.json not found. Run 'dbt docs generate' first.")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    with open(catalog_path) as f:
        catalog = json.load(f)

    registry = {"tables": []}

    for node_id, node in manifest["nodes"].items():
        if node["resource_type"] != "model":
            continue
        if node["config"]["schema"] not in ["marts", "metrics"]:
            continue

        table_name = node["name"]
        description = node.get("description", "")

        # Pull documented descriptions from manifest
        manifest_cols = {
            col_name: col_info.get("description", "")
            for col_name, col_info in node.get("columns", {}).items()
        }

        # Pull actual columns from catalog (has everything, not just documented ones)
        columns = []
        catalog_node = catalog.get("nodes", {}).get(node_id, {})
        catalog_cols = catalog_node.get("columns", {})

        for col_name, col_info in catalog_cols.items():
            columns.append({
                "name": col_name,
                "description": manifest_cols.get(col_name, ""),
                "data_type": col_info.get("type", "unknown"),
            })

        registry["tables"].append({
            "name": table_name,
            "schema": node["config"]["schema"],
            "full_name": f"main_{node['config']['schema']}.{table_name}",
            "description": description,
            "columns": columns,
        })

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    print(f"Schema registry written to {REGISTRY_PATH}")
    print(f"Tables registered: {len(registry['tables'])}")
    for t in registry["tables"]:
        print(f"  {t['full_name']}: {len(t['columns'])} columns")


if __name__ == "__main__":
    build_schema_registry()