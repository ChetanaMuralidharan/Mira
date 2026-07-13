import os
import psycopg2
import psycopg2.extras
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "dbname": os.getenv("POSTGRES_DB", "cliniq_db"),
    "user": os.getenv("POSTGRES_USER", "cliniq"),
    "password": os.getenv("POSTGRES_PASSWORD", "cliniq_pass"),
}

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_model = None  # lazy load


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def vector_search(conn, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
    """Cosine similarity search against pgvector."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT
                id,
                document_name,
                document_type,
                chunk_index,
                chunk_text,
                1 - (embedding <=> %s::vector) AS score
            FROM clinical_document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding.tolist(), query_embedding.tolist(), top_k)
        )
        return [dict(row) for row in cur.fetchall()]


def keyword_search(conn, query: str, top_k: int = 10) -> List[Dict]:
    """Full-text search using PostgreSQL tsvector."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT
                id,
                document_name,
                document_type,
                chunk_index,
                chunk_text,
                ts_rank(
                    to_tsvector('english', chunk_text),
                    plainto_tsquery('english', %s)
                ) AS score
            FROM clinical_document_chunks
            WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s)
            ORDER BY score DESC
            LIMIT %s
            """,
            (query, query, top_k)
        )
        return [dict(row) for row in cur.fetchall()]


def reciprocal_rank_fusion(
    vector_results: List[Dict],
    keyword_results: List[Dict],
    k: int = 60,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> List[Dict]:
    """
    Merges two ranked lists using Reciprocal Rank Fusion.
    RRF score = sum(weight / (k + rank)) across lists.
    k=60 is the standard constant that dampens the effect of rank position.
    """
    scores: Dict[int, float] = {}
    chunk_map: Dict[int, Dict] = {}

    for rank, result in enumerate(vector_results, start=1):
        chunk_id = result["id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + vector_weight / (k + rank)
        chunk_map[chunk_id] = result

    for rank, result in enumerate(keyword_results, start=1):
        chunk_id = result["id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + keyword_weight / (k + rank)
        chunk_map[chunk_id] = result

    sorted_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    merged = []
    for chunk_id in sorted_ids:
        chunk = dict(chunk_map[chunk_id])
        chunk["rrf_score"] = scores[chunk_id]
        merged.append(chunk)

    return merged


def hybrid_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Main entry point. Runs vector + keyword search, fuses with RRF,
    returns top_k chunks with source attribution.
    """
    model = get_model()
    query_embedding = model.encode([query], convert_to_numpy=True)[0]

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        vector_results = vector_search(conn, query_embedding, top_k=10)
        keyword_results = keyword_search(conn, query, top_k=10)
        merged = reciprocal_rank_fusion(vector_results, keyword_results)
        return merged[:top_k]
    finally:
        conn.close()


def list_document_sources() -> List[Dict]:
    """Returns available documents — used by the MCP server and frontend."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT document_name, document_type, chunk_count, embedded_at
                FROM document_ingestion_log
                ORDER BY document_type, document_name
            """)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


if __name__ == "__main__":
    # Quick smoke test
    results = hybrid_search("A1c target for elderly diabetic patients", top_k=3)
    for r in results:
        print(f"\n[{r['document_name']} — chunk {r['chunk_index']}] (rrf={r['rrf_score']:.4f})")
        print(r['chunk_text'][:300])