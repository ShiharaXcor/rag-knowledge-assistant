import sys
from pathlib import Path
from typing import List, Dict
import re

# Allow imports from sibling folders (security)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from security.rbac import get_allowed_roles, load_permissions


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
            overlap_text = current_chunk[-overlap:] if overlap and current_chunk else ""
            current_chunk = overlap_text + para + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_documents(documents: List[Dict], chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Take loaded documents and produce chunk-level records with metadata,
    including RBAC role permissions per source document.
    """
    all_chunks = []
    permissions = load_permissions()

    for doc in documents:
        chunks = chunk_text(doc["content"], chunk_size, overlap)
        allowed_roles = get_allowed_roles(doc["filename"], permissions)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["filename"],
                "chunk_id": f"{doc['filename']}_{i}",
                "chunk_index": i,
                "allowed_roles": ",".join(allowed_roles),
            })

    return all_chunks


if __name__ == "__main__":
    from loader import load_all_documents

    current_dir = Path(__file__).resolve().parent
    raw_data_path = current_dir.parent.parent / "data" / "raw"

    docs = load_all_documents(str(raw_data_path))
    chunks = chunk_documents(docs)

    print(f"\nTotal chunks created: {len(chunks)}")
    if chunks:
        print(f"\nSample chunk:\n{chunks[0]['text'][:200]}...")
        print(f"Allowed roles: {chunks[0]['allowed_roles']}")