import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json

from src.retrieval.vector_store import (
    query_store, add_chunks_to_store, get_chroma_client, get_or_create_collection
)
from src.generation.llm import generate_answer_guarded
from src.ingestion.loader import load_all_documents, load_document
from src.ingestion.chunker import chunk_documents
from src.utils.config import RAW_DATA_PATH
from src.utils.logger import get_all_logs
from src.api.schemas import ChatRequest, ChatResponse, UploadResponse, DocumentInfo, DeleteResponse

app = FastAPI(title="Nexora Knowledge Assistant API", version="1.0.0")

# Allow the Streamlit frontend to call this API (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

PERMISSIONS_FILE = RAW_DATA_PATH.parent / "doc_permissions.json"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        retrieved_chunks = query_store(request.query, user_role=request.user_role, top_k=3)
        result = generate_answer_guarded(
            request.query, request.user_role, retrieved_chunks, chat_history=request.chat_history
        )
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            blocked=result.get("blocked", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), allowed_roles: str = Form(...)):
    """allowed_roles: comma-separated string, e.g. 'employee,hr,leadership'"""
    try:
        roles_list = [r.strip() for r in allowed_roles.split(",")]

        RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
        save_path = RAW_DATA_PATH / file.filename
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # Update permissions file
        permissions = {}
        if PERMISSIONS_FILE.exists():
            with open(PERMISSIONS_FILE, "r") as f:
                permissions = json.load(f)
        permissions[file.filename] = roles_list
        with open(PERMISSIONS_FILE, "w") as f:
            json.dump(permissions, f, indent=2)

        # Index the new document
        docs = load_all_documents(str(RAW_DATA_PATH))
        docs = [d for d in docs if d["filename"] == file.filename]
        chunks = chunk_documents(docs)
        add_chunks_to_store(chunks)

        return UploadResponse(filename=file.filename, chunks_indexed=len(chunks), allowed_roles=roles_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=list[DocumentInfo])
def list_documents():
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        data = collection.get()

        permissions = {}
        if PERMISSIONS_FILE.exists():
            with open(PERMISSIONS_FILE, "r") as f:
                permissions = json.load(f)

        doc_counts = {}
        for meta in data["metadatas"]:
            source = meta["source"]
            doc_counts[source] = doc_counts.get(source, 0) + 1

        return [
            DocumentInfo(
                filename=fname,
                chunk_count=count,
                allowed_roles=permissions.get(fname, permissions.get("default", [])),
            )
            for fname, count in doc_counts.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}", response_model=DeleteResponse)
def delete_document(filename: str):
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        data = collection.get()

        ids_to_delete = [
            data["ids"][i] for i in range(len(data["ids"]))
            if data["metadatas"][i]["source"] == filename
        ]
        if not ids_to_delete:
            raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")

        collection.delete(ids=ids_to_delete)
        return DeleteResponse(filename=filename, chunks_deleted=len(ids_to_delete))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/logs")
def get_logs():
    try:
        return get_all_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))