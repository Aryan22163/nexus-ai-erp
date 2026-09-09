import uuid
from typing import Any, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_id: Optional[uuid.UUID] = None,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
        is_ai_initiated: bool = False,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            organization_id=self.organization_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=before_state,
            after_state=after_state,
            is_ai_initiated=is_ai_initiated,
            ip_address=ip_address,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_recent(self, limit: int = 50) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.organization_id == self.organization_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
