import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from ingestion.chunker import split_into_paragraphs, chunk_text


def test_split_into_paragraphs_basic():
    text = "First paragraph.\n\nSecond paragraph."
    result = split_into_paragraphs(text)
    assert len(result) == 2
    assert result[0] == "First paragraph."


def test_chunk_text_respects_size_limit():
    text = "A" * 100 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100
    chunks = chunk_text(text, chunk_size=150, overlap=10)
    assert len(chunks) >= 2


def test_chunk_text_handles_empty_string():
    chunks = chunk_text("", chunk_size=500, overlap=50)
    assert chunks == []