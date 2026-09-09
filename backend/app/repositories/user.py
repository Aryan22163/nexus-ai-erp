import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.auth import Role, User


class UserRepository:
    def __init__(self, session: AsyncSession, organization_id: Optional[uuid.UUID] = None):
        self.session = session
        self.organization_id = organization_id

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.organization),
            )
            .where(User.id == user_id, User.is_deleted.is_(False))
        )
        if self.organization_id:
            stmt = stmt.where(User.organization_id == self.organization_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.organization),
            )
            .where(User.email == email.lower(), User.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        assert self.organization_id is not None, "organization_id required to list tenant users"
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.organization_id == self.organization_id, User.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        organization_id: uuid.UUID,
        is_active: bool = True,
        is_superuser: bool = False,
        roles: Optional[Sequence[Role]] = None,
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        if roles:
            user.roles = list(roles)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
