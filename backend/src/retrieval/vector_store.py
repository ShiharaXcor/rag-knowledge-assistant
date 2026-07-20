import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.config import Settings
import ollama
from utils.config import VECTOR_DB_PATH, OLLAMA_EMBED_MODEL, COLLECTION_NAME, TOP_K
from security.rbac import is_allowed
from retrieval.hybrid_search import build_bm25_index, bm25_search, reciprocal_rank_fusion
from retrieval.reranker import rerank


def get_chroma_client():
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH),
        settings=Settings(anonymized_telemetry=False)
    )


def get_or_create_collection(client):
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_text(text: str) -> list:
    response = ollama.embeddings(model=OLLAMA_EMBED_MODEL, prompt=text)
    return response["embedding"]


def add_chunks_to_store(chunks: list):
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    ids, embeddings, documents, metadatas = [], [], [], []

    for chunk in chunks:
        print(f"Embedding chunk: {chunk['chunk_id']}")
        embedding = embed_text(chunk["text"])

        ids.append(chunk["chunk_id"])
        embeddings.append(embedding)
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "allowed_roles": chunk["allowed_roles"],
        })

    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    print(f"\nStored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'")


def get_all_chunks_from_store():
    """
    Pull every chunk currently stored in Chroma, formatted for BM25 indexing.
    Needed because BM25 requires the full corpus, not just top-k vector matches.
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    data = collection.get()  # returns all documents + metadatas

    all_chunks = []
    for i in range(len(data["ids"])):
        all_chunks.append({
            "text": data["documents"][i],
            "source": data["metadatas"][i]["source"],
            "chunk_index": data["metadatas"][i]["chunk_index"],
        })

    return all_chunks


def vector_search(query: str, user_role: str, top_k: int = 5):
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    query_embedding = embed_text(query)
    
    # Don't request more than what's actually in the collection
    collection_count = collection.count()
    n_results = min(top_k * 3, collection_count)
    
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

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


def query_store(query: str, user_role: str = "employee", top_k: int = TOP_K, use_hybrid: bool = True, use_reranking: bool = True):
    """
    Full retrieval pipeline: vector search + BM25 (hybrid) -> fusion -> re-ranking.
    Set use_hybrid=False or use_reranking=False to isolate stages for testing.
    """
    # Stage 1: Vector search (over-fetch for better fusion/re-ranking candidates)
    vector_results = vector_search(query, user_role, top_k=top_k * 2)

    if not use_hybrid:
        return vector_results[:top_k]

    # Stage 2: BM25 keyword search over the full corpus
    all_chunks = get_all_chunks_from_store()
    bm25, indexed_chunks = build_bm25_index(all_chunks)
    bm25_results = bm25_search(query, bm25, indexed_chunks, user_role, top_k=top_k * 2)

    # Stage 3: Fuse both result sets
    fused_results = reciprocal_rank_fusion(vector_results, bm25_results, top_k=top_k * 2)

    if not use_reranking:
        return fused_results[:top_k]

    # Stage 4: Cross-encoder re-ranking for final precision pass
    final_results = rerank(query, fused_results, top_k=top_k)

    return final_results


if __name__ == "__main__":
    from ingestion.loader import load_all_documents
    from ingestion.chunker import chunk_documents
    from utils.config import RAW_DATA_PATH

    print("Loading documents...")
    docs = load_all_documents(str(RAW_DATA_PATH))

    print("\nChunking documents...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print("\nEmbedding and storing in ChromaDB...")
    add_chunks_to_store(chunks)

    print("\n--- Full Hybrid + Re-ranked Query Test ---")
    test_query = "How many days of annual leave do I get?"
    results = query_store(test_query, user_role="employee")

    print(f"\nQuery: {test_query}\n")
    for r in results:
        rerank_score = r.get("rerank_score", "N/A")
        print(f"[{r['source']} | chunk {r['chunk_index']} | rerank_score: {rerank_score}]")
        print(r["text"][:200])
        print("---")

    print("\n--- RBAC Check: employee vs hr on confidential query ---")
    salary_query = "What is the salary range for a Staff Engineer?"

    emp_results = query_store(salary_query, user_role="employee")
    print(f"Employee results: {[r['source'] for r in emp_results]}")

    hr_results = query_store(salary_query, user_role="hr")
    print(f"HR results: {[r['source'] for r in hr_results]}")