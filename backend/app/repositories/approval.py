import uuid
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.approval import ApprovalRequest
from app.repositories.base import BaseTenantRepository


class ApprovalRepository(BaseTenantRepository[ApprovalRequest]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(ApprovalRequest, session, organization_id)

    async def list_pending(self) -> Sequence[ApprovalRequest]:
        stmt = (
            select(ApprovalRequest)
            .where(
                ApprovalRequest.organization_id == self.organization_id,
                ApprovalRequest.status == "PENDING",
                ApprovalRequest.is_deleted.is_(False),
            )
            .order_by(ApprovalRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
