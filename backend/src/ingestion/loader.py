import os
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF
import docx


def load_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def load_docx(file_path: str) -> str:
    """Extract text from a Word document."""
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def load_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_document(file_path: str) -> str:
    """Route a file to the correct loader based on its extension."""
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext in (".txt", ".md"):
        return load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def load_all_documents(folder_path: str) -> List[Dict]:
    """
    Load every supported document in a folder.
    Returns a list of dicts: {"filename": ..., "content": ..., "path": ...}
    """
    documents = []
    supported_ext = {".pdf", ".docx", ".txt", ".md"}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        ext = Path(filename).suffix.lower()

        if ext in supported_ext:
            try:
                content = load_document(file_path)
                documents.append({
                    "filename": filename,
                    "content": content,
                    "path": file_path
                })
                print(f"Loaded: {filename} ({len(content)} characters)")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    return documents


if __name__ == "__main__":
    # Resolve path relative to THIS file's location, not wherever the terminal happens to be.
    # loader.py lives at backend/src/ingestion/loader.py
    # so we go up 3 levels to reach backend/, then into data/raw
    current_dir = Path(__file__).resolve().parent
    raw_data_path = current_dir.parent.parent / "data" / "raw"

    docs = load_all_documents(str(raw_data_path))
    print(f"\nTotal documents loaded: {len(docs)}")