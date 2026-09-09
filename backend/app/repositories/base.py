import uuid
from typing import Any, Generic, Sequence, Type, TypeVar
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import TenantBaseModel

ModelType = TypeVar("ModelType", bound=TenantBaseModel)


class BaseTenantRepository(Generic[ModelType]):
    """Generic repository that strictly enforces multi-tenant scoping on all queries."""

    def __init__(self, model: Type[ModelType], session: AsyncSession, organization_id: uuid.UUID):
        self.model = model
        self.session = session
        self.organization_id = organization_id

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Fetch entity by ID, strictly filtered by the active organization and soft-delete flag."""
        stmt = (
            select(self.model)
            .where(
                self.model.id == id,
                self.model.organization_id == self.organization_id,
                self.model.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """List entities for the active organization."""
        stmt = (
            select(self.model)
            .where(
                self.model.organization_id == self.organization_id,
                self.model.is_deleted.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new entity, unconditionally setting organization_id to the tenant context."""
        kwargs["organization_id"] = self.organization_id
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: uuid.UUID) -> bool:
        """Soft-delete an entity within the organization scope."""
        stmt = (
            update(self.model)
            .where(
                self.model.id == id,
                self.model.organization_id == self.organization_id,
                self.model.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
