import os
import hashlib
import psycopg2
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# --- Config ---
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "dbname": os.getenv("POSTGRES_DB", "cliniq_db"),
    "user": os.getenv("POSTGRES_USER", "cliniq"),
    "password": os.getenv("POSTGRES_PASSWORD", "cliniq_pass"),
}
DOCUMENTS_DIR = Path(__file__).parent / "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 200       # tokens (approximate — we'll use word count as proxy)
CHUNK_OVERLAP = 40


def get_document_type(path: Path) -> str:
    parent = path.parent.name
    mapping = {"guidelines": "guideline", "protocols": "protocol", "policies": "policy"}
    return mapping.get(parent, "guideline")


def compute_file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Splits text into overlapping chunks by word count.
    chunk_size and overlap are approximate token counts (words ≈ tokens for English).
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap  # slide forward with overlap
    return chunks


def get_already_embedded(conn) -> dict:
    """Returns {document_name: file_hash} for all already-embedded docs."""
    with conn.cursor() as cur:
        cur.execute("SELECT document_name, file_hash FROM document_ingestion_log")
        return {row[0]: row[1] for row in cur.fetchall()}


def delete_document_chunks(conn, document_name: str):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clinical_document_chunks WHERE document_name = %s", (document_name,))
        cur.execute("DELETE FROM document_ingestion_log WHERE document_name = %s", (document_name,))
    conn.commit()


def insert_chunks(conn, document_name: str, document_type: str, chunks: List[str], embeddings: np.ndarray):
    with conn.cursor() as cur:
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                """
                INSERT INTO clinical_document_chunks
                    (document_name, document_type, chunk_index, chunk_text, embedding, token_count)
                VALUES (%s, %s, %s, %s, %s::vector, %s)
                ON CONFLICT (document_name, chunk_index) DO UPDATE
                    SET chunk_text = EXCLUDED.chunk_text,
                        embedding = EXCLUDED.embedding,
                        token_count = EXCLUDED.token_count
                """,
                (document_name, document_type, i, chunk, embedding.tolist(), len(chunk.split()))
            )
    conn.commit()


def log_ingestion(conn, document_name: str, file_hash: str, chunk_count: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO document_ingestion_log (document_name, file_hash, chunk_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (document_name) DO UPDATE
                SET file_hash = EXCLUDED.file_hash,
                    chunk_count = EXCLUDED.chunk_count,
                    embedded_at = NOW()
            """,
            (document_name, file_hash, chunk_count)
        )
    conn.commit()


def build_ivfflat_index(conn):
    """Build ANN index — only useful after enough rows exist."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM clinical_document_chunks")
        count = cur.fetchone()[0]
    if count >= 100:
        print(f"Building IVFFlat index on {count} chunks...")
        with conn.cursor() as cur:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding
                ON clinical_document_chunks
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 50)
            """)
        conn.commit()
        print("Index built.")
    else:
        print(f"Only {count} chunks — skipping IVFFlat index (need >= 100).")


def run_embedding_pipeline(force_reembed: bool = False):
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    conn = psycopg2.connect(**DB_CONFIG)
    already_embedded = get_already_embedded(conn)
    print(f"Found {len(already_embedded)} already-embedded documents.")

    doc_files = list(DOCUMENTS_DIR.rglob("*.txt"))
    print(f"Found {len(doc_files)} documents in corpus.")

    new_count = 0
    skipped_count = 0

    for doc_path in doc_files:
        doc_name = doc_path.stem
        doc_type = get_document_type(doc_path)
        file_hash = compute_file_hash(doc_path)

        # Skip if unchanged (unless force)
        if not force_reembed and doc_name in already_embedded:
            if already_embedded[doc_name] == file_hash:
                print(f"  SKIP (unchanged): {doc_name}")
                skipped_count += 1
                continue
            else:
                print(f"  CHANGED: {doc_name} — re-embedding")
                delete_document_chunks(conn, doc_name)

        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        print(f"  EMBEDDING: {doc_name} ({len(chunks)} chunks, type={doc_type})")

        embeddings = model.encode(chunks, show_progress_bar=False, convert_to_numpy=True)

        insert_chunks(conn, doc_name, doc_type, chunks, embeddings)
        log_ingestion(conn, doc_name, file_hash, len(chunks))
        new_count += 1

    print(f"\nDone. Embedded: {new_count}, Skipped: {skipped_count}")
    build_ivfflat_index(conn)
    conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Re-embed all documents even if unchanged")
    args = parser.parse_args()
    run_embedding_pipeline(force_reembed=args.force)