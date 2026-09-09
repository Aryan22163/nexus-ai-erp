import uuid
from typing import Annotated, Callable, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.exceptions import PermissionDeniedException, TenantIsolationException
from app.core.security import decode_token
from app.models.auth import Organization, User
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository

security = HTTPBearer()


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]
) -> dict:
    """Extract and validate JWT Bearer token payload."""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token expected.",
            )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    payload: Annotated[dict, Depends(get_token_payload)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Fetch the currently authenticated user from database."""
    try:
        user_id = uuid.UUID(payload.get("sub"))
        org_id = uuid.UUID(payload.get("org_id"))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
        )

    user_repo = UserRepository(db, organization_id=org_id)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been revoked.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    return user


async def get_current_tenant(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Organization:
    """Ensure the user's active tenant is valid and active."""
    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_id(current_user.organization_id)

    if not org or not org.is_active:
        raise TenantIsolationException("Organization is inactive or disabled.")

    return org


class RequirePermissions:
    """Dependency factory checking whether the current user has the required RBAC permissions."""
    def __init__(self, *required_permissions: str):
        self.required_permissions = set(required_permissions)

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.is_superuser:
            return current_user

        user_perms = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_perms.add(perm.code)

        missing = self.required_permissions - user_perms
        if missing:
            raise PermissionDeniedException(f"Missing required permission(s): {', '.join(sorted(missing))}")

        return current_user
