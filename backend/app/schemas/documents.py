import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    file_name: str
    file_type: str
    file_size: int
    is_processed: bool
    total_chunks: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, examples=["What is the return policy for damaged goods?"])
    top_k: int = Field(default=3, ge=1, le=10)


class RAGSearchResultItem(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    similarity_score: float
    chunk_index: int


class RAGSearchResponse(BaseModel):
    query: str
    results: List[RAGSearchResultItem]
    citations: List[str]
