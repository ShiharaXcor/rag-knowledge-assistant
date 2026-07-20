import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from rank_bm25 import BM25Okapi
from security.rbac import is_allowed


def build_bm25_index(all_chunks: list):
    """
    Build a BM25 index from all chunks currently in the system.
    all_chunks: list of dicts with at least 'text', 'source', 'chunk_index'
    """
    tokenized_corpus = [chunk["text"].lower().split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, all_chunks


def bm25_search(query: str, bm25, all_chunks: list, user_role: str, top_k: int = 5):
    """
    Run BM25 keyword search, filter by role, return top_k results.
    """
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    scored_chunks = list(zip(all_chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    results = []
    for chunk, score in scored_chunks:
        if is_allowed(chunk["source"], user_role):
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "bm25_score": float(score),
            })
        if len(results) >= top_k:
            break

    return results


def reciprocal_rank_fusion(vector_results: list, bm25_results: list, k: int = 60, top_k: int = 5):
    """
    Combine vector search and BM25 results using Reciprocal Rank Fusion (RRF).
    RRF score = sum(1 / (k + rank)) across each result list a chunk appears in.
    This avoids needing to normalize distance vs BM25 score directly.
    """
    scores = {}
    chunk_lookup = {}

    for rank, chunk in enumerate(vector_results):
        key = f"{chunk['source']}_{chunk['chunk_index']}"
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_lookup[key] = chunk

    for rank, chunk in enumerate(bm25_results):
        key = f"{chunk['source']}_{chunk['chunk_index']}"
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_lookup[key] = chunk

    ranked_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

    fused_results = []
    for key in ranked_keys[:top_k]:
        chunk = chunk_lookup[key]
        chunk["rrf_score"] = scores[key]
        fused_results.append(chunk)

    return fused_results