import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from vector_store.retriever import hybrid_search, list_document_sources

mcp = FastMCP("cliniq-vector-server", port=8766)


@mcp.tool()
def search_clinical_documents(query: str, top_k: int = 5) -> str:
    """Search the clinical document knowledge base using hybrid vector + keyword search.
    Use for questions about clinical guidelines, protocols, policies, standards of care,
    medication contraindications, and readmission criteria. Returns the most relevant
    document chunks with source attribution."""
    print(f"[VECTOR SERVER] search_clinical_documents: {query[:60]}", file=sys.stderr, flush=True)

    results = hybrid_search(query, top_k=top_k)

    if not results:
        return json.dumps({"chunks": [], "message": "No relevant documents found."})

    formatted = []
    for r in results:
        formatted.append({
            "document_name": r["document_name"],
            "document_type": r["document_type"],
            "chunk_index": r["chunk_index"],
            "chunk_text": r["chunk_text"],
            "relevance_score": round(r["rrf_score"], 4)
        })

    return json.dumps({"chunks": formatted, "query": query, "count": len(formatted)})


@mcp.tool()
def list_document_sources_tool() -> str:
    """Returns the list of clinical documents available in the knowledge base,
    including document type (guideline/protocol/policy) and when it was last embedded.
    Use this to tell users what topics the knowledge base covers."""
    sources = list_document_sources()
    return json.dumps({"sources": sources, "total": len(sources)})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")