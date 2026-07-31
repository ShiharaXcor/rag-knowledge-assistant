from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str
    user_role: str = "employee"
    chat_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    blocked: bool


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    allowed_roles: List[str]


class DocumentInfo(BaseModel):
    filename: str
    chunk_count: int
    allowed_roles: List[str]


class DeleteResponse(BaseModel):
    filename: str
    chunks_deleted: int