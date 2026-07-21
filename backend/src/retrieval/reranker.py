from sentence_transformers import CrossEncoder

# Loaded once, reused across calls (loading is the slow part)
_model = None


def get_reranker():
    global _model
    if _model is None:
        print("Loading cross-encoder re-ranker model (first call only)...")
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _model


def rerank(query: str, chunks: list, top_k: int = 5):
    """
    Re-rank a list of candidate chunks against the query using a cross-encoder.
    Returns the top_k chunks sorted by relevance score (descending).
    """
    if not chunks:
        return []

    model = get_reranker()
    pairs = [[query, chunk["text"]] for chunk in chunks]
    scores = model.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)

    chunks.sort(key=lambda c: c["rerank_score"], reverse=True)
    return chunks[:top_k]