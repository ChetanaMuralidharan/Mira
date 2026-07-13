import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from agent.state import ClinIQState
from agent.prompts import SCHEMA_TABLE_EMBEDDING_TEMPLATE

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMA_REGISTRY_PATH = PROJECT_ROOT / "docs" / "schema_registry.json"

_model = None
_table_embeddings = None
_table_texts = None
_table_names = None


def _get_model():
    global _model
    if _model is None:
        print("[NODE] schema_retriever: loading SentenceTransformer model...", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[NODE] schema_retriever: model loaded", flush=True)
    return _model


def _load_and_embed_schema():
    global _table_embeddings, _table_texts, _table_names
    if _table_embeddings is not None:
        return

    print(f"[NODE] schema_retriever: reading {SCHEMA_REGISTRY_PATH}", flush=True)
    registry = json.loads(SCHEMA_REGISTRY_PATH.read_text())
    tables = registry["tables"]
    model = _get_model()

    _table_names = [t.get("full_name", t["name"]) for t in tables]
    _table_texts = []
    for t in tables:
        columns = t.get("columns", [])
        column_summary = ", ".join(
            f"{c['name']}: {c['description']}" if c.get("description") else c["name"]
            for c in columns
        )
        full_name = t.get("full_name", t["name"])
        _table_texts.append(SCHEMA_TABLE_EMBEDDING_TEMPLATE.format(
            table_name=full_name,
            table_description=t.get("description", ""),
            column_summary=column_summary,
        ))
    print(f"[NODE] schema_retriever: embedding {len(_table_texts)} table descriptions...", flush=True)
    _table_embeddings = model.encode(_table_texts, convert_to_numpy=True)
    print("[NODE] schema_retriever: schema embeddings ready", flush=True)


def _cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int) -> list:
    query_norm = query_vec / np.linalg.norm(query_vec)
    matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    scores = matrix_norm @ query_norm
    top_idx = np.argsort(scores)[::-1][:k]
    return top_idx.tolist()


def schema_retriever(state: ClinIQState) -> ClinIQState:
    print("[NODE] schema_retriever: start", flush=True)
    _load_and_embed_schema()
    model = _get_model()

    query_vec = model.encode([state["user_question"]], convert_to_numpy=True)[0]
    top_idx = _cosine_top_k(query_vec, _table_embeddings, k=5)

    relevant_tables = [_table_names[i] for i in top_idx]
    schema_context = "\n\n".join(_table_texts[i] for i in top_idx)

    state["relevant_tables"] = relevant_tables
    state["schema_context"] = schema_context
    print(f"[NODE] schema_retriever: done, tables={relevant_tables}", flush=True)
    return state