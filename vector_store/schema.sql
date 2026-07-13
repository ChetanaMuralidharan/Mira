-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Main document chunks table
CREATE TABLE IF NOT EXISTS clinical_document_chunks (
    id              SERIAL PRIMARY KEY,
    document_name   TEXT NOT NULL,
    document_type   TEXT NOT NULL CHECK (document_type IN ('guideline', 'protocol', 'policy')),
    chunk_index     INTEGER NOT NULL,
    chunk_text      TEXT NOT NULL,
    embedding       vector(384),         -- matches all-MiniLM-L6-v2 output
    token_count     INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (document_name, chunk_index)
);

-- Tracks which documents have been embedded (for incremental updates)
CREATE TABLE IF NOT EXISTS document_ingestion_log (
    id              SERIAL PRIMARY KEY,
    document_name   TEXT UNIQUE NOT NULL,
    file_hash       TEXT NOT NULL,       -- MD5 of file content
    chunk_count     INTEGER NOT NULL,
    embedded_at     TIMESTAMP DEFAULT NOW()
);

-- Full-text search index (for hybrid search keyword path)
CREATE INDEX IF NOT EXISTS idx_chunks_fts 
    ON clinical_document_chunks 
    USING GIN (to_tsvector('english', chunk_text));

-- ANN index for fast vector search (build after initial load)
-- IVFFlat requires at least ~1000 rows before it's useful
-- You'll create this after loading all documents
-- CREATE INDEX idx_chunks_embedding ON clinical_document_chunks 
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);