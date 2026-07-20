from typing import List, Dict
from pathlib import Path
import re

def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs, cleaning up whitespace."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Heading/paragraph-aware chunking.
    Groups paragraphs together up to chunk_size characters,
    with a small overlap between chunks for context continuity.
    """
    paragraphs = split_into_paragraphs(text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # start new chunk, carry a small overlap from the end of the last one
            overlap_text = current_chunk[-overlap:] if overlap and current_chunk else ""
            current_chunk = overlap_text + para + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_documents(documents: List[Dict], chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Take loaded documents and produce chunk-level records with metadata.
    Each chunk becomes its own record, ready for embedding + indexing.
    """
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["content"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["filename"],
                "chunk_id": f"{doc['filename']}_{i}",
                "chunk_index": i,
            })

    return all_chunks


if __name__ == "__main__":
    from loader import load_all_documents

    # Resolve path relative to THIS file's location, not the terminal's cwd
    current_dir = Path(__file__).resolve().parent
    raw_data_path = current_dir.parent.parent / "data" / "raw"

    docs = load_all_documents(str(raw_data_path))
    chunks = chunk_documents(docs)

    print(f"\nTotal chunks created: {len(chunks)}")
    if chunks:
        print(f"\nSample chunk:\n{chunks[0]['text'][:200]}...")