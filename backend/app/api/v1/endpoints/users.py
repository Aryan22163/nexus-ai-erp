import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.core.exceptions import NexusException
from app.core.security import get_password_hash
from app.models.auth import Organization
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=List[UserResponse],
    dependencies=[Depends(RequirePermissions("users.read"))],
)
async def list_users(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 50,
) -> List[UserResponse]:
    """List users belonging to the active organization (requires users.read)."""
    user_repo = UserRepository(db, organization_id=tenant.id)
    users = await user_repo.list_by_organization(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("users.create"))],
)
async def create_user(
    payload: UserCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Create a new user within the organization and assign roles (requires users.create)."""
    user_repo = UserRepository(db, organization_id=tenant.id)
    role_repo = RoleRepository(db, organization_id=tenant.id)

    # Check if user already exists
    existing = await user_repo.get_by_email(payload.email)
    if existing:
        raise NexusException(f"User with email '{payload.email}' already exists.")

    # Resolve roles
    assigned_roles = []
    for r_id in payload.role_ids:
        role = await role_repo.get_by_id(r_id)
        if role:
            assigned_roles.append(role)

    user = await user_repo.create(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        organization_id=tenant.id,
        is_active=True,
        roles=assigned_roles,
    )

    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(RequirePermissions("users.read"))],
)
async def get_user_by_id(
    user_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Retrieve details for a specific user in the organization."""
    user_repo = UserRepository(db, organization_id=tenant.id)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserResponse.model_validate(user)
