import uuid
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.auth import Permission, Role, role_permissions


class RoleRepository:
    def __init__(self, session: AsyncSession, organization_id: Optional[uuid.UUID] = None):
        self.session = session
        self.organization_id = organization_id

    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name)
        )
        if self.organization_id:
            stmt = stmt.where(
                (Role.organization_id == self.organization_id) | (Role.organization_id.is_(None))
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_available_roles(self) -> Sequence[Role]:
        """List all system roles + tenant-specific custom roles."""
        stmt = select(Role).options(selectinload(Role.permissions))
        if self.organization_id:
            stmt = stmt.where(
                (Role.organization_id == self.organization_id) | (Role.organization_id.is_(None))
            )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_permissions(self) -> Sequence[Permission]:
        stmt = select(Permission).order_by(Permission.module, Permission.code)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permissions_by_codes(self, codes: List[str]) -> Sequence[Permission]:
        stmt = select(Permission).where(Permission.code.in_(codes))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_role(
        self,
        name: str,
        description: Optional[str],
        permissions: List[Permission],
        is_system: bool = False,
    ) -> Role:
        role = Role(
            name=name,
            description=description,
            organization_id=self.organization_id,
            is_system=is_system,
        )
        role.permissions = list(permissions)
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role
