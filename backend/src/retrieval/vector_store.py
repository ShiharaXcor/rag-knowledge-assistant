import sys
from pathlib import Path

# Allow imports from sibling folders (ingestion, utils, security)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.config import Settings
import ollama
from utils.config import VECTOR_DB_PATH, OLLAMA_EMBED_MODEL, COLLECTION_NAME, TOP_K
from security.rbac import is_allowed


def get_chroma_client():
    """Create a persistent Chroma client stored on disk."""
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH),
        settings=Settings(anonymized_telemetry=False)
    )


def get_or_create_collection(client):
    """Get the collection, or create it if it doesn't exist yet."""
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_text(text: str) -> list:
    """Generate an embedding vector for a piece of text using Ollama."""
    response = ollama.embeddings(model=OLLAMA_EMBED_MODEL, prompt=text)
    return response["embedding"]


def add_chunks_to_store(chunks: list):
    """
    Embed and store a list of chunk dicts (from chunker.py) into ChromaDB.
    Each chunk dict must have: text, source, chunk_id, chunk_index, allowed_roles
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks:
        print(f"Embedding chunk: {chunk['chunk_id']}")
        embedding = embed_text(chunk["text"])

        ids.append(chunk["chunk_id"])
        embeddings.append(embedding)
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "allowed_roles": chunk["allowed_roles"],  # comma-separated string, e.g. "hr,leadership"
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"\nStored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'")


def query_store(query: str, user_role: str = "employee", top_k: int = TOP_K):
    """
    Embed a query, retrieve candidates, then filter by role BEFORE returning.
    We over-fetch (3x top_k) so role-based filtering doesn't starve results.

    Returns a list of dicts: {text, source, chunk_index, distance}
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 3,  # over-fetch so filtering still leaves enough results
    )

    # Handle empty collection / no results edge case
    if not results["ids"] or not results["ids"][0]:
        return []

    candidates = []
    for i in range(len(results["ids"][0])):
        source = results["metadatas"][0][i]["source"]

        if is_allowed(source, user_role):
            candidates.append({
                "text": results["documents"][0][i],
                "source": source,
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
                "distance": results["distances"][0][i],
            })

    return candidates[:top_k]


if __name__ == "__main__":
    # End-to-end test: load -> chunk -> embed -> store -> query (role-aware)
    from ingestion.loader import load_all_documents
    from ingestion.chunker import chunk_documents
    from utils.config import RAW_DATA_PATH

    print("Loading documents...")
    docs = load_all_documents(str(RAW_DATA_PATH))

    print("\nChunking documents...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print("\nEmbedding and storing in ChromaDB (this may take a minute)...")
    add_chunks_to_store(chunks)

    print("\n--- Test Query: employee role ---")
    test_query = "How many days of annual leave do I get?"
    results = query_store(test_query, user_role="employee")

    print(f"\nQuery: {test_query}\n")
    for r in results:
        print(f"[{r['source']} | chunk {r['chunk_index']} | distance {r['distance']:.4f}]")
        print(r["text"][:200])
        print("---")

    print("\n--- Test Query: employee asking about confidential salary data ---")
    salary_query = "What is the salary range for a Staff Engineer?"
    results = query_store(salary_query, user_role="employee")
    print(f"Results returned for employee role: {len(results)} (should NOT include CONFIDENTIAL doc)")
    for r in results:
        print(f"  {r['source']}")

    print("\n--- Test Query: hr asking same question ---")
    results = query_store(salary_query, user_role="hr")
    print(f"Results returned for hr role: {len(results)} (should include confidential doc, likely ranked #1)")
    for r in results:
        print(f"  {r['source']}")