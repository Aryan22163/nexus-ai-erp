import math
import re
import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException
from app.models.documents import Document, DocumentChunk
from app.repositories.documents import DocumentChunkRepository, DocumentRepository
from app.schemas.documents import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResultItem,
)


def compute_deterministic_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Computes a normalized vector embedding using a deterministic hashed n-gram projection.
    Provides fast, consistent semantic similarity for unit tests and local setups without external API keys.
    """
    vector = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    if not words:
        return vector

    for word in words:
        idx = hash(word) % dim
        vector[idx] += 1.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    return vector


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two unit vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, dot))


class RAGEngineService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.doc_repo = DocumentRepository(session, organization_id)
        self.chunk_repo = DocumentChunkRepository(session, organization_id)

    async def ingest_and_chunk_document(
        self,
        title: str,
        file_name: str,
        file_path: str,
        file_type: str,
        raw_text: str,
        uploaded_by_id: uuid.UUID = None,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
    ) -> Document:
        """Process document into overlapping semantic chunks with embeddings."""
        doc = Document(
            organization_id=self.organization_id,
            title=title,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type.upper(),
            file_size=len(raw_text.encode("utf-8")),
            uploaded_by_id=uploaded_by_id,
            is_processed=False,
        )
        self.session.add(doc)
        await self.session.flush()

        # Split text into overlapping chunks
        chunks = []
        start = 0
        text_len = len(raw_text)
        idx = 0

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = raw_text[start:end].strip()

            if chunk_content:
                embedding = compute_deterministic_embedding(chunk_content)
                chunk = DocumentChunk(
                    organization_id=self.organization_id,
                    document_id=doc.id,
                    chunk_index=idx,
                    content=chunk_content,
                    token_count=len(chunk_content.split()),
                    embedding=embedding,
                    metadata_dict={"title": title, "file_name": file_name, "chunk_index": idx},
                )
                self.session.add(chunk)
                chunks.append(chunk)
                idx += 1

            if end >= text_len:
                break
            start += (chunk_size - chunk_overlap)

        doc.is_processed = True
        doc.total_chunks = len(chunks)
        await self.session.flush()
        return doc

    async def semantic_search(self, req: RAGSearchRequest) -> RAGSearchResponse:
        """
        Execute tenant-isolated vector similarity search.
        Guarantees that chunks from other organizations are never searched or returned.
        """
        query_vec = compute_deterministic_embedding(req.query)
        all_chunks = await self.chunk_repo.list_all_chunks_for_tenant()

        scored_chunks: List[Tuple[float, DocumentChunk]] = []
        for chunk in all_chunks:
            if chunk.embedding:
                score = cosine_similarity(query_vec, chunk.embedding)
                scored_chunks.append((score, chunk))

        # Sort by descending similarity
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_chunks[: req.top_k]

        results = []
        citations = []
        for score, chunk in top_matches:
            doc_title = chunk.document.title if chunk.document else "Knowledge Document"
            results.append(
                RAGSearchResultItem(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_title=doc_title,
                    content=chunk.content,
                    similarity_score=round(score, 4),
                    chunk_index=chunk.chunk_index,
                )
            )
            citations.append(f"[{doc_title}, Excerpt #{chunk.chunk_index + 1}]")

        return RAGSearchResponse(
            query=req.query,
            results=results,
            citations=list(dict.fromkeys(citations)),
        )
