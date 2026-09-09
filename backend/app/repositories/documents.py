import uuid
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.documents import Document, DocumentChunk
from app.repositories.base import BaseTenantRepository


class DocumentRepository(BaseTenantRepository[Document]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Document, session, organization_id)

    async def get_with_chunks(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = (
            select(Document)
            .options(selectinload(Document.chunks))
            .where(
                Document.id == document_id,
                Document.organization_id == self.organization_id,
                Document.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DocumentChunkRepository(BaseTenantRepository[DocumentChunk]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(DocumentChunk, session, organization_id)

    async def list_all_chunks_for_tenant(self) -> Sequence[DocumentChunk]:
        """Fetch all chunks belonging strictly to the organization."""
        stmt = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(
                DocumentChunk.organization_id == self.organization_id,
                DocumentChunk.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
